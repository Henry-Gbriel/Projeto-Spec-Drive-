"""Rotina diária: coleta → tratamento → validação → merge → publicação, por indicador.

A conexão deve estar em autocommit: cada etapa abre sua própria transação.

Uma falha num indicador não interrompe os demais e nunca altera os dados já publicados.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

import psycopg

from observatorio.catalogo import Indicador
from observatorio.coleta.base import Conector, ErroColeta, ErroEsquema, ResultadoColeta
from observatorio.config import FUSO_HORARIO
from observatorio.publicacao.publicar import confirmar_atualizacao, publicar, registrar_falha
from observatorio.regras.meses import interpretar_mes, primeiro_dia, somar_meses
from observatorio.repositorio import tratado
from observatorio.repositorio.bruto import gravar_coleta
from observatorio.tratamento.merge import calcular_diferencas, hash_observacoes
from observatorio.tratamento.modelos import Ocorrencia, ha_bloqueante
from observatorio.tratamento.padronizacao import padronizar
from observatorio.tratamento.validacao import (
    validar_conferencia,
    validar_datas_futuras,
    validar_fonte,
    validar_serie,
)

log = logging.getLogger(__name__)


@dataclass
class ResultadoIndicador:
    codigo: str
    status: str  # publicado | sem_mudancas | falha | rejeitado
    mensagem: str = ""
    n_inseridas: int = 0
    n_revisadas: int = 0
    ocorrencias: list[Ocorrencia] = field(default_factory=list)

    @property
    def com_erro(self) -> bool:
        return self.status in {"falha", "rejeitado"}


def janela_de_coleta(
    indicador: Indicador, ultima_vigente: date | None, hoje: date, carga_completa: bool
) -> tuple[date, date, bool]:
    """Intervalo a pedir à fonte. Carga completa na primeira vez, sob pedido ou no dia 1."""
    inicio_serie = interpretar_mes(indicador.parametros_conector.get("inicio_coleta", "1994-07"))
    completa = carga_completa or ultima_vigente is None or hoje.day == 1
    if completa:
        return inicio_serie, hoje, True
    inicio = somar_meses(primeiro_dia(ultima_vigente), -indicador.janela_revisao_meses)
    return max(inicio, inicio_serie), hoje, False


def processar_indicador(
    conn: psycopg.Connection,
    indicador: Indicador,
    conectores: dict[str, Conector],
    agora: datetime,
    execucao_id: uuid.UUID,
    carga_completa: bool = False,
    simular_falha: bool = False,
) -> ResultadoIndicador:
    hoje = agora.astimezone(FUSO_HORARIO).date()
    codigo = indicador.codigo
    conector = conectores[indicador.conector]

    ultima = tratado.ultima_data_vigente(conn, codigo)
    data_inicial, data_final, completa = janela_de_coleta(indicador, ultima, hoje, carga_completa)
    parametros = {"data_inicial": data_inicial.isoformat(), "data_final": data_final.isoformat()}

    # 1. Coleta (rede, fora de transação).
    try:
        if simular_falha:
            raise ErroColeta("falha simulada (--simular-falha)")
        resultado: ResultadoColeta = conector.coletar(
            indicador.parametros_conector, data_inicial, data_final
        )
    except ErroColeta as erro:
        with conn.transaction():
            gravar_coleta(
                conn,
                codigo=codigo,
                execucao_id=execucao_id,
                iniciada_em=agora,
                resultado=None,
                parametros=parametros,
                erro=str(erro),
            )
            registrar_falha(conn, codigo, agora)
        return ResultadoIndicador(codigo, "falha", str(erro))

    conferencia = _buscar_conferencia(indicador, conectores, data_inicial, data_final, hoje)

    # 2. Tratamento, validação, merge e publicação em uma única transação.
    with conn.transaction():
        tratado.travar_indicador(conn, codigo)
        coleta_id, _ = gravar_coleta(
            conn,
            codigo=codigo,
            execucao_id=execucao_id,
            iniciada_em=agora,
            resultado=resultado,
            parametros=parametros,
        )
        try:
            observacoes_fonte = conector.interpretar(resultado)
        except ErroEsquema as erro:
            ocorrencias = [Ocorrencia("esquema_invalido", "bloqueante", None, {"erro": str(erro)})]
            return _rejeitar(conn, codigo, coleta_id, ocorrencias, agora)

        ocorrencias = validar_fonte(observacoes_fonte, completa)
        padronizado = padronizar(indicador, observacoes_fonte, hoje)
        ocorrencias += validar_datas_futuras(padronizado.datas_futuras)

        intervalo = (primeiro_dia(data_inicial), data_final)
        vigentes = tratado.carregar_vigentes(conn, codigo)
        ocorrencias += validar_serie(indicador, padronizado.observacoes, vigentes, intervalo)
        if conferencia is not None:
            ocorrencias += validar_conferencia(
                padronizado.observacoes, conferencia[1], conferencia[0]
            )
        if ha_bloqueante(ocorrencias):
            return _rejeitar(conn, codigo, coleta_id, ocorrencias, agora)

        diferencas = calcular_diferencas(padronizado.observacoes, vigentes)
        if diferencas.vazia:
            confirmar_atualizacao(conn, codigo, agora)
            return ResultadoIndicador(codigo, "sem_mudancas", ocorrencias=ocorrencias)

        versao_id = tratado.criar_versao(conn, codigo, coleta_id, "em_tratamento")
        tratado.aplicar_diferencas(conn, codigo, versao_id, diferencas)
        tratado.registrar_ocorrencias(conn, versao_id, ocorrencias)
        todas = tratado.carregar_vigentes(conn, codigo)
        tratado.finalizar_versao(
            conn,
            versao_id,
            status="validada",
            diferencas=diferencas,
            vigentes=todas,
            hash_conteudo=hash_observacoes(todas),
        )
        publicar(conn, indicador, versao_id, agora)
        return ResultadoIndicador(
            codigo,
            "publicado",
            n_inseridas=len(diferencas.inserir),
            n_revisadas=len(diferencas.revisar),
            ocorrencias=ocorrencias,
        )


def _buscar_conferencia(
    indicador: Indicador,
    conectores: dict[str, Conector],
    inicio: date,
    fim: date,
    hoje: date,
) -> tuple[str, list] | None:
    config = indicador.parametros_conector.get("conferencia")
    if not config or config.get("conector") not in conectores:
        return None
    nome = f"{config['conector'].upper()} {config.get('codigo', '')}".strip()
    try:
        conector = conectores[config["conector"]]
        resultado = conector.coletar(config, inicio, fim)
        observacoes = conector.interpretar(resultado)
    except (ErroColeta, ErroEsquema) as erro:
        log.warning("conferência %s indisponível para %s: %s", nome, indicador.codigo, erro)
        return None
    return nome, padronizar(indicador, observacoes, hoje).observacoes


def _rejeitar(
    conn: psycopg.Connection,
    codigo: str,
    coleta_id: int,
    ocorrencias: list[Ocorrencia],
    agora: datetime,
) -> ResultadoIndicador:
    versao_id = tratado.criar_versao(conn, codigo, coleta_id, "rejeitada")
    tratado.registrar_ocorrencias(conn, versao_id, ocorrencias)
    registrar_falha(conn, codigo, agora)
    bloqueantes = [o for o in ocorrencias if o.severidade == "bloqueante"]
    resumo = ", ".join(
        f"{o.regra}{f' ({o.data:%Y-%m})' if o.data else ''}" for o in bloqueantes[:5]
    )
    return ResultadoIndicador(
        codigo, "rejeitado", f"validação bloqueante: {resumo}", ocorrencias=ocorrencias
    )


def executar(
    conn: psycopg.Connection,
    indicadores: list[Indicador],
    conectores: dict[str, Conector],
    agora: datetime | None = None,
    carga_completa: bool = False,
    simular_falha: bool = False,
) -> list[ResultadoIndicador]:
    agora = agora or datetime.now(FUSO_HORARIO)
    execucao_id = uuid.uuid4()
    resultados = []
    for indicador in indicadores:
        if not indicador.ativo:
            continue
        try:
            resultados.append(
                processar_indicador(
                    conn, indicador, conectores, agora, execucao_id, carga_completa, simular_falha
                )
            )
        except Exception as erro:  # noqa: BLE001 - isola a falha deste indicador
            log.exception("erro inesperado em %s", indicador.codigo)
            with conn.transaction():
                registrar_falha(conn, indicador.codigo, agora)
            resultados.append(ResultadoIndicador(indicador.codigo, "falha", repr(erro)))
    return resultados
