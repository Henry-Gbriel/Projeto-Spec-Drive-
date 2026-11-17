/** Dados do site: autor, páginas e entrega atual. */

export const ENTREGA_ATUAL = 1

export interface Pagina {
  caminho: string
  rotulo: string
  entrega: number
}

export const PAGINAS: Pagina[] = [
  { caminho: '/', rotulo: 'Início', entrega: 1 },
  { caminho: '/visao-geral', rotulo: 'Visão geral', entrega: 1 },
  { caminho: '/poder-de-compra', rotulo: 'Poder de compra', entrega: 1 },
  { caminho: '/cambio', rotulo: 'Câmbio', entrega: 2 },
  { caminho: '/moeda-em-circulacao', rotulo: 'Moeda em circulação', entrega: 3 },
  { caminho: '/comparar', rotulo: 'Comparar indicadores', entrega: 4 },
  { caminho: '/sobre', rotulo: 'Sobre e metodologia', entrega: 1 },
]

export function disponivel(pagina: Pagina): boolean {
  return pagina.entrega <= ENTREGA_ATUAL
}

export const PAGINAS_DISPONIVEIS = PAGINAS.filter(disponivel)

/**
 * Contatos do autor. São públicos (aparecem no rodapé), não são segredos; vêm de variáveis
 * de build para não ficarem fixos no código. O build de produção falha se faltarem
 * (vite.config.ts).
 */
export const AUTOR = {
  nome: 'Henry Gabriel Santos Silva',
  linkedin: import.meta.env.VITE_AUTOR_LINKEDIN as string | undefined,
  email: import.meta.env.VITE_AUTOR_EMAIL as string | undefined,
}
