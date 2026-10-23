import { Link } from 'react-router'
import { useTitulo } from '../app/Layout'
import { Icone } from '../componentes/Icone'
import { EtiquetaSecao } from '../componentes/Selo'
import { PAGINAS, disponivel, type Pagina } from '../conteudo/site'
import estilos from './Inicio.module.css'

const pagina = (caminho: string) => PAGINAS.find((p) => p.caminho === caminho) as Pagina

interface Caminho {
  numero: string
  rotulo: string
  titulo: string
  texto: string
  acao: string
  pagina: Pagina
  miniatura: 'linha' | 'barras-poder' | 'cambio' | 'barras-moeda'
  tom: string | undefined
}

const CAMINHOS: Caminho[] = [
  {
    numero: '01',
    rotulo: 'Preços',
    titulo: 'Inflação',
    texto: 'Entenda como os preços mudam ao longo do tempo.',
    acao: 'Ver painel',
    pagina: pagina('/visao-geral'),
    miniatura: 'linha',
    tom: estilos.tomVerde,
  },
  {
    numero: '02',
    rotulo: 'Simulador',
    titulo: 'Poder de compra',
    texto: 'Descubra como muda o que você consegue comprar com o mesmo valor.',
    acao: 'Simular',
    pagina: pagina('/poder-de-compra'),
    miniatura: 'barras-poder',
    tom: estilos.tomAmarelo,
  },
  {
    numero: '03',
    rotulo: 'Moedas estrangeiras',
    titulo: 'Câmbio',
    texto: 'Acompanhe o valor do real em relação a outras moedas.',
    acao: 'Ver cotações',
    pagina: pagina('/cambio'),
    miniatura: 'cambio',
    tom: estilos.tomAzul,
  },
  {
    numero: '04',
    rotulo: 'Agregados',
    titulo: 'Moeda em circulação',
    texto: 'Conheça os indicadores sobre a quantidade de dinheiro na economia.',
    acao: 'Explorar',
    pagina: pagina('/moeda-em-circulacao'),
    miniatura: 'barras-moeda',
    tom: estilos.tomCinza,
  },
]

const ETAPAS = [
  {
    titulo: 'Coleta',
    texto: 'Séries oficiais do Banco Central e do IBGE, obtidas nas fontes de origem.',
  },
  {
    titulo: 'Armazenamento',
    texto: 'Histórico guardado com data de coleta, para saber de onde veio cada número.',
  },
  {
    titulo: 'Tratamento',
    texto: 'Padronização de datas e unidades, checagem de lacunas e registro de revisões.',
  },
  {
    titulo: 'Apresentação',
    texto: 'Gráficos e explicações em linguagem simples, sempre com fonte e período.',
  },
]

const COMPROMISSOS = [
  'Fontes oficiais',
  'Linguagem simples',
  'Dados abertos em CSV',
  'Unidade sempre visível',
  'Acessibilidade',
  'Rigor metodológico',
]

const ATALHOS = [
  { pagina: pagina('/visao-geral'), texto: 'Inflação em um painel, com gráfico e tabela' },
  { pagina: pagina('/poder-de-compra'), texto: 'Corrija um valor pelo IPCA' },
  { pagina: pagina('/comparar'), texto: 'Séries lado a lado em base 100' },
  { pagina: pagina('/sobre'), texto: 'Fontes, catálogo e download em CSV' },
]

