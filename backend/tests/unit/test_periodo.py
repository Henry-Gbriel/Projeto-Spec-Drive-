from datetime import date

import pytest

from observatorio.regras.periodo import EntradaInvalida, resolver_periodo

PRIMEIRO = date(1994, 7, 1)
ULTIMO = date(2026, 9, 1)


def resolver(**kwargs):
    base = {"periodo": None, "inicio": None, "fim": None}
    base.update(kwargs)
    return resolver_periodo(
        **base, primeiro_mes=PRIMEIRO, ultimo_mes=ULTIMO, nome="IPCA", instituicao="IBGE"
    )


@pytest.mark.parametrize(
    "atalho,inicio",
    [
        ("12m", date(2025, 10, 1)),
        ("3a", date(2023, 10, 1)),
        ("5a", date(2021, 10, 1)),
        ("10a", date(2016, 10, 1)),
    ],
)
def test_atalhos_terminam_no_ultimo_mes_publicado(atalho, inicio):
    periodo = resolver(periodo=atalho)
    assert periodo.inicio == inicio
    assert periodo.fim_utilizado == ULTIMO
    assert periodo.aviso_nao_publicado is None


def test_padrao_e_cinco_anos():
    assert resolver().inicio == date(2021, 10, 1)


def test_atalho_limitado_ao_inicio_da_serie():
    periodo = resolver_periodo(
        periodo="10a",
        inicio=None,
        fim=None,
        primeiro_mes=date(2020, 1, 1),
        ultimo_mes=ULTIMO,
        nome="IPCA",
        instituicao="IBGE",
    )
    assert periodo.inicio == date(2020, 1, 1)


def test_periodo_personalizado():
    periodo = resolver(inicio="2016-01", fim="2025-12")
    assert (periodo.inicio, periodo.fim_utilizado) == (date(2016, 1, 1), date(2025, 12, 1))


def test_fim_nao_publicado_usa_ultimo_mes_com_aviso():
    periodo = resolver(inicio="2016-01", fim="2026-12")
    assert periodo.fim_solicitado == date(2026, 12, 1)
    assert periodo.fim_utilizado == ULTIMO
    assert periodo.aviso_nao_publicado == (
        "O IPCA de dez/2026 ainda não foi publicado pelo IBGE. O cálculo usa set/2026."
    )


@pytest.mark.parametrize(
    "kwargs,campo,trecho",
    [
        ({"inicio": "2020-05", "fim": "2020-01"}, "inicio", "anterior ou igual"),
        ({"inicio": "1990-01", "fim": "2020-01"}, "inicio", "a partir de jul/1994"),
        ({"inicio": "2026-10", "fim": "2026-12"}, "inicio", "Ainda não há IPCA publicado"),
        ({"inicio": "2020-13", "fim": "2021-01"}, "inicio", "AAAA-MM"),
        ({"inicio": "2020-01"}, "fim", "Informe a data final"),
        ({"periodo": "7a"}, "periodo", "Período inválido"),
        ({"periodo": "5a", "inicio": "2020-01", "fim": "2020-02"}, "periodo", "não os dois"),
    ],
)
def test_entradas_invalidas(kwargs, campo, trecho):
    with pytest.raises(EntradaInvalida) as erro:
        resolver(**kwargs)
    assert erro.value.erros[0].campo == campo
    assert trecho in erro.value.erros[0].mensagem
