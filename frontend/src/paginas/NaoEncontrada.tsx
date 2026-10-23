import { Link } from 'react-router'
import { useTitulo } from '../app/Layout'

export function NaoEncontrada() {
  useTitulo('Página não encontrada')
  return (
    <section className="conteiner" style={{ paddingBlock: '5rem' }}>
      <h1 className="titulo-composto" style={{ fontSize: '2.5rem' }}>
        Página <strong>não encontrada</strong>
      </h1>
      <p className="texto-apoio" style={{ marginBlock: '1rem 2rem' }}>
        O endereço pode ter mudado ou a página ainda não foi publicada.
      </p>
      <Link to="/" className="botao botao-primario">
        Voltar ao início
      </Link>
    </section>
  )
}
