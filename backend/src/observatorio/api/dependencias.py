"""Dependências da API: conexão de leitura (papel api_leitura)."""

from collections.abc import Iterator

import psycopg

from observatorio.repositorio.conexao import pool_api


def obter_conexao() -> Iterator[psycopg.Connection]:
    with pool_api().connection() as conn:
        yield conn
