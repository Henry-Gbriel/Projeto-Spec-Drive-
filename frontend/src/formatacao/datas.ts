/** Datas em português (FR-024). As datas de referência chegam como "AAAA-MM-DD". */

const MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
const MESES_EXTENSO = [
  'janeiro',
  'fevereiro',
  'março',
  'abril',
  'maio',
  'junho',
  'julho',
  'agosto',
  'setembro',
  'outubro',
  'novembro',
  'dezembro',
]

function partes(data: string): [number, number] {
  const [ano, mes] = data.split('-').map(Number)
  return [ano ?? 0, mes ?? 1]
}

/** "2016-01-01" ou "2016-01" -> "jan/2016". */
export function mesAbreviado(data: string): string {
  const [ano, mes] = partes(data)
  return `${MESES[mes - 1]}/${ano}`
}

/** "2016-01-01" -> "janeiro de 2016" (para leitores de tela). */
export function mesPorExtenso(data: string): string {
  const [ano, mes] = partes(data)
  return `${MESES_EXTENSO[mes - 1]} de ${ano}`
}

/** "2016-01-01" -> "2016-01" (formato dos parâmetros da API). */
export function paraMesIso(data: string): string {
  return data.slice(0, 7)
}

/** Data e hora de atualização em Brasília: "22/10/2026 às 06:17". */
export function dataHora(isoDataHora: string): string {
  const data = new Date(isoDataHora)
  const formatador = new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'America/Sao_Paulo',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
  return formatador.format(data).replace(', ', ' às ')
}

/** Data de atualização sem hora: "22/10/2026". */
export function dataCurta(isoDataHora: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'America/Sao_Paulo',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(isoDataHora))
}
