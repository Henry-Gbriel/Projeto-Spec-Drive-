/**
 * Verificações transversais em todas as páginas disponíveis (T112–T114):
 * responsividade (SC-008), acessibilidade (SC-007) e metadados visíveis (SC-003).
 */
import { expect, test } from '@playwright/test'
import { semRolagemHorizontal, semViolacoesDeAcessibilidade, simularApi } from './apoio'

const PAGINAS = ['/', '/visao-geral', '/poder-de-compra', '/sobre']

for (const largura of [360, 768, 1440]) {
  test(`sem rolagem horizontal em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 900 })
    await simularApi(page)
    for (const caminho of PAGINAS) {
      await page.goto(caminho)
      await page.waitForLoadState('networkidle')
      await semRolagemHorizontal(page)
    }
  })
}

test('todas as páginas sem violações WCAG 2.1 AA', async ({ page }) => {
  await simularApi(page)
  for (const caminho of PAGINAS) {
    await page.goto(caminho)
    await page.waitForLoadState('networkidle')
    await semViolacoesDeAcessibilidade(page)
  }
})

test('todo cartão, gráfico e tabela mostra fonte, unidade, período e atualização', async ({
  page,
}) => {
  await simularApi(page)
  await page.goto('/visao-geral')
  const cartao = page.getByRole('article', { name: /Inflação acumulada/ })
  for (const termo of ['Período', 'Fonte', 'Unidade', 'Atualização']) {
    await expect(cartao.getByRole('term').filter({ hasText: termo })).toBeVisible()
  }
  const grafico = page.locator('figure')
  await expect(grafico).toContainText('unidade:')
  await expect(grafico).toContainText('Fonte: IBGE')
  await expect(grafico).toContainText('Período:')
  await expect(grafico).toContainText('Atualização:')
  await page.getByText('Ver valores em tabela').click()
  const legenda = page.locator('caption')
  for (const trecho of [
    'Fonte: IBGE',
    'Unidade: % ao mês',
    'Atualização:',
    'out/2021 a set/2026',
  ]) {
    await expect(legenda).toContainText(trecho)
  }

  await page.goto('/poder-de-compra')
  const formulario = page.locator('form')
  for (const termo of ['Fonte', 'Unidade', 'Atualização']) {
    await expect(formulario.getByRole('term').filter({ hasText: termo })).toBeVisible()
  }
})

test('navegação por teclado: pular para o conteúdo', async ({ page }) => {
  await simularApi(page)
  await page.goto('/')
  await page.keyboard.press('Tab')
  const pular = page.getByRole('link', { name: 'Pular para o conteúdo' })
  await expect(pular).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL(/#conteudo$/)
})
