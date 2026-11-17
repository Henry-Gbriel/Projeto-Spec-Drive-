/** Consultas à API com cache e estados de carregamento/erro (TanStack Query). */
import { useQuery } from '@tanstack/react-query'
import {
  ErroDaApi,
  obterJson,
  parametrosDoPeriodo,
  type Indicador,
  type Periodo,
  type Resumo,
  type Serie,
  type Simulacao,
} from './api'

function repetirSeTemporario(tentativas: number, erro: Error): boolean {
  // Erros de entrada (4xx) não melhoram com nova tentativa.
  return !(erro instanceof ErroDaApi && erro.status < 500) && tentativas < 2
}

export function useCatalogo() {
  return useQuery({
    queryKey: ['indicadores'],
    queryFn: ({ signal }) => obterJson<{ indicadores: Indicador[] }>('/v1/indicadores', {}, signal),
    retry: repetirSeTemporario,
  })
}

export function useSerie(codigo: string, periodo: Periodo) {
  return useQuery({
    queryKey: ['serie', codigo, periodo],
    queryFn: ({ signal }) =>
      obterJson<Serie>(`/v1/indicadores/${codigo}/serie`, parametrosDoPeriodo(periodo), signal),
    retry: repetirSeTemporario,
    placeholderData: (anterior) => anterior,
  })
}

export function useResumo(codigo: string, periodo: Periodo) {
  return useQuery({
    queryKey: ['resumo', codigo, periodo],
    queryFn: ({ signal }) =>
      obterJson<Resumo>(`/v1/indicadores/${codigo}/resumo`, parametrosDoPeriodo(periodo), signal),
    retry: repetirSeTemporario,
    placeholderData: (anterior) => anterior,
  })
}

export interface PedidoSimulacao {
  valor: string
  inicio: string
  fim: string
}

export function useSimulacao(pedido: PedidoSimulacao | null) {
  return useQuery({
    queryKey: ['simulacao', pedido],
    queryFn: ({ signal }) =>
      obterJson<Simulacao>('/v1/simulador/poder-de-compra', { ...pedido! }, signal),
    enabled: pedido !== null,
    retry: repetirSeTemporario,
  })
}

export function useIndicador(codigo: string) {
  return useQuery({
    queryKey: ['indicador', codigo],
    queryFn: ({ signal }) => obterJson<Indicador>(`/v1/indicadores/${codigo}`, {}, signal),
    retry: repetirSeTemporario,
  })
}
