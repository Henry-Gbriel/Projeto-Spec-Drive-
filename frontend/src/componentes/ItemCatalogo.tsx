import { mesAbreviado } from '../formatacao/datas'
import type { Indicador } from '../servicos/api'
import { BotaoCsv } from './BotaoCsv'
import estilos from './ItemCatalogo.module.css'
import { textoAtualizacao } from './Metadados'
import { Selo } from './Selo'

const FREQUENCIAS: Record<Indicador['frequencia'], string> = {
  diaria: 'Diária',
  mensal: 'Mensal',
  anual: 'Anual',
  por_reuniao: 'A cada reunião do Copom',
}

/** Entrada do catálogo de dados (US8, FR-042). */
export function ItemCatalogo({ indicador }: { indicador: Indicador }) {
  const integrado = indicador.periodo_disponivel !== null
  const periodo = indicador.periodo_disponivel
    ? `${mesAbreviado(indicador.periodo_disponivel.inicio)} a ${mesAbreviado(indicador.periodo_disponivel.fim)}`
    : 'A confirmar na primeira coleta'

  return (
    <li className={`cartao ${estilos.item}`}>
      <div className={estilos.topo}>
        <h3 className="rotulo">{indicador.nome}</h3>
        <Selo tipo={indicador.atualizacao.situacao} />
      </div>
      <p className={estilos.descricao}>{indicador.descricao}</p>
      <dl className="metadados">
        <dt>Fonte oficial</dt>
        <dd>
          <a
            href={indicador.fonte.url_origem}
            target="_blank"
            rel="noopener noreferrer"
            className={estilos.link}
          >
            {indicador.fonte.instituicao}
            <span className="somente-leitor-de-tela"> (abre em nova aba)</span>
          </a>
          {indicador.fonte.codigo_serie && (
            <span className="texto-apoio"> · {indicador.fonte.codigo_serie}</span>
          )}
        </dd>
        <dt>Unidade</dt>
        <dd>{indicador.unidade}</dd>
        <dt>Frequência</dt>
        <dd>{FREQUENCIAS[indicador.frequencia]}</dd>
        <dt>Período</dt>
        <dd>{periodo}</dd>
        <dt>Atualização</dt>
        <dd>{textoAtualizacao(indicador)}</dd>
      </dl>
      {indicador.atualizacao.situacao === 'falha_atualizacao' && indicador.atualizacao.mensagem && (
        <p className={estilos.falha}>{indicador.atualizacao.mensagem}</p>
      )}
      <div className={estilos.rodape}>
        <BotaoCsv codigo={indicador.codigo} disponivel={integrado} rotulo="Baixar CSV" />
      </div>
    </li>
  )
}
