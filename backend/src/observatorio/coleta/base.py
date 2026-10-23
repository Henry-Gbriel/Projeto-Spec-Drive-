"""Tipos e utilitários comuns aos conectores das fontes oficiais."""

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Protocol

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

TIMEOUT_SEGUNDOS = 30.0
TENTATIVAS = 3
USER_AGENT = (
    "ObservatorioDoReal/0.1 (projeto de educacao economica)"  # cabeçalho HTTP só aceita ASCII
)


class ErroColeta(Exception):  # noqa: N818 (nome de domínio)
    """A fonte não respondeu corretamente mesmo após as novas tentativas."""


class ErroEsquema(Exception):  # noqa: N818 (nome de domínio)
    """A resposta da fonte não tem o formato esperado (regra esquema_invalido)."""


class _ErroTemporario(Exception):
    """Resposta 5xx ou 429: vale tentar de novo."""


@dataclass(frozen=True)
class RespostaBruta:
    """Uma resposta HTTP da fonte, exatamente como chegou."""

    url: str
    http_status: int
    conteudo: bytes


@dataclass(frozen=True)
class ObservacaoFonte:
    """Valor lido da fonte. `valor` None significa que a fonte não trouxe número."""

    data: date
    valor: Decimal | None
    texto_fonte: str | None = None


@dataclass(frozen=True)
class ResultadoColeta:
    respostas: list[RespostaBruta]
    parametros: dict[str, Any] = field(default_factory=dict)

    @property
    def conteudo_bruto(self) -> bytes:
        """Bytes concatenados das respostas, usados para o hash de deduplicação."""
        return b"\n".join(r.conteudo for r in self.respostas)

    @property
    def conteudo_json(self) -> list[Any]:
        """Corpos JSON das respostas, na ordem das requisições (guardado em bruto.payload)."""
        return [json.loads(r.conteudo) for r in self.respostas]

    @property
    def http_status(self) -> int:
        return max(r.http_status for r in self.respostas)

    @property
    def url(self) -> str:
        return " ".join(r.url for r in self.respostas)


class Conector(Protocol):
    def coletar(
        self, parametros: dict[str, Any], data_inicial: date, data_final: date
    ) -> ResultadoColeta: ...

    def interpretar(self, resultado: ResultadoColeta) -> list[ObservacaoFonte]: ...


def ler_decimal(texto: Any) -> Decimal | None:
    """Converte o texto da fonte em Decimal; textos não numéricos ('...', '-', 'X') viram None."""
    if texto is None:
        return None
    try:
        valor = Decimal(str(texto).strip())
    except InvalidOperation:
        return None
    return valor if valor.is_finite() else None


class ClienteHttp:
    """GET com timeout de 30 s e 3 tentativas com espera exponencial (research R-12)."""

    def __init__(
        self,
        cliente: httpx.Client | None = None,
        espera_maxima: float = 10.0,
        aceitar: tuple[int, ...] = (),
    ):
        self._cliente = cliente or httpx.Client(
            timeout=TIMEOUT_SEGUNDOS, headers={"User-Agent": USER_AGENT}, follow_redirects=True
        )
        self._espera_maxima = espera_maxima
        self._aceitar = aceitar

    def get(self, url: str, params: dict[str, Any] | None = None) -> RespostaBruta:
        tentar = retry(
            reraise=True,
            stop=stop_after_attempt(TENTATIVAS),
            wait=wait_exponential(multiplier=1, max=self._espera_maxima),
            retry=retry_if_exception_type((httpx.TransportError, _ErroTemporario)),
        )
        try:
            return tentar(self._get_uma_vez)(url, params)
        except (httpx.TransportError, _ErroTemporario) as erro:
            raise ErroColeta(f"falha ao consultar {url}: {erro}") from erro

    def _get_uma_vez(self, url: str, params: dict[str, Any] | None) -> RespostaBruta:
        resposta = self._cliente.get(url, params=params)
        if resposta.status_code >= 500 or resposta.status_code == 429:
            raise _ErroTemporario(f"HTTP {resposta.status_code}")
        if resposta.status_code >= 400 and resposta.status_code not in self._aceitar:
            raise ErroColeta(f"HTTP {resposta.status_code} em {resposta.url}")
        return RespostaBruta(str(resposta.url), resposta.status_code, resposta.content)
