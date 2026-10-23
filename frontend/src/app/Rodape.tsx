import { Link } from 'react-router'
import { Icone } from '../componentes/Icone'
import { AUTOR, PAGINAS_DISPONIVEIS } from '../conteudo/site'
import { Logo } from './Logo'
import estilos from './Rodape.module.css'

export function Rodape() {
  return (
    <footer className={estilos.rodape}>
      <div className={`conteiner ${estilos.grade}`}>
        <div className={estilos.marca}>
          <Logo />
          <p className={`editorial ${estilos.frase}`}>
            Engenharia de dados a serviço do conhecimento sobre o Brasil.
          </p>
          <p>Desenvolvido por {AUTOR.nome}.</p>
        </div>

        <nav aria-label="Rodapé">
          <ul className={estilos.links}>
            {PAGINAS_DISPONIVEIS.map((pagina) => (
              <li key={pagina.caminho}>
                <Link to={pagina.caminho}>{pagina.rotulo}</Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className={estilos.contato}>
          <h2 className="rotulo-apoio">Contato</h2>
          {AUTOR.linkedin ? (
            <a
              className={estilos.botaoContato}
              href={AUTOR.linkedin}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Icone nome="linkedin" /> LinkedIn <span className={estilos.novaAba}>(nova aba)</span>
            </a>
          ) : (
            <p className="texto-apoio">LinkedIn ainda não informado.</p>
          )}
          {AUTOR.email ? (
            <a className={estilos.botaoContato} href={`mailto:${AUTOR.email}`}>
              <Icone nome="email" /> E-mail
            </a>
          ) : (
            <p className="texto-apoio">E-mail ainda não informado.</p>
          )}
        </div>
      </div>

      <div className={`conteiner ${estilos.base}`}>
        <p>Fontes: Banco Central do Brasil e IBGE.</p>
        <p>Projeto independente de engenharia de dados e educação econômica.</p>
      </div>
    </footer>
  )
}
