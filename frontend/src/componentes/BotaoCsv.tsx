import { montarUrl } from '../servicos/api'
import { Icone } from './Icone'

/** Download da série em CSV (FR-030). Desabilitado quando o indicador não está integrado. */
export function BotaoCsv({
  codigo,
  parametros = {},
  disponivel = true,
  rotulo = 'Baixar CSV',
}: {
  codigo: string
  parametros?: Record<string, string>
  disponivel?: boolean
  rotulo?: string
}) {
  if (!disponivel) {
    const idAviso = `csv-indisponivel-${codigo}`
    return (
      <div>
        <button type="button" className="botao" aria-disabled="true" aria-describedby={idAviso}>
          <Icone nome="download" /> {rotulo}
        </button>
        <p
          id={idAviso}
          className="texto-apoio"
          style={{ fontSize: '0.75rem', marginTop: '0.4rem' }}
        >
          Disponível após a integração com a fonte.
        </p>
      </div>
    )
  }
  return (
    <a
      className="botao"
      href={montarUrl(`/v1/indicadores/${codigo}/serie.csv`, parametros)}
      download
    >
      <Icone nome="download" /> {rotulo}
    </a>
  )
}
