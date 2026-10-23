import type { ReactNode } from 'react'
import estilos from './CabecalhoPagina.module.css'
import { EtiquetaSecao } from './Selo'

/** Cabeçalho das páginas internas: etiqueta, título em duas partes e descrição. */
export function CabecalhoPagina({
  etiqueta,
  tituloFino,
  tituloForte,
  descricao,
  lateral,
  tom = 'neutro',
}: {
  etiqueta: string
  tituloFino: string
  tituloForte: string
  descricao: string
  lateral?: ReactNode
  tom?: 'neutro' | 'azul'
}) {
  return (
    <section className={`${estilos.cabecalho} ${tom === 'azul' ? estilos.azul : ''}`}>
      <div className={`conteiner ${estilos.grade}`}>
        <div className={estilos.texto}>
          <EtiquetaSecao>{etiqueta}</EtiquetaSecao>
          <h1 className={`titulo-composto ${estilos.titulo}`}>
            {tituloFino} <strong>{tituloForte}</strong>
          </h1>
          <p className={estilos.descricao}>{descricao}</p>
        </div>
        {lateral && <div className={estilos.lateral}>{lateral}</div>}
      </div>
    </section>
  )
}
