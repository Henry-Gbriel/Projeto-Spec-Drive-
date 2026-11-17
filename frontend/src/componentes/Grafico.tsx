import type { ReactNode } from 'react'
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
  type TooltipValueType,
} from 'recharts'
import { mesAbreviado } from '../formatacao/datas'
import { formatarNumero } from '../formatacao/numeros'
import estilos from './Grafico.module.css'

export interface SerieGrafico {
  chave: string
  rotulo: string
  /** Variável CSS da cor (ex.: "var(--serie-ipca)"). */
  cor: string
  /** Traço: contínuo, tracejado ou pontilhado — a cor nunca é a única diferença. */
  traco: 'continuo' | 'tracejado' | 'pontilhado' | 'traco-ponto'
  /** Valores em texto (da API); null = ausente: a linha é interrompida. */
  valores: (string | null)[]
  preencher?: boolean
}

const TRACOS: Record<SerieGrafico['traco'], string | undefined> = {
  continuo: undefined,
  tracejado: '7 5',
  pontilhado: '2 4',
  'traco-ponto': '8 4 2 4',
}

interface Props {
  titulo: ReactNode
  subtitulo: ReactNode
  datas: string[]
  series: SerieGrafico[]
  unidade: string
  casas: number
  rodape: ReactNode
  /** Resumo textual do gráfico para tecnologias assistivas. */
  descricao: string
  altura?: number
  acoes?: ReactNode
}

/**
 * Gráfico de linhas com título, unidade visível, eixos rotulados em pt-BR e leitura de ponto
 * por ponteiro, toque e teclado (camada de acessibilidade do Recharts). Os números
 * exibidos vêm da API; a conversão para número serve apenas para desenhar.
 */
export function Grafico(props: Props) {
  const {
    titulo,
    subtitulo,
    datas,
    series,
    unidade,
    casas,
    rodape,
    descricao,
    altura = 320,
  } = props
  const dados = datas.map((data, i) => {
    const ponto: Record<string, string | number | null> = { data }
    for (const serie of series) {
      const valor = serie.valores[i]
      ponto[serie.chave] = valor === null || valor === undefined ? null : Number(valor)
      ponto[`${serie.chave}__texto`] = valor ?? null
    }
    return ponto
  })

  const Dica = ({
    active,
    payload,
    label,
  }: TooltipContentProps<TooltipValueType, string | number>) => {
    if (!active || !payload?.length) return null
    const ponto = payload[0]?.payload as Record<string, string | null>
    return (
      <div className={estilos.dica}>
        <p className="rotulo-apoio">{mesAbreviado(String(label))}</p>
        {series.map((serie) => {
          const texto = ponto[`${serie.chave}__texto`]
          return (
            <p key={serie.chave}>
              {series.length > 1 && `${serie.rotulo}: `}
              <strong>{texto ? `${formatarNumero(texto, casas)} ${unidade}` : 'sem dado'}</strong>
            </p>
          )
        })}
      </div>
    )
  }

  return (
    <figure className={`cartao ${estilos.figura}`}>
      <figcaption className={estilos.legenda}>
        <div>
          <h2 className={`titulo-composto ${estilos.titulo}`}>{titulo}</h2>
          <p className={estilos.subtitulo}>{subtitulo}</p>
        </div>
        {props.acoes}
      </figcaption>
      {series.length > 1 && (
        <ul className={estilos.legendaSeries}>
          {series.map((serie) => (
            <li key={serie.chave}>
              <svg width="28" height="8" aria-hidden="true">
                <line
                  x1="0"
                  y1="4"
                  x2="28"
                  y2="4"
                  stroke={serie.cor}
                  strokeWidth="2.5"
                  strokeDasharray={TRACOS[serie.traco]}
                />
              </svg>
              {serie.rotulo}
            </li>
          ))}
        </ul>
      )}
      <p className="somente-leitor-de-tela">{descricao}</p>
      <div className={estilos.area} style={{ height: altura }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={dados}
            margin={{ top: 8, right: 12, bottom: 0, left: 0 }}
            accessibilityLayer
            title={typeof titulo === 'string' ? titulo : undefined}
          >
            <CartesianGrid stroke="var(--cor-linha)" vertical={false} />
            <XAxis
              dataKey="data"
              tickFormatter={(data: string) => mesAbreviado(data).toUpperCase()}
              tick={{ fill: 'var(--cor-texto-apoio)', fontSize: 11 }}
              stroke="var(--cor-linha-forte)"
              minTickGap={32}
            />
            <YAxis
              width={64}
              tickFormatter={(valor: number) => formatarNumero(String(valor), Math.min(casas, 1))}
              tick={{ fill: 'var(--cor-texto-apoio)', fontSize: 11 }}
              stroke="var(--cor-linha-forte)"
              domain={['auto', 'auto']}
            />
            <Tooltip
              content={Dica}
              cursor={{ stroke: 'var(--cor-texto-apoio)', strokeDasharray: '3 3' }}
            />
            {series.map((serie) =>
              serie.preencher ? (
                <Area
                  key={serie.chave}
                  type="monotone"
                  dataKey={serie.chave}
                  name={serie.rotulo}
                  stroke={serie.cor}
                  strokeWidth={2.5}
                  strokeDasharray={TRACOS[serie.traco]}
                  fill={serie.cor}
                  fillOpacity={0.12}
                  connectNulls={false}
                  isAnimationActive={false}
                  dot={false}
                  activeDot={{ r: 4, stroke: 'var(--cor-fundo)', fill: serie.cor }}
                />
              ) : (
                <Line
                  key={serie.chave}
                  type="monotone"
                  dataKey={serie.chave}
                  name={serie.rotulo}
                  stroke={serie.cor}
                  strokeWidth={2.5}
                  strokeDasharray={TRACOS[serie.traco]}
                  connectNulls={false}
                  isAnimationActive={false}
                  dot={false}
                  activeDot={{ r: 4, stroke: 'var(--cor-fundo)', fill: serie.cor }}
                />
              ),
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className={estilos.rodape}>{rodape}</div>
    </figure>
  )
}
