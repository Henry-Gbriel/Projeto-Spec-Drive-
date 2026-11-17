"""Consultas de leitura na camada publico (papel api_leitura)."""

from datetime import date
from typing import Any

import psycopg

COLUNAS_INDICADOR = """
    codigo, nome, descricao, instituicao, codigo_serie, url_origem, unidade, frequencia,
    casas_decimais, natureza, situacao, periodo_inicio, periodo_fim,
    ultima_atualizacao_valida, ultima_tentativa, mensagem_publica, versao_id, entrega, ordem
"""


def listar_indicadores(conn: psycopg.Connection) -> list[dict[str, Any]]:
    return conn.execute(
        f"SELECT {COLUNAS_INDICADOR} FROM publico.indicador_publicado "
        "WHERE publicado ORDER BY ordem, codigo"
    ).fetchall()


def obter_indicador(conn: psycopg.Connection, codigo: str) -> dict[str, Any] | None:
    return conn.execute(
        f"SELECT {COLUNAS_INDICADOR} FROM publico.indicador_publicado "
        "WHERE publicado AND codigo = %s",
        (codigo,),
    ).fetchone()


def obter_observacoes(
    conn: psycopg.Connection, codigo: str, inicio: date | None = None, fim: date | None = None
) -> list[dict[str, Any]]:
    return conn.execute(
        """
        SELECT data_referencia, valor, situacao FROM publico.observacao_publicada
        WHERE indicador_codigo = %s
          AND (%s::date IS NULL OR data_referencia >= %s::date)
          AND (%s::date IS NULL OR data_referencia <= %s::date)
        ORDER BY data_referencia
        """,
        (codigo, inicio, inicio, fim, fim),
    ).fetchall()


def verificar_banco(conn: psycopg.Connection) -> bool:
    return conn.execute("SELECT 1 AS ok").fetchone() is not None
