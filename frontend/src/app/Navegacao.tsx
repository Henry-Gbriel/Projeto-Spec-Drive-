import { NavLink } from 'react-router'
import { PAGINAS_DISPONIVEIS } from '../conteudo/site'
import { Logo } from './Logo'
import estilos from './Navegacao.module.css'

/**
 * Cabeçalho com a navegação principal. Só páginas já entregues viram links (FR-005).
 * No celular, a fileira de links rola na horizontal dentro do próprio cabeçalho.
 */
export function Navegacao() {
  return (
    <header className={estilos.cabecalho}>
      <div className={`conteiner ${estilos.barra}`}>
        <Logo />
        <nav aria-label="Principal" className={estilos.nav}>
          <ul className={estilos.lista}>
            {PAGINAS_DISPONIVEIS.map((pagina) => (
              <li key={pagina.caminho}>
                <NavLink
                  to={pagina.caminho}
                  end={pagina.caminho === '/'}
                  className={({ isActive }) => `${estilos.link} ${isActive ? estilos.ativo : ''}`}
                >
                  {pagina.rotulo}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <NavLink to="/sobre" className={`botao botao-contorno ${estilos.explorar}`}>
          Explorar dados
        </NavLink>
      </div>
    </header>
  )
}
