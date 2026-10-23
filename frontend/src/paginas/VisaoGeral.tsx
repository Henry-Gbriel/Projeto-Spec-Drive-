import { lazy, Suspense, useState } from 'react'
import { Link } from 'react-router'
import { useTitulo } from '../app/Layout'
import { BotaoCsv } from '../componentes/BotaoCsv'
import { CabecalhoPagina } from '../componentes/CabecalhoPagina'
import { CartaoIndicador } from '../componentes/CartaoIndicador'
import {
  AvisoFalhaAtualizacao,
  EstadoDados,
  estadoDoErro,
  type EstadoBloqueante,
} from '../componentes/EstadoDados'
import { textoAtualizacao, textoFonte, textoPeriodo } from '../componentes/Metadados'
import { SeletorPeriodo } from '../componentes/SeletorPeriodo'
import { TabelaAlternativa } from '../componentes/TabelaAlternativa'
import { TermoExplicado } from '../componentes/TermoExplicado'
import { DOIS_JEITOS, INFLACAO_X_CAMBIO, NUMERO_INDICE, O_QUE_E_IPCA } from '../conteudo/glossario'
import { mesAbreviado } from '../formatacao/datas'
import { formatarNumero, formatarPercentual, sinal } from '../formatacao/numeros'
import { parametrosDoPeriodo, type Periodo, type Resumo, type Serie } from '../servicos/api'
import { useIndicador, useResumo, useSerie } from '../servicos/consultas'
import estilos from './VisaoGeral.module.css'

const CODIGO = 'ipca'

// A biblioteca de gráficos é grande: baixada à parte para o cartão e o título aparecerem
// antes (SC-006).
const Grafico = lazy(() => import('../componentes/Grafico').then((m) => ({ default: m.Grafico })))

function direcaoIpca(acumulado: string) {
  const s = sinal(acumulado)
  if (s > 0) return { sinal: s, texto: 'Alta de preços: o real comprou menos.' }
  if (s < 0) return { sinal: s, texto: 'Queda de preços (deflação): o real comprou mais.' }
  return { sinal: s, texto: 'Preços estáveis no período.' }
}

function Explicacoes() {
  return (
    <>
      <TermoExplicado titulo={O_QUE_E_IPCA.titulo}>
        {O_QUE_E_IPCA.paragrafos.map((p) => (
          <p key={p}>{p}</p>
        ))}
      </TermoExplicado>
      <TermoExplicado titulo={INFLACAO_X_CAMBIO.titulo}>
        {INFLACAO_X_CAMBIO.paragrafos.map((p) => (
          <p key={p}>{p}</p>
        ))}
      </TermoExplicado>
    </>
  )
}

function CartaoIpca({ resumo, serie }: { resumo: Resumo; serie?: Serie }) {
  if (resumo.situacao === 'sem_dados') return <EstadoDados estado={{ tipo: 'sem_dados' }} />
  if (resumo.situacao === 'lacuna') {
    return <EstadoDados estado={{ tipo: 'lacuna', meses: resumo.meses_ausentes ?? [] }} />
  }
  const acumulado = resumo.acumulado_percentual ?? '0'
  return (
    <CartaoIndicador
      titulo="Inflação acumulada · IPCA"
      indicador={resumo.indicador}
      periodo={resumo.periodo}
      valor={formatarPercentual(acumulado, 2, true).replace('%', '')}
      sufixo={`% no período (${resumo.meses_considerados} meses)`}
      direcao={direcaoIpca(acumulado)}
      explicacao={<Explicacoes />}
      miniatura={
        serie?.derivadas?.acumulado_no_periodo && (
          <Miniatura valores={serie.derivadas.acumulado_no_periodo} />
        )
      }
    />
  )
}

/** Linha pequena do acumulado (decorativa: os valores estão no gráfico e na tabela). */
function Miniatura({ valores }: { valores: (string | null)[] }) {
  const numeros = valores.map((v) => (v === null ? null : Number(v)))
  const validos = numeros.filter((v): v is number => v !== null)
  if (validos.length < 2) return null
  const min = Math.min(0, ...validos)
  const max = Math.max(...validos)
  const pontos = numeros
    .map((v, i) =>
      v === null
        ? null
        : `${(i / (numeros.length - 1)) * 200},${50 - ((v - min) / (max - min || 1)) * 46}`,
    )
    .filter(Boolean)
    .join(' ')
  return (
    <svg
      viewBox="0 0 200 52"
      width="100%"
      height="100%"
      preserveAspectRatio="none"
      focusable="false"
    >
      <polyline
        points={pontos}
        fill="none"
        stroke="var(--serie-ipca)"
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  )
}

