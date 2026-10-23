"""Conexões com o banco para as rotinas (papel coletor) e para a API (papel api_leitura)."""

from functools import lru_cache

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from observatorio.config import obter_configuracao


class BancoNaoConfigurado(RuntimeError):
    pass


def conectar_coletor() -> psycopg.Connection:
    """Conexão única das rotinas, no pooler em modo sessão (porta 5432) na nuvem.

    Em autocommit: as rotinas delimitam cada transação com `conn.transaction()`.
    """
    url = obter_configuracao().coletor_database_url
    if not url:
        raise BancoNaoConfigurado("defina COLETOR_DATABASE_URL (veja backend/.env.example)")
    return psycopg.connect(url, row_factory=dict_row, autocommit=True)


@lru_cache
def pool_api() -> ConnectionPool:
    """Pool pequeno da API.

    Na nuvem a API usa o pooler em modo transação (porta 6543), que não aceita prepared
    statements: por isso prepare_threshold=None (research R-07).
    """
    config = obter_configuracao()
    if not config.api_database_url:
        raise BancoNaoConfigurado("defina API_DATABASE_URL (veja backend/.env.example)")
    kwargs: dict = {"row_factory": dict_row, "prepare_threshold": None}
    if config.producao:
        kwargs["sslmode"] = "require"
    return ConnectionPool(config.api_database_url, min_size=0, max_size=4, kwargs=kwargs, open=True)
