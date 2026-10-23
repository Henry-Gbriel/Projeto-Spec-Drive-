"""Acesso à camada tratada: versões, observações vigentes e ocorrências."""

import os
import subprocess
from datetime import date
from decimal import Decimal

import psycopg
from psycopg.types.json import Jsonb

from observatorio.config import RAIZ_REPOSITORIO
from observatorio.tratamento.merge import Diferencas
from observatorio.tratamento.modelos import Ocorrencia


def versao_do_codigo() -> str:
    """Identifica a versão do código de tratamento (reprodutibilidade, Princípio IV)."""
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.run(  # noqa: S603
            ["git", "rev-parse", "HEAD"],  # noqa: S607
            cwd=RAIZ_REPOSITORIO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconhecida"


def travar_indicador(conn: psycopg.Connection, codigo: str) -> None:
    """Impede duas rotinas simultâneas no mesmo indicador (vale até o fim da transação)."""
    conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (codigo,))


def ultima_data_vigente(conn: psycopg.Connection, codigo: str) -> date | None:
    linha = conn.execute(
        """
        SELECT max(data_referencia) AS ultima FROM tratado.observacao
        WHERE indicador_codigo = %s AND versao_fim_id IS NULL
        """,
        (codigo,),
    ).fetchone()
    return linha["ultima"]


def carregar_vigentes(
    conn: psycopg.Connection, codigo: str, inicio: date | None = None, fim: date | None = None
) -> dict[date, Decimal | None]:
    linhas = conn.execute(
        """
        SELECT data_referencia, valor FROM tratado.observacao
        WHERE indicador_codigo = %s AND versao_fim_id IS NULL
          AND (%s::date IS NULL OR data_referencia >= %s::date)
          AND (%s::date IS NULL OR data_referencia <= %s::date)
        ORDER BY data_referencia
        """,
        (codigo, inicio, inicio, fim, fim),
    ).fetchall()
    return {linha["data_referencia"]: linha["valor"] for linha in linhas}


def criar_versao(conn: psycopg.Connection, codigo: str, coleta_id: int, status: str) -> int:
    linha = conn.execute(
        """
        INSERT INTO tratado.versao_serie (indicador_codigo, coleta_id, status, versao_codigo)
        VALUES (%s, %s, %s, %s) RETURNING id
        """,
        (codigo, coleta_id, status, versao_do_codigo()),
    ).fetchone()
    return linha["id"]


def registrar_ocorrencias(
    conn: psycopg.Connection, versao_id: int, ocorrencias: list[Ocorrencia]
) -> None:
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO tratado.ocorrencia_validacao
              (versao_id, regra, severidade, data_referencia, detalhe)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [(versao_id, o.regra, o.severidade, o.data, Jsonb(o.detalhe)) for o in ocorrencias],
        )


def aplicar_diferencas(
    conn: psycopg.Connection, codigo: str, versao_id: int, diferencas: Diferencas
) -> None:
    """Fecha as linhas revisadas e insere os valores novos. Nunca altera um valor existente."""
    with conn.cursor() as cur:
        if diferencas.revisar:
            cur.executemany(
                """
                UPDATE tratado.observacao SET versao_fim_id = %s
                WHERE indicador_codigo = %s AND data_referencia = %s AND versao_fim_id IS NULL
                """,
                [(versao_id, codigo, o.data) for o in diferencas.revisar],
            )
        cur.executemany(
            """
            INSERT INTO tratado.observacao
              (indicador_codigo, data_referencia, valor, situacao, versao_inicio_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                (codigo, o.data, o.valor, o.situacao, versao_id)
                for o in diferencas.inserir + diferencas.revisar
            ],
        )


def finalizar_versao(
    conn: psycopg.Connection,
    versao_id: int,
    *,
    status: str,
    diferencas: Diferencas | None = None,
    vigentes: dict[date, Decimal | None] | None = None,
    hash_conteudo: str | None = None,
) -> None:
    datas = sorted(vigentes) if vigentes else []
    conn.execute(
        """
        UPDATE tratado.versao_serie SET status = %s, n_observacoes = %s, primeira_data = %s,
          ultima_data = %s, n_inseridas = %s, n_revisadas = %s, n_inalteradas = %s,
          hash_conteudo = %s
        WHERE id = %s
        """,
        (
            status,
            len(datas),
            datas[0] if datas else None,
            datas[-1] if datas else None,
            len(diferencas.inserir) if diferencas else 0,
            len(diferencas.revisar) if diferencas else 0,
            diferencas.inalteradas if diferencas else 0,
            hash_conteudo,
            versao_id,
        ),
    )
