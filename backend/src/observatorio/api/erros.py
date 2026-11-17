"""Erros no formato RFC 9457 (application/problem+json), com mensagens em português."""

import logging
from datetime import date

import psycopg
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg_pool import PoolTimeout

from observatorio.regras.ipca import LacunaNaSerie
from observatorio.regras.periodo import EntradaInvalida, ErroCampo

TIPO_BASE = "https://observatorio-do-real.example/erros/"
TIPO_MIDIA = "application/problem+json"

log = logging.getLogger(__name__)


class ErroApi(Exception):  # noqa: N818 (nome de domínio)
    def __init__(
        self,
        status: int,
        tipo: str,
        titulo: str,
        detalhe: str,
        erros: list[ErroCampo] | None = None,
        meses_ausentes: list[date] | None = None,
    ):
        self.status = status
        self.tipo = tipo
        self.titulo = titulo
        self.detalhe = detalhe
        self.erros = erros or []
        self.meses_ausentes = meses_ausentes or []
        super().__init__(detalhe)


def nao_encontrado(codigo: str) -> ErroApi:
    return ErroApi(
        404, "nao-encontrado", "Indicador não encontrado", f"Não há o indicador {codigo!r}."
    )


def nao_integrado(nome: str) -> ErroApi:
    return ErroApi(
        409,
        "nao-integrado",
        "Dados ainda não disponíveis",
        f"Ainda não há dados publicados de {nome}. Disponível após a integração com a fonte.",
    )


def entrada_invalida(erros: list[ErroCampo]) -> ErroApi:
    detalhe = erros[0].mensagem if len(erros) == 1 else "Há campos com valores inválidos."
    return ErroApi(400, "entrada-invalida", "Entrada inválida", detalhe, erros=erros)


def lacuna(meses: list[date]) -> ErroApi:
    from observatorio.regras.formatacao import mes_abreviado

    lista = ", ".join(mes_abreviado(m) for m in meses[:6])
    return ErroApi(
        422,
        "lacuna-na-serie",
        "Cálculo não realizado",
        f"Não calculado: falta o dado de {lista}. O Observatório não estima valores ausentes.",
        meses_ausentes=meses,
    )


def _resposta(erro: ErroApi) -> JSONResponse:
    corpo = {
        "type": TIPO_BASE + erro.tipo,
        "title": erro.titulo,
        "status": erro.status,
        "detail": erro.detalhe,
    }
    if erro.erros:
        corpo["erros"] = [{"campo": e.campo, "mensagem": e.mensagem} for e in erro.erros]
    if erro.meses_ausentes:
        corpo["meses_ausentes"] = [m.isoformat() for m in erro.meses_ausentes]
    return JSONResponse(corpo, status_code=erro.status, media_type=TIPO_MIDIA)


def registrar_tratadores(app: FastAPI) -> None:
    @app.exception_handler(ErroApi)
    async def _erro_api(_: Request, erro: ErroApi) -> JSONResponse:
        return _resposta(erro)

    @app.exception_handler(EntradaInvalida)
    async def _entrada(_: Request, erro: EntradaInvalida) -> JSONResponse:
        return _resposta(entrada_invalida(erro.erros))

    @app.exception_handler(LacunaNaSerie)
    async def _lacuna(_: Request, erro: LacunaNaSerie) -> JSONResponse:
        return _resposta(lacuna(erro.meses_ausentes))

    @app.exception_handler(psycopg.OperationalError)
    @app.exception_handler(PoolTimeout)
    async def _banco(_: Request, erro: Exception) -> JSONResponse:
        log.error("banco indisponível: %s", erro)
        return _resposta(
            ErroApi(
                503,
                "indisponivel",
                "Dados temporariamente indisponíveis",
                "Não foi possível consultar os dados agora. Tente novamente em instantes.",
            )
        )

    @app.exception_handler(RequestValidationError)
    async def _validacao(_: Request, erro: RequestValidationError) -> JSONResponse:
        erros = [
            ErroCampo(str(item["loc"][-1]), "Valor em formato inválido.") for item in erro.errors()
        ]
        return _resposta(entrada_invalida(erros))
