"""Conector do Sistema Gerenciador de Séries Temporais (SGS) do Banco Central (research R-02).

- Datas em dd/mm/aaaa; valores em texto com ponto decimal.
- Séries diárias aceitam no máximo 10 anos por consulta: a carga é dividida em blocos.
- Janela sem dados responde HTTP 404 com {"erro": {...}}: tratado como "sem dados", não falha.
"""

import json
from datetime import date, datetime, timedelta
from typing import Any

from observatorio.coleta.base import (
    ClienteHttp,
    ErroEsquema,
    ObservacaoFonte,
    ResultadoColeta,
    ler_decimal,
)

URL_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
ANOS_POR_CONSULTA = 10


def blocos_de_datas(
    data_inicial: date, data_final: date, anos: int = ANOS_POR_CONSULTA
) -> list[tuple[date, date]]:
    """Divide o intervalo em blocos de até `anos` anos (o último dia de cada bloco incluso)."""
    blocos = []
    inicio = data_inicial
    while inicio <= data_final:
        try:
            limite = inicio.replace(year=inicio.year + anos) - timedelta(days=1)
        except ValueError:  # 29/02
            limite = inicio.replace(year=inicio.year + anos, day=28) - timedelta(days=1)
        fim = min(limite, data_final)
        blocos.append((inicio, fim))
        inicio = fim + timedelta(days=1)
    return blocos


class ConectorSgs:
    def __init__(self, http: ClienteHttp | None = None):
        self._http = http or ClienteHttp(aceitar=(404,))

    def coletar(
        self, parametros: dict[str, Any], data_inicial: date, data_final: date
    ) -> ResultadoColeta:
        url = URL_BASE.format(codigo=int(parametros["codigo"]))
        respostas = [
            self._http.get(
                url,
                params={
                    "formato": "json",
                    "dataInicial": inicio.strftime("%d/%m/%Y"),
                    "dataFinal": fim.strftime("%d/%m/%Y"),
                },
            )
            for inicio, fim in blocos_de_datas(data_inicial, data_final)
        ]
        return ResultadoColeta(
            respostas,
            {"data_inicial": data_inicial.isoformat(), "data_final": data_final.isoformat()},
        )

    def interpretar(self, resultado: ResultadoColeta) -> list[ObservacaoFonte]:
        observacoes: list[ObservacaoFonte] = []
        for resposta in resultado.respostas:
            observacoes.extend(interpretar_corpo(resposta.conteudo))
        return observacoes


def interpretar_corpo(conteudo: bytes) -> list[ObservacaoFonte]:
    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise ErroEsquema(f"resposta do SGS não é JSON: {erro}") from erro
    if isinstance(dados, dict) and "erro" in dados:
        if dados["erro"].get("statusCode") == 404:
            return []  # janela sem valores
        raise ErroEsquema(f"erro do SGS: {dados['erro']}")
    if not isinstance(dados, list):
        raise ErroEsquema("resposta do SGS não é uma lista")

    observacoes = []
    for item in dados:
        if not isinstance(item, dict) or "data" not in item or "valor" not in item:
            raise ErroEsquema(f"item do SGS inesperado: {item!r}")
        try:
            data = datetime.strptime(item["data"], "%d/%m/%Y").date()  # noqa: DTZ007
        except (TypeError, ValueError) as erro:
            raise ErroEsquema(f"data inválida no SGS: {item['data']!r}") from erro
        valor = ler_decimal(item["valor"])
        observacoes.append(
            ObservacaoFonte(data, valor, None if valor is not None else str(item["valor"]))
        )
    return observacoes
