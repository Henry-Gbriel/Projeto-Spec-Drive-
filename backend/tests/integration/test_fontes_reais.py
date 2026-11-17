"""Consulta as fontes oficiais de verdade (rede). Não roda por padrão.

Uso: `uv run pytest -m fontes_reais`. No CI roda toda segunda-feira sem bloquear PRs:
detecta cedo mudanças de formato ou de endereço nas APIs do IBGE e do Banco Central.
"""

from datetime import date
from decimal import Decimal

import pytest

from observatorio.coleta.sgs import ConectorSgs
from observatorio.coleta.sidra import ConectorSidra

pytestmark = pytest.mark.fontes_reais


def test_sidra_ipca_variacao_mensal():
    conector = ConectorSidra()
    resultado = conector.coletar(
        {"tabela": 1737, "variavel": 63}, date(2025, 1, 1), date(2025, 3, 1)
    )
    observacoes = conector.interpretar(resultado)
    assert [o.data for o in observacoes] == [date(2025, 1, 1), date(2025, 2, 1), date(2025, 3, 1)]
    assert all(isinstance(o.valor, Decimal) for o in observacoes)


def test_sidra_numero_indice_base_dez_1993():
    conector = ConectorSidra()
    resultado = conector.coletar(
        {"tabela": 1737, "variavel": 2266}, date(1993, 12, 1), date(1993, 12, 1)
    )
    [observacao] = conector.interpretar(resultado)
    assert observacao.valor == Decimal(100)


def test_sgs_433_confere_com_sidra():
    sgs = ConectorSgs()
    sidra = ConectorSidra()
    inicio, fim = date(2024, 1, 1), date(2024, 12, 31)
    pelo_sgs = {o.data: o.valor for o in sgs.interpretar(sgs.coletar({"codigo": 433}, inicio, fim))}
    pelo_sidra = {
        o.data: o.valor
        for o in sidra.interpretar(sidra.coletar({"tabela": 1737, "variavel": 63}, inicio, fim))
    }
    assert pelo_sgs == pelo_sidra
    assert len(pelo_sgs) == 12
