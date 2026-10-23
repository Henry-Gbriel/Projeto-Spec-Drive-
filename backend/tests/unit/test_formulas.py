"""Regras do IPCA contra valores de referência (SC-001, SC-002, FR-022, FR-026).

Os valores esperados foram calculados à parte, em 2026-10-22, com aritmética racional exata
(fractions.Fraction) sobre a série oficial do IBGE gravada em
fixtures/sidra_1737_v63.json (SIDRA tabela 1737, variável 63, jan/1994 a set/2026).
"""

import ast
import inspect
from datetime import date
from decimal import Decimal

import pytest

from apoio import serie_sidra
from observatorio.regras import ipca
from observatorio.regras.ipca import (
    LacunaNaSerie,
    acumulado_percentual,
    arredondar,
    fator_acumulado,
    fator_por_indice,
    simular_poder_de_compra,
)

VARIACOES = serie_sidra("sidra_1737_v63.json")
INDICES = serie_sidra("sidra_1737_v2266.json")


def mes(texto: str) -> date:
    return date(int(texto[:4]), int(texto[5:]), 1)


# valor, início, fim, meses, corrigido, acumulado %, poder de compra %, equivalente no início
CASOS_REFERENCIA = [
    ("100.00", "2016-01", "2025-12", 120, "164.77", "64.77", "-39.31", "60.69"),
    ("100.00", "2026-09", "2026-09", 1, "100.82", "0.82", "-0.81", "99.19"),
    ("1500.00", "2025-10", "2026-09", 12, "1568.64", "4.58", "-4.38", "1434.36"),
    ("1000.00", "1994-07", "2026-09", 387, "8977.07", "797.71", "-88.86", "111.39"),
    ("250.50", "2010-01", "2019-12", 120, "441.65", "76.31", "-43.28", "142.08"),
    ("1.00", "1994-07", "1994-12", 6, "1.19", "18.57", "-15.66", "0.84"),
    ("100.00", "2021-01", "2025-12", 60, "133.14", "33.14", "-24.89", "75.11"),
    ("99999.99", "2000-01", "2026-09", 321, "484457.02", "384.46", "-79.36", "20641.66"),
    ("50.00", "2020-01", "2020-12", 12, "52.26", "4.52", "-4.32", "47.84"),
    ("100.00", "1995-01", "2024-12", 360, "698.56", "598.56", "-85.68", "14.32"),
    ("3.33", "2022-03", "2022-03", 1, "3.38", "1.62", "-1.59", "3.28"),
    (
        "1000000000.00",
        "1994-07",
        "2026-09",
        387,
        "8977072379.59",
        "797.71",
        "-88.86",
        "111394891.09",
    ),
]


@pytest.mark.parametrize(
    "valor,inicio,fim,meses,corrigido,acumulado,poder,equivalente", CASOS_REFERENCIA
)
def test_simulador_confere_com_referencia(
    valor, inicio, fim, meses, corrigido, acumulado, poder, equivalente
):
    resultado = simular_poder_de_compra(Decimal(valor), VARIACOES, mes(inicio), mes(fim))
    assert resultado.meses_considerados == meses
    assert abs(resultado.valor_corrigido - Decimal(corrigido)) <= Decimal("0.01")
    assert resultado.inflacao_acumulada_percentual == Decimal(acumulado)
    assert resultado.variacao_poder_compra_percentual == Decimal(poder)
    assert abs(resultado.equivalente_no_inicio - Decimal(equivalente)) <= Decimal("0.01")


def test_quantidade_de_casos_de_referencia():
    assert len(CASOS_REFERENCIA) >= 10


def test_mes_unico_usa_apenas_a_variacao_do_mes():
    fator, meses = fator_acumulado(VARIACOES, mes("2026-09"), mes("2026-09"))
    assert meses == 1
    assert fator == Decimal("1.0082")


def test_acumulado_jan2016_dez2025_tem_120_meses():
    fator, meses = fator_acumulado(VARIACOES, mes("2016-01"), mes("2025-12"))
    assert meses == 120
    assert arredondar(acumulado_percentual(fator), 2) == Decimal("64.77")


@pytest.mark.parametrize(
    "inicio,fim",
    [
        ("1994-07", "2026-09"),
        ("2016-01", "2025-12"),
        ("2021-01", "2025-12"),
        ("2026-09", "2026-09"),
    ],
)
def test_conferencia_pelo_numero_indice(inicio, fim):
    fator, _ = fator_acumulado(VARIACOES, mes(inicio), mes(fim))
    pelo_indice = fator_por_indice(INDICES, mes(inicio), mes(fim))
    assert abs(fator / pelo_indice - 1) <= Decimal("0.0001")


def test_valor_corrigido_arredonda_meio_centavo_para_cima():
    variacoes = {mes("2020-01"): Decimal("0.5")}
    # 1,01 × 1,005 = 1,01505 -> 1,02 (ROUND_HALF_UP)
    resultado = simular_poder_de_compra(Decimal("1.01"), variacoes, mes("2020-01"), mes("2020-01"))
    assert resultado.valor_corrigido == Decimal("1.02")


def test_lacuna_impede_o_calculo_e_informa_os_meses():
    variacoes = dict(VARIACOES)
    variacoes[mes("2020-03")] = None
    del variacoes[mes("2020-05")]
    with pytest.raises(LacunaNaSerie) as erro:
        fator_acumulado(variacoes, mes("2020-01"), mes("2020-12"))
    assert erro.value.meses_ausentes == [mes("2020-03"), mes("2020-05")]


def test_periodo_invertido_e_valor_nao_positivo_sao_rejeitados():
    with pytest.raises(ValueError):
        fator_acumulado(VARIACOES, mes("2020-02"), mes("2020-01"))
    with pytest.raises(ValueError):
        simular_poder_de_compra(Decimal("0"), VARIACOES, mes("2020-01"), mes("2020-02"))


def test_regras_nao_usam_float():
    arvore = ast.parse(inspect.getsource(ipca))
    for no in ast.walk(arvore):
        assert not (isinstance(no, ast.Name) and no.id == "float"), "use Decimal, não float"
        assert not (isinstance(no, ast.Constant) and isinstance(no.value, float))
