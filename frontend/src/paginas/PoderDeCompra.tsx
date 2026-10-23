import { useMemo, useState } from 'react'
import { useTitulo } from '../app/Layout'
import { CabecalhoPagina } from '../componentes/CabecalhoPagina'
import { EstadoDados, estadoDoErro } from '../componentes/EstadoDados'
import { ErroDaApi } from '../servicos/api'
import { useIndicador, useSimulacao, type PedidoSimulacao } from '../servicos/consultas'
import { ComoFunciona } from './poder-de-compra/ComoFunciona'
import { FormularioSimulacao, type ErrosCampos } from './poder-de-compra/FormularioSimulacao'
import estilos from './poder-de-compra/PoderDeCompra.module.css'
import { ResultadoSimulacao } from './poder-de-compra/ResultadoSimulacao'

function mesAtual(): string {
  const hoje = new Date()
  return `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`
}

const INICIAL = { valor: '100,00', inicio: '2016-01', fim: mesAtual() }

export function PoderDeCompra() {
  useTitulo('Simulador de poder de compra')
  const indicador = useIndicador('ipca')
  const [pedido, setPedido] = useState<PedidoSimulacao | null>({
    valor: '100.00',
    inicio: INICIAL.inicio,
    fim: INICIAL.fim,
  })
  const simulacao = useSimulacao(pedido)

  // Erros por campo vindos do servidor (400): exibidos junto aos campos (FR-028).
  const errosServidor = useMemo<ErrosCampos>(() => {
    const erro = simulacao.error
    if (!(erro instanceof ErroDaApi) || erro.status !== 400) return {}
    return Object.fromEntries((erro.problema?.erros ?? []).map((e) => [e.campo, e.mensagem]))
  }, [simulacao.error])

  const erroDeEntrada = simulacao.error instanceof ErroDaApi && simulacao.error.status === 400

  return (
    <>
      <CabecalhoPagina
        etiqueta="Poder de compra · Simulador"
        tituloFino="Quanto você precisaria hoje"
        tituloForte="para comprar o que comprava antes?"
        descricao="Informe um valor e duas datas. O simulador corrige a quantia pela inflação oficial (IPCA) do período."
      />
      <div className={`conteiner ${estilos.grade}`}>
        <FormularioSimulacao
          indicador={indicador.data}
          inicial={INICIAL}
          errosServidor={errosServidor}
          aoSimular={setPedido}
        />
        <div aria-live="polite" aria-busy={simulacao.isFetching}>
          {indicador.isError ? (
            <EstadoDados estado={estadoDoErro(indicador.error, () => void indicador.refetch())} />
          ) : simulacao.isPending || (simulacao.isFetching && !simulacao.data) ? (
            <EstadoDados estado={{ tipo: 'carregando', rotulo: 'simulação' }} />
          ) : simulacao.isError && !erroDeEntrada ? (
            <EstadoDados
              estado={estadoDoErro(simulacao.error, () => void simulacao.refetch(), indicador.data)}
            />
          ) : erroDeEntrada ? (
            <p className={`cartao texto-apoio ${estilos.semResultado}`}>
              Corrija os campos indicados para ver o resultado.
            </p>
          ) : (
            simulacao.data && <ResultadoSimulacao simulacao={simulacao.data} />
          )}
        </div>
      </div>
      <div className="conteiner">
        <ComoFunciona simulacao={erroDeEntrada ? undefined : simulacao.data} />
      </div>
    </>
  )
}
