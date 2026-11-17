import type { ReactNode } from 'react'
import type { Indicador, PeriodoReferencia } from '../servicos/api'
import estilos from './CartaoIndicador.module.css'
import { AvisoFalhaAtualizacao, AvisoNaoPublicado, EstadoDados } from './EstadoDados'
import { Icone } from './Icone'
import { ListaMetadados, metadadosCompletos } from './Metadados'
import { SeloNatureza } from './Selo'

interface Props {
  titulo: string
  indicador: Indicador
  periodo: PeriodoReferencia
  /** Número já formatado ("+33,14"). */
  valor: string
  sufixo: string
  direcao: { sinal: -1 | 0 | 1; texto: string }
  /** Gráfico pequeno decorativo (os valores estão na tabela da página). */
  miniatura?: ReactNode
  explicacao?: ReactNode
}

/**
 * Cartão de indicador. Não mostra números sem fonte, unidade, período e atualização
 * (Princípio III). A direção é dada por seta E texto, nunca só por cor.
 */
export function CartaoIndicador(props: Props) {
  const { titulo, indicador, periodo, valor, sufixo, direcao, miniatura, explicacao } = props
  if (!metadadosCompletos(indicador)) {
    return (
      <EstadoDados
        estado={{ tipo: 'erro', mensagem: 'Metadados incompletos: o número não será exibido.' }}
      />
    )
  }
  const icone = direcao.sinal > 0 ? 'seta-cima' : direcao.sinal < 0 ? 'seta-baixo' : null

  return (
    <article className={`cartao ${estilos.cartao}`} aria-labelledby={`cartao-${indicador.codigo}`}>
      <header className={estilos.topo}>
        <h2 id={`cartao-${indicador.codigo}`} className="rotulo">
          {titulo}
        </h2>
        <SeloNatureza natureza={indicador.natureza} />
      </header>
      <p className={estilos.valor}>
        <span className={estilos.numero}>{valor}</span>{' '}
        <span className={estilos.sufixo}>{sufixo}</span>
      </p>
      <p className={estilos.direcao}>
        {icone && <Icone nome={icone} />}
        <span>{direcao.texto}</span>
      </p>
      {miniatura && (
        <div className={estilos.miniatura} aria-hidden="true">
          {miniatura}
        </div>
      )}
      <ListaMetadados indicador={indicador} periodo={periodo} />
      {periodo.aviso_nao_publicado && <AvisoNaoPublicado texto={periodo.aviso_nao_publicado} />}
      {indicador.atualizacao.situacao === 'falha_atualizacao' && (
        <AvisoFalhaAtualizacao mensagem={indicador.atualizacao.mensagem} />
      )}
      {explicacao}
    </article>
  )
}
