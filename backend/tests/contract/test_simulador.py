"""Simulador de poder de compra (US3; cenários V1, V3, V4 do quickstart)."""

import psycopg
import pytest

pytestmark = pytest.mark.integracao

ROTA = "/v1/simulador/poder-de-compra"


def test_simulacao_de_referencia(api, validar_resposta):
    resposta = api.get(f"{ROTA}?valor=100.00&inicio=2016-01&fim=2025-12")
    assert resposta.status_code == 200
    corpo = resposta.json()
    validar_resposta(ROTA, 200, corpo)
    assert corpo["meses_considerados"] == 120
    assert corpo["valor_corrigido"] == "164.77"
    assert corpo["inflacao_acumulada_percentual"] == "64.77"
    assert corpo["variacao_poder_compra_percentual"] == "-39.31"
    assert corpo["equivalente_no_inicio"] == "60.69"
    assert corpo["diferenca_nominal"] == "64.77"
    assert corpo["valor_informado"] == "100.00"
    assert len(corpo["passos"]) == 120
    assert corpo["passos"][0]["data"] == "2016-01-01"


def test_um_unico_mes(api):
    corpo = api.get(f"{ROTA}?valor=100&inicio=2026-09&fim=2026-09").json()
    assert (corpo["meses_considerados"], corpo["valor_corrigido"]) == (1, "100.82")


def test_data_final_nao_publicada_usa_ultimo_mes(api):
    corpo = api.get(f"{ROTA}?valor=100&inicio=2025-10&fim=2027-01").json()
    assert corpo["periodo"]["fim_utilizado"] == "2026-09-01"
    assert corpo["meses_considerados"] == 12
    assert "jan/2027 ainda não foi publicado pelo IBGE" in corpo["periodo"]["aviso_nao_publicado"]


@pytest.mark.parametrize(
    "consulta,campo,mensagem",
    [
        ("inicio=2020-01&fim=2020-12", "valor", "Informe um valor em reais."),
        ("valor=&inicio=2020-01&fim=2020-12", "valor", "Informe um valor em reais."),
        ("valor=0&inicio=2020-01&fim=2020-12", "valor", "O valor deve ser maior que zero."),
        ("valor=-5&inicio=2020-01&fim=2020-12", "valor", "Use apenas números"),
        ("valor=abc&inicio=2020-01&fim=2020-12", "valor", "Use apenas números"),
        ("valor=1.505&inicio=2020-01&fim=2020-12", "valor", "no máximo dois dígitos"),
        ("valor=99999999999999&inicio=2020-01&fim=2020-12", "valor", "acima do limite"),
        ("valor=100&inicio=2020-12&fim=2020-01", "inicio", "anterior ou igual"),
        ("valor=100&inicio=1994-06&fim=2020-01", "inicio", "a partir de jul/1994"),
        ("valor=100&inicio=2026-10&fim=2026-12", "inicio", "Ainda não há IPCA publicado"),
        ("valor=100", "inicio", "Informe a data inicial."),
    ],
)
def test_entradas_invalidas(api, validar_resposta, consulta, campo, mensagem):
    resposta = api.get(f"{ROTA}?{consulta}")
    assert resposta.status_code == 400
    corpo = resposta.json()
    validar_resposta(ROTA, 400, corpo)
    erro = next(e for e in corpo["erros"] if e["campo"] == campo)
    assert mensagem in erro["mensagem"]


def test_lacuna_retorna_422_com_meses(api, banco, validar_resposta):
    with psycopg.connect(banco["admin"], autocommit=True) as conn:
        conn.execute(
            """
            UPDATE publico.observacao_publicada SET valor = NULL, situacao = 'ausente'
            WHERE indicador_codigo = 'ipca' AND data_referencia = '2020-04-01'
            """
        )
    resposta = api.get(f"{ROTA}?valor=100&inicio=2020-01&fim=2020-12")
    assert resposta.status_code == 422
    corpo = resposta.json()
    validar_resposta(ROTA, 422, corpo)
    assert corpo["meses_ausentes"] == ["2020-04-01"]
    assert "abr/2020" in corpo["detail"]
