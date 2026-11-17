"""Regras do IPCA: fator acumulado e simulador de poder de compra (FR-022, FR-026).

Funções puras com Decimal. O arredondamento acontece apenas nos valores de saída.
Convenção (research R-13): o acumulado de a até b inclui os meses a e b.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, localcontext

from observatorio.regras.meses import meses_entre, somar_meses

CEM = Decimal(100)
CENTAVO = Decimal("0.01")
PRECISAO = 28

Variacoes = Mapping[date, Decimal | None]


class LacunaNaSerie(Exception):  # noqa: N818 (nome de domínio)
    """Falta o dado de um ou mais meses: o cálculo não é feito (FR-012)."""

    def __init__(self, meses_ausentes: list[date]):
        self.meses_ausentes = meses_ausentes
        super().__init__(f"meses ausentes: {[m.isoformat() for m in meses_ausentes]}")


@dataclass(frozen=True)
class ResultadoSimulacao:
    valor_informado: Decimal
    inicio: date
    fim: date
    meses_considerados: int
    fator: Decimal
    valor_corrigido: Decimal
    inflacao_acumulada_percentual: Decimal
    variacao_poder_compra_percentual: Decimal
    equivalente_no_inicio: Decimal
    diferenca_nominal: Decimal


def arredondar(valor: Decimal, casas: int) -> Decimal:
    return valor.quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)


def fator_acumulado(variacoes: Variacoes, inicio: date, fim: date) -> tuple[Decimal, int]:
    """F = ∏ (1 + v_m / 100) para m de inicio a fim, inclusive. Retorna (F, número de meses)."""
    meses = meses_entre(inicio, fim)
    if not meses:
        raise ValueError("a data inicial deve ser anterior ou igual à data final")
    ausentes = [m for m in meses if variacoes.get(m) is None]
    if ausentes:
        raise LacunaNaSerie(ausentes)
    with localcontext() as ctx:
        ctx.prec = PRECISAO
        fator = Decimal(1)
        for mes in meses:
            fator *= 1 + variacoes[mes] / CEM  # type: ignore[operator]
    return fator, len(meses)


def acumulado_percentual(fator: Decimal) -> Decimal:
    """(F − 1) × 100, sem arredondar."""
    with localcontext() as ctx:
        ctx.prec = PRECISAO
        return (fator - 1) * CEM


def fator_por_indice(indices: Mapping[date, Decimal | None], inicio: date, fim: date) -> Decimal:
    """Conferência pelo número-índice: I_fim / I_(inicio − 1 mês)."""
    anterior = somar_meses(inicio, -1)
    ausentes = [m for m in (anterior, fim) if indices.get(m) is None]
    if ausentes:
        raise LacunaNaSerie(ausentes)
    with localcontext() as ctx:
        ctx.prec = PRECISAO
        return indices[fim] / indices[anterior]  # type: ignore[operator]


def simular_poder_de_compra(
    valor: Decimal, variacoes: Variacoes, inicio: date, fim: date
) -> ResultadoSimulacao:
    if valor <= 0:
        raise ValueError("o valor deve ser maior que zero")
    fator, meses = fator_acumulado(variacoes, inicio, fim)
    with localcontext() as ctx:
        ctx.prec = PRECISAO
        valor_corrigido = valor * fator
        variacao_poder = (1 / fator - 1) * CEM
        equivalente = valor / fator
    corrigido = arredondar(valor_corrigido, 2)
    return ResultadoSimulacao(
        valor_informado=arredondar(valor, 2),
        inicio=inicio,
        fim=fim,
        meses_considerados=meses,
        fator=fator,
        valor_corrigido=corrigido,
        inflacao_acumulada_percentual=arredondar(acumulado_percentual(fator), 2),
        variacao_poder_compra_percentual=arredondar(variacao_poder, 2),
        equivalente_no_inicio=arredondar(equivalente, 2),
        diferenca_nominal=corrigido - arredondar(valor, 2),
    )
