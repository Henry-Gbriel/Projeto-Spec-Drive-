/**
 * Formatação de números no padrão brasileiro (FR-024).
 *
 * A API envia decimais como texto ("1234.5678") para não perder precisão; aqui a
 * formatação é feita sobre o texto com BigInt, sem passar por ponto flutuante.
 * A interface não calcula indicadores: apenas arredonda para exibir.
 */

const PADRAO_DECIMAL = /^(-)?(\d+)(?:\.(\d+))?$/

/** Arredonda um decimal em texto para `casas` casas (meio para cima, longe do zero). */
export function arredondarTexto(texto: string, casas: number): string {
  const partes = PADRAO_DECIMAL.exec(texto.trim())
  if (!partes) throw new Error(`número inválido: ${texto}`)
  const [, sinal, inteiro, fracao = ''] = partes
  const digitos = BigInt(inteiro + fracao.padEnd(casas + 1, '0').slice(0, casas + 1))
  const arredondado = (digitos + 5n) / 10n
  const texto10 = arredondado.toString().padStart(casas + 1, '0')
  const parteInteira = casas > 0 ? texto10.slice(0, -casas) : texto10
  const parteFracao = casas > 0 ? texto10.slice(-casas) : ''
  const negativo = sinal === '-' && arredondado !== 0n
  return `${negativo ? '-' : ''}${parteInteira}${casas > 0 ? `.${parteFracao}` : ''}`
}

function agruparMilhares(inteiro: string): string {
  return inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

/** "1234567.891" -> "1.234.567,89" (com `casas` casas). */
export function formatarNumero(texto: string, casas: number): string {
  const arredondado = arredondarTexto(texto, casas)
  const negativo = arredondado.startsWith('-')
  const [inteiro, fracao] = arredondado.replace('-', '').split('.')
  const corpo = agruparMilhares(inteiro ?? '0') + (fracao ? `,${fracao}` : '')
  return negativo ? `−${corpo}` : corpo
}

/** "164.77" -> "R$ 164,77". */
export function formatarMoeda(texto: string): string {
  return `R$ ${formatarNumero(texto, 2)}`
}

/** "63.31" -> "63,31%" ou, com sinal, "+63,31%". */
export function formatarPercentual(texto: string, casas = 2, comSinal = false): string {
  const numero = formatarNumero(texto, casas)
  const positivo =
    !numero.startsWith('−') && arredondarTexto(texto, casas).replace(/[-.0]/g, '') !== ''
  return `${comSinal && positivo ? '+' : ''}${numero}%`
}

/** Sinal do número em texto: 1, 0 ou -1. */
export function sinal(texto: string): -1 | 0 | 1 {
  const limpo = texto.trim()
  if (/^-?0*(\.0*)?$/.test(limpo)) return 0
  return limpo.startsWith('-') ? -1 : 1
}
