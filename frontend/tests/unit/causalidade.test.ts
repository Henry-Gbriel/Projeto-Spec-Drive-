/**
 * Princípio V e SC-012: nenhum texto do site afirma causalidade entre indicadores.
 * Varre os textos exibidos (conteúdo e páginas) em busca de conectivos causais.
 */
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const PASTAS = ['src/conteudo', 'src/paginas', 'src/componentes', 'src/app']
const PROIBIDAS = [
  /\bpor causa d/i,
  /\bcausou\b/i,
  /\bcausa(m|ram)?\b(?! o outro)/i, // "não comprovam que um causa o outro" é a ressalva permitida
  /\bdevido (a|ao|à)\b/i,
  /\bprovoc(a|ou|aram|am)\b/i,
  /\blevou a\b/i,
  /\bfaz com que\b/i,
  /\bem consequência\b/i,
]

function arquivos(pasta: string): string[] {
  return readdirSync(pasta).flatMap((nome) => {
    const caminho = join(pasta, nome)
    if (statSync(caminho).isDirectory()) return arquivos(caminho)
    return /\.(ts|tsx)$/.test(nome) ? [caminho] : []
  })
}

describe('linguagem descritiva, sem causalidade', () => {
  const todos = PASTAS.flatMap(arquivos)

  it('encontra os arquivos de texto do site', () => {
    expect(todos.length).toBeGreaterThan(10)
  })

  it.each(todos)('%s não usa conectivos causais', (arquivo) => {
    const texto = readFileSync(arquivo, 'utf-8')
    for (const padrao of PROIBIDAS) expect(texto).not.toMatch(padrao)
  })
})
