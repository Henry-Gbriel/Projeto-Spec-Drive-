"""Variação de séries de nível (FR-023, Constitution IV).

Valores esperados calculados à parte, em 2026-10-23, com fractions.Fraction sobre o
número-índice oficial do IPCA (fixtures/sidra_1737_v2266.json).
"""

import ast
import inspect
from datetime import date
from decimal import Decimal

import pytest

from apoio import serie_sidra
from observatorio.regras import variacao
from observatorio.regras.ipca import LacunaNaSerie
from observatorio.regras.meses import meses_entre
from observatorio.regras.variacao import resumir_nivel

INDICES = serie_sidra("sidra_1737_v2266.json")


def recorte(inicio: date, fim: date) -> list[tuple[date, Decimal | None]]:
    return [(m, INDICES.get(m)) for m in meses_entre(inicio, fim)]


@pytest.mark.parametrize(
    "inicio,fim,inicial,final,variacao_esperada",
    [
        (date(2021, 1, 1), date(2025, 12, 1), "5574.49", "7403.29", "32.81"),
        (date(1994, 7, 1), date(2026, 9, 1), "915.93", "7695.82", "740.22"),
        (date(2026, 9, 1), date(2026, 9, 1), "7695.82", "7695.82", "0.00"),
    ],
)
def test_referencias_do_numero_indice(inicio, fim, inicial, final, variacao_esperada):
    resumo = resumir_nivel(recorte(inicio, fim))
    assert resumo.valor_inicial == Decimal(inicial)
    assert resumo.valor_final == Decimal(final)
    assert resumo.variacao_percentual == Decimal(variacao_esperada)
    assert resumo.minimo == Decimal(inicial)
    assert resumo.maximo == Decimal(final)


def test_queda_minimo_e_maximo_no_meio_do_periodo():
    serie = [
        (date(2026, 1, 1), Decimal("5.6100")),
        (date(2026, 2, 1), Decimal("6.1000")),
        (date(2026, 3, 1), Decimal("4.9000")),
        (date(2026, 4, 1), Decimal("5.1447")),
    ]
    resumo = resumir_nivel(serie)
    assert resumo.variacao_percentual == Decimal("-8.29")  # (5,1447 / 5,61 − 1) × 100
    assert (resumo.minimo, resumo.maximo) == (Decimal("4.9000"), Decimal("6.1000"))


def test_arredonda_meio_para_cima():
    serie = [(date(2026, 1, 1), Decimal("200")), (date(2026, 2, 1), Decimal("200.01"))]
    assert resumir_nivel(serie).variacao_percentual == Decimal("0.01")  # 0,005 -> 0,01


def test_lacuna_impede_o_calculo():
    serie = recorte(date(2025, 1, 1), date(2025, 6, 1))
    serie[2] = (serie[2][0], None)
    with pytest.raises(LacunaNaSerie) as erro:
        resumir_nivel(serie)
    assert erro.value.meses_ausentes == [date(2025, 3, 1)]


def test_serie_vazia_e_valor_inicial_zero():
    with pytest.raises(ValueError, match="vazia"):
        resumir_nivel([])
    with pytest.raises(ValueError, match="zero"):
        resumir_nivel([(date(2026, 1, 1), Decimal(0)), (date(2026, 2, 1), Decimal(1))])


def test_regra_nao_usa_float():
    arvore = ast.parse(inspect.getsource(variacao))
    for no in ast.walk(arvore):
        assert not (isinstance(no, ast.Name) and no.id == "float")
        assert not (isinstance(no, ast.Constant) and isinstance(no.value, float))
