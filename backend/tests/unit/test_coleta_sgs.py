from datetime import date
from decimal import Decimal

import httpx
import pytest
import respx

from apoio import ler_fixture
from observatorio.coleta.base import ClienteHttp, ErroEsquema
from observatorio.coleta.sgs import ConectorSgs, blocos_de_datas, interpretar_corpo

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"


def test_interpreta_resposta_real():
    observacoes = interpretar_corpo(ler_fixture("sgs_433.json"))
    assert len(observacoes) == 393
    assert observacoes[0].data == date(1994, 1, 1)
    assert observacoes[-1].valor == Decimal("0.82")


def test_janela_sem_dados_retorna_lista_vazia():
    corpo = b'{"erro":{"statusCode":404,"detail":"Value(s) not found"}}'
    assert interpretar_corpo(corpo) == []


@pytest.mark.parametrize(
    "corpo",
    [b'{"erro":{"statusCode":500}}', b'{"x":1}', b'[{"data":"2025-01-01","valor":"1"}]', b"[1]"],
)
def test_esquema_invalido(corpo):
    with pytest.raises(ErroEsquema):
        interpretar_corpo(corpo)


def test_blocos_de_no_maximo_dez_anos():
    blocos = blocos_de_datas(date(1999, 1, 1), date(2026, 10, 22))
    assert blocos[0] == (date(1999, 1, 1), date(2008, 12, 31))
    assert blocos[1] == (date(2009, 1, 1), date(2018, 12, 31))
    assert blocos[-1] == (date(2019, 1, 1), date(2026, 10, 22))
    assert blocos_de_datas(date(2026, 1, 1), date(2026, 3, 1)) == [
        (date(2026, 1, 1), date(2026, 3, 1))
    ]


@respx.mock
def test_coleta_em_blocos_e_aceita_404_de_janela_vazia():
    rota = respx.get(URL).mock(
        side_effect=[
            httpx.Response(200, content=b'[{"data":"01/01/2000","valor":"0.62"}]'),
            httpx.Response(404, content=b'{"erro":{"statusCode":404}}'),
        ]
    )
    conector = ConectorSgs(ClienteHttp(espera_maxima=0, aceitar=(404,)))
    resultado = conector.coletar({"codigo": 433}, date(2000, 1, 1), date(2015, 1, 1))
    assert rota.call_count == 2
    assert rota.calls[0].request.url.params["dataInicial"] == "01/01/2000"
    assert rota.calls[0].request.url.params["dataFinal"] == "31/12/2009"
    assert [o.valor for o in conector.interpretar(resultado)] == [Decimal("0.62")]
