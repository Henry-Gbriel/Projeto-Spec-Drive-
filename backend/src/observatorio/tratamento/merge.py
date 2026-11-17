"""Cálculo das diferenças entre a coleta e os valores vigentes (merge SCD tipo 2).

Nunca há UPDATE de valor: uma revisão fecha a linha vigente e abre outra (data-model.md).
"""

import hashlib
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from observatorio.tratamento.modelos import ObservacaoTratada


@dataclass
class Diferencas:
    inserir: list[ObservacaoTratada] = field(default_factory=list)
    revisar: list[ObservacaoTratada] = field(default_factory=list)
    inalteradas: int = 0

    @property
    def vazia(self) -> bool:
        return not self.inserir and not self.revisar


def calcular_diferencas(
    novas: list[ObservacaoTratada], vigentes: dict[date, Decimal | None]
) -> Diferencas:
    diferencas = Diferencas()
    for o in novas:
        if o.data not in vigentes:
            diferencas.inserir.append(o)
        elif vigentes[o.data] == o.valor:
            diferencas.inalteradas += 1
        else:
            diferencas.revisar.append(o)
    return diferencas


def hash_observacoes(observacoes: dict[date, Decimal | None]) -> str:
    """Hash estável das observações vigentes, para identificar o conteúdo de uma versão."""
    texto = "\n".join(
        f"{data.isoformat()};{'' if valor is None else format(valor, 'f')}"
        for data, valor in sorted(observacoes.items())
    )
    return hashlib.sha256(texto.encode()).hexdigest()
