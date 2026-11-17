/** API simulada para os testes ponta a ponta. */
import AxeBuilder from '@axe-core/playwright'
import { expect, type Page, type Route } from '@playwright/test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const PASTA = join(dirname(fileURLToPath(import.meta.url)), 'fixtures')

export function fixture<T = unknown>(nome: string): T {
  return JSON.parse(readFileSync(join(PASTA, nome), 'utf-8')) as T
}

export function texto(nome: string): string {
  return readFileSync(join(PASTA, nome), 'utf-8')
}

type Resposta = { status?: number; corpo: unknown; tipo?: string } | 'pendente'

/** Rotas da API: caminho -> função que decide a resposta pelos parâmetros. */
export type Sobrescritas = Record<string, (params: URLSearchParams) => Resposta>

const PADRAO: Sobrescritas = {
  '/v1/indicadores': () => ({ corpo: fixture('catalogo.json') }),
  '/v1/indicadores/ipca': () => ({ corpo: fixture('ipca.json') }),
  '/v1/indicadores/ipca/resumo': (p) => ({
    corpo: fixture(p.get('periodo') === '12m' ? 'resumo_12m.json' : 'resumo_5a.json'),
  }),
  '/v1/indicadores/ipca/serie': (p) => ({
    corpo: fixture(p.get('periodo') === '12m' ? 'serie_12m.json' : 'serie_5a.json'),
  }),
  '/v1/indicadores/ipca/serie.csv': () => ({
    corpo: texto('ipca_12m.csv'),
    tipo: 'text/csv; charset=utf-8',
  }),
  '/v1/simulador/poder-de-compra': (p) => ({
    corpo: fixture(p.get('valor') === '1500.00' ? 'simulacao_1500.json' : 'simulacao_padrao.json'),
  }),
}

export async function simularApi(page: Page, sobrescritas: Sobrescritas = {}) {
  const rotas = { ...PADRAO, ...sobrescritas }
  await page.route('http://api.teste/**', async (route: Route) => {
    const url = new URL(route.request().url())
    const decidir = rotas[url.pathname]
    if (!decidir) {
      return route.fulfill({
        status: 404,
        contentType: 'application/problem+json',
        body: JSON.stringify({ type: 'x', title: 'Não encontrado', status: 404, detail: 'x' }),
      })
    }
    const resposta = decidir(url.searchParams)
    if (resposta === 'pendente') return // nunca responde: estado de carregamento
    const status = resposta.status ?? 200
    await route.fulfill({
      status,
      contentType:
        resposta.tipo ?? (status >= 400 ? 'application/problem+json' : 'application/json'),
      headers: { 'Access-Control-Allow-Origin': '*' },
      body: typeof resposta.corpo === 'string' ? resposta.corpo : JSON.stringify(resposta.corpo),
    })
  })
}

/** Zero violações WCAG 2.1 A/AA (SC-007). */
export async function semViolacoesDeAcessibilidade(page: Page) {
  const resultado = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze()
  const resumo = resultado.violations.map(
    (v) => `${v.id}: ${v.nodes.map((n) => n.target).join(' | ')}`,
  )
  expect(resumo).toEqual([])
}

/** Sem rolagem horizontal da página (SC-008). */
export async function semRolagemHorizontal(page: Page) {
  const excesso = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(excesso).toBeLessThanOrEqual(0)
}
