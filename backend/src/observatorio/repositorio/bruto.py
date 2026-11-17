"""Gravação da camada bruta: coletas e payloads deduplicados por hash (FR-051)."""

import hashlib
import uuid
from datetime import datetime

import psycopg
from psycopg.types.json import Jsonb

from observatorio.coleta.base import ResultadoColeta


def gravar_payload(conn: psycopg.Connection, resultado: ResultadoColeta) -> tuple[int, bool]:
    """Grava o conteúdo bruto se ele ainda não existir. Retorna (id, se é novo)."""
    conteudo = resultado.conteudo_bruto
    sha256 = hashlib.sha256(conteudo).hexdigest()
    linha = conn.execute(
        """
        INSERT INTO bruto.payload (sha256, conteudo, tamanho_bytes)
        VALUES (%s, %s, %s)
        ON CONFLICT (sha256) DO NOTHING
        RETURNING id
        """,
        (sha256, Jsonb(resultado.conteudo_json), len(conteudo)),
    ).fetchone()
    if linha:
        return linha["id"], True
    existente = conn.execute("SELECT id FROM bruto.payload WHERE sha256 = %s", (sha256,)).fetchone()
    return existente["id"], False


def gravar_coleta(
    conn: psycopg.Connection,
    *,
    codigo: str,
    execucao_id: uuid.UUID,
    iniciada_em: datetime,
    resultado: ResultadoColeta | None,
    parametros: dict,
    erro: str | None = None,
) -> tuple[int, str]:
    """Registra uma tentativa de coleta. Retorna (id da coleta, status)."""
    payload_id = None
    if resultado is None:
        status = "falha"
    else:
        payload_id, novo = gravar_payload(conn, resultado)
        status = "sucesso" if novo else "sem_novidade"
    linha = conn.execute(
        """
        INSERT INTO bruto.coleta (indicador_codigo, execucao_id, iniciada_em, concluida_em,
          status, url_requisitada, parametros, http_status, erro, payload_id)
        VALUES (%s, %s, %s, now(), %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            codigo,
            execucao_id,
            iniciada_em,
            status,
            resultado.url if resultado else None,
            Jsonb(parametros),
            resultado.http_status if resultado else None,
            erro,
            payload_id,
        ),
    ).fetchone()
    return linha["id"], status
