import { AvisoFalhaAtualizacao, AvisoNaoPublicado } from '../../componentes/EstadoDados'
import { Icone } from '../../componentes/Icone'
import { DIFERENCA_NOMINAL } from '../../conteudo/glossario'
import { mesAbreviado } from '../../formatacao/datas'
import { formatarMoeda, formatarPercentual, sinal } from '../../formatacao/numeros'
import type { Simulacao } from '../../servicos/api'
import estilos from './PoderDeCompra.module.css'

export function ResultadoSimulacao({ simulacao }: { simulacao: Simulacao }) {
  const { periodo, indicador } = simulacao
  const inicio = mesAbreviado(periodo.inicio)
  const fim = mesAbreviado(periodo.fim_utilizado)
  const informado = formatarMoeda(simulacao.valor_informado)
  const corrigido = formatarMoeda(simulacao.valor_corrigido)
  const sinalInflacao = sinal(simulacao.inflacao_acumulada_percentual)

  // Proporção das barras: apenas visual (os números exibidos vêm da API).
  const razao = Number(simulacao.valor_informado) / Number(simulacao.valor_corrigido)
  const larguraNominal = sinalInflacao >= 0 ? `${Math.max(razao * 100, 2)}%` : '100%'
  const larguraCorrigida = sinalInflacao >= 0 ? '100%' : `${Math.max(100 / razao, 2)}%`

  return (
    <div className={estilos.resultado}>
      {periodo.aviso_nao_publicado && <AvisoNaoPublicado texto={periodo.aviso_nao_publicado} />}
      {indicador.atualizacao.situacao === 'falha_atualizacao' && (
        <AvisoFalhaAtualizacao mensagem={indicador.atualizacao.mensagem} />
      )}

      <section className={estilos.destaque} aria-label="Resultado">
        <p>
          Para manter o poder de compra de <strong>{informado}</strong> de {inicio}, em {fim} você
          precisaria de
        </p>
        <p className={estilos.valorCorrigido}>{corrigido}</p>
        <p className="rotulo-apoio">Valor equivalente corrigido pelo IPCA</p>
      </section>

      <div className={estilos.indicadores}>
        <div className="cartao">
          <p className="rotulo-apoio">Inflação acumulada</p>
          <p className={estilos.numeroMedio}>
            {sinalInflacao !== 0 && (
              <Icone nome={sinalInflacao > 0 ? 'seta-cima' : 'seta-baixo'} tamanho={20} />
            )}
            {formatarPercentual(simulacao.inflacao_acumulada_percentual)}
          </p>
          <p className="texto-apoio">
            {simulacao.meses_considerados} {simulacao.meses_considerados === 1 ? 'mês' : 'meses'} de
            IPCA ({inicio} a {fim})
          </p>
        </div>
        <div className="cartao">
          <p className="rotulo-apoio">Mudança no poder de compra</p>
          <p className={estilos.numeroMedio}>
            {sinal(simulacao.variacao_poder_compra_percentual) !== 0 && (
              <Icone
                nome={
                  sinal(simulacao.variacao_poder_compra_percentual) < 0 ? 'seta-baixo' : 'seta-cima'
                }
                tamanho={20}
              />
            )}
            {formatarPercentual(simulacao.variacao_poder_compra_percentual, 2, true)}
          </p>
          <p className="texto-apoio">
            Os {informado} originais passaram a comprar o equivalente a{' '}
            {formatarMoeda(simulacao.equivalente_no_inicio)} de {inicio}.
          </p>
        </div>
      </div>

      <section className={`cartao ${estilos.comparacao}`} aria-labelledby="titulo-comparacao">
        <h2 id="titulo-comparacao" className="rotulo">
          Quantia nominal × valor que mantém o poder de compra
        </h2>
        <div className={estilos.barraLinha}>
          <p>
            <span>Quantia nominal informada</span> <strong>{informado}</strong>
          </p>
          <div className={estilos.trilho} aria-hidden="true">
            <div className={estilos.barraNominal} style={{ width: larguraNominal }} />
          </div>
        </div>
        <div className={estilos.barraLinha}>
          <p>
            <span>Necessário para comprar o mesmo</span>{' '}
            <strong className="destaque-amarelo">{corrigido}</strong>
          </p>
          <div className={estilos.trilho} aria-hidden="true">
            <div className={estilos.barraCorrigida} style={{ width: larguraCorrigida }} />
          </div>
        </div>
        <p className="texto-apoio">
          A diferença de{' '}
          <strong>{formatarMoeda(simulacao.diferenca_nominal.replace('-', ''))}</strong>{' '}
          {DIFERENCA_NOMINAL.replace('A diferença ', '')}
        </p>
      </section>
    </div>
  )
}
