"""Rotas do IPCA e do catálogo (US2, US8; cenário V2 do quickstart)."""

import pytest

pytestmark = pytest.mark.integracao


def test_catalogo_lista_todos_com_metadados(api, validar_resposta):
    resposta = api.get("/v1/indicadores")
    assert resposta.status_code == 200
    corpo = resposta.json()
    validar_resposta("/v1/indicadores", 200, corpo)
    situacoes = {i["codigo"]: i["atualizacao"]["situacao"] for i in corpo["indicadores"]}
    assert len(situacoes) == 12
    assert situacoes["ipca"] == "atualizado"
    assert situacoes["dolar_ptax"] == "aguardando_integracao"
    assert situacoes["producao_cedulas_moedas"] == "em_definicao"
    assert "ETag" in resposta.headers
    assert resposta.headers["Cache-Control"] == "public, max-age=3600"


def test_metadados_do_ipca(api, validar_resposta):
    corpo = api.get("/v1/indicadores/ipca").json()
    validar_resposta("/v1/indicadores/{codigo}", 200, corpo)
    assert corpo["fonte"]["instituicao"] == "IBGE"
    assert corpo["unidade"] == "% ao mês"
    assert corpo["periodo_disponivel"] == {"inicio": "1994-01-01", "fim": "2026-09-01"}
    assert corpo["natureza"] == "real"


def test_serie_padrao_cinco_anos(api, validar_resposta):
    corpo = api.get("/v1/indicadores/ipca/serie").json()
    validar_resposta("/v1/indicadores/{codigo}/serie", 200, corpo)
    assert corpo["periodo"]["inicio"] == "2021-10-01"
    assert corpo["periodo"]["fim_utilizado"] == "2026-09-01"
    assert len(corpo["observacoes"]) == 60
    assert corpo["observacoes"][-1] == {"data": "2026-09-01", "valor": "0.82", "situacao": "ok"}
    assert len(corpo["derivadas"]["acumulado_no_periodo"]) == 60
    assert corpo["derivadas"]["numero_indice"][-1] == "7695.82"


def test_resumo_confere_com_calculo_manual(api, validar_resposta):
    """V2: jan/2021 a dez/2025, 60 meses, acumulado 33,14 % (fractions, test_formulas.py)."""
    corpo = api.get("/v1/indicadores/ipca/resumo?inicio=2021-01&fim=2025-12").json()
    validar_resposta("/v1/indicadores/{codigo}/resumo", 200, corpo)
    assert corpo["situacao"] == "ok"
    assert corpo["meses_considerados"] == 60
    assert corpo["acumulado_percentual"] == "33.14"


def test_acumulado_da_tabela_termina_igual_ao_resumo(api):
    serie = api.get("/v1/indicadores/ipca/serie?inicio=2016-01&fim=2025-12").json()
    assert serie["derivadas"]["acumulado_no_periodo"][-1] == "64.77"


@pytest.mark.parametrize(
    "consulta,campo",
    [
        ("inicio=2020-05&fim=2020-01", "inicio"),
        ("inicio=1990-01&fim=2020-01", "inicio"),
        ("inicio=2020-13&fim=2021-01", "inicio"),
        ("inicio=2020-01", "fim"),
        ("periodo=7a", "periodo"),
    ],
)
def test_entrada_invalida_retorna_400_por_campo(api, validar_resposta, consulta, campo):
    resposta = api.get(f"/v1/indicadores/ipca/serie?{consulta}")
    assert resposta.status_code == 400
    assert resposta.headers["content-type"] == "application/problem+json"
    corpo = resposta.json()
    validar_resposta("/v1/indicadores/{codigo}/serie", 400, corpo)
    assert corpo["erros"][0]["campo"] == campo


def test_indicador_inexistente_404(api, validar_resposta):
    resposta = api.get("/v1/indicadores/nao_existe/serie")
    assert resposta.status_code == 404
    validar_resposta("/v1/indicadores/{codigo}/serie", 404, resposta.json())


def test_indicador_nao_integrado_409(api, validar_resposta):
    resposta = api.get("/v1/indicadores/dolar_ptax/serie")
    assert resposta.status_code == 409
    validar_resposta("/v1/indicadores/{codigo}/serie", 409, resposta.json())
    assert "Disponível após a integração" in resposta.json()["detail"]


def test_mes_final_nao_publicado(api):
    corpo = api.get("/v1/indicadores/ipca/resumo?inicio=2026-01&fim=2026-12").json()
    assert corpo["periodo"]["fim_solicitado"] == "2026-12-01"
    assert corpo["periodo"]["fim_utilizado"] == "2026-09-01"
    assert corpo["periodo"]["aviso_nao_publicado"] == (
        "O IPCA de dez/2026 ainda não foi publicado pelo IBGE. O cálculo usa set/2026."
    )


def test_lacuna_no_resumo(api, banco):
    import psycopg

    with psycopg.connect(banco["admin"], autocommit=True) as conn:
        conn.execute(
            """
            UPDATE publico.observacao_publicada SET valor = NULL, situacao = 'ausente'
            WHERE indicador_codigo = 'ipca' AND data_referencia = '2025-03-01'
            """
        )
    corpo = api.get("/v1/indicadores/ipca/resumo?inicio=2025-01&fim=2025-12").json()
    assert corpo["situacao"] == "lacuna"
    assert corpo["meses_ausentes"] == ["2025-03-01"]
    assert corpo["acumulado_percentual"] is None
    serie = api.get("/v1/indicadores/ipca/serie?inicio=2025-01&fim=2025-12").json()
    assert serie["observacoes"][2] == {"data": "2025-03-01", "valor": None, "situacao": "ausente"}
    assert serie["derivadas"]["acumulado_no_periodo"][2:] == [None] * 10


def test_etag_devolve_304(api):
    primeira = api.get("/v1/indicadores/ipca/serie")
    segunda = api.get(
        "/v1/indicadores/ipca/serie", headers={"If-None-Match": primeira.headers["ETag"]}
    )
    assert segunda.status_code == 304


def test_resumo_de_serie_de_nivel(api, validar_resposta):
    """Séries de nível usam variação simples (FR-023); aqui com o número-índice do IPCA."""
    corpo = api.get("/v1/indicadores/ipca_indice/resumo?inicio=2021-01&fim=2025-12").json()
    validar_resposta("/v1/indicadores/{codigo}/resumo", 200, corpo)
    assert corpo["situacao"] == "ok"
    assert (corpo["valor_inicial"], corpo["valor_final"]) == ("5574.49", "7403.29")
    assert corpo["variacao_percentual"] == "32.81"
    assert (corpo["minimo"], corpo["maximo"]) == ("5574.49", "7403.29")
    assert corpo["meses_considerados"] == 60
    assert corpo["acumulado_percentual"] is None
