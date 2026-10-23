"""Políticas de acesso (cenário V13 do quickstart, Princípio VII)."""

import psycopg
import pytest
from psycopg.rows import dict_row

from observatorio.catalogo import carregar_catalogo, sincronizar_catalogo

pytestmark = pytest.mark.integracao


def test_todas_as_tabelas_tem_rls(conn_admin):
    sem_rls = conn_admin.execute(
        """
        SELECT n.nspname || '.' || c.relname AS tabela
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r' AND n.nspname IN ('bruto', 'tratado', 'publico')
          AND NOT c.relrowsecurity
        """
    ).fetchall()
    assert sem_rls == []


def _como(conn_admin, papel: str, sql: str):
    """Executa uma consulta assumindo um papel do Supabase (anon/authenticated)."""
    with conn_admin.transaction():
        conn_admin.execute(f"SET LOCAL ROLE {papel}")
        return conn_admin.execute(sql).fetchall()


@pytest.mark.parametrize("papel", ["anon", "authenticated"])
@pytest.mark.parametrize("tabela", ["bruto.coleta", "bruto.payload", "tratado.observacao"])
def test_publico_nao_le_camadas_internas(conn_admin, papel, tabela):
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        _como(conn_admin, papel, f"SELECT * FROM {tabela}")


def test_anon_le_somente_indicadores_publicados(conn_coletor, conn_admin):
    sincronizar_catalogo(conn_coletor, carregar_catalogo())
    conn_coletor.execute(
        "UPDATE publico.indicador_publicado SET publicado = false WHERE codigo = 'm4'"
    )
    linhas = _como(conn_admin, "anon", "SELECT codigo FROM publico.indicador_publicado")
    codigos = {linha["codigo"] for linha in linhas}
    assert "ipca" in codigos
    assert "m4" not in codigos


def test_api_leitura_nao_ve_nao_publicados_e_nao_escreve(banco, conn_coletor):
    sincronizar_catalogo(conn_coletor, carregar_catalogo())
    conn_coletor.execute(
        "UPDATE publico.indicador_publicado SET publicado = false WHERE codigo = 'm4'"
    )
    with psycopg.connect(banco["api_leitura"], row_factory=dict_row, autocommit=True) as api:
        codigos = {
            linha["codigo"]
            for linha in api.execute("SELECT codigo FROM publico.indicador_publicado").fetchall()
        }
        assert "m4" not in codigos and "ipca" in codigos
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            api.execute("SELECT * FROM tratado.indicador")
        for comando in (
            "UPDATE publico.indicador_publicado SET nome = 'x'",
            "DELETE FROM publico.observacao_publicada",
            "INSERT INTO bruto.payload (sha256, conteudo, tamanho_bytes) VALUES ('a', '[]', 0)",
        ):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                api.execute(comando)
