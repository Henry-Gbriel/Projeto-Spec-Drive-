"""Séries, resumos e CSV de um indicador (US2, FR-020 a FR-024, FR-030)."""

from datetime import date
from decimal import Decimal

import psycopg
from fastapi import APIRouter, Depends, Request, Response

from observatorio.api import servico
from observatorio.api.csv import gerar_csv, nome_arquivo
from observatorio.api.dependencias import obter_conexao
from observatorio.api.esquemas import Resumo, Serie, decimal_texto
from observatorio.regras.ipca import LacunaNaSerie, acumulado_percentual, arredondar
from observatorio.regras.variacao import resumir_nivel

roteador = APIRouter()

# Indicadores cujo número-síntese é a variação acumulada (encadeada) no período.
INDICADORES_ACUMULADOS = {"ipca"}


def _acumulado_corrente(serie: list[tuple[date, Decimal | None]]) -> list[str | None]:
    """Acumulado do início do período até cada mês; para de ser calculado após uma lacuna."""
    resultado: list[str | None] = []
    fator: Decimal | None = Decimal(1)
    for _, valor in serie:
        if fator is None or valor is None:
            fator = None
            resultado.append(None)
            continue
        fator *= 1 + valor / 100
        resultado.append(decimal_texto(arredondar(acumulado_percentual(fator), 2), 2))
    return resultado


@roteador.get("/v1/indicadores/{codigo}/serie", response_model=Serie, operation_id="obterSerie")
def obter_serie(
    codigo: str,
    request: Request,
    inicio: str | None = None,
    fim: str | None = None,
    periodo: str | None = None,
    conn: psycopg.Connection = Depends(obter_conexao),
) -> Response:
    linha = servico.indicador_com_dados(conn, codigo)
    resolvido = servico.resolver(linha, periodo, inicio, fim)
    serie = servico.observacoes_do_periodo(conn, codigo, resolvido.inicio, resolvido.fim_utilizado)

    derivadas = None
    if codigo in INDICADORES_ACUMULADOS:
        derivadas = {"acumulado_no_periodo": _acumulado_corrente(serie)}
        indice = servico.observacoes_do_periodo(
            conn, "ipca_indice", resolvido.inicio, resolvido.fim_utilizado
        )
        if any(v is not None for _, v in indice):
            derivadas["numero_indice"] = [decimal_texto(v, 2) for _, v in indice]

    modelo = Serie(
        indicador=servico.modelo_indicador(linha),
        periodo=servico.periodo_referencia(resolvido),
        observacoes=servico.para_observacoes(serie, linha["casas_decimais"]),
        derivadas=derivadas,
    )
    return servico.responder(request, modelo, linha["versao_id"], linha["situacao"])


@roteador.get("/v1/indicadores/{codigo}/resumo", response_model=Resumo, operation_id="obterResumo")
def obter_resumo(
    codigo: str,
    request: Request,
    inicio: str | None = None,
    fim: str | None = None,
    periodo: str | None = None,
    conn: psycopg.Connection = Depends(obter_conexao),
) -> Response:
    linha = servico.indicador_com_dados(conn, codigo)
    resolvido = servico.resolver(linha, periodo, inicio, fim)
    serie = servico.observacoes_do_periodo(conn, codigo, resolvido.inicio, resolvido.fim_utilizado)
    modelo = montar_resumo(linha, resolvido, serie)
    return servico.responder(request, modelo, linha["versao_id"], linha["situacao"])


def montar_resumo(linha, resolvido, serie: list[tuple[date, Decimal | None]]) -> Resumo:
    base = {
        "indicador": servico.modelo_indicador(linha),
        "periodo": servico.periodo_referencia(resolvido),
    }
    if all(v is None for _, v in serie):
        return Resumo(**base, situacao="sem_dados")
    ausentes = [d for d, v in serie if v is None]
    if ausentes:
        return Resumo(**base, situacao="lacuna", meses_ausentes=ausentes)

    casas = linha["casas_decimais"]
    if linha["codigo"] in INDICADORES_ACUMULADOS:
        from observatorio.regras.ipca import fator_acumulado

        fator, meses = fator_acumulado(dict(serie), resolvido.inicio, resolvido.fim_utilizado)
        return Resumo(
            **base,
            situacao="ok",
            acumulado_percentual=decimal_texto(arredondar(acumulado_percentual(fator), 2), 2),
            fator=decimal_texto(fator),
            meses_considerados=meses,
        )
    try:
        nivel = resumir_nivel(serie)
    except LacunaNaSerie as erro:  # pragma: no cover - já tratado acima
        return Resumo(**base, situacao="lacuna", meses_ausentes=erro.meses_ausentes)
    return Resumo(
        **base,
        situacao="ok",
        meses_considerados=len(serie),
        valor_inicial=decimal_texto(nivel.valor_inicial, casas),
        valor_final=decimal_texto(nivel.valor_final, casas),
        variacao_percentual=decimal_texto(nivel.variacao_percentual, 2),
        minimo=decimal_texto(nivel.minimo, casas),
        maximo=decimal_texto(nivel.maximo, casas),
    )


@roteador.get(
    "/v1/indicadores/{codigo}/serie.csv",
    operation_id="baixarSerieCsv",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}},
)
def baixar_csv(
    codigo: str,
    inicio: str | None = None,
    fim: str | None = None,
    periodo: str | None = None,
    conn: psycopg.Connection = Depends(obter_conexao),
) -> Response:
    linha = servico.indicador_com_dados(conn, codigo)
    if inicio is None and fim is None and periodo is None:
        serie = servico.observacoes_do_periodo(
            conn, codigo, linha["periodo_inicio"], linha["periodo_fim"]
        )
        arquivo = nome_arquivo(codigo, None, None)
    else:
        resolvido = servico.resolver(linha, periodo, inicio, fim)
        serie = servico.observacoes_do_periodo(
            conn, codigo, resolvido.inicio, resolvido.fim_utilizado
        )
        arquivo = nome_arquivo(codigo, resolvido.inicio, resolvido.fim_utilizado)
    return Response(
        gerar_csv(linha, serie).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{arquivo}"',
            "Cache-Control": servico.CACHE_CONTROL,
        },
    )
