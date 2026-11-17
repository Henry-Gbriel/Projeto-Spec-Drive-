"""Formato dos arquivos CSV (contracts/csv.md, SC-010)."""

from datetime import date, datetime
from decimal import Decimal

from observatorio.api.csv import BOM, gerar_csv, nome_arquivo, valor_br
from observatorio.config import FUSO_HORARIO

INDICADOR = {
    "nome": "IPCA — variação mensal",
    "descricao": "Índice oficial de inflação.",
    "instituicao": "IBGE",
    "codigo_serie": "SIDRA tabela 1737, variável 63",
    "url_origem": "https://sidra.ibge.gov.br/tabela/1737",
    "unidade": "% ao mês",
    "frequencia": "mensal",
    "natureza": "real",
    "ultima_atualizacao_valida": datetime(2026, 10, 22, 6, 17, tzinfo=FUSO_HORARIO),
}
SERIE = [
    (date(2025, 1, 1), Decimal("0.160000")),
    (date(2025, 2, 1), Decimal("1.310000")),
    (date(2025, 3, 1), None),
    (date(2025, 4, 1), Decimal("1234.5")),
]
GERADO = datetime(2026, 10, 22, 12, 0, tzinfo=FUSO_HORARIO)


def gerar() -> str:
    return gerar_csv(INDICADOR, SERIE, GERADO)


def test_bom_e_quebras_de_linha():
    texto = gerar()
    assert texto.startswith(BOM)
    assert "\r\n" in texto and "\n" not in texto.replace("\r\n", "")


def test_metadados_na_ordem_do_contrato():
    linhas = gerar().lstrip(BOM).split("\r\n")
    chaves = [linha[2:].split(":")[0] for linha in linhas if linha.startswith("# ")]
    assert chaves == [
        "indicador", "descricao", "fonte", "codigo_serie", "url_origem", "unidade",
        "frequencia", "natureza", "periodo_referencia", "atualizado_em", "gerado_em",
        "observacao",
    ]  # fmt: skip
    assert "# periodo_referencia: 2025-01 a 2025-04" in linhas
    assert "# atualizado_em: 2026-10-22T06:17:00-03:00" in linhas


def test_cabecalho_linhas_e_ausentes():
    linhas = [
        linha for linha in gerar().lstrip(BOM).split("\r\n") if linha and not linha.startswith("#")
    ]
    assert linhas == [
        "data;valor;unidade;situacao",
        "2025-01-01;0,16;% ao mês;ok",
        "2025-02-01;1,31;% ao mês;ok",
        "2025-03-01;;% ao mês;ausente",
        "2025-04-01;1234,5;% ao mês;ok",
    ]


def test_valor_sem_separador_de_milhar_nem_notacao_cientifica():
    assert valor_br(Decimal("514321.987000")) == "514321,987"
    assert valor_br(Decimal("1E+3")) == "1000"
    assert valor_br(None) == ""


def test_nome_do_arquivo():
    assert nome_arquivo("ipca", date(2021, 1, 1), date(2025, 12, 1)) == "ipca_2021-01_2025-12.csv"
    assert nome_arquivo("ipca", None, None) == "ipca_completo.csv"
