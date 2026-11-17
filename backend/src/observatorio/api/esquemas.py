"""Modelos de resposta (espelham contracts/api-openapi.yaml).

Valores decimais são enviados como texto para preservar a precisão; a interface formata.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel


def decimal_texto(valor: Decimal | None, casas: int | None = None) -> str | None:
    """Decimal -> texto sem notação científica, com no mínimo `casas` casas decimais."""
    if valor is None:
        return None
    normalizado = valor.normalize()
    if casas is not None and -normalizado.as_tuple().exponent < casas:  # type: ignore[operator]
        normalizado = valor.quantize(Decimal(1).scaleb(-casas))
    texto = format(normalizado, "f")
    return "0" if texto in ("-0", "") else texto


class Fonte(BaseModel):
    instituicao: str
    codigo_serie: str | None
    url_origem: str


class PeriodoDisponivel(BaseModel):
    inicio: date
    fim: date


class Atualizacao(BaseModel):
    situacao: Literal["atualizado", "aguardando_integracao", "em_definicao", "falha_atualizacao"]
    ultima_atualizacao_valida: datetime | None
    ultima_tentativa: datetime | None = None
    mensagem: str | None = None


class Indicador(BaseModel):
    codigo: str
    nome: str
    descricao: str
    fonte: Fonte
    unidade: str
    frequencia: Literal["diaria", "mensal", "anual", "por_reuniao"]
    casas_decimais: int
    natureza: Literal["real", "ilustrativo"]
    periodo_disponivel: PeriodoDisponivel | None
    atualizacao: Atualizacao

    @classmethod
    def da_linha(cls, linha: dict[str, Any]) -> "Indicador":
        periodo = (
            PeriodoDisponivel(inicio=linha["periodo_inicio"], fim=linha["periodo_fim"])
            if linha["periodo_inicio"] and linha["periodo_fim"]
            else None
        )
        return cls(
            codigo=linha["codigo"],
            nome=linha["nome"],
            descricao=linha["descricao"],
            fonte=Fonte(
                instituicao=linha["instituicao"],
                codigo_serie=linha["codigo_serie"],
                url_origem=linha["url_origem"],
            ),
            unidade=linha["unidade"],
            frequencia=linha["frequencia"],
            casas_decimais=linha["casas_decimais"],
            natureza=linha["natureza"],
            periodo_disponivel=periodo,
            atualizacao=Atualizacao(
                situacao=linha["situacao"],
                ultima_atualizacao_valida=linha["ultima_atualizacao_valida"],
                ultima_tentativa=linha["ultima_tentativa"],
                mensagem=linha["mensagem_publica"],
            ),
        )


class Catalogo(BaseModel):
    indicadores: list[Indicador]


class PeriodoReferencia(BaseModel):
    inicio: date
    fim_solicitado: date
    fim_utilizado: date
    aviso_nao_publicado: str | None = None


class Observacao(BaseModel):
    data: date
    valor: str | None
    situacao: Literal["ok", "ausente"]


class Serie(BaseModel):
    indicador: Indicador
    periodo: PeriodoReferencia
    observacoes: list[Observacao]
    derivadas: dict[str, list[str | None]] | None = None


class Resumo(BaseModel):
    indicador: Indicador
    periodo: PeriodoReferencia
    situacao: Literal["ok", "sem_dados", "lacuna"]
    meses_ausentes: list[date] = []
    acumulado_percentual: str | None = None
    fator: str | None = None
    meses_considerados: int | None = None
    valor_inicial: str | None = None
    valor_final: str | None = None
    variacao_percentual: str | None = None
    minimo: str | None = None
    maximo: str | None = None


class Simulacao(BaseModel):
    valor_informado: str
    periodo: PeriodoReferencia
    meses_considerados: int
    fator: str
    valor_corrigido: str
    inflacao_acumulada_percentual: str
    variacao_poder_compra_percentual: str
    equivalente_no_inicio: str
    diferenca_nominal: str
    passos: list[Observacao]
    indicador: Indicador


class Saude(BaseModel):
    status: Literal["ok"]
    banco: Literal["ok", "indisponivel"]
