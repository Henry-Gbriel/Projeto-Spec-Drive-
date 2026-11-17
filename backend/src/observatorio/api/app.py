"""API pública e somente leitura do Observatório do Real (contracts/api-openapi.yaml)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from observatorio.api.erros import registrar_tratadores
from observatorio.api.rotas import indicadores, saude, series, simulador
from observatorio.config import obter_configuracao

VERSAO_CONTRATO = "1.0.0"


def criar_app() -> FastAPI:
    config = obter_configuracao()
    app = FastAPI(
        title="API pública do Observatório do Real",
        version=VERSAO_CONTRATO,
        description="Dados oficiais publicados pelo Observatório do Real. Somente leitura.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.lista_cors,
        allow_methods=["GET"],
        allow_headers=["If-None-Match"],
        expose_headers=["ETag", "Content-Disposition"],
    )
    registrar_tratadores(app)
    for modulo in (saude, indicadores, series, simulador):
        app.include_router(modulo.roteador)
    return app


app = criar_app()
