import { Link } from 'react-router'
import estilos from './Logo.module.css'

export function Logo() {
  return (
    <Link to="/" className={estilos.logo}>
      <svg width="34" height="34" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
        <path d="M16 3 29 16 16 29 3 16Z" fill="none" stroke="var(--cor-amarelo)" strokeWidth="2" />
        <circle cx="16" cy="16" r="5.5" fill="none" stroke="currentColor" strokeWidth="2" />
        <path
          d="M10.6 15.2c3.4-1.6 7.4-1.6 10.8 0"
          fill="none"
          stroke="var(--cor-amarelo)"
          strokeWidth="1.6"
        />
      </svg>
      <span className={estilos.texto}>
        <span className={estilos.observatorio}>Observatório</span>{' '}
        <span className={estilos.real}>do Real</span>
        <span className="somente-leitor-de-tela">, página inicial</span>
      </span>
    </Link>
  )
}
