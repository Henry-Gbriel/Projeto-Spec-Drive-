import { EtiquetaSecao } from '../../componentes/Selo'
import { TermoExplicado } from '../../componentes/TermoExplicado'
import { O_QUE_E_IPCA } from '../../conteudo/glossario'
import { mesAbreviado } from '../../formatacao/datas'
import { arredondarTexto, formatarMoeda, formatarNumero } from '../../formatacao/numeros'
import type { Simulacao } from '../../servicos/api'
import estilos from './PoderDeCompra.module.css'

/** Metodologia passo a passo, com os números reais da simulação (FR-027). */
export function ComoFunciona({ simulacao }: { simulacao: Simulacao | undefined }) {
  const exemplos = (simulacao?.passos ?? []).filter((p) => p.valor !== null).slice(0, 2)
  const fator = simulacao ? formatarNumero(simulacao.fator, 4) : null
  const fatorExato = simulacao && arredondarTexto(simulacao.fator, 4) !== simulacao.fator

  return (
    <section className={estilos.metodologia} aria-labelledby="titulo-como-funciona">
      <div className={estilos.metodologiaTexto}>
        <EtiquetaSecao clara>Metodologia</EtiquetaSecao>
        <h2 id="titulo-como-funciona" className="titulo-composto">
          Como o cálculo <strong>funciona</strong>
        </h2>
        <p>
          Pense na inflação de cada mês como um pequeno aumento de preços. Para saber o total, os
          aumentos são encadeados: o de um mês incide sobre os preços já reajustados do mês
          anterior. O mês inicial e o mês final entram no cálculo.
        </p>
        <TermoExplicado titulo={O_QUE_E_IPCA.titulo} clara>
          {O_QUE_E_IPCA.paragrafos.map((p) => (
            <p key={p}>{p}</p>
          ))}
        </TermoExplicado>
      </div>
      <ol className={estilos.passos}>
        <li>
          <span className="editorial" aria-hidden="true">
            01
          </span>
          <p>
            {simulacao
              ? `Pegamos o IPCA de cada mês entre ${mesAbreviado(simulacao.periodo.inicio)} e ${mesAbreviado(simulacao.periodo.fim_utilizado)} (${simulacao.meses_considerados} ${simulacao.meses_considerados === 1 ? 'mês' : 'meses'}).`
              : 'Pegamos o IPCA de cada mês do período escolhido.'}
          </p>
        </li>
        <li>
          <span className="editorial" aria-hidden="true">
            02
          </span>
          <p>
            Multiplicamos os fatores mensais
            {exemplos.length > 0 &&
              `, como ${exemplos.map((p) => `(1 + ${formatarNumero(p.valor!, 2)}%)`).join(' × ')}${simulacao!.meses_considerados > exemplos.length ? ' × …' : ''}`}
            , e chegamos ao fator do período
            {fator ? (
              <>
                :{' '}
                <strong>
                  {fator}
                  {fatorExato ? '…' : ''}
                </strong>
              </>
            ) : (
              ''
            )}
            {fatorExato ? '' : '.'}
          </p>
        </li>
        <li>
          <span className="editorial" aria-hidden="true">
            03
          </span>
          <p>
            Multiplicamos o valor informado pelo fator
            {simulacao && (
              <>
                : {formatarMoeda(simulacao.valor_informado)} × {fator}
                {fatorExato ? '…' : ''} ={' '}
                <strong>{formatarMoeda(simulacao.valor_corrigido)}</strong>
              </>
            )}
            .
          </p>
        </li>
      </ol>
    </section>
  )
}
