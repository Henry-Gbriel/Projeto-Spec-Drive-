"""Tipos do tratamento de dados."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Literal

Severidade = Literal["bloqueante", "aviso"]


@dataclass(frozen=True)
class ObservacaoTratada:
    """Valor padronizado na frequência de exibição. `valor` None = ausente na fonte."""

    data: date
    valor: Decimal | None

    @property
    def situacao(self) -> str:
        return "ausente" if self.valor is None else "ok"


@dataclass(frozen=True)
class Ocorrencia:
    regra: str
    severidade: Severidade
    data: date | None = None
    detalhe: dict[str, Any] = field(default_factory=dict)


def ha_bloqueante(ocorrencias: list[Ocorrencia]) -> bool:
    return any(o.severidade == "bloqueante" for o in ocorrencias)
