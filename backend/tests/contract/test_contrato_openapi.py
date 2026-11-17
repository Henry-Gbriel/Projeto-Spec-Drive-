"""A API implementa exatamente as rotas documentadas da Entrega 1 (portão de CI 'contrato')."""

from observatorio.api.app import criar_app


def test_rotas_documentadas(contrato):
    servidas = set(criar_app().openapi()["paths"])
    entrega_1 = {
        caminho
        for caminho, operacoes in contrato["paths"].items()
        if operacoes["get"].get("x-entrega") == 1
    }
    assert entrega_1 <= servidas, f"faltam rotas: {entrega_1 - servidas}"
    assert servidas <= set(contrato["paths"]), (
        f"rotas sem contrato: {servidas - set(contrato['paths'])}"
    )


def test_somente_get(contrato):
    for caminho, operacoes in criar_app().openapi()["paths"].items():
        assert set(operacoes) == {"get"}, caminho


def test_saude(api, validar_resposta):
    resposta = api.get("/v1/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok", "banco": "ok"}
    validar_resposta("/v1/saude", 200, resposta.json())


def _schema_200(documento: dict, caminho: str) -> dict:
    """Schema JSON da resposta 200 de um caminho, com o $ref de topo resolvido."""
    resposta = documento["paths"][caminho]["get"]["responses"]["200"]
    conteudo = resposta.get("content", {}).get("application/json")
    if not conteudo:
        return {}
    schema = conteudo["schema"]
    while "$ref" in schema:
        nome = schema["$ref"].split("/")[-1]
        schema = documento["components"]["schemas"][nome]
    return schema


def test_campos_das_respostas_batem_com_o_contrato(contrato):
    """Para cada rota JSON da Entrega 1, o OpenAPI servido tem os mesmos campos do contrato
    e exige pelo menos os campos que o contrato exige."""
    servido = criar_app().openapi()
    comparadas = 0
    for caminho, operacoes in contrato["paths"].items():
        if operacoes["get"].get("x-entrega") != 1:
            continue
        esperado = _schema_200(contrato, caminho)
        obtido = _schema_200(servido, caminho)
        if not esperado.get("properties"):
            continue  # CSV
        assert set(obtido["properties"]) == set(esperado["properties"]), caminho
        faltando = set(esperado.get("required", [])) - set(obtido.get("required", []))
        assert not faltando, (
            f"{caminho}: campos obrigatórios no contrato e opcionais na API: {faltando}"
        )
        comparadas += 1
    assert comparadas >= 6, f"só {comparadas} rotas comparadas"
