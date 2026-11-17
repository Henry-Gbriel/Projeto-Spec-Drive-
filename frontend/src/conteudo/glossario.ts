/**
 * Textos educativos em linguagem simples (FR-013, FR-014).
 * Revisados para não afirmar causalidade entre indicadores (FR-015, Princípio V).
 */

export interface Verbete {
  titulo: string
  paragrafos: string[]
}

export const O_QUE_E_IPCA: Verbete = {
  titulo: 'O que é IPCA?',
  paragrafos: [
    'O IPCA (Índice Nacional de Preços ao Consumidor Amplo) é o índice oficial de inflação do Brasil, calculado pelo IBGE.',
    'Ele mede, a cada mês, quanto variaram os preços de produtos e serviços consumidos pelas famílias: alimentação, aluguel, transporte, saúde, educação e outros.',
    'Quando o IPCA sobe, a mesma quantia em reais compra menos coisas do que antes.',
  ],
}

export const NUMERO_INDICE: Verbete = {
  titulo: 'O que é o número-índice?',
  paragrafos: [
    'É o IPCA acumulado desde dezembro de 1993, quando o índice vale 100. Dividir o índice de dois meses mostra quanto os preços mudaram entre eles.',
  ],
}

export const INFLACAO_X_CAMBIO: Verbete = {
  titulo: 'Inflação é o mesmo que desvalorização cambial?',
  paragrafos: [
    'Não. Inflação é a alta geral de preços dentro do Brasil, medida pelo IPCA: o real passa a comprar menos no mercado, no aluguel ou na farmácia.',
    'Desvalorização cambial é quando são necessários mais reais para comprar uma moeda estrangeira, como o dólar ou o euro.',
    'Os dois movimentos podem acontecer juntos, mas não são a mesma coisa e não andam sempre no mesmo ritmo.',
  ],
}

export const DOIS_JEITOS = [
  {
    numero: '01',
    titulo: 'Dentro do Brasil · Inflação',
    texto:
      'Os preços sobem e o mesmo valor em reais compra menos no mercado, no aluguel ou na farmácia. Medida pelo IPCA.',
  },
  {
    numero: '02',
    titulo: 'Diante de outras moedas · Câmbio',
    texto:
      'São necessários mais reais para comprar um dólar ou um euro. Medida pela cotação de câmbio.',
  },
]

export const DIFERENCA_NOMINAL =
  'A diferença não é ganho nem perda de dinheiro: é o quanto os preços subiram. A quantia nominal continua a mesma; o que muda é o que ela compra.'
