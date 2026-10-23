import { expect, test } from '@playwright/test'
import { fixture, semRolagemHorizontal, semViolacoesDeAcessibilidade, simularApi } from './apoio'

type Json = Record<string, any> // eslint-disable-line @typescript-eslint/no-explicit-any

test('período padrão de 5 anos com referência explícita (US2-1)', async ({ page }) => {
  await simularApi(page)
  await page.goto('/visao-geral')
  await expect(page.getByRole('button', { name: '5 anos' })).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByText(/Referência:/)).toContainText('out/2021 a set/2026')
})

test('cartão do IPCA com número, direção em texto e metadados (US2-2)', async ({ page }) => {
  await simularApi(page)
  await page.goto('/visao-geral')
  const cartao = page.getByRole('article', { name: /Inflação acumulada/ })
  await expect(cartao.getByText('+29,47')).toBeVisible()
  await expect(cartao.getByText('Alta de preços: o real comprou menos.')).toBeVisible()
  for (const rotulo of ['Período', 'Fonte', 'Unidade', 'Atualização']) {
    await expect(cartao.getByRole('term').filter({ hasText: rotulo })).toBeVisible()
  }
  await expect(cartao.getByText(/IBGE \(SIDRA tabela 1737/)).toBeVisible()
  await expect(cartao.getByText('Ilustrativo')).toHaveCount(0)
})

test('troca de período atualiza cartão, gráfico e tabela (US2-1, US2-3)', async ({ page }) => {
  await simularApi(page)
  await page.goto('/visao-geral')
  await page.getByRole('button', { name: '12 meses' }).click()
  await expect(page.getByText(/Referência:/)).toContainText('out/2025 a set/2026')
  await page.getByText('Ver valores em tabela').click()
  const tabela = page.getByRole('table')
  await expect(tabela.getByRole('row')).toHaveCount(13) // cabeçalho + 12 meses
  const ultima = tabela.getByRole('row').last()
  await expect(ultima.getByRole('rowheader')).toHaveText('set/2026')
  await expect(ultima.getByRole('cell').first()).toHaveText('0,82')
})

test('explicação "O que é IPCA?" e diferença para câmbio (US2-5)', async ({ page }) => {
  await simularApi(page)
  await page.goto('/visao-geral')
  await page.getByText('O que é IPCA?').first().click()
  await expect(
    page.getByText(/índice oficial de inflação do Brasil, calculado pelo IBGE/),
  ).toBeVisible()
  await expect(page.getByRole('heading', { name: /Dois jeitos de o real/ })).toBeVisible()
})

test('download do CSV com o período escolhido (US2-6)', async ({ page }) => {
  await simularApi(page)
  await page.goto('/visao-geral')
  await page.getByRole('button', { name: '12 meses' }).click()
  const link = page.getByRole('link', { name: /Baixar CSV/ })
  await expect(link).toHaveAttribute(
    'href',
    'http://api.teste/v1/indicadores/ipca/serie.csv?periodo=12m',
  )
})

test('aviso de mês não publicado (US2-7)', async ({ page }) => {
  const resumo = fixture<Json>('resumo_5a.json')
  resumo.periodo.aviso_nao_publicado =
    'O IPCA de out/2026 ainda não foi publicado pelo IBGE. O cálculo usa set/2026.'
  await simularApi(page, { '/v1/indicadores/ipca/resumo': () => ({ corpo: resumo }) })
  await page.goto('/visao-geral')
  await expect(page.getByRole('note').filter({ hasText: 'ainda não foi publicado' })).toBeVisible()
})

test('estado de carregamento', async ({ page }) => {
  await simularApi(page, {
    '/v1/indicadores/ipca/resumo': () => 'pendente',
    '/v1/indicadores/ipca/serie': () => 'pendente',
  })
  await page.goto('/visao-geral')
  await expect(page.getByText('Carregando dados de IPCA…').first()).toBeAttached()
})

test('lacuna: linha interrompida, "sem dado" e cálculo não feito (V5)', async ({ page }) => {
  const resumo = fixture<Json>('resumo_5a.json')
  Object.assign(resumo, {
    situacao: 'lacuna',
    meses_ausentes: ['2025-03-01'],
    acumulado_percentual: null,
  })
  const serie = fixture<Json>('serie_5a.json')
  const i = serie.observacoes.findIndex((o: Json) => o.data === '2025-03-01')
  serie.observacoes[i] = { data: '2025-03-01', valor: null, situacao: 'ausente' }
  serie.derivadas.acumulado_no_periodo = serie.derivadas.acumulado_no_periodo.map(
    (v: string | null, j: number) => (j >= i ? null : v),
  )
  await simularApi(page, {
    '/v1/indicadores/ipca/resumo': () => ({ corpo: resumo }),
    '/v1/indicadores/ipca/serie': () => ({ corpo: serie }),
  })
  await page.goto('/visao-geral')
  await expect(page.getByText(/Falta o dado de mar\/2025/)).toBeVisible()
  await expect(page.getByText(/Linha interrompida: sem dado em mar\/2025/)).toBeVisible()
  await page.getByText('Ver valores em tabela').click()
  const linha = page
    .getByRole('row')
    .filter({ has: page.getByRole('rowheader', { name: 'mar/2025' }) })
  await expect(linha.getByRole('cell').first()).toHaveText('sem dado')
})

test('falha na atualização: mostra a última versão válida com aviso (V6)', async ({ page }) => {
  const mensagem = 'A atualização de 23/10/2026 falhou. Exibindo a última versão válida.'
  const comFalha = (nome: string) => {
    const corpo = fixture<Json>(nome)
    corpo.indicador.atualizacao = {
      ...corpo.indicador.atualizacao,
      situacao: 'falha_atualizacao',
      mensagem,
    }
    return { corpo }
  }
  await simularApi(page, {
    '/v1/indicadores/ipca/resumo': () => comFalha('resumo_5a.json'),
    '/v1/indicadores/ipca/serie': () => comFalha('serie_5a.json'),
  })
  await page.goto('/visao-geral')
  await expect(page.getByText('+29,47')).toBeVisible()
  await expect(page.getByText(mensagem).first()).toBeVisible()
})

test('erro de rede: mensagem e "Tentar novamente"', async ({ page }) => {
  await simularApi(page, {
    '/v1/indicadores/ipca/resumo': () => ({
      status: 503,
      corpo: { type: 'x', title: 'x', status: 503, detail: 'x' },
    }),
  })
  await page.goto('/visao-geral')
  await expect(page.getByRole('button', { name: /Tentar novamente/ })).toBeVisible({
    timeout: 15_000,
  })
})

test('leitura de ponto do gráfico pelo teclado', async ({ page }) => {
  await simularApi(page)
  await page.goto('/visao-geral')
  const grafico = page.locator('.recharts-surface').first()
  await grafico.focus()
  await page.keyboard.press('ArrowRight')
  await expect(page.locator('.recharts-tooltip-wrapper')).toContainText('%')
})

test('responsiva e acessível', async ({ page }) => {
  await simularApi(page)
  await page.goto('/visao-geral')
  await expect(page.getByText('+29,47')).toBeVisible()
  await semRolagemHorizontal(page)
  await semViolacoesDeAcessibilidade(page)
})

test('falha antes da primeira publicação: estado de falha, sem números (FR-040)', async ({
  page,
}) => {
  const mensagem = 'A atualização de 23/10/2026 falhou e ainda não há versão válida para exibir.'
  const indicador = fixture<Json>('ipca.json')
  indicador.periodo_disponivel = null
  indicador.atualizacao = {
    situacao: 'falha_atualizacao',
    ultima_atualizacao_valida: null,
    ultima_tentativa: '2026-10-23T09:17:00Z',
    mensagem,
  }
  const semVersao = () => ({
    status: 409,
    corpo: {
      type: 'x',
      title: 'Dados ainda não disponíveis',
      status: 409,
      detail: 'Ainda não há dados.',
    },
  })
  await simularApi(page, {
    '/v1/indicadores/ipca': () => ({ corpo: indicador }),
    '/v1/indicadores/ipca/resumo': semVersao,
    '/v1/indicadores/ipca/serie': semVersao,
  })
  await page.goto('/visao-geral')
  await expect(page.getByRole('alert').filter({ hasText: mensagem }).first()).toBeVisible()
  await expect(page.getByText('Aguardando integração')).toHaveCount(0)
  await expect(page.getByText('+29,47')).toHaveCount(0)
})
