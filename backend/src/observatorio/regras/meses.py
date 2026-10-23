"""Aritmética de meses. Séries mensais usam sempre o dia 1 como data de referência."""

import re
from datetime import date

PADRAO_MES = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


def primeiro_dia(data: date) -> date:
    return data.replace(day=1)


def somar_meses(mes: date, quantidade: int) -> date:
    indice = mes.year * 12 + (mes.month - 1) + quantidade
    return date(indice // 12, indice % 12 + 1, 1)


def meses_entre(inicio: date, fim: date) -> list[date]:
    """Meses de inicio a fim, inclusive. Vazio se inicio > fim."""
    resultado = []
    atual = primeiro_dia(inicio)
    while atual <= fim:
        resultado.append(atual)
        atual = somar_meses(atual, 1)
    return resultado


def interpretar_mes(texto: str) -> date:
    """'2016-01' -> date(2016, 1, 1). Levanta ValueError se o formato for inválido."""
    encontrado = PADRAO_MES.match(texto or "")
    if not encontrado:
        raise ValueError(f"mês inválido: {texto!r}; use AAAA-MM")
    return date(int(encontrado.group(1)), int(encontrado.group(2)), 1)