function Miniatura({ tipo }: { tipo: Caminho['miniatura'] }) {
  // Ilustrações decorativas: não representam dados (aviso visível abaixo dos cartões).
  return (
    <svg viewBox="0 0 200 90" className={estilos.miniatura} aria-hidden="true" focusable="false">
      {tipo === 'linha' && (
        <polyline
          points="10,75 40,68 70,60 90,52 115,48 140,38 165,30 190,14"
          fill="none"
          stroke="var(--serie-ipca)"
          strokeWidth="2.5"
        />
      )}
      {tipo === 'barras-poder' && (
        <>
          <rect
            x="30"
            y="15"
            width="45"
            height="65"
            fill="none"
            stroke="var(--cor-amarelo)"
            strokeWidth="2"
          />
          <rect
            x="85"
            y="35"
            width="40"
            height="45"
            fill="none"
            stroke="var(--cor-amarelo)"
            strokeWidth="2"
            strokeDasharray="4 3"
          />
          <rect x="135" y="50" width="40" height="30" fill="var(--cor-amarelo)" />
        </>
      )}
      {tipo === 'cambio' && (
        <>
          <polyline
            points="10,70 40,60 60,64 90,50 120,52 150,40 190,30"
            fill="none"
            stroke="var(--serie-dolar)"
            strokeWidth="2.5"
          />
          <polyline
            points="10,55 40,48 60,50 90,38 120,40 150,28 190,18"
            fill="none"
            stroke="var(--serie-euro)"
            strokeWidth="2.5"
            strokeDasharray="5 4"
          />
        </>
      )}
      {tipo === 'barras-moeda' &&
        [0, 1, 2, 3, 4, 5].map((i) => (
          <rect
            key={i}
            x={30 + i * 25}
            y={70 - i * 9}
            width="18"
            height={10 + i * 9}
            fill={i === 5 ? 'var(--cor-amarelo)' : '#b9c0bc'}
          />
        ))}
    </svg>
  )
}

