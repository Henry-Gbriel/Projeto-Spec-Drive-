"""Padronização: datas, unidades e frequência de exibição (FR-052).

Nada é estimado: meses sem valor permanecem ausentes. Valores não são corrigidos; apenas a
unidade é convertida quando o catálogo define `fator_unidade` (ex.: R$ mil -> R$ bilhões).
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext

from observatorio.catalogo import Indicador
from observatorio.coleta.base import ObservacaoFonte
from observatorio.regras.meses import primeiro_dia
from observatorio.tratamento.modelos import ObservacaoTratada

CASAS_ARMAZENAMENTO = Decimal("0.000001")  # numeric(20, 6)


@dataclass(frozen=True)
class ResultadoPadronizacao:
    observacoes: list[ObservacaoTratada]
    datas_futuras: list[date]


def _quantizar(valor: Decimal | None) -> Decimal | None:
    return None if valor is None else valor.quantize(CASAS_ARMAZENAMENTO)


def _data_exibicao(indicador: Indicador, data: date) -> date:
    if indicador.frequencia_exibicao == "anual":
        return date(data.year, 1, 1)
    return primeiro_dia(data)


def padronizar(
    indicador: Indicador, observacoes: list[ObservacaoFonte], hoje: date
) -> ResultadoPadronizacao:
    futuras = sorted({o.data for o in observacoes if o.data > hoje})
    validas = sorted((o for o in observacoes if o.data <= hoje), key=lambda o: o.data)

    fator = indicador.parametros_conector.get("fator_unidade")
    if fator is not None:
        with localcontext() as ctx:
            ctx.prec = 28
            validas = [
                ObservacaoFonte(o.data, None if o.valor is None else o.valor * Decimal(str(fator)))
                for o in validas
            ]

    if indicador.agregacao_mensal is None:
        tratadas = [
            ObservacaoTratada(_data_exibicao(indicador, o.data), _quantizar(o.valor))
            for o in validas
        ]
        return ResultadoPadronizacao(tratadas, futuras)

    # Agregação de dados diários em mensais: só meses completos (anteriores ao mês corrente).
    mes_corrente = primeiro_dia(hoje)
    por_mes: dict[date, list[ObservacaoFonte]] = defaultdict(list)
    for o in validas:
        mes = primeiro_dia(o.data)
        if mes < mes_corrente:
            por_mes[mes].append(o)

    tratadas = []
    for mes in sorted(por_mes):
        numeros = [o.valor for o in por_mes[mes] if o.valor is not None]
        if not numeros:
            valor = None
        elif indicador.agregacao_mensal == "media":
            with localcontext() as ctx:
                ctx.prec = 28
                valor = sum(numeros, Decimal(0)) / len(numeros)
        else:  # fim_de_mes e vigente_fim_de_mes: último valor do mês
            valor = numeros[-1]
        tratadas.append(ObservacaoTratada(mes, _quantizar(valor)))
    return ResultadoPadronizacao(tratadas, futuras)
