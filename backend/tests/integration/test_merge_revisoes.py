"""Atualização incremental, revisões e idempotência (cenários V7 e V8 do quickstart)."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from apoio import ConectorFixture
from observatorio.catalogo import carregar_catalogo, sincronizar_catalogo
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


def vigentes(conn):
    return conn.execute(
        """
        SELECT data_referencia, valor FROM tratado.observacao
        WHERE indicador_codigo = 'ipca' AND versao_fim_id IS NULL ORDER BY 1
        """
    ).fetchall()


def test_carga_inicial_insere_e_publica(conn):
    conector = ConectorFixture("sidra_recorte_2025_2026.json")
    resultado = rodar(conn, conector)
    assert (resultado.status, resultado.n_inseridas) == ("publicado", 21)
    assert conector.chamadas == [(date(1994, 1, 1), date(2026, 10, 22))]  # carga completa
    assert len(vigentes(conn)) == 21
    versao = conn.execute("SELECT * FROM tratado.versao_serie").fetchone()
    assert versao["status"] == "publicada"
    assert versao["n_inseridas"] == 21 and versao["versao_codigo"]


def test_reexecucao_sem_mudanca_nao_cria_versao(conn):
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    conector = ConectorFixture("sidra_recorte_2025_2026.json")
    resultado = rodar(conn, conector, agora=DEPOIS)
    assert resultado.status == "sem_mudancas"
    # incremental: janela de 3 meses antes do último mês vigente (set/2026)
    assert conector.chamadas == [(date(2026, 6, 1), date(2026, 10, 23))]
    assert conn.execute("SELECT count(*) AS n FROM tratado.versao_serie").fetchone()["n"] == 1
    coletas = conn.execute("SELECT status FROM bruto.coleta ORDER BY id").fetchall()
    assert [c["status"] for c in coletas] == ["sucesso", "sem_novidade"]
    assert conn.execute("SELECT count(*) AS n FROM bruto.payload").fetchone()["n"] == 1


def test_revisao_fecha_linha_antiga_e_abre_nova(conn):
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    resultado = rodar(conn, ConectorFixture("sidra_revisada.json"), agora=DEPOIS)
    assert (resultado.status, resultado.n_revisadas, resultado.n_inseridas) == ("publicado", 1, 0)
    assert any(o.regra == "revisao_grande" for o in resultado.ocorrencias)

    historico = conn.execute(
        """
        SELECT valor, versao_inicio_id, versao_fim_id FROM tratado.observacao
        WHERE indicador_codigo = 'ipca' AND data_referencia = '2026-08-01' ORDER BY id
        """
    ).fetchall()
    assert [(h["valor"], h["versao_fim_id"]) for h in historico] == [
        (Decimal("-0.320000"), 2),
        (Decimal("0.990000"), None),
    ]
    versoes = conn.execute("SELECT id, status FROM tratado.versao_serie ORDER BY id").fetchall()
    assert [v["status"] for v in versoes] == ["substituida", "publicada"]
    publicado = conn.execute(
        "SELECT valor FROM publico.observacao_publicada WHERE data_referencia = '2026-08-01'"
    ).fetchone()
    assert publicado["valor"] == Decimal("0.990000")


def test_datas_vigentes_fora_da_janela_ficam_intocadas(conn):
    rodar(conn, ConectorFixture("sidra_1737_v63.json"))
    total = len(vigentes(conn))
    resultado = rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"), agora=DEPOIS)
    assert resultado.status == "sem_mudancas"
    assert len(vigentes(conn)) == total == 393


def test_queda_de_cobertura_rejeita_e_desfaz(conn):
    rodar(conn, ConectorFixture("sidra_recorte_2025_2026.json"))
    antes = vigentes(conn)
    resultado = rodar(conn, ConectorFixture("sidra_com_lacuna.json"), carga_completa=True)
    assert resultado.status == "rejeitado"
    assert "queda_de_cobertura" in resultado.mensagem
    assert vigentes(conn) == antes
    versoes = conn.execute("SELECT status FROM tratado.versao_serie ORDER BY id").fetchall()
    assert [v["status"] for v in versoes] == ["publicada", "rejeitada"]
    ocorrencia = conn.execute(
        "SELECT regra, severidade FROM tratado.ocorrencia_validacao WHERE severidade = 'bloqueante'"
    ).fetchone()
    assert (ocorrencia["regra"], ocorrencia["severidade"]) == ("queda_de_cobertura", "bloqueante")
