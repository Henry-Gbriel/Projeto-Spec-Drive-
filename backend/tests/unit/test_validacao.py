from datetime import date
from decimal import Decimal

import pytest

from apoio import ler_fixture
from observatorio.catalogo import carregar_catalogo
from observatorio.coleta.base import ObservacaoFonte
from observatorio.coleta.sidra import interpretar_corpo
from observatorio.tratamento.merge import calcular_diferencas
from observatorio.tratamento.modelos import ObservacaoTratada, ha_bloqueante
from observatorio.tratamento.padronizacao import padronizar
from observatorio.tratamento.validacao import (
    validar_conferencia,
    validar_datas_futuras,
    validar_fonte,
    validar_serie,
)

CATALOGO = {i.codigo: i for i in carregar_catalogo()}
IPCA = CATALOGO["ipca"]
HOJE = date(2026, 10, 22)
INTERVALO = (date(2025, 1, 1), HOJE)


def regras(ocorrencias):
    return {(o.regra, o.severidade) for o in ocorrencias}


def tratar(nome: str) -> list[ObservacaoTratada]:
    return padronizar(IPCA, interpretar_corpo(ler_fixture(nome)), HOJE).observacoes


def vigentes_de(nome: str) -> dict[date, Decimal | None]:
    return {o.data: o.valor for o in tratar(nome)}


def test_esquema_invalido_e_tratado_pelo_conector():
    from observatorio.coleta.base import ErroEsquema

    with pytest.raises(ErroEsquema):
        interpretar_corpo(ler_fixture("sidra_esquema_invalido.json"))


def test_data_duplicada_na_fonte_e_bloqueante():
    observacoes = interpretar_corpo(ler_fixture("sidra_data_duplicada.json"))
    ocorrencias = validar_fonte(observacoes, carga_completa=False)
    assert ("data_duplicada_na_fonte", "bloqueante") in regras(ocorrencias)
    assert ha_bloqueante(ocorrencias)


def test_serie_vazia_na_carga_completa_e_bloqueante():
    assert ("serie_vazia", "bloqueante") in regras(validar_fonte([], carga_completa=True))
    assert validar_fonte([], carga_completa=False) == []


def test_valor_nao_numerico_e_aviso():
    observacoes = interpretar_corpo(ler_fixture("sidra_com_lacuna.json"))
    ocorrencias = validar_fonte(observacoes, carga_completa=False)
    assert regras(ocorrencias) == {("valor_nao_numerico", "aviso")}


def test_lacuna_e_aviso():
    ocorrencias = validar_serie(IPCA, tratar("sidra_com_lacuna.json"), {}, INTERVALO)
    assert [(o.regra, o.data) for o in ocorrencias] == [("lacuna", date(2025, 3, 1))]
    assert not ha_bloqueante(ocorrencias)


def test_fora_do_intervalo_e_bloqueante():
    novas = [ObservacaoTratada(date(2026, 9, 1), Decimal("120"))]
    ocorrencias = validar_serie(IPCA, novas, {}, INTERVALO)
    assert ("fora_do_intervalo", "bloqueante") in regras(ocorrencias)
    novas = [ObservacaoTratada(date(2026, 9, 1), Decimal("-5.01"))]
    assert ha_bloqueante(validar_serie(IPCA, novas, {}, INTERVALO))


def test_queda_de_cobertura_e_bloqueante():
    vigentes = vigentes_de("sidra_recorte_2025_2026.json")
    novas = [o for o in tratar("sidra_recorte_2025_2026.json") if o.data != date(2026, 6, 1)]
    ocorrencias = validar_serie(IPCA, novas, vigentes, INTERVALO)
    assert [(o.regra, o.data) for o in ocorrencias if o.severidade == "bloqueante"] == [
        ("queda_de_cobertura", date(2026, 6, 1))
    ]


def test_valor_publicado_que_vira_ausente_e_queda_de_cobertura():
    vigentes = vigentes_de("sidra_recorte_2025_2026.json")
    ocorrencias = validar_serie(IPCA, tratar("sidra_com_lacuna.json"), vigentes, INTERVALO)
    assert ("queda_de_cobertura", "bloqueante") in regras(ocorrencias)


def test_vigentes_fora_do_intervalo_nao_sao_cobrados():
    vigentes = {date(2010, 1, 1): Decimal("0.75")}
    ocorrencias = validar_serie(IPCA, tratar("sidra_recorte_2025_2026.json"), vigentes, INTERVALO)
    assert not ha_bloqueante(ocorrencias)


def test_revisao_grande_e_aviso():
    vigentes = vigentes_de("sidra_recorte_2025_2026.json")
    ocorrencias = validar_serie(IPCA, tratar("sidra_revisada.json"), vigentes, INTERVALO)
    assert [(o.regra, o.severidade, o.data) for o in ocorrencias] == [
        ("revisao_grande", "aviso", date(2026, 8, 1))
    ]


def test_data_futura_e_descartada_com_aviso():
    selic = CATALOGO["selic_meta"]
    observacoes = [
        ObservacaoFonte(date(2026, 9, 30), Decimal("13.75")),
        ObservacaoFonte(date(2026, 11, 4), Decimal("13.75")),
    ]
    resultado = padronizar(selic, observacoes, HOJE)
    assert resultado.datas_futuras == [date(2026, 11, 4)]
    assert regras(validar_datas_futuras(resultado.datas_futuras)) == {("data_futura", "aviso")}


def test_divergencia_entre_fontes_e_aviso():
    novas = tratar("sidra_recorte_2025_2026.json")
    conferencia = [ObservacaoTratada(date(2026, 9, 1), Decimal("0.83"))]
    ocorrencias = validar_conferencia(novas, conferencia, "SGS 433")
    assert [(o.regra, o.severidade, o.data) for o in ocorrencias] == [
        ("divergencia_fontes", "aviso", date(2026, 9, 1))
    ]


def test_diferencas_do_merge():
    vigentes = vigentes_de("sidra_recorte_2025_2026.json")
    del vigentes[date(2026, 9, 1)]
    diferencas = calcular_diferencas(tratar("sidra_revisada.json"), vigentes)
    assert [o.data for o in diferencas.inserir] == [date(2026, 9, 1)]
    assert [(o.data, o.valor) for o in diferencas.revisar] == [
        (date(2026, 8, 1), Decimal("0.990000"))
    ]
    assert diferencas.inalteradas == 19


def test_sem_mudancas_gera_diferenca_vazia():
    vigentes = vigentes_de("sidra_recorte_2025_2026.json")
    assert calcular_diferencas(tratar("sidra_recorte_2025_2026.json"), vigentes).vazia
