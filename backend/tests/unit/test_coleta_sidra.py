import json
from datetime import date
from decimal import Decimal

import httpx
import pytest
import respx

from apoio import ler_fixture
from observatorio.coleta.base import ClienteHttp, ErroColeta, ErroEsquema
from observatorio.coleta.sidra import ConectorSidra, interpretar_corpo, montar_url

PARAMETROS = {"tabela": 1737, "variavel": 63}
URL = "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/63/p/202501-202610"


def conector() -> ConectorSidra:
    return ConectorSidra(ClienteHttp(espera_maxima=0))


def test_monta_url_com_intervalo_de_meses():
    assert montar_url(1737, 63, date(2025, 1, 1), date(2026, 10, 22)) == URL


def test_interpreta_resposta_real_ignorando_cabecalho():
    observacoes = interpretar_corpo(ler_fixture("sidra_1737_v63.json"))
    assert len(observacoes) == 393
    assert observacoes[0].data == date(1994, 1, 1)
    assert observacoes[-1].data == date(2026, 9, 1)
    assert observacoes[-1].valor == Decimal("0.82")
    assert all(isinstance(o.valor, Decimal) for o in observacoes)


def test_numero_indice_mantem_precisao():
    observacoes = interpretar_corpo(ler_fixture("sidra_1737_v2266.json"))
    assert observacoes[-1].valor == Decimal("7695.8200000000000")


@pytest.mark.parametrize("texto", ["...", "-", "X", ""])
def test_textos_nao_numericos_viram_ausente(texto):
    corpo = json.dumps([{"V": "Valor", "D3C": "Mês (Código)"}, {"V": texto, "D3C": "202503"}])
    corpo = corpo.encode()
    [observacao] = interpretar_corpo(corpo)
    assert observacao.valor is None
    assert observacao.texto_fonte == texto


def test_fixture_com_lacuna_tem_um_mes_ausente():
    observacoes = interpretar_corpo(ler_fixture("sidra_com_lacuna.json"))
    assert [o.data for o in observacoes if o.valor is None] == [date(2025, 3, 1)]


@pytest.mark.parametrize(
    "corpo",
    [
        b"<html>erro</html>",
        b'{"V":"Valor"}',
        b'[{"mensagem":"Tabela nao encontrada"}]',
        b'[{"V":"Valor","D3C":"Mes"},{"V":"0.5","D3C":"2025-01"}]',
        b'[{"V":"Valor","D3C":"Mes"},{"D3C":"202501"}]',
    ],
)
def test_esquema_invalido(corpo):
    with pytest.raises(ErroEsquema):
        interpretar_corpo(corpo)


@respx.mock
def test_coleta_e_interpreta():
    respx.get(URL).mock(
        return_value=httpx.Response(200, content=ler_fixture("sidra_recorte_2025_2026.json"))
    )
    resultado = conector().coletar(PARAMETROS, date(2025, 1, 1), date(2026, 10, 22))
    assert resultado.http_status == 200
    assert resultado.parametros == {"data_inicial": "2025-01-01", "data_final": "2026-10-22"}
    assert len(conector().interpretar(resultado)) == 21


@respx.mock
def test_tenta_de_novo_apos_erro_temporario():
    rota = respx.get(URL).mock(
        side_effect=[
            httpx.Response(503),
            httpx.ConnectTimeout("tempo esgotado"),
            httpx.Response(200, content=ler_fixture("sidra_recorte_2025_2026.json")),
        ]
    )
    conector().coletar(PARAMETROS, date(2025, 1, 1), date(2026, 10, 22))
    assert rota.call_count == 3


@respx.mock
def test_falha_com_erro_claro_apos_tres_tentativas():
    rota = respx.get(URL).mock(return_value=httpx.Response(502))
    with pytest.raises(ErroColeta, match="falha ao consultar"):
        conector().coletar(PARAMETROS, date(2025, 1, 1), date(2026, 10, 22))
    assert rota.call_count == 3


@respx.mock
def test_erro_4xx_nao_e_repetido():
    rota = respx.get(URL).mock(return_value=httpx.Response(400))
    with pytest.raises(ErroColeta, match="HTTP 400"):
        conector().coletar(PARAMETROS, date(2025, 1, 1), date(2026, 10, 22))
    assert rota.call_count == 1
