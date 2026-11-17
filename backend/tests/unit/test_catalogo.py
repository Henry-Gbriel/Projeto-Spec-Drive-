import pytest
from pydantic import ValidationError

from observatorio.catalogo import Indicador, carregar_catalogo

BASE = {
    "codigo": "ipca",
    "nome": "IPCA",
    "descricao": "Inflação",
    "instituicao": "IBGE",
    "url_origem": "https://sidra.ibge.gov.br/tabela/1737",
    "conector": "sidra",
    "unidade": "% ao mês",
    "frequencia_fonte": "mensal",
    "frequencia_exibicao": "mensal",
    "casas_decimais": 2,
    "natureza": "real",
    "situacao_catalogo": "ativo",
    "entrega": 1,
}


def test_catalogo_do_repositorio_e_valido():
    indicadores = carregar_catalogo()
    codigos = {i.codigo for i in indicadores}
    assert {"ipca", "ipca_indice", "dolar_ptax", "selic_meta", "m2"} <= codigos
    assert len(indicadores) == 12
    assert all(i.natureza == "real" for i in indicadores)
    assert [i.codigo for i in indicadores if i.ativo] == ["ipca", "ipca_indice"]


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("codigo", "IPCA-Mensal"),
        ("natureza", "estimado"),
        ("casas_decimais", 7),
        ("casas_decimais", -1),
        ("unidade", "   "),
        ("instituicao", ""),
        ("conector", "ftp"),
    ],
)
def test_rejeita_metadados_invalidos(campo, valor):
    with pytest.raises(ValidationError):
        Indicador.model_validate({**BASE, campo: valor})


def test_unidade_e_instituicao_sao_obrigatorias():
    for campo in ("unidade", "instituicao"):
        dados = dict(BASE)
        del dados[campo]
        with pytest.raises(ValidationError):
            Indicador.model_validate(dados)
