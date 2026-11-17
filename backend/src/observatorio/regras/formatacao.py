"""Formatação de datas em português para mensagens da API."""

from datetime import date

MESES_ABREVIADOS = (
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
)


def mes_abreviado(data: date) -> str:
    """Ex.: date(2016, 1, 1) -> 'jan/2016'."""
    return f"{MESES_ABREVIADOS[data.month - 1]}/{data.year}"


def data_br(data: date) -> str:
    """Ex.: date(2026, 10, 22) -> '22/10/2026'."""
    return data.strftime("%d/%m/%Y")
