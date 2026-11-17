import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router'
import estilos from './Layout.module.css'
import { Navegacao } from './Navegacao'
import { Rodape } from './Rodape'

export function Layout() {
  const { pathname } = useLocation()
  useEffect(() => {
    // Bloco explícito: scrollTo pode devolver uma Promise, que não é função de limpeza.
    window.scrollTo(0, 0)
  }, [pathname])

  return (
    <>
      <a href="#conteudo" className={estilos.pular}>
        Pular para o conteúdo
      </a>
      <Navegacao />
      <main id="conteudo" tabIndex={-1} className={estilos.principal}>
        <Outlet />
      </main>
      <Rodape />
    </>
  )
}

/** Define o título da aba do navegador de cada página. */
export function useTitulo(titulo: string) {
  useEffect(() => {
    document.title = titulo ? `${titulo} · Observatório do Real` : 'Observatório do Real'
  }, [titulo])
}
