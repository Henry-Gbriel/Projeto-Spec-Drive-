import { render, screen, within } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it } from 'vitest'
import { Navegacao } from '../../src/app/Navegacao'
import { PAGINAS, disponivel } from '../../src/conteudo/site'

function renderizarEm(caminho: string) {
  const roteador = createMemoryRouter([{ path: '*', element: <Navegacao /> }], {
    initialEntries: [caminho],
  })
  render(<RouterProvider router={roteador} />)
  return within(screen.getByRole('navigation', { name: 'Principal' }))
}

describe('Navegacao', () => {
  it('marca a página atual com aria-current', () => {
    const nav = renderizarEm('/poder-de-compra')
    expect(nav.getByRole('link', { name: 'Poder de compra' })).toHaveAttribute(
      'aria-current',
      'page',
    )
    expect(nav.getByRole('link', { name: 'Início' })).not.toHaveAttribute('aria-current')
  })

  it('não mostra como link páginas de entregas futuras (FR-005)', () => {
    const nav = renderizarEm('/')
    for (const pagina of PAGINAS) {
      const links = nav.queryAllByRole('link', { name: pagina.rotulo })
      expect(links).toHaveLength(disponivel(pagina) ? 1 : 0)
    }
  })
})
