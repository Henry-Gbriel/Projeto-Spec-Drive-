import { expect, test } from '@playwright/test'
import { semRolagemHorizontal, semViolacoesDeAcessibilidade, simularApi } from './apoio'

test.beforeEach(async ({ page }) => {
  await simularApi(page)
  await page.goto('/sobre')
})

test('catálogo com metadados e selo de cada indicador (US8-1)', async ({ page }) => {
  const itens = page
    .getByRole('list')
    .filter({ has: page.getByRole('heading', { name: 'IPCA — variação mensal' }) })
    .getByRole('listitem')
  await expect(itens).toHaveCount(12)
  const ipca = itens.filter({ has: page.getByRole('heading', { name: 'IPCA — variação mensal' }) })
  await expect(ipca.getByText('Atualizado')).toBeVisible()
  for (const termo of ['Fonte oficial', 'Unidade', 'Frequência', 'Período', 'Atualização']) {
    await expect(ipca.getByRole('term').filter({ hasText: termo })).toBeVisible()
  }
  await expect(ipca.getByText('jan/1994 a set/2026')).toBeVisible()
  const dolar = itens.filter({ has: page.getByRole('heading', { name: 'Dólar (PTAX)' }) })
  await expect(dolar.getByText('Aguardando integração')).toBeVisible()
  const cedulas = itens.filter({
    has: page.getByRole('heading', { name: 'Produção de cédulas e moedas' }),
  })
  await expect(cedulas.getByText('Em definição')).toBeVisible()
})

test('CSV completo para integrados e botão desabilitado para os demais (US8-2)', async ({
  page,
}) => {
  const ipca = page
    .getByRole('listitem')
    .filter({ has: page.getByRole('heading', { name: 'IPCA — variação mensal' }) })
  await expect(ipca.getByRole('link', { name: /Baixar CSV/ })).toHaveAttribute(
    'href',
    'http://api.teste/v1/indicadores/ipca/serie.csv',
  )
  const dolar = page
    .getByRole('listitem')
    .filter({ has: page.getByRole('heading', { name: 'Dólar (PTAX)' }) })
  const botao = dolar.getByRole('button', { name: /Baixar CSV/ })
  await expect(botao).toHaveAttribute('aria-disabled', 'true')
  await expect(botao).toHaveAccessibleDescription('Disponível após a integração com a fonte.')
})

test('metodologia declara que meses ausentes não são estimados (US8-3)', async ({ page }) => {
  await expect(page.getByText(/nunca preenchidos com estimativas/)).toBeVisible()
  await expect(page.getByText(/mantém a última versão válida/)).toBeVisible()
})

test('sobre o projeto e a metodologia Spec-Driven (US8-4)', async ({ page }) => {
  await expect(page.getByRole('heading', { name: /Um projeto independente/ })).toBeVisible()
  await expect(page.getByText('Spec-Driven')).toBeVisible()
})

test('responsiva e acessível', async ({ page }) => {
  await expect(page.getByText('Atualizado').first()).toBeVisible()
  await semRolagemHorizontal(page)
  await semViolacoesDeAcessibilidade(page)
})
