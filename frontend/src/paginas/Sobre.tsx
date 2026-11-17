import { useTitulo } from '../app/Layout'
import { CabecalhoPagina } from '../componentes/CabecalhoPagina'
import { EstadoDados, estadoDoErro } from '../componentes/EstadoDados'
import { Icone } from '../componentes/Icone'
import { ItemCatalogo } from '../componentes/ItemCatalogo'
import { EtiquetaSecao } from '../componentes/Selo'
import { CAMINHO_DO_NUMERO, CONVENCOES, ETAPAS_PROJETO, POLITICAS } from '../conteudo/metodologia'
import { useCatalogo } from '../servicos/consultas'
import estilos from './Sobre.module.css'

export function Sobre() {
  useTitulo('Sobre e metodologia')
  const catalogo = useCatalogo()

  return (
    <>
      <CabecalhoPagina
        etiqueta="Sobre e metodologia"
        tituloFino="De onde vêm os dados"
        tituloForte="e como chegam até você"
        descricao="Cada número do observatório tem fonte oficial, unidade e período. Aqui você confere tudo e pode baixar as séries."
      />

      <section className={`conteiner ${estilos.secao}`} aria-labelledby="titulo-catalogo">
        <div className={estilos.topoCatalogo}>
          <h2 id="titulo-catalogo" className={`titulo-composto ${estilos.titulo}`}>
            Catálogo de <strong>indicadores</strong>
          </h2>
          <p className="texto-apoio">
            <Icone nome="relogio" /> Aguardando integração: chega numa próxima entrega. Em
            definição: a fonte ainda está sendo confirmada.
          </p>
        </div>
        {catalogo.isPending ? (
          <EstadoDados estado={{ tipo: 'carregando', rotulo: 'catálogo' }} />
        ) : catalogo.isError ? (
          <EstadoDados estado={estadoDoErro(catalogo.error, () => void catalogo.refetch())} />
        ) : catalogo.data.indicadores.length === 0 ? (
          <EstadoDados estado={{ tipo: 'sem_dados' }} />
        ) : (
          <ul className={estilos.catalogo}>
            {catalogo.data.indicadores.map((indicador) => (
              <ItemCatalogo key={indicador.codigo} indicador={indicador} />
            ))}
          </ul>
        )}
      </section>

      <section className={estilos.caminho} aria-labelledby="titulo-caminho">
        <div className="conteiner">
          <EtiquetaSecao clara>Engenharia de dados</EtiquetaSecao>
          <h2 id="titulo-caminho" className={`titulo-composto ${estilos.titulo}`}>
            O caminho <strong>de cada número</strong>
          </h2>
          <ol className={estilos.etapas}>
            {CAMINHO_DO_NUMERO.map((etapa, i) => (
              <li key={etapa.titulo}>
                <span className={`editorial ${estilos.numero}`} aria-hidden="true">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <h3 className="rotulo">{etapa.titulo}</h3>
                <p>{etapa.texto}</p>
                <p className={estilos.detalhe}>{etapa.detalhe}</p>
              </li>
            ))}
          </ol>
          <ul className={estilos.politicas}>
            {POLITICAS.map((politica) => (
              <li key={politica}>{politica}</li>
            ))}
          </ul>
          <h3 className={`rotulo ${estilos.subtitulo}`}>Convenções de cálculo e de arquivo</h3>
          <dl className={estilos.convencoes}>
            {CONVENCOES.map((c) => (
              <div key={c.titulo}>
                <dt>{c.titulo}</dt>
                <dd>{c.texto}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section className={`conteiner ${estilos.sobre}`} aria-labelledby="titulo-sobre">
        <div>
          <EtiquetaSecao>Sobre o projeto</EtiquetaSecao>
          <h2 id="titulo-sobre" className={`editorial ${estilos.fraseSobre}`}>
            Um projeto independente de <strong>dados e educação econômica.</strong>
          </h2>
          <p className="texto-apoio">
            O Observatório do Real é um projeto independente de engenharia de dados e educação
            econômica, desenvolvido para transformar dados públicos em conhecimento acessível.
          </p>
          <p className="texto-apoio">
            O desenvolvimento segue a metodologia <strong>Spec-Driven</strong>: antes do código,
            cada parte é descrita em requisitos, planejada e dividida em tarefas documentadas.
          </p>
        </div>
        <div className={estilos.ladoSobre}>
          <ol className={estilos.projeto}>
            {ETAPAS_PROJETO.map((etapa, i) => (
              <li key={etapa.titulo}>
                <span className={`editorial destaque-amarelo ${estilos.numero}`} aria-hidden="true">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <h3 className="rotulo">{etapa.titulo}</h3>
                <p className="texto-apoio">{etapa.texto}</p>
              </li>
            ))}
          </ol>
          <details className={`cartao ${estilos.tecnico}`}>
            <summary className="rotulo">Detalhes técnicos para visitantes interessados</summary>
            <ul>
              <li>
                Coleta, tratamento e API em Python (FastAPI), com banco PostgreSQL (Supabase).
              </li>
              <li>Camadas separadas: dados brutos, dados tratados e resultados publicados.</li>
              <li>Revisões das fontes guardadas em histórico; nenhum valor é sobrescrito.</li>
              <li>
                Interface em React com TypeScript, testada quanto a acessibilidade (WCAG 2.1 AA).
              </li>
              <li>Cálculos com aritmética decimal exata e testes contra valores de referência.</li>
            </ul>
          </details>
        </div>
      </section>
    </>
  )
}
