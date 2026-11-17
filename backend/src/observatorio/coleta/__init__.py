"""Conectores das fontes oficiais."""

from observatorio.coleta.base import Conector
from observatorio.coleta.sgs import ConectorSgs
from observatorio.coleta.sidra import ConectorSidra


def conectores_padrao() -> dict[str, Conector]:
    return {"sidra": ConectorSidra(), "sgs": ConectorSgs()}