function Historico({ serie, periodo }: { serie: Serie; periodo: Periodo }) {
  if (!serie.observacoes.length) return <EstadoDados estado={{ tipo: 'sem_dados' }} />
  const datas = serie.observacoes.map((o) => o.data)
  const acumulado = serie.derivadas?.acumulado_no_periodo ?? []
  const indice = serie.derivadas?.numero_indice
  const ausentes = serie.observacoes.filter((o) => o.situacao === 'ausente')
  const ultimo = acumulado.at(-1)

  const linhas = serie.observacoes.map((o, i) => [
    mesAbreviado(o.data),
    o.valor === null ? 'sem dado' : formatarNumero(o.valor, 2),
    acumulado[i] == null ? 'sem dado' : formatarNumero(acumulado[i]!, 2),
    ...(indice ? [indice[i] == null ? 'sem dado' : formatarNumero(indice[i]!, 2)] : []),
  ])

  return (
    <section className={estilos.historico} aria-label="Histórico do período">
      <Suspense
        fallback={<EstadoDados estado={{ tipo: 'carregando', rotulo: 'gráfico do IPCA' }} />}
      >
        <Grafico
          titulo={
            <>
              Histórico <strong>do período</strong>
            </>
          }
          subtitulo={
            <>
              Inflação acumulada (IPCA) · unidade: <strong>% acumulado no período</strong>
            </>
          }
          datas={datas}
          series={[
            {
              chave: 'acumulado',
              rotulo: 'IPCA acumulado',
              cor: 'var(--serie-ipca)',
              traco: 'continuo',
              valores: acumulado,
              preencher: true,
            },
          ]}
          unidade="%"
          casas={2}
          descricao={`Gráfico da inflação acumulada pelo IPCA de ${textoPeriodo(serie.periodo)}${
            ultimo ? `, terminando em ${formatarNumero(ultimo, 2)}%` : ''
          }. Os valores mês a mês estão na tabela a seguir.`}
          rodape={
            <>
              <span>
                Fonte: {textoFonte(serie.indicador)} · Período: {textoPeriodo(serie.periodo)} ·
                Atualização: {textoAtualizacao(serie.indicador)}
              </span>
              {ausentes.length > 0 && (
                <span>
                  Linha interrompida: sem dado em{' '}
                  {ausentes.map((o) => mesAbreviado(o.data)).join(', ')}. O acumulado não é
                  calculado depois de um mês ausente.
                </span>
              )}
            </>
          }
          acoes={<BotaoCsv codigo={CODIGO} parametros={parametrosDoPeriodo(periodo)} />}
        />
      </Suspense>
      <TabelaAlternativa
        legenda={`IPCA mês a mês, ${textoPeriodo(serie.periodo)}. Unidade: ${serie.indicador.unidade} (variação mensal) e % acumulado no período. Fonte: ${textoFonte(serie.indicador)}. Atualização: ${textoAtualizacao(serie.indicador)}.`}
        colunas={[
          { titulo: 'Mês' },
          { titulo: 'Variação mensal (%)', numerica: true },
          { titulo: 'Acumulado no período (%)', numerica: true },
          ...(indice ? [{ titulo: 'Número-índice (dez/1993 = 100)', numerica: true }] : []),
        ]}
        linhas={linhas}
      />
      {indice && (
        <TermoExplicado titulo={NUMERO_INDICE.titulo}>
          <p>{NUMERO_INDICE.paragrafos[0]}</p>
        </TermoExplicado>
      )}
    </section>
  )
}

