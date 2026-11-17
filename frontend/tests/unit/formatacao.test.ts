import { describe, expect, it } from 'vitest'
import { dataCurta, dataHora, mesAbreviado, mesPorExtenso } from '../../src/formatacao/datas'
import {
  arredondarTexto,
  formatarMoeda,
  formatarNumero,
  formatarPercentual,
  sinal,
} from '../../src/formatacao/numeros'
import { converterValorEmReais } from '../../src/formatacao/valorEmReais'

describe('números no padrão brasileiro', () => {
  it('usa vírgula decimal e ponto de milhar', () => {
    expect(formatarNumero('1234567.891', 2)).toBe('1.234.567,89')
    expect(formatarMoeda('8977072379.59')).toBe('R$ 8.977.072.379,59')
    expect(formatarNumero('7695.82', 2)).toBe('7.695,82')
  })

  it('não usa notação científica nem perde precisão em valores grandes', () => {
    expect(formatarMoeda('9999999999999.99')).toBe('R$ 9.999.999.999.999,99')
  })

  it('arredonda meio para cima', () => {
    expect(arredondarTexto('1.6331049', 4)).toBe('1.6331')
    expect(arredondarTexto('0.125', 2)).toBe('0.13')
    expect(arredondarTexto('-0.125', 2)).toBe('-0.13')
    expect(arredondarTexto('-0.001', 2)).toBe('0.00')
  })

  it('formata percentuais com sinal opcional', () => {
    expect(formatarPercentual('63.31')).toBe('63,31%')
    expect(formatarPercentual('63.31', 2, true)).toBe('+63,31%')
    expect(formatarPercentual('-38.77', 2, true)).toBe('−38,77%')
    expect(formatarPercentual('0', 2, true)).toBe('0,00%')
  })

  it('identifica o sinal', () => {
    expect(sinal('0.82')).toBe(1)
    expect(sinal('-0.32')).toBe(-1)
    expect(sinal('0.00')).toBe(0)
  })
})

describe('datas em português', () => {
  it('formata meses', () => {
    expect(mesAbreviado('2016-01-01')).toBe('jan/2016')
    expect(mesAbreviado('2026-09')).toBe('set/2026')
    expect(mesPorExtenso('2025-03-01')).toBe('março de 2025')
  })

  it('usa o horário de Brasília', () => {
    expect(dataHora('2026-10-22T09:17:00Z')).toBe('22/10/2026 às 06:17')
    expect(dataCurta('2026-10-22T02:00:00Z')).toBe('21/10/2026')
  })
})

describe('valor digitado no simulador', () => {
  it.each([
    ['1.500,00', '1500.00'],
    ['1500,00', '1500.00'],
    ['1500', '1500.00'],
    ['100,5', '100.50'],
    ['R$ 2.000', '2000.00'],
    ['0,01', '0.01'],
  ])('converte %s', (digitado, esperado) => {
    expect(converterValorEmReais(digitado)).toEqual({ valor: esperado })
  })

  it.each([
    ['', 'Informe um valor em reais.'],
    ['abc', 'Use apenas números'],
    ['-5', 'Use apenas números'],
    ['1.50', 'Use apenas números'],
    ['10,505', 'no máximo dois dígitos'],
    ['0,00', 'maior que zero'],
    ['99999999999999', 'acima do limite'],
  ])('rejeita %s', (digitado, mensagem) => {
    const resultado = converterValorEmReais(digitado)
    expect('erro' in resultado && resultado.erro).toContain(mensagem)
  })
})
