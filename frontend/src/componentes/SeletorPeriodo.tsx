import { useId, useRef, useState, type FormEvent } from 'react'
import { mesAbreviado, paraMesIso } from '../formatacao/datas'
import type { Periodo, PeriodoReferencia } from '../servicos/api'
import estilos from './SeletorPeriodo.module.css'

const ATALHOS = [
  { atalho: '12m', rotulo: '12 meses' },
  { atalho: '3a', rotulo: '3 anos' },
  { atalho: '5a', rotulo: '5 anos' },
  { atalho: '10a', rotulo: '10 anos' },
] as const

interface Props {
  periodo: Periodo
  aoMudar: (periodo: Periodo) => void
  /** Primeiro e último mês disponíveis ("AAAA-MM-DD"), para limitar o período personalizado. */
  limites?: { inicio: string; fim: string } | null
  referencia?: PeriodoReferencia
}

/** Seleção de período (FR-020): atalhos ou mês/ano inicial e final. */
export function SeletorPeriodo({ periodo, aoMudar, limites, referencia }: Props) {
  const id = useId()
  const [abertoPersonalizado, setAbertoPersonalizado] = useState(periodo.tipo === 'personalizado')
  const [inicio, setInicio] = useState(
    periodo.tipo === 'personalizado'
      ? periodo.inicio
      : referencia
        ? paraMesIso(referencia.inicio)
        : '',
  )
  const [fim, setFim] = useState(
    periodo.tipo === 'personalizado'
      ? periodo.fim
      : referencia
        ? paraMesIso(referencia.fim_utilizado)
        : '',
  )
  const [erro, setErro] = useState<{ campo: 'inicio' | 'fim'; mensagem: string } | null>(null)
  const refInicio = useRef<HTMLInputElement>(null)
  const refFim = useRef<HTMLInputElement>(null)

  const falhar = (campo: 'inicio' | 'fim', mensagem: string) => {
    setErro({ campo, mensagem })
    ;(campo === 'inicio' ? refInicio : refFim).current?.focus()
  }

  const aplicar = (evento: FormEvent) => {
    evento.preventDefault()
    if (!inicio) return falhar('inicio', 'Informe o mês inicial.')
    if (!fim) return falhar('fim', 'Informe o mês final.')
    if (inicio > fim) {
      return falhar('inicio', 'A data inicial deve ser anterior ou igual à data final.')
    }
    if (limites && inicio < paraMesIso(limites.inicio)) {
      return falhar(
        'inicio',
        `Os dados estão disponíveis a partir de ${mesAbreviado(limites.inicio)}.`,
      )
    }
    setErro(null)
    aoMudar({ tipo: 'personalizado', inicio, fim })
  }

  const ativo = (atalho: string) => periodo.tipo === 'atalho' && periodo.atalho === atalho

  return (
    <div className={`cartao ${estilos.seletor}`}>
      <div className={estilos.linha}>
        <span className="rotulo-apoio" id={`${id}-rotulo`}>
          Período
        </span>
        <div className={estilos.botoes} role="group" aria-labelledby={`${id}-rotulo`}>
          {ATALHOS.map(({ atalho, rotulo }) => (
            <button
              key={atalho}
              type="button"
              className={`${estilos.opcao} ${ativo(atalho) ? estilos.ativo : ''}`}
              aria-pressed={ativo(atalho)}
              onClick={() => {
                setAbertoPersonalizado(false)
                setErro(null)
                aoMudar({ tipo: 'atalho', atalho })
              }}
            >
              {rotulo}
            </button>
          ))}
          <button
            type="button"
            className={`${estilos.opcao} ${periodo.tipo === 'personalizado' ? estilos.ativo : ''}`}
            aria-pressed={periodo.tipo === 'personalizado'}
            aria-expanded={abertoPersonalizado}
            aria-controls={`${id}-personalizado`}
            onClick={() => setAbertoPersonalizado((aberto) => !aberto)}
          >
            Personalizado
          </button>
        </div>
        {referencia && (
          <p className={estilos.referencia} aria-live="polite">
            Referência:{' '}
            <strong>
              {mesAbreviado(referencia.inicio)} a {mesAbreviado(referencia.fim_utilizado)}
            </strong>
          </p>
        )}
      </div>

      {abertoPersonalizado && (
        <form
          id={`${id}-personalizado`}
          className={estilos.personalizado}
          onSubmit={aplicar}
          noValidate
        >
          <div className={estilos.campo}>
            <label htmlFor={`${id}-inicio`} className="rotulo-apoio">
              De (mês/ano)
            </label>
            <input
              ref={refInicio}
              id={`${id}-inicio`}
              type="month"
              value={inicio}
              min={limites ? paraMesIso(limites.inicio) : undefined}
              max={limites ? paraMesIso(limites.fim) : undefined}
              onChange={(e) => setInicio(e.target.value)}
              aria-invalid={erro?.campo === 'inicio'}
              aria-describedby={erro?.campo === 'inicio' ? `${id}-erro` : undefined}
            />
          </div>
          <div className={estilos.campo}>
            <label htmlFor={`${id}-fim`} className="rotulo-apoio">
              Até (mês/ano)
            </label>
            <input
              ref={refFim}
              id={`${id}-fim`}
              type="month"
              value={fim}
              min={limites ? paraMesIso(limites.inicio) : undefined}
              onChange={(e) => setFim(e.target.value)}
              aria-invalid={erro?.campo === 'fim'}
              aria-describedby={erro?.campo === 'fim' ? `${id}-erro` : undefined}
            />
          </div>
          <button type="submit" className="botao botao-contorno">
            Aplicar período
          </button>
          {erro && (
            <p id={`${id}-erro`} className={estilos.erro} role="alert">
              {erro.mensagem}
            </p>
          )}
        </form>
      )}
    </div>
  )
}
