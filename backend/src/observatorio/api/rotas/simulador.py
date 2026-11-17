"""Simulador de poder de compra pelo IPCA (US3, FR-025 a FR-028)."""

import re
from datetime import date
from decimal import Decimal

import psycopg
from fastapi import APIRouter, Depends, Request, Response

from observatorio.api import erros, servico
from observatorio.api.dependencias import obter_conexao
from observatorio.api.esquemas import Simulacao, decimal_texto
from observatorio.regras.ipca import simular_poder_de_compra
from observatorio.regras.periodo import EntradaInvalida, ErroCampo

roteador = APIRouter()

INICIO_PLANO_REAL = date(1994, 7, 1)
VALOR_MAXIMO = Decimal("9999999999999.99")
PADRAO_NUMERO = re.compile(r"^\d+(\.\d+)?$")


def validar_valor(texto: str | None) -> tuple[Decimal | None, list[ErroCampo]]:
    """Mesmas regras e mensagens da interface (contracts/ui-estados.md)."""
    if texto is None or not texto.strip():
        return None, [ErroCampo("valor", "Informe um valor em reais.")]
    texto = texto.strip()
    if not PADRAO_NUMERO.match(texto):
        return None, [
            ErroCampo(
                "valor",
                "Use apenas números, com vírgula para os centavos. Exemplo: 1.500,00",
            )
        ]
    if "." in texto and len(texto.split(".")[1]) > 2:
        return None, [ErroCampo("valor", "Use no máximo dois dígitos de centavos.")]
    valor = Decimal(texto)
    if valor <= 0:
        return None, [ErroCampo("valor", "O valor deve ser maior que zero.")]
    if valor > VALOR_MAXIMO:
        return None, [ErroCampo("valor", "Valor acima do limite do simulador.")]
    return valor, []


@roteador.get(
    "/v1/simulador/poder-de-compra",
    response_model=Simulacao,
    operation_id="simularPoderDeCompra",
)
def simular(
    request: Request,
    valor: str | None = None,
    inicio: str | None = None,
    fim: str | None = None,
    conn: psycopg.Connection = Depends(obter_conexao),
) -> Response:
    linha = servico.indicador_com_dados(conn, "ipca")
    valor_decimal, erros_valor = validar_valor(valor)
    primeiro_mes = max(INICIO_PLANO_REAL, linha["periodo_inicio"])

    erros_periodo: list[ErroCampo] = []
    resolvido = None
    if inicio is None and fim is None:
        erros_periodo = [
            ErroCampo("inicio", "Informe a data inicial."),
            ErroCampo("fim", "Informe a data final."),
        ]
    else:
        try:
            resolvido = servico.resolver(linha, None, inicio, fim, primeiro_mes=primeiro_mes)
        except EntradaInvalida as erro:
            erros_periodo = erro.erros
    if erros_valor or erros_periodo:
        raise erros.entrada_invalida(erros_valor + erros_periodo)
    assert resolvido is not None and valor_decimal is not None

    serie = servico.observacoes_do_periodo(conn, "ipca", resolvido.inicio, resolvido.fim_utilizado)
    resultado = simular_poder_de_compra(
        valor_decimal, dict(serie), resolvido.inicio, resolvido.fim_utilizado
    )
    modelo = Simulacao(
        valor_informado=decimal_texto(resultado.valor_informado, 2),
        periodo=servico.periodo_referencia(resolvido),
        meses_considerados=resultado.meses_considerados,
        fator=decimal_texto(resultado.fator),
        valor_corrigido=decimal_texto(resultado.valor_corrigido, 2),
        inflacao_acumulada_percentual=decimal_texto(resultado.inflacao_acumulada_percentual, 2),
        variacao_poder_compra_percentual=decimal_texto(
            resultado.variacao_poder_compra_percentual, 2
        ),
        equivalente_no_inicio=decimal_texto(resultado.equivalente_no_inicio, 2),
        diferenca_nominal=decimal_texto(resultado.diferenca_nominal, 2),
        passos=servico.para_observacoes(serie, linha["casas_decimais"]),
        indicador=servico.modelo_indicador(linha),
    )
    return servico.responder(request, modelo, linha["versao_id"], linha["situacao"])
