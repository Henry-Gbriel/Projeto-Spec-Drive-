"""Regras de validação (data-model.md, "Regras de validação").

Bloqueantes impedem a publicação da nova versão; avisos ficam registrados.
"""

from collections import Counter
from datetime import date
from decimal import Decimal

from observatorio.catalogo import Indicador
from observatorio.coleta.base import ObservacaoFonte
from observatorio.regras.meses import meses_entre
from observatorio.tratamento.modelos import ObservacaoTratada, Ocorrencia

LIMITE_REVISAO_GRANDE = Decimal("0.01")  # 1 %


def validar_fonte(observacoes: list[ObservacaoFonte], carga_completa: bool) -> list[Ocorrencia]:
    """Regras sobre o que veio da fonte, antes da padronização."""
    ocorrencias = []
    if carga_completa and not observacoes:
        ocorrencias.append(Ocorrencia("serie_vazia", "bloqueante"))
    contagem = Counter(o.data for o in observacoes)
    for data, vezes in sorted(contagem.items()):
        if vezes > 1:
            ocorrencias.append(
                Ocorrencia("data_duplicada_na_fonte", "bloqueante", data, {"vezes": vezes})
            )
    for o in observacoes:
        if o.valor is None:
            ocorrencias.append(
                Ocorrencia("valor_nao_numerico", "aviso", o.data, {"texto": o.texto_fonte})
            )
    return ocorrencias


def validar_datas_futuras(datas: list[date]) -> list[Ocorrencia]:
    return [Ocorrencia("data_futura", "aviso", d, {"acao": "descartada"}) for d in datas]


def validar_serie(
    indicador: Indicador,
    novas: list[ObservacaoTratada],
    vigentes: dict[date, Decimal | None],
    intervalo: tuple[date, date],
) -> list[Ocorrencia]:
    """Regras sobre a série padronizada, comparando com os valores vigentes.

    `vigentes` traz as observações vigentes da série; `intervalo` é o recorte pedido à fonte,
    dentro do qual um valor publicado não pode desaparecer (queda_de_cobertura).
    """
    ocorrencias: list[Ocorrencia] = []
    por_data = {o.data: o.valor for o in novas}

    for o in novas:
        if o.valor is None:
            continue
        abaixo = indicador.limite_inferior is not None and o.valor < indicador.limite_inferior
        acima = indicador.limite_superior is not None and o.valor > indicador.limite_superior
        if abaixo or acima:
            ocorrencias.append(
                Ocorrencia("fora_do_intervalo", "bloqueante", o.data, {"valor": str(o.valor)})
            )

    inicio, fim = intervalo
    for data, valor_antigo in sorted(vigentes.items()):
        if valor_antigo is None:
            continue
        if data not in por_data or por_data[data] is None:
            if inicio <= data <= fim:
                # A fonte deixou de trazer um valor já publicado: exige revisão humana.
                ocorrencias.append(
                    Ocorrencia(
                        "queda_de_cobertura", "bloqueante", data, {"valor": str(valor_antigo)}
                    )
                )
            continue
        novo = por_data[data]
        base = abs(valor_antigo) if valor_antigo != 0 else Decimal(1)
        if abs(novo - valor_antigo) / base > LIMITE_REVISAO_GRANDE:  # type: ignore[operator]
            ocorrencias.append(
                Ocorrencia(
                    "revisao_grande",
                    "aviso",
                    data,
                    {"anterior": str(valor_antigo), "novo": str(novo)},
                )
            )

    ocorrencias.extend(_lacunas(indicador, novas, vigentes))
    return ocorrencias


def _lacunas(
    indicador: Indicador, novas: list[ObservacaoTratada], vigentes: dict[date, Decimal | None]
) -> list[Ocorrencia]:
    if indicador.frequencia_exibicao != "mensal":
        return []
    combinadas = {**vigentes, **{o.data: o.valor for o in novas}}
    com_valor = sorted(d for d, v in combinadas.items() if v is not None)
    if len(com_valor) < 2:
        return []
    return [
        Ocorrencia("lacuna", "aviso", mes)
        for mes in meses_entre(com_valor[0], com_valor[-1])
        if combinadas.get(mes) is None
    ]


def validar_conferencia(
    novas: list[ObservacaoTratada], conferencia: list[ObservacaoTratada], fonte: str
) -> list[Ocorrencia]:
    """Compara com uma segunda fonte (ex.: IPCA do SIDRA x SGS 433). Divergência é aviso."""
    referencia = {o.data: o.valor for o in conferencia}
    ocorrencias = []
    for o in novas:
        outro = referencia.get(o.data)
        if o.valor is not None and outro is not None and o.valor != outro:
            ocorrencias.append(
                Ocorrencia(
                    "divergencia_fontes",
                    "aviso",
                    o.data,
                    {"fonte": fonte, "valor": str(o.valor), "conferencia": str(outro)},
                )
            )
    return ocorrencias
