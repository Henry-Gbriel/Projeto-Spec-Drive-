"""Utilitários compartilhados pelos testes."""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

PASTA_FIXTURES = Path(__file__).parent / "fixtures"


def ler_fixture(nome: str) -> bytes:
    return (PASTA_FIXTURES / nome).read_bytes()


def serie_sidra(nome: str) -> dict[date, Decimal]:
    """Lê uma fixture do SIDRA como {mês: valor} (sem passar pelo conector)."""
    linhas = json.loads(ler_fixture(nome))[1:]
    return {
        date(int(item["D3C"][:4]), int(item["D3C"][4:]), 1): Decimal(item["V"]) for item in linhas
    }


class ConectorFixture:
    """Conector falso do SIDRA que devolve fixtures em sequência (ou levanta um erro)."""

    def __init__(self, *respostas):
        from observatorio.coleta.base import RespostaBruta, ResultadoColeta

        self._fila = list(respostas)
        self._resposta = RespostaBruta
        self._resultado = ResultadoColeta
        self.chamadas: list[tuple[date, date]] = []

    def coletar(self, parametros, data_inicial, data_final):
        self.chamadas.append((data_inicial, data_final))
        proxima = self._fila.pop(0) if len(self._fila) > 1 else self._fila[0]
        if isinstance(proxima, Exception):
            raise proxima
        return self._resultado(
            [self._resposta("https://fixture.local", 200, ler_fixture(proxima))],
            {"data_inicial": data_inicial.isoformat(), "data_final": data_final.isoformat()},
        )

    def interpretar(self, resultado):
        from observatorio.coleta.sidra import interpretar_corpo

        return [o for r in resultado.respostas for o in interpretar_corpo(r.conteudo)]


class ConectorPorVariavel(ConectorFixture):
    """Conector falso do SIDRA que escolhe a fixture pela variável pedida (63, 2266...)."""

    def __init__(self, fixtures: dict[int, str]):
        super().__init__("sidra_recorte_2025_2026.json")
        self._fixtures = fixtures

    def coletar(self, parametros, data_inicial, data_final):
        self._fila = [self._fixtures[parametros["variavel"]]]
        return super().coletar(parametros, data_inicial, data_final)
