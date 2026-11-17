import { dataHora, mesAbreviado } from '../formatacao/datas'
import type { Indicador, PeriodoReferencia } from '../servicos/api'

/** Texto de atualização exibido ao público (Princípio III). */
export function textoAtualizacao(indicador: Indicador): string {
  const valida = indicador.atualizacao.ultima_atualizacao_valida
  return valida ? dataHora(valida) : 'Ainda não há atualização registrada'
}

export function textoPeriodo(periodo: PeriodoReferencia): string {
  return `${mesAbreviado(periodo.inicio)} a ${mesAbreviado(periodo.fim_utilizado)}`
}

export function textoFonte(indicador: Indicador): string {
  const { instituicao, codigo_serie } = indicador.fonte
  return codigo_serie ? `${instituicao} (${codigo_serie})` : instituicao
}

/** Período / Fonte / Unidade / Atualização — sempre visíveis junto ao dado. */
export function ListaMetadados({
  indicador,
  periodo,
}: {
  indicador: Indicador
  periodo?: PeriodoReferencia
}) {
  return (
    <dl className="metadados">
      {periodo && (
        <>
          <dt>Período</dt>
          <dd>{textoPeriodo(periodo)}</dd>
        </>
      )}
      <dt>Fonte</dt>
      <dd>
        <a href={indicador.fonte.url_origem} target="_blank" rel="noopener noreferrer">
          {textoFonte(indicador)}
          <span className="somente-leitor-de-tela"> (abre em nova aba)</span>
        </a>
      </dd>
      <dt>Unidade</dt>
      <dd>{indicador.unidade}</dd>
      <dt>Atualização</dt>
      <dd>{textoAtualizacao(indicador)}</dd>
    </dl>
  )
}

/** Verdadeiro se o indicador traz os metadados obrigatórios para exibir números. */
export function metadadosCompletos(indicador: Indicador | undefined): indicador is Indicador {
  return Boolean(
    indicador?.fonte?.instituicao && indicador.unidade && indicador.atualizacao?.situacao,
  )
}
