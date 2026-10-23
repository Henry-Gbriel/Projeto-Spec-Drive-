/**
 * Cliente da API pública. A interface só conhece a URL pública da API (VITE_API_URL);
 * nenhuma credencial é usada no navegador (Princípio VII).
 */
import type { components } from './api-tipos'

export type Indicador = components['schemas']['Indicador']
export type Serie = components['schemas']['Serie']
export type Resumo = components['schemas']['Resumo']
export type Simulacao = components['schemas']['Simulacao']
export type Observacao = components['schemas']['Observacao']
export type PeriodoReferencia = components['schemas']['PeriodoReferencia']
export type Problema = components['schemas']['Problema']

export const URL_API = (import.meta.env.VITE_API_URL ?? 'http://localhost:8010').replace(/\/$/, '')

export class ErroDaApi extends Error {
  readonly status: number
  readonly problema: Problema | null

  constructor(status: number, problema: Problema | null) {
    super(problema?.detail ?? `Erro ${status} ao consultar os dados.`)
    this.status = status
    this.problema = problema
  }
}

/** Atalhos de período da API e período personalizado (AAAA-MM). */
export type Periodo =
  | { tipo: 'atalho'; atalho: '12m' | '3a' | '5a' | '10a' }
  | { tipo: 'personalizado'; inicio: string; fim: string }

export function parametrosDoPeriodo(periodo: Periodo): Record<string, string> {
  return periodo.tipo === 'atalho'
    ? { periodo: periodo.atalho }
    : { inicio: periodo.inicio, fim: periodo.fim }
}

export function montarUrl(caminho: string, parametros: Record<string, string> = {}): string {
  const consulta = new URLSearchParams(parametros).toString()
  return `${URL_API}${caminho}${consulta ? `?${consulta}` : ''}`
}

export async function obterJson<T>(
  caminho: string,
  parametros: Record<string, string> = {},
  sinal?: AbortSignal,
): Promise<T> {
  const resposta = await fetch(montarUrl(caminho, parametros), {
    signal: sinal,
    headers: { Accept: 'application/json' },
  })
  if (!resposta.ok) {
    let problema: Problema | null = null
    if (resposta.headers.get('content-type')?.includes('json')) {
      problema = (await resposta.json()) as Problema
    }
    throw new ErroDaApi(resposta.status, problema)
  }
  return (await resposta.json()) as T
}