function ResumoTexto({ resumo }: { resumo: Resumo }) {
  if (resumo.situacao !== 'ok' || !resumo.acumulado_percentual) return null
  const s = sinal(resumo.acumulado_percentual)
  const verbo = s > 0 ? 'subiram' : s < 0 ? 'caíram' : 'ficaram estáveis'
  return (
    <section className={`cartao ${estilos.resumo}`} aria-labelledby="titulo-resumo">
      <p className="rotulo-apoio">Resumo do período</p>
      <h2 id="titulo-resumo" className={`editorial ${estilos.resumoTitulo}`}>
        O que aconteceu com os preços no período escolhido
      </h2>
      <p>
        Os preços medidos pelo IPCA {verbo}{' '}
        {s !== 0 && (
          <strong>{formatarPercentual(resumo.acumulado_percentual.replace('-', ''))}</strong>
        )}{' '}
        no acumulado de {textoPeriodo(resumo.periodo)} ({resumo.meses_considerados} meses).
      </p>
      <p>
        Para ver quanto um valor precisaria hoje para comprar o mesmo que antes, use o{' '}
        <Link to="/poder-de-compra">simulador de poder de compra</Link>.
      </p>
      <p className="rotulo-apoio">Texto gerado a partir dos dados oficiais do IBGE</p>
    </section>
  )
}

export function VisaoGeral() {
  useTitulo('Painel de indicadores')
  const [periodo, setPeriodo] = useState<Periodo>({ tipo: 'atalho', atalho: '5a' })
  const resumo = useResumo(CODIGO, periodo)
  const serie = useSerie(CODIGO, periodo)
  // Metadados do indicador: distinguem "sem versão por falha" de "ainda não integrado".
  const metadados = useIndicador(CODIGO)

  const estadoBloqueante = (consulta: typeof resumo | typeof serie): EstadoBloqueante | null => {
    if (consulta.isPending) return { tipo: 'carregando', rotulo: 'IPCA' }
    if (consulta.isError) {
      return estadoDoErro(consulta.error, () => void consulta.refetch(), metadados.data)
    }
    return null
  }

  const estadoResumo = estadoBloqueante(resumo)
  const estadoSerie = estadoBloqueante(serie)
  const indicador = resumo.data?.indicador ?? serie.data?.indicador

  return (
    <>
      <CabecalhoPagina
        etiqueta="Visão geral"
        tituloFino="Painel de"
        tituloForte="indicadores"
        descricao="Os principais números sobre o valor do real em um só lugar. Escolha um período para ver como cada indicador se comportou."
      />
      <div className={`conteiner ${estilos.pagina}`}>
        <SeletorPeriodo
          periodo={periodo}
          aoMudar={setPeriodo}
          referencia={resumo.data?.periodo}
          limites={indicador?.periodo_disponivel}
        />
        {resumo.isFetching && !resumo.isPending && (
          <p className="somente-leitor-de-tela" role="status">
            Atualizando os dados do período…
          </p>
        )}

        <div className={estilos.cartoes}>
          {estadoResumo ? (
            <EstadoDados estado={estadoResumo} />
          ) : (
            resumo.data && <CartaoIpca resumo={resumo.data} serie={serie.data} />
          )}
          <div className={`cartao ${estilos.emBreve}`}>
            <p className="rotulo">Dólar, Selic e quantidade de moeda</p>
            <p className="texto-apoio">
              Os demais indicadores do painel chegam na próxima entrega, com a mesma transparência
              de fonte, unidade e período.
            </p>
            <Link to="/sobre" className="botao">
              Ver o catálogo de dados
            </Link>
          </div>
        </div>

        {indicador?.atualizacao.situacao === 'falha_atualizacao' && !estadoSerie && (
          <AvisoFalhaAtualizacao mensagem={indicador.atualizacao.mensagem} />
        )}

        {estadoSerie ? (
          <EstadoDados estado={estadoSerie} />
        ) : (
          serie.data && <Historico serie={serie.data} periodo={periodo} />
        )}

        <div className={estilos.duasColunas}>
          {resumo.data && <ResumoTexto resumo={resumo.data} />}
          <section className={`cartao ${estilos.doisJeitos}`} aria-labelledby="titulo-dois-jeitos">
            <h2 id="titulo-dois-jeitos" className={`titulo-composto ${estilos.doisJeitosTitulo}`}>
              Dois jeitos de o real <strong>perder valor</strong>
            </h2>
            <ol>
              {DOIS_JEITOS.map((item) => (
                <li key={item.numero}>
                  <span className={`editorial ${estilos.numero}`} aria-hidden="true">
                    {item.numero}
                  </span>
                  <div>
                    <h3 className="rotulo">{item.titulo}</h3>
                    <p>{item.texto}</p>
                  </div>
                </li>
              ))}
            </ol>
            <p className="texto-apoio">
              Os dois movimentos podem acontecer juntos, mas não são a mesma coisa e não andam
              sempre no mesmo ritmo.
            </p>
          </section>
        </div>
      </div>
    </>
  )
}
