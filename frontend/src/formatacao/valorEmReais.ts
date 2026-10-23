/**
 * Conversão do valor digitado no simulador ("1.500,00") para o formato da API ("1500.00").
 * Mensagens idênticas às da API (contracts/ui-estados.md); o servidor continua sendo a
 * autoridade.
 */

export type ResultadoConversao = { valor: string } | { erro: string }

const LIMITE = 9_999_999_999_999.99
const COM_MILHAR = /^\d{1,3}(\.\d{3})+(,\d+)?$/
const SEM_MILHAR = /^\d+(,\d+)?$/

export function converterValorEmReais(digitado: string): ResultadoConversao {
  const texto = digitado.trim().replace(/^R\$\s*/, '')
  if (!texto) return { erro: 'Informe um valor em reais.' }
  if (!COM_MILHAR.test(texto) && !SEM_MILHAR.test(texto)) {
    return { erro: 'Use apenas números, com vírgula para os centavos. Exemplo: 1.500,00' }
  }
  const [inteiro = '0', centavos = ''] = texto.replace(/\./g, '').split(',')
  if (centavos.length > 2) return { erro: 'Use no máximo dois dígitos de centavos.' }
  const valor = `${BigInt(inteiro).toString()}.${centavos.padEnd(2, '0')}`
  if (/^0\.00$/.test(valor)) return { erro: 'O valor deve ser maior que zero.' }
  if (Number(valor) > LIMITE) return { erro: 'Valor acima do limite do simulador.' }
  return { valor }
}
