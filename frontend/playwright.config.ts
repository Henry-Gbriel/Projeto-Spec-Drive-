import { defineConfig, devices } from '@playwright/test'

/**
 * Testes ponta a ponta contra o build de produção, com a API simulada (respostas reais
 * gravadas em tests/e2e/fixtures). Nenhum teste depende de rede.
 */
const API_TESTE = 'http://api.teste'

export default defineConfig({
  testDir: 'tests/e2e',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: 'http://localhost:4174',
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
    },
    { name: 'celular', use: { ...devices['Pixel 7'], viewport: { width: 360, height: 780 } } },
  ],
  webServer: {
    command: 'npx vite build && npx vite preview --port 4174 --strictPort',
    url: 'http://localhost:4174',
    reuseExistingServer: false,
    timeout: 120_000,
    env: {
      VITE_API_URL: API_TESTE,
      VITE_AUTOR_LINKEDIN: 'https://www.linkedin.com/in/autor-exemplo',
      VITE_AUTOR_EMAIL: 'autor@example.com',
    },
  },
})
