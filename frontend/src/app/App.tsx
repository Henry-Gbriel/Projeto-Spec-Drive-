import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createBrowserRouter, RouterProvider } from 'react-router'
import { Inicio } from '../paginas/Inicio'
import { NaoEncontrada } from '../paginas/NaoEncontrada'
import { PoderDeCompra } from '../paginas/PoderDeCompra'
import { Sobre } from '../paginas/Sobre'
import { VisaoGeral } from '../paginas/VisaoGeral'
import { Layout } from './Layout'

const UMA_HORA = 60 * 60 * 1000

export function criarClienteConsultas() {
  return new QueryClient({
    defaultOptions: { queries: { staleTime: UMA_HORA, refetchOnWindowFocus: false } },
  })
}

const roteador = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <Inicio /> },
      { path: '/visao-geral', element: <VisaoGeral /> },
      { path: '/poder-de-compra', element: <PoderDeCompra /> },
      { path: '/sobre', element: <Sobre /> },
      { path: '*', element: <NaoEncontrada /> },
    ],
  },
])

const clienteConsultas = criarClienteConsultas()

export function App() {
  return (
    <QueryClientProvider client={clienteConsultas}>
      <RouterProvider router={roteador} />
    </QueryClientProvider>
  )
}