export function Inicio() {
  useTitulo('')
  return (
    <>
      <section className={estilos.hero}>
        <div className={`conteiner ${estilos.heroConteudo}`}>
          <p className={`rotulo ${estilos.chamadaRotulo}`}>Educação econômica com dados públicos</p>
          <h1 className={`titulo-composto ${estilos.heroTitulo}`}>
            Conhecer nossa moeda é <strong>compreender o nosso Brasil.</strong>
          </h1>
          <p className={estilos.heroTexto}>
            O real faz parte da nossa história e do dia a dia de milhões de brasileiros. Entender
            seu valor, seu poder de compra e suas transformações é um passo para uma sociedade mais
            consciente e preparada para o futuro.
          </p>
          <div className={estilos.acoes}>
            <Link to="/visao-geral" className="botao botao-primario">
              Explore o valor do real <Icone nome="seta-direita" />
            </Link>
            <Link to="/sobre" className="botao">
              Conheça o projeto
            </Link>
          </div>
        </div>
      </section>

      <section
        className={`conteiner ${estilos.observatorio}`}
        aria-labelledby="titulo-observatorio"
      >
        <div>
          <EtiquetaSecao>O observatório</EtiquetaSecao>
          <h2 id="titulo-observatorio" className={`editorial ${estilos.frase}`}>
            O real conta a história do país em cada preço, salário e cotação —{' '}
            <strong className={estilos.fraseForte}>e merece ser entendido por todos.</strong>
          </h2>
        </div>
        <div className={estilos.observatorioTexto}>
          <p>
            Inflação, câmbio, juros e quantidade de moeda aparecem todos os dias no noticiário, mas
            quase nunca explicados. O Observatório do Real reúne esses indicadores em um só lugar,
            com fonte oficial, unidade e período sempre à vista.
          </p>
          <p>
            Cada gráfico vem acompanhado de uma explicação simples: o que mede, como ler e o que ele
            não diz.
          </p>
          <dl className={estilos.numeros}>
            <div>
              <dt>Fontes</dt>
              <dd>BCB · IBGE</dd>
            </div>
            <div>
              <dt>Indicadores</dt>
              <dd>4 temas</dd>
            </div>
            <div>
              <dt>Dados</dt>
              <dd>Abertos, CSV</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className={estilos.faixa} aria-label="Lema">
        <p className={`editorial ${estilos.lema}`}>
          Ordem e progresso também se constroem{' '}
          <span className="destaque-amarelo">com conhecimento.</span>
        </p>
        <p className="rotulo-apoio">Observatório do Real · dados públicos para toda a sociedade</p>
      </section>

      <section className={`conteiner ${estilos.caminhos}`} aria-labelledby="titulo-caminhos">
        <div className={estilos.caminhosTopo}>
          <div>
            <EtiquetaSecao>Temas apresentados</EtiquetaSecao>
            <h2 id="titulo-caminhos" className={`titulo-composto ${estilos.tituloSecao}`}>
              Quatro caminhos <strong>para entender o real</strong>
            </h2>
          </div>
          <p className="texto-apoio">
            Cada tema olha para a moeda de um ângulo diferente, com gráficos, definições e a fonte
            de cada número.
          </p>
        </div>
        <ul className={estilos.cartoes}>
          {CAMINHOS.map((caminho) => {
            const ativo = disponivel(caminho.pagina)
            return (
              <li key={caminho.numero} className={estilos.cartao}>
                <div className={`${estilos.miniaturaFundo} ${caminho.tom}`}>
                  <Miniatura tipo={caminho.miniatura} />
                </div>
                <div className={estilos.cartaoCorpo}>
                  <p className="rotulo-apoio">
                    {caminho.numero} · {caminho.rotulo}
                  </p>
                  <h3 className="rotulo">{caminho.titulo}</h3>
                  <p className={estilos.cartaoTexto}>{caminho.texto}</p>
                  {ativo ? (
                    <Link to={caminho.pagina.caminho} className={estilos.cartaoAcao}>
                      {caminho.acao}{' '}
                      <span className="somente-leitor-de-tela">: {caminho.titulo}</span>
                      <Icone nome="seta-direita" />
                    </Link>
                  ) : (
                    <p className={estilos.emBreve}>
                      <Icone nome="relogio" /> Em breve
                    </p>
                  )}
                </div>
              </li>
            )
          })}
        </ul>
        <p className={`texto-apoio ${estilos.avisoMiniaturas}`}>
          As miniaturas dos cards são ilustrações, não dados.
        </p>
      </section>

      <section className={estilos.engenharia} aria-labelledby="titulo-engenharia">
        <div className="conteiner">
          <EtiquetaSecao clara>Engenharia de dados</EtiquetaSecao>
          <h2 id="titulo-engenharia" className={`titulo-composto ${estilos.tituloSecao}`}>
            Do dado público <strong>ao conhecimento</strong>
          </h2>
          <ol className={estilos.etapas}>
            {ETAPAS.map((etapa, indice) => (
              <li key={etapa.titulo}>
                <span className={`editorial ${estilos.etapaNumero}`} aria-hidden="true">
                  {String(indice + 1).padStart(2, '0')}
                </span>
                <h3 className="rotulo">{etapa.titulo}</h3>
                <p>{etapa.texto}</p>
              </li>
            ))}
          </ol>
          <ul className={estilos.compromissos}>
            {COMPROMISSOS.map((compromisso) => (
              <li key={compromisso}>
                <span aria-hidden="true">◆</span> {compromisso}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className={`conteiner ${estilos.proposito}`} aria-labelledby="titulo-proposito">
        <EtiquetaSecao>Propósito</EtiquetaSecao>
        <h2 id="titulo-proposito" className={`titulo-composto ${estilos.tituloProposito}`}>
          Pelo Brasil e pelo conhecimento <strong>de toda a sociedade.</strong>
        </h2>
        <p className={`editorial ${estilos.propositoTexto}`}>
          Transformamos dados públicos em informações acessíveis para compreender nossa moeda,
          conhecer nossa história econômica e construir uma visão mais consciente do futuro.
        </p>
        <ul className={estilos.atalhos}>
          {ATALHOS.map(({ pagina: destino, texto }) => (
            <li key={destino.caminho}>
              {disponivel(destino) ? (
                <Link to={destino.caminho} className={estilos.atalho}>
                  <span>
                    <span className="rotulo">{destino.rotulo}</span>
                    <span className={estilos.atalhoTexto}>{texto}</span>
                  </span>
                  <Icone nome="seta-direita" />
                </Link>
              ) : (
                <div className={`${estilos.atalho} ${estilos.atalhoInativo}`}>
                  <span>
                    <span className="rotulo">{destino.rotulo}</span>
                    <span className={estilos.atalhoTexto}>{texto}</span>
                  </span>
                  <span className={estilos.emBreve}>
                    <Icone nome="relogio" /> Em breve
                  </span>
                </div>
              )}
            </li>
          ))}
        </ul>
      </section>
    </>
  )
}
