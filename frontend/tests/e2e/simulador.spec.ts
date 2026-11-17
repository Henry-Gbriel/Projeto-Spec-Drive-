import { expect, test } from '@playwright/test'
import { fixture, semRolagemHorizontal, semViolacoesDeAcessibilidade, simularApi } from './apoio'

test('resultado completo da simulação padrão (US3-1)', async ({ page }) => {
  await simularApi(page)
  await page.goto('/poder-de-compra')
  await expect(page.getByText('R$ 171,28').first()).toBeVisible()
  await expect(page.getByText('71,28%')).toBeVisible()
  await expect(page.getByText('−41,62%')).toBeVisible()
  await expect(page.getByText(/129 meses de IPCA/)).toBeVisible()
  await expect(
    page.getByText(/não é ganho nem perda de dinheiro: é o quanto os preços subiram/),
  ).toBeVisible()
  await expect(page.getByRole('note').filter({ hasText: 'ainda não foi publicado' })).toBeVisible()
})

test('passo a passo com os números da simulação (US3-2)', async ({ page }) => {
  await simularApi(page)
  await page.goto('/poder-de-compra')
  const metodologia = page.getByRole('region', { name: /Como o cálculo/ })
  await expect(metodologia).toContainText('jan/2016 e set/2026 (129 meses)')
  await expect(metodologia).toContainText('1,7128')
  await expect(metodologia).toContainText('R$ 171,28')
})

test('valor "1.500,00" é enviado como 1500.00 (US3-6)', async ({ page }) => {
  await simularApi(page)
  await page.goto('/poder-de-compra')
  const pedido = page.waitForRequest((r) => r.url().includes('valor=1500.00'))
  await page.getByLabel('Valor em reais').fill('1.500,00')
  await page.getByLabel('Data inicial').fill('2016-01')
  await page.getByLabel('Data final').fill('2025-12')
  await page.getByRole('button', { name: 'Calcular' }).click()
  await pedido
  await expect(page.getByText('R$ 2.471,50').first()).toBeVisible()
})

test('entrada inválida local: sem resultado, mensagem junto ao campo e foco (US3-4)', async ({
  page,
}) => {
  await simularApi(page)
  await page.goto('/poder-de-compra')
  const valor = page.getByLabel('Valor em reais')
  await valor.fill('abc')
  await page.getByRole('button', { name: 'Calcular' }).click()
  await expect(valor).toHaveAttribute('aria-invalid', 'true')
  await expect(valor).toBeFocused()
  await expect(valor).toHaveAccessibleDescription(/Use apenas números/)
})

test('data inicial posterior à final', async ({ page }) => {
  await simularApi(page)
  await page.goto('/poder-de-compra')
  await page.getByLabel('Data inicial').fill('2020-05')
  await page.getByLabel('Data final').fill('2020-01')
  await page.getByRole('button', { name: 'Calcular' }).click()
  await expect(page.getByLabel('Data inicial')).toBeFocused()
  await expect(
    page.getByText('A data inicial deve ser anterior ou igual à data final.'),
  ).toBeVisible()
})

test('erro devolvido pelo servidor aparece junto ao campo', async ({ page }) => {
  await simularApi(page, {
    '/v1/simulador/poder-de-compra': (p) =>
      p.get('inicio') === '2026-10'
        ? { status: 400, corpo: fixture('simulacao_erro_inicio.json') }
        : { corpo: fixture('simulacao_padrao.json') },
  })
  // Força a validação do servidor: o indicador local não informa o período disponível.
  await page.route('http://api.teste/v1/indicadores/ipca', (r) => {
    const corpo = fixture<Record<string, unknown>>('ipca.json')
    return r.fulfill({
      json: { ...corpo, periodo_disponivel: null },
      headers: { 'Access-Control-Allow-Origin': '*' },
    })
  })
  await page.goto('/poder-de-compra')
  await page.getByLabel('Data inicial').fill('2026-10')
  await page.getByLabel('Data final').fill('2026-12')
  await page.getByRole('button', { name: 'Calcular' }).click()
  await expect(page.getByText('Ainda não há IPCA publicado para out/2026.')).toBeVisible()
  await expect(page.getByText('Corrija os campos indicados para ver o resultado.')).toBeVisible()
})

test('fluxo inteiro só com teclado', async ({ page }) => {
  await simularApi(page)
  await page.goto('/poder-de-compra')
  await page.getByLabel('Valor em reais').focus()
  await page.keyboard.press('Control+A')
  await page.keyboard.type('1.500,00')
  await page.getByLabel('Data inicial').focus()
  await page.keyboard.type('012016')
  await page.getByLabel('Data final').focus()
  await page.keyboard.type('122025')
  await page.getByRole('button', { name: 'Calcular' }).focus()
  await page.keyboard.press('Enter')
  await expect(page.getByText('R$ 2.471,50').first()).toBeVisible()
})

test('responsivo e acessível', async ({ page }) => {
  await simularApi(page)
  await page.goto('/poder-de-compra')
  await expect(page.getByText('R$ 171,28').first()).toBeVisible()
  await semRolagemHorizontal(page)
  await semViolacoesDeAcessibilidade(page)
})

test('valor muito grande: separadores brasileiros, sem notação científica e sem quebrar o layout', async ({
  page,
}) => {
  await simularApi(page, {
    '/v1/simulador/poder-de-compra': () => ({ corpo: fixture('simulacao_bilhao.json') }),
  })
  await page.setViewportSize({ width: 360, height: 780 })
  await page.goto('/poder-de-compra')
  await page.getByLabel('Valor em reais').fill('1.000.000.000,00')
  await page.getByLabel('Data inicial').fill('1994-07')
  await page.getByLabel('Data final').fill('2026-09')
  await page.getByRole('button', { name: 'Calcular' }).click()
  const resultado = page.getByRole('region', { name: 'Resultado' })
  await expect(resultado).toContainText('R$ 8.977.072.379,59')
  await expect(page.getByText('R$ 111.394.891,09')).toBeVisible()
  await expect(page.locator('body')).not.toContainText(/\de[+-]?\d/i)
  await semRolagemHorizontal(page)
  const caixa = await resultado.boundingBox()
  expect(caixa!.x + caixa!.width).toBeLessThanOrEqual(360)
})
