"""Catálogo de indicadores: leitura de dados/catalogo.yaml e sincronização com o banco."""

from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

import psycopg
import yaml
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field, field_validator

from observatorio.config import CAMINHO_CATALOGO


class Indicador(BaseModel):
    """Metadados de um indicador; as regras espelham os CHECKs de tratado.indicador."""

    codigo: str = Field(pattern=r"^[a-z0-9_]+$")
    nome: str = Field(min_length=1)
    descricao: str = Field(min_length=1)
    instituicao: str = Field(min_length=1)
    codigo_serie: str | None = None
    url_origem: str = Field(min_length=1)
    conector: Literal["sidra", "sgs", "olinda", "manual"]
    parametros_conector: dict[str, Any] = Field(default_factory=dict)
    unidade: str = Field(min_length=1)
    frequencia_fonte: Literal["diaria", "mensal", "anual", "por_reuniao"]
    frequencia_exibicao: Literal["mensal", "anual"]
    agregacao_mensal: Literal["media", "fim_de_mes", "vigente_fim_de_mes"] | None = None
    casas_decimais: int = Field(ge=0, le=6)
    natureza: Literal["real", "ilustrativo"]
    janela_revisao_meses: int = Field(default=3, ge=0)
    situacao_catalogo: Literal["ativo", "aguardando_integracao", "em_definicao"]
    entrega: int = Field(ge=1, le=4)
    limite_inferior: Decimal | None = None
    limite_superior: Decimal | None = None
    ordem: int = 0

    @field_validator("nome", "descricao", "instituicao", "unidade", "url_origem")
    @classmethod
    def _sem_espacos_vazios(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("campo obrigatório")
        return valor.strip()

    @property
    def ativo(self) -> bool:
        return self.situacao_catalogo == "ativo"


def carregar_catalogo(caminho: Path = CAMINHO_CATALOGO) -> list[Indicador]:
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    indicadores = [Indicador.model_validate(item) for item in dados["indicadores"]]
    codigos = [i.codigo for i in indicadores]
    repetidos = {c for c in codigos if codigos.count(c) > 1}
    if repetidos:
        raise ValueError(f"códigos repetidos no catálogo: {sorted(repetidos)}")
    return indicadores


def sincronizar_catalogo(conn: psycopg.Connection, indicadores: list[Indicador]) -> None:
    """Atualiza tratado.indicador e os metadados de publico.indicador_publicado.

    Não mexe em versões nem em observações. Indicadores fora do catálogo deixam de ser
    publicados (publicado = false).
    """
    with conn.transaction():
        for ind in indicadores:
            conn.execute(
                """
                INSERT INTO tratado.indicador (
                  codigo, nome, descricao, instituicao, codigo_serie, url_origem, conector,
                  parametros_conector, unidade, frequencia_fonte, frequencia_exibicao,
                  agregacao_mensal, casas_decimais, natureza, janela_revisao_meses,
                  situacao_catalogo, entrega, limite_inferior, limite_superior, ordem)
                VALUES (%(codigo)s, %(nome)s, %(descricao)s, %(instituicao)s, %(codigo_serie)s,
                  %(url_origem)s, %(conector)s, %(parametros)s, %(unidade)s,
                  %(frequencia_fonte)s, %(frequencia_exibicao)s, %(agregacao_mensal)s,
                  %(casas_decimais)s, %(natureza)s, %(janela_revisao_meses)s,
                  %(situacao_catalogo)s, %(entrega)s, %(limite_inferior)s,
                  %(limite_superior)s, %(ordem)s)
                ON CONFLICT (codigo) DO UPDATE SET
                  nome = EXCLUDED.nome, descricao = EXCLUDED.descricao,
                  instituicao = EXCLUDED.instituicao, codigo_serie = EXCLUDED.codigo_serie,
                  url_origem = EXCLUDED.url_origem, conector = EXCLUDED.conector,
                  parametros_conector = EXCLUDED.parametros_conector,
                  unidade = EXCLUDED.unidade, frequencia_fonte = EXCLUDED.frequencia_fonte,
                  frequencia_exibicao = EXCLUDED.frequencia_exibicao,
                  agregacao_mensal = EXCLUDED.agregacao_mensal,
                  casas_decimais = EXCLUDED.casas_decimais, natureza = EXCLUDED.natureza,
                  janela_revisao_meses = EXCLUDED.janela_revisao_meses,
                  situacao_catalogo = EXCLUDED.situacao_catalogo, entrega = EXCLUDED.entrega,
                  limite_inferior = EXCLUDED.limite_inferior,
                  limite_superior = EXCLUDED.limite_superior, ordem = EXCLUDED.ordem
                """,
                {**ind.model_dump(), "parametros": Jsonb(ind.parametros_conector)},
            )
            # Situação pública: indicadores não ativos mostram o selo do catálogo; ativos
            # ainda sem versão publicada aparecem como "aguardando integração".
            situacao_inicial = "aguardando_integracao" if ind.ativo else ind.situacao_catalogo
            conn.execute(
                """
                INSERT INTO publico.indicador_publicado (
                  codigo, nome, descricao, instituicao, codigo_serie, url_origem, unidade,
                  frequencia, casas_decimais, natureza, situacao, entrega, ordem, publicado)
                VALUES (%(codigo)s, %(nome)s, %(descricao)s, %(instituicao)s, %(codigo_serie)s,
                  %(url_origem)s, %(unidade)s, %(frequencia_exibicao)s, %(casas_decimais)s,
                  %(natureza)s, %(situacao)s, %(entrega)s, %(ordem)s, true)
                ON CONFLICT (codigo) DO UPDATE SET
                  nome = EXCLUDED.nome, descricao = EXCLUDED.descricao,
                  instituicao = EXCLUDED.instituicao, codigo_serie = EXCLUDED.codigo_serie,
                  url_origem = EXCLUDED.url_origem, unidade = EXCLUDED.unidade,
                  frequencia = EXCLUDED.frequencia, casas_decimais = EXCLUDED.casas_decimais,
                  natureza = EXCLUDED.natureza, entrega = EXCLUDED.entrega,
                  ordem = EXCLUDED.ordem, publicado = true,
                  situacao = CASE
                    WHEN %(ativo)s THEN publico.indicador_publicado.situacao
                    ELSE EXCLUDED.situacao END
                """,
                {**ind.model_dump(), "situacao": situacao_inicial, "ativo": ind.ativo},
            )
        conn.execute(
            "UPDATE publico.indicador_publicado SET publicado = false WHERE NOT codigo = ANY(%s)",
            ([i.codigo for i in indicadores],),
        )
