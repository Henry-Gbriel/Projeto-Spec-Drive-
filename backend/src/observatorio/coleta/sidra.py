"""Conector do IBGE SIDRA (research R-01).

Resposta: lista JSON cujo primeiro elemento é o cabeçalho; os demais são observações com
`D3C` (período AAAAMM) e `V` (valor em texto, com ponto decimal).
"""

import json
from datetime import date
from typing import Any

from observatorio.coleta.base import (
    ClienteHttp,
    ErroEsquema,
    ObservacaoFonte,
    ResultadoColeta,
    ler_decimal,
)

URL_BASE = "https://apisidra.ibge.gov.br/values"


def montar_url(tabela: int, variavel: int, data_inicial: date, data_final: date) -> str:
    return f"{URL_BASE}/t/{tabela}/n1/all/v/{variavel}/p/{data_inicial:%Y%m}-{data_final:%Y%m}"


class ConectorSidra:
    def __init__(self, http: ClienteHttp | None = None):
        self._http = http or ClienteHttp()

    def coletar(
        self, parametros: dict[str, Any], data_inicial: date, data_final: date
    ) -> ResultadoColeta:
        url = montar_url(parametros["tabela"], parametros["variavel"], data_inicial, data_final)
        resposta = self._http.get(url)
        return ResultadoColeta(
            [resposta],
            {"data_inicial": data_inicial.isoformat(), "data_final": data_final.isoformat()},
        )

    def interpretar(self, resultado: ResultadoColeta) -> list[ObservacaoFonte]:
        observacoes: list[ObservacaoFonte] = []
        for resposta in resultado.respostas:
            observacoes.extend(interpretar_corpo(resposta.conteudo))
        return observacoes


def interpretar_corpo(conteudo: bytes) -> list[ObservacaoFonte]:
    try:
        linhas = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise ErroEsquema(f"resposta do SIDRA não é JSON: {erro}") from erro
    if not isinstance(linhas, list) or not linhas or not isinstance(linhas[0], dict):
        raise ErroEsquema("resposta do SIDRA sem cabeçalho")
    if linhas[0].get("V") != "Valor" or "D3C" not in linhas[0]:
        raise ErroEsquema("cabeçalho do SIDRA inesperado")

    observacoes = []
    for linha in linhas[1:]:
        periodo = linha.get("D3C") if isinstance(linha, dict) else None
        if not isinstance(periodo, str) or len(periodo) != 6 or not periodo.isdigit():
            raise ErroEsquema(f"período inválido no SIDRA: {periodo!r}")
        if "V" not in linha:
            raise ErroEsquema(f"linha do SIDRA sem valor: {periodo}")
        mes = int(periodo[4:])
        if not 1 <= mes <= 12:
            raise ErroEsquema(f"mês inválido no SIDRA: {periodo}")
        texto = linha["V"]
        valor = ler_decimal(texto)
        observacoes.append(
            ObservacaoFonte(
                date(int(periodo[:4]), mes, 1), valor, None if valor is not None else str(texto)
            )
        )
    return observacoes
