import { useEffect, useId, useRef, useState, type FormEvent } from 'react'
import { ListaMetadados } from '../../componentes/Metadados'
import { mesAbreviado, paraMesIso } from '../../formatacao/datas'
import { converterValorEmReais } from '../../formatacao/valorEmReais'
import type { Indicador } from '../../servicos/api'
import type { PedidoSimulacao } from '../../servicos/consultas'
import estilos from './PoderDeCompra.module.css'

export type ErrosCampos = Partial<Record<'valor' | 'inicio' | 'fim', string>>

export const INICIO_PLANO_REAL = '1994-07'

interface Props {
  indicador: Indicador | undefined
  inicial: { valor: string; inicio: string; fim: string }
  errosServidor: ErrosCampos
  aoSimular: (pedido: PedidoSimulacao) => void
}

/** Validação local com as mesmas regras e mensagens do servidor (contracts/ui-estados.md). */
export function validar(
  campos: { valor: string; inicio: string; fim: string },
  indicador: Indicador | undefined,
): { erros: ErrosCampos; pedido?: PedidoSimulacao } {
  const erros: ErrosCampos = {}
  const valor = converterValorEmReais(campos.valor)
  if ('erro' in valor) erros.valor = valor.erro

  const disponivel = indicador?.periodo_disponivel
  const primeiro =
    disponivel && paraMesIso(disponivel.inicio) > INICIO_PLANO_REAL
      ? paraMesIso(disponivel.inicio)
      : INICIO_PLANO_REAL
  const ultimo = disponivel ? paraMesIso(disponivel.fim) : null

  if (!campos.inicio) erros.inicio = 'Informe a data inicial.'
  else if (campos.fim && campos.inicio > campos.fim) {
    erros.inicio = 'A data inicial deve ser anterior ou igual à data final.'
  } else if (campos.inicio < primeiro) {
    erros.inicio = `O IPCA está disponível a partir de ${mesAbreviado(primeiro)}.`
  } else if (ultimo && campos.inicio > ultimo) {
    erros.inicio = `Ainda não há IPCA publicado para ${mesAbreviado(campos.inicio)}.`
  }
  if (!campos.fim) erros.fim = 'Informe a data final.'

  if (Object.keys(erros).length || 'erro' in valor) return { erros }
  return { erros, pedido: { valor: valor.valor, inicio: campos.inicio, fim: campos.fim } }
}

export function FormularioSimulacao({ indicador, inicial, errosServidor, aoSimular }: Props) {
  const id = useId()
  const [campos, setCampos] = useState(inicial)
  const [errosLocais, setErrosLocais] = useState<ErrosCampos>({})
  const refs = {
    valor: useRef<HTMLInputElement>(null),
    inicio: useRef<HTMLInputElement>(null),
    fim: useRef<HTMLInputElement>(null),
  }
  const erros = { ...errosServidor, ...errosLocais }

  const focarPrimeiroErro = (lista: ErrosCampos) => {
    const primeiro = (['valor', 'inicio', 'fim'] as const).find((campo) => lista[campo])
    if (primeiro) refs[primeiro].current?.focus()
  }

  useEffect(() => {
    focarPrimeiroErro(errosServidor)
  }, [errosServidor]) // eslint-disable-line react-hooks/exhaustive-deps

  const enviar = (evento: FormEvent) => {
    evento.preventDefault()
    const { erros: novos, pedido } = validar(campos, indicador)
    setErrosLocais(novos)
    if (pedido) aoSimular(pedido)
    else focarPrimeiroErro(novos)
  }

  const descricao = (campo: keyof ErrosCampos, dica?: string) =>
    [erros[campo] ? `${id}-${campo}-erro` : null, dica].filter(Boolean).join(' ') || undefined

  const limiteMaximo = indicador?.periodo_disponivel
    ? paraMesIso(indicador.periodo_disponivel.fim)
    : undefined

  return (
    <form
      className={`cartao ${estilos.formulario}`}
      onSubmit={enviar}
      noValidate
      aria-labelledby={`${id}-titulo`}
    >
      <h2 id={`${id}-titulo`} className="rotulo">
        Simulação
      </h2>

      <div className={estilos.campo}>
        <label htmlFor={`${id}-valor`} className="rotulo">
          Valor em reais
        </label>
        <div className={`${estilos.entradaValor} ${erros.valor ? estilos.invalido : ''}`}>
          <span aria-hidden="true">R$</span>
          <input
            ref={refs.valor}
            id={`${id}-valor`}
            name="valor"
            inputMode="decimal"
            autoComplete="off"
            value={campos.valor}
            onChange={(e) => setCampos({ ...campos, valor: e.target.value })}
            aria-invalid={Boolean(erros.valor)}
            aria-describedby={descricao('valor', `${id}-valor-dica`)}
          />
        </div>
        <p id={`${id}-valor-dica`} className={estilos.dica}>
          Use vírgula para os centavos. Exemplo: 1.500,00
        </p>
        {erros.valor && (
          <p id={`${id}-valor-erro`} className={estilos.erro}>
            {erros.valor}
          </p>
        )}
      </div>

      <div className={estilos.datas}>
        <div className={estilos.campo}>
          <label htmlFor={`${id}-inicio`} className="rotulo">
            Data inicial
          </label>
          <input
            ref={refs.inicio}
            id={`${id}-inicio`}
            name="inicio"
            type="month"
            className={estilos.entradaData}
            value={campos.inicio}
            min={INICIO_PLANO_REAL}
            max={limiteMaximo}
            onChange={(e) => setCampos({ ...campos, inicio: e.target.value })}
            aria-invalid={Boolean(erros.inicio)}
            aria-describedby={descricao('inicio')}
          />
          {erros.inicio && (
            <p id={`${id}-inicio-erro`} className={estilos.erro}>
              {erros.inicio}
            </p>
          )}
        </div>
        <div className={estilos.campo}>
          <label htmlFor={`${id}-fim`} className="rotulo">
            Data final
          </label>
          <input
            ref={refs.fim}
            id={`${id}-fim`}
            name="fim"
            type="month"
            className={estilos.entradaData}
            value={campos.fim}
            min={INICIO_PLANO_REAL}
            onChange={(e) => setCampos({ ...campos, fim: e.target.value })}
            aria-invalid={Boolean(erros.fim)}
            aria-describedby={descricao('fim')}
          />
          {erros.fim && (
            <p id={`${id}-fim-erro`} className={estilos.erro}>
              {erros.fim}
            </p>
          )}
        </div>
      </div>

      <button type="submit" className="botao botao-primario">
        Calcular
      </button>

      {indicador && <ListaMetadados indicador={indicador} />}
    </form>
  )
}
