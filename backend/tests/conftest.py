"""Infraestrutura dos testes de integração.

Cria um banco temporário no Postgres apontado por TESTE_DATABASE_URL (padrão: o
docker-compose.yml da raiz, porta 54329), aplica as migrações de supabase/migrations e
fornece conexões com os papéis reais `coletor` e `api_leitura`.
"""

import os
import uuid
from pathlib import Path

import psycopg
import pytest
from psycopg import conninfo
from psycopg.rows import dict_row

RAIZ = Path(__file__).resolve().parents[2]
URL_PADRAO = "postgresql://postgres:postgres@localhost:54329/observatorio"
# Papéis valem para o servidor inteiro: a mesma senha local do infra/preparar-banco-local.sh
# evita que os testes quebrem o banco de desenvolvimento no mesmo Postgres.
SENHA_TESTE = "local"  # noqa: S105


def _url(base: str, **trocas: str) -> str:
    partes = conninfo.conninfo_to_dict(base)
    partes.update(trocas)
    return conninfo.make_conninfo(**partes)


@pytest.fixture(scope="session")
def banco_urls():
    base = os.environ.get("TESTE_DATABASE_URL", URL_PADRAO)
    nome = f"observatorio_teste_{uuid.uuid4().hex[:8]}"
    try:
        admin = psycopg.connect(_url(base, dbname="postgres"), autocommit=True, connect_timeout=3)
    except psycopg.OperationalError as erro:
        pytest.skip(f"Postgres de teste indisponível ({erro}); rode `docker compose up -d banco`")
    with admin:
        admin.execute(f'CREATE DATABASE "{nome}"')
        url_admin = _url(base, dbname=nome)
        with psycopg.connect(url_admin, autocommit=True) as conn:
            conn.execute((RAIZ / "infra" / "bootstrap-supabase-local.sql").read_text())
            for arquivo in sorted((RAIZ / "supabase" / "migrations").glob("*.sql")):
                conn.execute(arquivo.read_text())
            for papel in ("coletor", "api_leitura"):
                conn.execute(f"ALTER ROLE {papel} WITH LOGIN PASSWORD '{SENHA_TESTE}'")
        yield {
            "admin": url_admin,
            "coletor": _url(base, dbname=nome, user="coletor", password=SENHA_TESTE),
            "api_leitura": _url(base, dbname=nome, user="api_leitura", password=SENHA_TESTE),
        }
        admin.execute(f'DROP DATABASE "{nome}" WITH (FORCE)')


@pytest.fixture
def banco(banco_urls):
    """Banco limpo a cada teste."""
    with psycopg.connect(banco_urls["admin"], autocommit=True) as conn:
        tabelas = conn.execute(
            """
            SELECT string_agg(format('%I.%I', schemaname, tablename), ', ') AS lista
            FROM pg_tables WHERE schemaname IN ('bruto', 'tratado', 'publico')
            """
        ).fetchone()[0]
        conn.execute(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE")
    return banco_urls


@pytest.fixture
def conn_coletor(banco):
    with psycopg.connect(banco["coletor"], row_factory=dict_row, autocommit=True) as conn:
        yield conn


@pytest.fixture
def conn_admin(banco):
    with psycopg.connect(banco["admin"], row_factory=dict_row, autocommit=True) as conn:
        yield conn
