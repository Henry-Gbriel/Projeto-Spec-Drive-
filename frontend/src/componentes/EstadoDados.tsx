/**
 * Estados dos dados (contracts/ui-estados.md, FR-040, FR-041).
 * Todo estado é comunicado por texto e ícone, nunca só por cor.
 */
import { useEffect, useRef, useState } from 'react'
import { mesAbreviado } from '../formatacao/datas'
import { ErroDaApi, type Indicador } from '../servicos/api'
import estilos from './EstadoDados.module.css'
import { Icone } from './Icone'

export type EstadoBloqueante =
  | { tipo: 'carregando'; rotulo: string }
  | { tipo: 'sem_dados' }
  | { tipo: 'lacuna'; meses: string[] }
  | { tipo: 'erro'; mensagem?: string; tentarNovamente?: () => void }
  | { tipo: 'nao_integrado'; mensagem?: string }
  | { tipo: 'falha_sem_versao'; mensagem?: string | null }

export function EstadoDados({ estado }: { estado: EstadoBloqueante }) {
  switch (estado.tipo) {
    case 'carregando':
      return <Carregando rotulo={estado.rotulo} />
    case 'sem_dados':
      return (
        <div className={`${estilos.caixa} ${estilos.sem_dados}`} role="status">
          <Icone nome="vazio" tamanho={28} />
          <p className={estilos.titulo}>Sem dados</p>
          <p>Não há valores para o período escolhido.</p>
        </div>
      )
    case 'lacuna':
      return (
        <div className={`${estilos.caixa} ${estilos.lacuna}`} role="status">
          <p className={estilos.titulo}>
            <Icone nome="info" /> Não calculado
          </p>
          <p>
            Falta o dado de {estado.meses.map(mesAbreviado).join(', ')}. O Observatório não estima
            valores ausentes.
          </p>
        </div>
      )
    case 'erro':
      return <CaixaErro mensagem={estado.mensagem} tentarNovamente={estado.tentarNovamente} />
    case 'nao_integrado':
      return (
        <div className={`${estilos.caixa} ${estilos.nao_integrado}`} role="status">
          <p className={estilos.titulo}>
            <Icone nome="relogio" /> Aguardando integração
          </p>
          <p>{estado.mensagem ?? 'Disponível após a integração com a fonte.'}</p>
        </div>
      )
    case 'falha_sem_versao':
      return (
        <div className={`${estilos.caixa} ${estilos.falha}`} role="alert">
          <p className={estilos.titulo}>
            <Icone nome="alerta" /> Falha na atualização
          </p>
          <p>{estado.mensagem ?? 'Ainda não há uma versão válida destes dados para exibir.'}</p>
        </div>
      )
  }
}

/** Depois deste tempo, avisa que o servidor gratuito da API pode estar acordando. */
export const ESPERA_AVISO_LENTIDAO_MS = 5000

function Carregando({ rotulo }: { rotulo: string }) {
  const [demorando, setDemorando] = useState(false)
  useEffect(() => {
    const temporizador = setTimeout(() => setDemorando(true), ESPERA_AVISO_LENTIDAO_MS)
    return () => clearTimeout(temporizador)
  }, [])
  return (
    <div className={estilos.esqueleto} aria-busy="true" role="status">
      <span className="somente-leitor-de-tela">Carregando dados de {rotulo}…</span>
      {demorando && (
        <p className={`${estilos.aviso} ${estilos.avisoNaoPublicado}`}>
          <Icone nome="relogio" />
          <span>
            Os dados estão demorando um pouco: o servidor gratuito pode levar até um minuto para
            responder na primeira visita. A página continua carregando.
          </span>
        </p>
      )}
      <div className={estilos.barra} style={{ width: '40%' }} />
      <div className={estilos.barra} style={{ width: '70%', height: '2.2rem' }} />
      <div className={estilos.barra} style={{ width: '100%', height: '5rem' }} />
    </div>
  )
}

function CaixaErro({
  mensagem,
  tentarNovamente,
}: {
  mensagem?: string
  tentarNovamente?: () => void
}) {
  const botao = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    botao.current?.focus()
  }, [])
  return (
    <div className={`${estilos.caixa} ${estilos.erro}`} role="alert">
      <p className={estilos.titulo}>
        <Icone nome="alerta" /> Falha ao carregar
      </p>
      <p>{mensagem ?? 'Não foi possível carregar os dados agora. Tente novamente em instantes.'}</p>
      {tentarNovamente && (
        <button ref={botao} type="button" className="botao" onClick={tentarNovamente}>
          <Icone nome="atualizar" /> Tentar novamente
        </button>
      )}
    </div>
  )
}

/** Aviso azul de mês ainda não publicado (combinável com os dados). */
export function AvisoNaoPublicado({ texto }: { texto: string }) {
  return (
    <p className={`${estilos.aviso} ${estilos.avisoNaoPublicado}`} role="note">
      <Icone nome="relogio" />
      <span>{texto}</span>
    </p>
  )
}

/** Aviso de falha na atualização: os dados mostrados são da última versão válida. */
export function AvisoFalhaAtualizacao({ mensagem }: { mensagem: string | null | undefined }) {
  return (
    <p className={`${estilos.aviso} ${estilos.avisoFalha}`} role="note">
      <Icone nome="alerta" />
      <span>
        <strong>Falha na atualização.</strong>{' '}
        {mensagem ?? 'Exibindo a última versão válida dos dados.'}
      </span>
    </p>
  )
}

/**
 * Converte o erro de uma consulta no estado a exibir. Com o indicador em mãos, um 409
 * (sem versão publicada) após uma coleta que falhou vira "Falha na atualização", e não
 * "Aguardando integração" (FR-040).
 */
export function estadoDoErro(
  erro: unknown,
  tentarNovamente: () => void,
  indicador?: Indicador,
): EstadoBloqueante {
  if (erro instanceof ErroDaApi) {
    if (erro.status === 409) {
      if (indicador?.atualizacao.situacao === 'falha_atualizacao') {
        return { tipo: 'falha_sem_versao', mensagem: indicador.atualizacao.mensagem }
      }
      return { tipo: 'nao_integrado', mensagem: erro.problema?.detail }
    }
    if (erro.status === 422 && erro.problema?.meses_ausentes) {
      return { tipo: 'lacuna', meses: erro.problema.meses_ausentes }
    }
    if (erro.status < 500 && erro.problema) return { tipo: 'erro', mensagem: erro.problema.detail }
  }
  return { tipo: 'erro', tentarNovamente }
}
