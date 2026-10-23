"""API de teste com o IPCA real (fixtures gravadas) publicado num banco temporário."""

from datetime import datetime
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from apoio import ConectorPorVariavel
from observatorio.catalogo import carregar_catalogo, sincronizar_catalogo
from observatorio.config import FUSO_HORARIO, obter_configuracao
from observatorio.repositorio.conexao import pool_api
from observatorio.rotina import executar

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs"
    / "001-observatorio-do-real"
    / "contracts"
    / "api-openapi.yaml"
)
URI = "urn:contrato"
AGORA = datetime(2026, 10, 22, 6, 17, tzinfo=FUSO_HORARIO)


@pytest.fixture(scope="session")
def contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def validar_resposta(contrato):
    """Valida corpo JSON contra o schema do contrato para (caminho, método, status)."""
    registro = Registry().with_resource(URI, Resource(contrato, specification=DRAFT202012))

    def validar(caminho: str, status: int, corpo, metodo: str = "get") -> None:
        operacao = contrato["paths"][caminho][metodo]
        resposta = operacao["responses"][str(status)]
        if "$ref" in resposta:
            nome = resposta["$ref"].split("/")[-1]
            resposta = contrato["components"]["responses"][nome]
            ponteiro = f"/components/responses/{nome}"
        else:
            ponteiro = f"/paths/{caminho.replace('/', '~1')}/{metodo}/responses/{status}"
        [tipo] = resposta["content"]
        ponteiro += f"/content/{tipo.replace('/', '~1')}/schema"
        Draft202012Validator({"$ref": f"{URI}#{ponteiro}"}, registry=registro).validate(corpo)

    return validar


@pytest.fixture
def api(banco, monkeypatch, conn_coletor):
    catalogo = carregar_catalogo()
    sincronizar_catalogo(conn_coletor, catalogo)
    conector = ConectorPorVariavel({63: "sidra_1737_v63.json", 2266: "sidra_1737_v2266.json"})
    resultados = executar(conn_coletor, catalogo, {"sidra": conector}, agora=AGORA)
    assert {r.status for r in resultados} == {"publicado"}

    monkeypatch.setenv("API_DATABASE_URL", banco["api_leitura"])
    obter_configuracao.cache_clear()
    pool_api.cache_clear()
    from observatorio.api.app import criar_app

    with TestClient(criar_app()) as cliente:
        yield cliente
    pool_api().close()
    pool_api.cache_clear()
    obter_configuracao.cache_clear()
