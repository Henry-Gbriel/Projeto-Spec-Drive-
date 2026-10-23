/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

const OBRIGATORIAS_EM_PRODUCAO = ['VITE_API_URL', 'VITE_AUTOR_LINKEDIN', 'VITE_AUTOR_EMAIL']

export default defineConfig(({ command, mode }) => {
  if (command === 'build' && mode === 'production') {
    const env = { ...loadEnv(mode, process.cwd(), 'VITE_'), ...process.env }
    const faltando = OBRIGATORIAS_EM_PRODUCAO.filter((nome) => !env[nome])
    if (faltando.length) {
      throw new Error(
        `Defina ${faltando.join(', ')} para o build de produção (veja frontend/.env.example).`,
      )
    }
  }
  return {
    plugins: [react()],
    test: {
      environment: 'jsdom',
      include: ['tests/unit/**/*.test.{ts,tsx}'],
      setupFiles: ['tests/unit/setup.ts'],
      css: { modules: { classNameStrategy: 'non-scoped' } },
    },
  }
})
