import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import {
  AvisoFalhaAtualizacao,
  AvisoNaoPublicado,
  EstadoDados,
  estadoDoErro,
} from '../../src/componentes/EstadoDados'
import { Selo, SeloNatureza } from '../../src/componentes/Selo'
import { ErroDaApi } from '../../src/servicos/api'

describe('EstadoDados', () => {
  it('carregando: aria-busy e texto para leitores de tela', () => {
    render(<EstadoDados estado={{ tipo: 'carregando', rotulo: 'IPCA' }} />)
    expect(screen.getByRole('status')).toHaveAttribute('aria-busy', 'true')
    expect(screen.getByText('Carregando dados de IPCA…')).toBeInTheDocument()
  })

  it('carregando demorado: avisa que o servidor gratuito pode estar acordando', () => {
    vi.useFakeTimers()
    render(<EstadoDados estado={{ tipo: 'carregando', rotulo: 'IPCA' }} />)
    expect(screen.queryByText(/servidor gratuito/)).not.toBeInTheDocument()
    act(() => vi.advanceTimersByTime(5000))
    expect(screen.getByText(/servidor gratuito pode levar até um minuto/)).toBeInTheDocument()
    vi.useRealTimers()
  })

  it('sem dados', () => {
    render(<EstadoDados estado={{ tipo: 'sem_dados' }} />)
    expect(screen.getByText('Não há valores para o período escolhido.')).toBeInTheDocument()
  })

  it('lacuna lista os meses ausentes em texto', () => {
    render(<EstadoDados estado={{ tipo: 'lacuna', meses: ['2025-03-01', '2025-04-01'] }} />)
    expect(screen.getByText(/Falta o dado de mar\/2025, abr\/2025/)).toBeInTheDocument()
  })

  it('erro: botão Tentar novamente recebe o foco e funciona', async () => {
    const tentar = vi.fn()
    render(<EstadoDados estado={{ tipo: 'erro', tentarNovamente: tentar }} />)
    const botao = screen.getByRole('button', { name: /Tentar novamente/ })
    expect(botao).toHaveFocus()
    await userEvent.click(botao)
    expect(tentar).toHaveBeenCalledOnce()
  })

  it('não integrado e falha sem versão', () => {
    const { rerender } = render(<EstadoDados estado={{ tipo: 'nao_integrado' }} />)
    expect(screen.getByText('Disponível após a integração com a fonte.')).toBeInTheDocument()
    rerender(<EstadoDados estado={{ tipo: 'falha_sem_versao', mensagem: null }} />)
    expect(screen.getByRole('alert')).toHaveTextContent('Falha na atualização')
  })

  it('avisos combináveis com os dados', () => {
    render(
      <>
        <AvisoNaoPublicado texto="O IPCA de out/2026 ainda não foi publicado pelo IBGE." />
        <AvisoFalhaAtualizacao mensagem="A atualização de 23/10/2026 falhou." />
      </>,
    )
    expect(screen.getAllByRole('note')).toHaveLength(2)
    expect(screen.getByText(/Falha na atualização\./)).toBeInTheDocument()
  })

  it('mapeia erros da API para estados', () => {
    const tentar = () => {}
    expect(estadoDoErro(new ErroDaApi(409, null), tentar).tipo).toBe('nao_integrado')
    const lacuna = new ErroDaApi(422, {
      type: 't',
      title: 't',
      status: 422,
      detail: 'd',
      meses_ausentes: ['2020-04-01'],
    })
    expect(estadoDoErro(lacuna, tentar)).toEqual({ tipo: 'lacuna', meses: ['2020-04-01'] })
    expect(estadoDoErro(new TypeError('rede'), tentar).tipo).toBe('erro')
  })

  it('409 de indicador com falha antes da primeira publicação vira falha_sem_versao', () => {
    const indicador = {
      atualizacao: {
        situacao: 'falha_atualizacao',
        ultima_atualizacao_valida: null,
        mensagem: 'A atualização de 23/10/2026 falhou e ainda não há versão válida para exibir.',
      },
    } as Parameters<typeof estadoDoErro>[2]
    expect(estadoDoErro(new ErroDaApi(409, null), () => {}, indicador)).toEqual({
      tipo: 'falha_sem_versao',
      mensagem: 'A atualização de 23/10/2026 falhou e ainda não há versão válida para exibir.',
    })
  })
})

describe('Selo', () => {
  it('ilustrativo só aparece para natureza ilustrativa', () => {
    const { rerender, container } = render(<SeloNatureza natureza="real" />)
    expect(container).toBeEmptyDOMElement()
    rerender(<SeloNatureza natureza="ilustrativo" />)
    expect(screen.getByText('Ilustrativo')).toBeInTheDocument()
  })

  it('situação sempre com texto', () => {
    render(<Selo tipo="falha_atualizacao" />)
    expect(screen.getByText('Falha na atualização')).toBeInTheDocument()
  })
})
