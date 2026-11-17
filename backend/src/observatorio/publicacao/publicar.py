"""Publicação: regrava a camada publico a partir da versão validada (FR-053).

Sempre chamada dentro da mesma transação do merge: ou tudo é publicado, ou nada muda.
"""

from datetime import date, datetime
from decimal import Decimal

import psycopg

from observatorio.catalogo import Indicador
from observatorio.config import FUSO_HORARIO
from observatorio.regras.formatacao import data_br
from observatorio.regras.meses import meses_entre
from observatorio.repositorio.tratado import carregar_vigentes


def serie_para_publicacao(
    vigentes: dict[date, Decimal | None], frequencia: str
) -> list[tuple[date, Decimal | None]]:
    """Recorta ausentes nas pontas e cria linhas 'ausente' para os períodos sem dado no meio.

    Ausentes nas pontas não são lacunas: são períodos ainda não publicados pela fonte.
    """
    com_valor = sorted(d for d, v in vigentes.items() if v is not None)
    if not com_valor:
        return []
    primeira, ultima = com_valor[0], com_valor[-1]
    if frequencia == "anual":
        datas = [date(ano, 1, 1) for ano in range(primeira.year, ultima.year + 1)]
    else:
        datas = meses_entre(primeira, ultima)
    return [(d, vigentes.get(d)) for d in datas]


def _regravar_observacoes(conn: psycopg.Connection, indicador: Indicador) -> list:
    """Regrava publico.observacao_publicada a partir das observações vigentes."""
    serie = serie_para_publicacao(
        carregar_vigentes(conn, indicador.codigo), indicador.frequencia_exibicao
    )
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM publico.observacao_publicada WHERE indicador_codigo = %s",
            (indicador.codigo,),
        )
        cur.executemany(
            """
            INSERT INTO publico.observacao_publicada
              (indicador_codigo, data_referencia, valor, situacao)
            VALUES (%s, %s, %s, %s)
            """,
            [(indicador.codigo, d, v, "ausente" if v is None else "ok") for d, v in serie],
        )
    return serie


def publicar(
    conn: psycopg.Connection, indicador: Indicador, versao_id: int, agora: datetime
) -> None:
    serie = _regravar_observacoes(conn, indicador)
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE tratado.versao_serie SET status = 'substituida'
            WHERE indicador_codigo = %s AND status = 'publicada'
            """,
            (indicador.codigo,),
        )
        cur.execute(
            "UPDATE tratado.versao_serie SET status = 'publicada' WHERE id = %s", (versao_id,)
        )
        cur.execute(
            "UPDATE tratado.indicador SET versao_publicada_id = %s WHERE codigo = %s",
            (versao_id, indicador.codigo),
        )
        cur.execute(
            """
            UPDATE publico.indicador_publicado SET situacao = 'atualizado',
              periodo_inicio = %s, periodo_fim = %s, ultima_atualizacao_valida = %s,
              ultima_tentativa = %s, mensagem_publica = NULL, versao_id = %s
            WHERE codigo = %s
            """,
            (
                serie[0][0] if serie else None,
                serie[-1][0] if serie else None,
                agora,
                agora,
                versao_id,
                indicador.codigo,
            ),
        )


def republicar(conn: psycopg.Connection, indicador: Indicador) -> int:
    """Regrava a camada publico a partir da versão já publicada, sem coletar.

    Útil depois de mudar o catálogo ou corrigir a publicação. Não altera a data de
    atualização: os dados continuam sendo os obtidos na última coleta válida.
    Retorna o número de observações publicadas.
    """
    linha = conn.execute(
        "SELECT versao_publicada_id FROM tratado.indicador WHERE codigo = %s",
        (indicador.codigo,),
    ).fetchone()
    if not linha or linha["versao_publicada_id"] is None:
        raise ValueError(f"{indicador.codigo} ainda não tem versão publicada; rode a coleta")
    serie = _regravar_observacoes(conn, indicador)
    conn.execute(
        """
        UPDATE publico.indicador_publicado SET periodo_inicio = %s, periodo_fim = %s,
          versao_id = %s
        WHERE codigo = %s
        """,
        (
            serie[0][0] if serie else None,
            serie[-1][0] if serie else None,
            linha["versao_publicada_id"],
            indicador.codigo,
        ),
    )
    return len(serie)


def confirmar_atualizacao(conn: psycopg.Connection, codigo: str, agora: datetime) -> None:
    """A fonte foi consultada com sucesso e nada mudou: os dados publicados seguem válidos."""
    conn.execute(
        """
        UPDATE publico.indicador_publicado SET situacao = 'atualizado',
          ultima_atualizacao_valida = %s, ultima_tentativa = %s, mensagem_publica = NULL
        WHERE codigo = %s AND versao_id IS NOT NULL
        """,
        (agora, agora, codigo),
    )


def registrar_falha(conn: psycopg.Connection, codigo: str, agora: datetime) -> None:
    """Marca a falha sem tocar nas observações publicadas.

    A última versão válida continua no ar (FR-053, SC-011).
    """
    linha = conn.execute(
        "SELECT versao_id FROM publico.indicador_publicado WHERE codigo = %s", (codigo,)
    ).fetchone()
    tem_versao = bool(linha and linha["versao_id"])
    quando = data_br(agora.astimezone(FUSO_HORARIO).date())
    mensagem = (
        f"A atualização de {quando} falhou. Exibindo a última versão válida."
        if tem_versao
        else f"A atualização de {quando} falhou e ainda não há versão válida para exibir."
    )
    conn.execute(
        """
        UPDATE publico.indicador_publicado SET situacao = 'falha_atualizacao',
          ultima_tentativa = %s, mensagem_publica = %s
        WHERE codigo = %s
        """,
        (agora, mensagem, codigo),
    )
