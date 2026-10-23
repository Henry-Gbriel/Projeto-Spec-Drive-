import { expect, test } from '@playwright/test'
import { semRolagemHorizontal, semViolacoesDeAcessibilidade, simularApi } from './apoio'

test.beforeEach(async ({ page }) => {
  await simularApi(page)
  await page.goto('/')
})

test('apresenta o projeto, os temas e as etapas do fluxo de dados (US1-1)', async ({ page }) => {
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Conhecer nossa moeda')
  await expect(page.getByText('BCB · IBGE')).toBeVisible()
  for (const tema of ['Inflação', 'Poder de compra', 'Câmbio', 'Moeda em circulação']) {
    await expect(page.getByRole('heading', { name: tema, exact: true })).toBeVisible()
  }
  for (const etapa of ['Coleta', 'Armazenamento', 'Tratamento', 'Apresentação']) {
    await expect(page.getByRole('heading', { name: etapa, exact: true })).toBeVisible()
  }
})

test('avisa que as miniaturas são ilustrações (US1-2)', async ({ page }) => {
  await expect(page.getByText('As miniaturas dos cards são ilustrações, não dados.')).toBeVisible()
})

test('temas não entregues aparecem como "Em breve", sem link (US1-3, FR-005)', async ({ page }) => {
  const cambio = page
    .getByRole('listitem')
    .filter({ has: page.getByRole('heading', { name: 'Câmbio' }) })
  await expect(cambio.getByText('Em breve')).toBeVisible()
  await expect(cambio.getByRole('link')).toHaveCount(0)
  await expect(
    page.getByRole('navigation', { name: 'Principal' }).getByRole('link', { name: 'Câmbio' }),
  ).toHaveCount(0)
})

test('contatos do autor no rodapé (US1-4)', async ({ page }) => {
  const rodape = page.getByRole('contentinfo')
  const linkedin = rodape.getByRole('link', { name: /LinkedIn/ })
  await expect(linkedin).toHaveAttribute('href', 'https://www.linkedin.com/in/autor-exemplo')
  await expect(linkedin).toHaveAttribute('target', '_blank')
  await expect(linkedin).toHaveAttribute('rel', /noopener/)
  await expect(linkedin).toContainText('(nova aba)')
  await expect(rodape.getByRole('link', { name: 'E-mail' })).toHaveAttribute(
    'href',
    'mailto:autor@example.com',
  )
})

test('navega para as páginas disponíveis', async ({ page }) => {
  await page.getByRole('link', { name: /Ver painel/ }).click()
  await expect(page).toHaveURL(/\/visao-geral$/)
  await expect(
    page.getByRole('navigation', { name: 'Principal' }).getByRole('link', { name: 'Visão geral' }),
  ).toHaveAttribute('aria-current', 'page')
})

test('responsiva e acessível (US1-5, SC-007, SC-008)', async ({ page }) => {
  await semRolagemHorizontal(page)
  await semViolacoesDeAcessibilidade(page)
})
