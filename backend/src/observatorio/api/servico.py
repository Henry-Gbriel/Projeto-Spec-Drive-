"""Lógica compartilhada pelas rotas: indicador publicado, período e observações do período."""

import hashlib
from datetime import date
from decimal import Decimal
from typing import Any

import psycopg
from fastapi import Request, Response
from pydantic import BaseModel

from observatorio.api import erros
from observatorio.api.esquemas import Indicador, Observacao, PeriodoReferencia, decimal_texto
from observatorio.regras.meses import meses_entre
from observatorio.regras.periodo import PeriodoResolvido, resolver_periodo
from observatorio.repositorio import publico

CACHE_CONTROL = "public, max-age=3600"


def nome_curto(nome: str) -> str:
    """'IPCA — variação mensal' -> 'IPCA'."""
    return nome.split(" — ")[0]


def indicador_publicado(conn: psycopg.Connection, codigo: str) -> dict[str, Any]:
    linha = publico.obter_indicador(conn, codigo)
    if linha is None:
        raise erros.nao_encontrado(codigo)
    return linha


def indicador_com_dados(conn: psycopg.Connection, codigo: str) -> dict[str, Any]:
    linha = indicador_publicado(conn, codigo)
    if linha["versao_id"] is None or linha["periodo_inicio"] is None:
        raise erros.nao_integrado(nome_curto(linha["nome"]))
    return linha


def resolver(
    linha: dict[str, Any],
    periodo: str | None,
    inicio: str | None,
    fim: str | None,
    primeiro_mes: date | None = None,
) -> PeriodoResolvido:
    return resolver_periodo(
        periodo=periodo,
        inicio=inicio,
        fim=fim,
        primeiro_mes=primeiro_mes or linha["periodo_inicio"],
        ultimo_mes=linha["periodo_fim"],
        nome=nome_curto(linha["nome"]),
        instituicao=linha["instituicao"],
    )


def periodo_referencia(periodo: PeriodoResolvido) -> PeriodoReferencia:
    return PeriodoReferencia(
        inicio=periodo.inicio,
        fim_solicitado=periodo.fim_solicitado,
        fim_utilizado=periodo.fim_utilizado,
        aviso_nao_publicado=periodo.aviso_nao_publicado,
    )


def observacoes_do_periodo(
    conn: psycopg.Connection, codigo: str, inicio: date, fim: date
) -> list[tuple[date, Decimal | None]]:
    """Uma entrada por mês do período; mês sem linha publicada é tratado como ausente."""
    linhas = {
        linha["data_referencia"]: linha["valor"]
        for linha in publico.obter_observacoes(conn, codigo, inicio, fim)
    }
    return [(mes, linhas.get(mes)) for mes in meses_entre(inicio, fim)]


def para_observacoes(
    serie: list[tuple[date, Decimal | None]], casas: int | None = None
) -> list[Observacao]:
    return [
        Observacao(data=d, valor=decimal_texto(v, casas), situacao="ausente" if v is None else "ok")
        for d, v in serie
    ]


def modelo_indicador(linha: dict[str, Any]) -> Indicador:
    return Indicador.da_linha(linha)


def responder(request: Request, modelo: BaseModel, *versoes: object) -> Response:
    """JSON com cache HTTP de 1 h e ETag ligado à versão publicada (304 se não mudou)."""
    chave = f"{versoes}|{request.url.path}?{request.url.query}"
    etag = f'W/"{hashlib.sha256(chave.encode()).hexdigest()[:20]}"'
    cabecalhos = {"Cache-Control": CACHE_CONTROL, "ETag": etag}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=cabecalhos)
    return Response(modelo.model_dump_json(), media_type="application/json", headers=cabecalhos)
