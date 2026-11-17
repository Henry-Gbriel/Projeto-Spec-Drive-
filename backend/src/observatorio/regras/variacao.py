"""Variação de séries de nível: câmbio, Selic, base monetária, agregados (FR-023)."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext

from observatorio.regras.ipca import CEM, PRECISAO, LacunaNaSerie, arredondar


@dataclass(frozen=True)
class ResumoNivel:
    valor_inicial: Decimal
    valor_final: Decimal
    variacao_percentual: Decimal
    minimo: Decimal
    maximo: Decimal


def resumir_nivel(observacoes: list[tuple[date, Decimal | None]]) -> ResumoNivel:
    """(x_b / x_a − 1) × 100, mínimo e máximo. Ausência em qualquer mês impede o cálculo."""
    if not observacoes:
        raise ValueError("série vazia")
    ausentes = [d for d, v in observacoes if v is None]
    if ausentes:
        raise LacunaNaSerie(ausentes)
    valores = [v for _, v in observacoes]
    inicial, final = valores[0], valores[-1]
    if inicial == 0:
        raise ValueError("valor inicial igual a zero: variação indefinida")
    with localcontext() as ctx:
        ctx.prec = PRECISAO
        variacao = (final / inicial - 1) * CEM  # type: ignore[operator]
    return ResumoNivel(inicial, final, arredondar(variacao, 2), min(valores), max(valores))  # type: ignore[arg-type,type-var]
