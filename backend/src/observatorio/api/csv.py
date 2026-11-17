"""Geração dos arquivos CSV (contracts/csv.md, FR-030, FR-031)."""

import csv
import io
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from observatorio.config import FUSO_HORARIO

BOM = "﻿"
OBSERVACAO = (
    "Células de valor vazias indicam observação ausente na fonte; "
    "o Observatório não estima valores."
)


def valor_br(valor: Decimal | None) -> str:
    """Vírgula decimal, sem separador de milhar; vazio para ausente."""
    if valor is None:
        return ""
    texto = format(valor.normalize(), "f")
    return texto.replace(".", ",")


def nome_arquivo(codigo: str, inicio: date | None, fim: date | None) -> str:
    if inicio is None or fim is None:
        return f"{codigo}_completo.csv"
    return f"{codigo}_{inicio:%Y-%m}_{fim:%Y-%m}.csv"


def gerar_csv(
    indicador: dict[str, Any],
    serie: list[tuple[date, Decimal | None]],
    gerado_em: datetime | None = None,
) -> str:
    gerado_em = gerado_em or datetime.now(FUSO_HORARIO)
    atualizado = indicador["ultima_atualizacao_valida"]
    periodo = f"{serie[0][0]:%Y-%m} a {serie[-1][0]:%Y-%m}" if serie else ""
    metadados = [
        ("indicador", indicador["nome"]),
        ("descricao", indicador["descricao"]),
        ("fonte", indicador["instituicao"]),
        ("codigo_serie", indicador["codigo_serie"] or ""),
        ("url_origem", indicador["url_origem"]),
        ("unidade", indicador["unidade"]),
        ("frequencia", indicador["frequencia"]),
        ("natureza", indicador["natureza"]),
        ("periodo_referencia", periodo),
        ("atualizado_em", atualizado.astimezone(FUSO_HORARIO).isoformat() if atualizado else ""),
        ("gerado_em", gerado_em.astimezone(FUSO_HORARIO).isoformat(timespec="seconds")),
        ("observacao", OBSERVACAO),
    ]
    saida = io.StringIO()
    for chave, valor in metadados:
        saida.write(f"# {chave}: {' '.join(str(valor).split())}\r\n")
    escritor = csv.writer(saida, delimiter=";", lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    escritor.writerow(["data", "valor", "unidade", "situacao"])
    for data, valor in serie:
        escritor.writerow(
            [
                data.isoformat(),
                valor_br(valor),
                indicador["unidade"],
                "ausente" if valor is None else "ok",
            ]
        )
    return BOM + saida.getvalue()
