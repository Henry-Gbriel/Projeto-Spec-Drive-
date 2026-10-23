import type { ReactNode } from 'react'
import estilos from './TermoExplicado.module.css'

/** Explicação em linguagem simples, expansível ("O que é?") — FR-013. */
export function TermoExplicado({
  titulo,
  children,
  clara = false,
}: {
  titulo: string
  children: ReactNode
  clara?: boolean
}) {
  return (
    <details className={`${estilos.termo} ${clara ? estilos.clara : ''}`}>
      <summary>{titulo}</summary>
      <div className={estilos.corpo}>{children}</div>
    </details>
  )
}
