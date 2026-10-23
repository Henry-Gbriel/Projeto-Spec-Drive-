from datetime import date
from decimal import Decimal

from observatorio.catalogo import carregar_catalogo
from observatorio.coleta.base import ObservacaoFonte
from observatorio.tratamento.padronizacao import padronizar

CATALOGO = {i.codigo: i for i in carregar_catalogo()}
HOJE = date(2026, 10, 22)


def obs(texto: str, valor: str | None) -> ObservacaoFonte:
    return ObservacaoFonte(date.fromisoformat(texto), None if valor is None else Decimal(valor))


def test_media_mensal_exclui_mes_corrente_incompleto():
    euro = CATALOGO["euro_ptax"]
    resultado = padronizar(
        euro,
        [
            obs("2026-08-31", "6.10"),
            obs("2026-09-01", "6.00"),
            obs("2026-09-02", "6.20"),
            obs("2026-10-01", "6.30"),
        ],
        HOJE,
    )
    assert [(o.data, o.valor) for o in resultado.observacoes] == [
        (date(2026, 8, 1), Decimal("6.100000")),
        (date(2026, 9, 1), Decimal("6.100000")),
    ]


def test_mes_sem_nenhum_valor_fica_ausente():
    euro = CATALOGO["euro_ptax"]
    resultado = padronizar(euro, [obs("2026-09-01", None)], HOJE)
    assert resultado.observacoes[0].valor is None
    assert resultado.observacoes[0].situacao == "ausente"


def test_selic_vigente_no_fim_do_mes():
    selic = CATALOGO["selic_meta"]
    resultado = padronizar(
        selic,
        [obs("2026-09-01", "14.25"), obs("2026-09-17", "13.75"), obs("2026-09-30", "13.75")],
        HOJE,
    )
    assert resultado.observacoes[0].valor == Decimal("13.750000")


def test_conversao_de_reais_mil_para_bilhoes():
    base = CATALOGO["base_monetaria"]
    resultado = padronizar(base, [obs("2026-08-01", "514321987")], HOJE)
    assert resultado.observacoes[0].valor == Decimal("514.321987")


def test_mensal_sem_agregacao_mantem_valores_e_quantiza():
    ipca = CATALOGO["ipca_indice"]
    resultado = padronizar(ipca, [obs("2026-09-01", "7695.8200000000000")], HOJE)
    assert resultado.observacoes[0].valor == Decimal("7695.820000")
