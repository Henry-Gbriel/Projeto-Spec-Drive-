"""Publicação e preservação da última versão válida (cenários V5 e V6, SC-004, SC-011)."""

from datetime import date, datetime

import pytest

from apoio import ConectorFixture
from observatorio.catalogo import carregar_catalogo, sincronizar_catalogo
from observatorio.coleta.base import ErroColeta
from observatorio.config import FUSO_HORARIO
from observatorio.rotina import executar

pytestmark = pytest.mark.integracao

CATALOGO = carregar_catalogo()
IPCA = [i for i in CATALOGO if i.codigo == "ipca"]
AGORA = datetime(2026, 10, 22, 6, 17, tzinfo=FUSO_HORARIO)
DEPOIS = datetime(2026, 10, 23, 6, 17, tzinfo=FUSO_HORARIO)


@pytest.fixture
def conn(conn_coletor):
    sincronizar_catalogo(conn_coletor, CATALOGO)
    return conn_coletor


def rodar(conn, conector, agora=AGORA, **kwargs):
    [resultado] = executar(conn, IPCA, {"sidra": conector}, agora=agora, **kwargs)
    return resultado


def publicadas(conn):
    return conn.execute(
        """
        SELECT data_referencia, valor, situacao FROM publico.observacao_publicada
        WHERE indicador_codigo = 'ipca' ORDER BY 1
        """
    ).fetchall()


def indicador(conn):
    return conn.execute(
        "SELECT * FROM publico.indicador_publicado WHERE codigo = 'ipca'"
    ).fetchone()


def test_publicacao_com_metadados_e_periodo(conn):
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    ind = indicador(conn)
    assert ind["situacao"] == "atualizado"
    assert (ind["periodo_inicio"], ind["periodo_fim"]) == (date(2025, 1, 1), date(2026, 9, 1))
    assert ind["ultima_atualizacao_valida"] == AGORA
    assert ind["unidade"] == "% ao mês" and ind["instituicao"] == "IBGE"
    assert len(publicadas(conn)) == 21


def test_lacuna_vira_linha_ausente_sem_valor(conn):
    rodar(conn, ConectorFixture("sidra_com_lacuna.json"))
    linhas = {linha["data_referencia"]: linha for linha in publicadas(conn)}
    assert linhas[date(2025, 3, 1)]["situacao"] == "ausente"
    assert linhas[date(2025, 3, 1)]["valor"] is None
    assert sum(1 for linha in linhas.values() if linha["situacao"] == "ausente") == 1


def test_falha_de_coleta_mantem_dados_publicados(conn):
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    antes = publicadas(conn)
    resultado = rodar(conn, ConectorFixture(ErroColeta("SIDRA fora do ar")), agora=DEPOIS)
    assert resultado.status == "falha"
    assert publicadas(conn) == antes
    ind = indicador(conn)
    assert ind["situacao"] == "falha_atualizacao"
    assert ind["ultima_atualizacao_valida"] == AGORA
    assert ind["ultima_tentativa"] == DEPOIS
    assert ind["mensagem_publica"] == (
        "A atualização de 23/10/2026 falhou. Exibindo a última versão válida."
    )
    coleta = conn.execute("SELECT status, erro FROM bruto.coleta ORDER BY id DESC").fetchone()
    assert (coleta["status"], coleta["erro"]) == ("falha", "SIDRA fora do ar")


def test_falha_simulada_pela_cli(conn):
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    antes = publicadas(conn)
    conector = ConectorFixture("sidra_recorte_2025_2026.json")
    resultado = rodar(conn, conector, agora=DEPOIS, simular_falha=True)
    assert resultado.status == "falha" and conector.chamadas == []
    assert publicadas(conn) == antes


def test_validacao_bloqueante_mantem_dados_publicados(conn):
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    antes = publicadas(conn)
    resultado = rodar(conn, ConectorFixture("sidra_data_duplicada.json"), agora=DEPOIS)
    assert resultado.status == "rejeitado"
    assert publicadas(conn) == antes
    assert indicador(conn)["situacao"] == "falha_atualizacao"


def test_esquema_invalido_rejeita(conn):
    resultado = rodar(conn, ConectorFixture("sidra_esquema_invalido.json"))
    assert resultado.status == "rejeitado"
    ind = indicador(conn)
    assert ind["situacao"] == "falha_atualizacao"
    assert "ainda não há versão válida" in ind["mensagem_publica"]
    assert publicadas(conn) == []


def test_sucesso_depois_de_falha_volta_a_atualizado(conn):
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    rodar(conn, ConectorFixture(ErroColeta("fora do ar")), agora=DEPOIS)
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"), agora=DEPOIS)
    ind = indicador(conn)
    assert ind["situacao"] == "atualizado" and ind["mensagem_publica"] is None
    assert ind["ultima_atualizacao_valida"] == DEPOIS


def test_indicadores_nao_ativos_mostram_selo_do_catalogo(conn):
    linhas = conn.execute("SELECT codigo, situacao FROM publico.indicador_publicado").fetchall()
    situacoes = {linha["codigo"]: linha["situacao"] for linha in linhas}
    assert situacoes["ipca"] == "aguardando_integracao"  # ativo, ainda sem versão
    assert situacoes["dolar_ptax"] == "aguardando_integracao"
    assert situacoes["producao_cedulas_moedas"] == "em_definicao"


def test_republicar_regrava_sem_mudar_a_data_de_atualizacao(conn):
    from observatorio.publicacao.publicar import republicar

    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    antes = publicadas(conn)
    conn.execute("DELETE FROM publico.observacao_publicada WHERE indicador_codigo = 'ipca'")
    with conn.transaction():
        total = republicar(conn, IPCA[0])
    assert total == 21
    assert publicadas(conn) == antes
    assert indicador(conn)["ultima_atualizacao_valida"] == AGORA


def test_republicar_sem_versao_publicada_falha(conn):
    from observatorio.publicacao.publicar import republicar

    with pytest.raises(ValueError, match="ainda não tem versão publicada"):
        republicar(conn, IPCA[0])
