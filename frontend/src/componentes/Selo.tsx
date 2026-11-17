import type { Indicador } from '../servicos/api'
import { Icone, type NomeIcone } from './Icone'
import estilos from './Selo.module.css'

type Situacao = Indicador['atualizacao']['situacao']

const SELOS: Record<Situacao | 'ilustrativo', { texto: string; icone: NomeIcone }> = {
  ilustrativo: { texto: 'Ilustrativo', icone: 'info' },
  atualizado: { texto: 'Atualizado', icone: 'check' },
  aguardando_integracao: { texto: 'Aguardando integração', icone: 'relogio' },
  em_definicao: { texto: 'Em definição', icone: 'info' },
  falha_atualizacao: { texto: 'Falha na atualização', icone: 'alerta' },
}

/** Selo de situação (FR-042) ou de natureza ilustrativa (FR-011). Sempre com texto. */
export function Selo({ tipo }: { tipo: Situacao | 'ilustrativo' }) {
  const { texto, icone } = SELOS[tipo]
  return (
    <span className={`${estilos.selo} ${estilos[tipo]}`}>
      <Icone nome={icone} tamanho={12} />
      {texto}
    </span>
  )
}

/** Selo "Ilustrativo" que só aparece quando o indicador é de fato ilustrativo. */
export function SeloNatureza({ natureza }: { natureza: Indicador['natureza'] }) {
  return natureza === 'ilustrativo' ? <Selo tipo="ilustrativo" /> : null
}

/** Etiqueta de seção ("VISÃO GERAL", "METODOLOGIA"...). */
export function EtiquetaSecao({ children, clara = false }: { children: string; clara?: boolean }) {
  return (
    <span className={`${estilos.selo} ${clara ? estilos.claro : estilos.secao}`}>{children}</span>
  )
}
