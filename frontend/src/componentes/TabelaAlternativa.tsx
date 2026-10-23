import estilos from './TabelaAlternativa.module.css'

export interface ColunaTabela {
  titulo: string
  numerica?: boolean
}

/** Alternativa em tabela para todo gráfico (FR-021). Mesmos valores do gráfico. */
export function TabelaAlternativa({
  legenda,
  colunas,
  linhas,
  aberta = false,
}: {
  legenda: string
  colunas: ColunaTabela[]
  linhas: string[][]
  aberta?: boolean
}) {
  return (
    <details className={estilos.detalhes} open={aberta}>
      <summary>Ver valores em tabela</summary>
      {/* Região rolável precisa ser alcançável pelo teclado (WCAG 2.1.1, regra axe
          scrollable-region-focusable). */}
      {/* eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex */}
      <div className={estilos.rolagem} tabIndex={0} role="region" aria-label={legenda}>
        <table className={estilos.tabela}>
          <caption>{legenda}</caption>
          <thead>
            <tr>
              {colunas.map((coluna) => (
                <th
                  key={coluna.titulo}
                  scope="col"
                  className={coluna.numerica ? estilos.numerica : ''}
                >
                  {coluna.titulo}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {linhas.map((linha) => (
              <tr key={linha[0]}>
                {linha.map((celula, i) =>
                  i === 0 ? (
                    <th key={i} scope="row">
                      {celula}
                    </th>
                  ) : (
                    <td key={i} className={colunas[i]?.numerica ? estilos.numerica : ''}>
                      {celula}
                    </td>
                  ),
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  )
}
