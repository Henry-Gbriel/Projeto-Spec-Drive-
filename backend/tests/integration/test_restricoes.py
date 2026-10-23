"""Restrições do banco que impedem dados inválidos ou duplicados (data-model.md)."""

import psycopg
import pytest

from observatorio.catalogo import carregar_catalogo, sincronizar_catalogo

pytestmark = pytest.mark.integracao


@pytest.fixture
def com_versao(conn_coletor):
    sincronizar_catalogo(conn_coletor, carregar_catalogo())
    coleta = conn_coletor.execute(
        """
        INSERT INTO bruto.coleta (indicador_codigo, execucao_id, status)
        VALUES ('ipca', gen_random_uuid(), 'sucesso') RETURNING id
        """
    ).fetchone()["id"]
    versao = conn_coletor.execute(
        """
        INSERT INTO tratado.versao_serie (indicador_codigo, coleta_id, status, versao_codigo)
        VALUES ('ipca', %s, 'validada', 'teste') RETURNING id
        """,
        (coleta,),
    ).fetchone()["id"]
    return conn_coletor, coleta, versao


def test_natureza_so_aceita_real_ou_ilustrativo(conn_coletor):
    sincronizar_catalogo(conn_coletor, carregar_catalogo())
    with pytest.raises(psycopg.errors.CheckViolation):
        conn_coletor.execute("UPDATE tratado.indicador SET natureza = 'estimado'")


@pytest.mark.parametrize("valor,situacao", [(None, "ok"), ("0.5", "ausente"), ("0.5", "estimado")])
def test_ausente_se_e_somente_se_valor_nulo(com_versao, valor, situacao):
    conn, _, versao = com_versao
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute(
            """
            INSERT INTO tratado.observacao
              (indicador_codigo, data_referencia, valor, situacao, versao_inicio_id)
            VALUES ('ipca', '2026-09-01', %s, %s, %s)
            """,
            (valor, situacao, versao),
        )


def test_um_valor_vigente_por_data(com_versao):
    conn, _, versao = com_versao
    sql = """
        INSERT INTO tratado.observacao
          (indicador_codigo, data_referencia, valor, situacao, versao_inicio_id)
        VALUES ('ipca', '2026-09-01', 0.82, 'ok', %s)
    """
    conn.execute(sql, (versao,))
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute(sql, (versao,))


def test_payload_unico_por_hash(conn_coletor):
    sql = "INSERT INTO bruto.payload (sha256, conteudo, tamanho_bytes) VALUES (%s, '[]', 2)"
    conn_coletor.execute(sql, ("a" * 64,))
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn_coletor.execute(sql, ("a" * 64,))


def test_uma_versao_publicada_por_indicador(com_versao):
    conn, coleta, versao = com_versao
    conn.execute("UPDATE tratado.versao_serie SET status = 'publicada' WHERE id = %s", (versao,))
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute(
            """
            INSERT INTO tratado.versao_serie (indicador_codigo, coleta_id, status, versao_codigo)
            VALUES ('ipca', %s, 'publicada', 'teste')
            """,
            (coleta,),
        )
