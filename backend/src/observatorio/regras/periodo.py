"""Resolução do período de referência (FR-020) e avisos de mês não publicado."""

from dataclasses import dataclass
from datetime import date

from observatorio.regras.formatacao import mes_abreviado
from observatorio.regras.meses import interpretar_mes, somar_meses

ATALHOS_MESES = {"12m": 12, "3a": 36, "5a": 60, "10a": 120}
PERIODO_PADRAO = "5a"


@dataclass(frozen=True)
class ErroCampo:
    campo: str
    mensagem: str


class EntradaInvalida(Exception):  # noqa: N818 (nome de domínio)
    def __init__(self, erros: list[ErroCampo]):
        self.erros = erros
        super().__init__("; ".join(f"{e.campo}: {e.mensagem}" for e in erros))


@dataclass(frozen=True)
class PeriodoResolvido:
    inicio: date
    fim_solicitado: date
    fim_utilizado: date
    aviso_nao_publicado: str | None = None


def _ler_mes(campo: str, texto: str, erros: list[ErroCampo]) -> date | None:
    try:
        return interpretar_mes(texto)
    except ValueError:
        erros.append(ErroCampo(campo, "Use o formato AAAA-MM, por exemplo 2016-01."))
        return None


def resolver_periodo(
    *,
    periodo: str | None,
    inicio: str | None,
    fim: str | None,
    primeiro_mes: date,
    ultimo_mes: date,
    nome: str,
    instituicao: str,
) -> PeriodoResolvido:
    """Converte os parâmetros recebidos num período válido ou levanta EntradaInvalida.

    - Atalhos (12m, 3a, 5a, 10a) terminam no último mês publicado.
    - Sem nada informado, vale o atalho padrão de 5 anos.
    - Data final posterior ao último mês publicado não é erro: o período termina no último
      mês disponível e um aviso é devolvido (US2-7, US3-3).
    """
    erros: list[ErroCampo] = []
    usa_datas = inicio is not None or fim is not None

    if periodo is not None and usa_datas:
        erros.append(ErroCampo("periodo", "Informe um atalho de período ou datas, não os dois."))
        raise EntradaInvalida(erros)

    if not usa_datas:
        atalho = periodo or PERIODO_PADRAO
        if atalho not in ATALHOS_MESES:
            raise EntradaInvalida(
                [ErroCampo("periodo", "Período inválido. Use 12m, 3a, 5a ou 10a.")]
            )
        inicio_resolvido = max(somar_meses(ultimo_mes, -(ATALHOS_MESES[atalho] - 1)), primeiro_mes)
        return PeriodoResolvido(inicio_resolvido, ultimo_mes, ultimo_mes)

    if inicio is None:
        erros.append(ErroCampo("inicio", "Informe a data inicial."))
    if fim is None:
        erros.append(ErroCampo("fim", "Informe a data final."))
    mes_inicio = _ler_mes("inicio", inicio, erros) if inicio is not None else None
    mes_fim = _ler_mes("fim", fim, erros) if fim is not None else None
    if erros or mes_inicio is None or mes_fim is None:
        raise EntradaInvalida(erros)

    if mes_inicio > mes_fim:
        erros.append(ErroCampo("inicio", "A data inicial deve ser anterior ou igual à data final."))
    elif mes_inicio < primeiro_mes:
        erros.append(
            ErroCampo(
                "inicio", f"O {nome} está disponível a partir de {mes_abreviado(primeiro_mes)}."
            )
        )
    elif mes_inicio > ultimo_mes:
        erros.append(
            ErroCampo("inicio", f"Ainda não há {nome} publicado para {mes_abreviado(mes_inicio)}.")
        )
    if erros:
        raise EntradaInvalida(erros)

    if mes_fim > ultimo_mes:
        aviso = (
            f"O {nome} de {mes_abreviado(mes_fim)} ainda não foi publicado pelo {instituicao}. "
            f"O cálculo usa {mes_abreviado(ultimo_mes)}."
        )
        return PeriodoResolvido(mes_inicio, mes_fim, ultimo_mes, aviso)
    return PeriodoResolvido(mes_inicio, mes_fim, mes_fim)
