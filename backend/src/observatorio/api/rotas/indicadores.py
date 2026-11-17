"""Catálogo e metadados de indicadores (US8, FR-010, FR-042)."""

import psycopg
from fastapi import APIRouter, Depends, Request, Response

from observatorio.api import servico
from observatorio.api.dependencias import obter_conexao
from observatorio.api.esquemas import Catalogo, Indicador
from observatorio.repositorio import publico

roteador = APIRouter()


@roteador.get("/v1/indicadores", response_model=Catalogo, operation_id="listarIndicadores")
def listar_indicadores(
    request: Request, conn: psycopg.Connection = Depends(obter_conexao)
) -> Response:
    linhas = publico.listar_indicadores(conn)
    catalogo = Catalogo(indicadores=[Indicador.da_linha(linha) for linha in linhas])
    versoes = tuple((linha["codigo"], linha["versao_id"], linha["situacao"]) for linha in linhas)
    return servico.responder(request, catalogo, versoes)


@roteador.get("/v1/indicadores/{codigo}", response_model=Indicador, operation_id="obterIndicador")
def obter_indicador(
    codigo: str, request: Request, conn: psycopg.Connection = Depends(obter_conexao)
) -> Response:
    linha = servico.indicador_publicado(conn, codigo)
    return servico.responder(
        request, Indicador.da_linha(linha), linha["versao_id"], linha["situacao"]
    )
