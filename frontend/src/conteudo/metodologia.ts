/** Textos da página "Sobre e metodologia". */

export const CAMINHO_DO_NUMERO = [
  {
    titulo: 'Coleta',
    texto: 'Busca das séries nas fontes oficiais, com registro de data e origem.',
    detalhe: 'Banco Central do Brasil, IBGE e publicações oficiais',
  },
  {
    titulo: 'Armazenamento',
    texto: 'Os dados brutos são guardados como chegaram, para permitir auditoria.',
    detalhe: 'Histórico de versões e revisões das fontes',
  },
  {
    titulo: 'Tratamento',
    texto: 'Padronização de datas, unidades e nomes; checagem de lacunas e valores fora do padrão.',
    detalhe: 'Cálculos como acumulados e base 100',
  },
  {
    titulo: 'Apresentação',
    texto: 'Gráficos, simuladores e textos simples, sempre com fonte e período.',
    detalhe: 'Download em CSV para quem quiser analisar',
  },
]

export const POLITICAS = [
  'Quando uma fonte não responde, o Observatório mantém a última versão válida e avisa na tela que a atualização falhou.',
  'Meses ainda não publicados aparecem identificados, nunca preenchidos com estimativas. Lacunas na série ficam visíveis: a linha do gráfico é interrompida e a tabela mostra "sem dado".',
  'Se uma fonte mudar a base, a unidade ou a metodologia de uma série, a série tratada continua na unidade informada no catálogo e a mudança é registrada nesta página, com a data e o motivo. Revisões de valores passados ficam guardadas no histórico; nenhum valor é apagado sem registro.',
  'Os dados são consultados nas fontes uma vez por dia. O IPCA é divulgado pelo IBGE uma vez por mês, por volta do dia 10 do mês seguinte.',
]

export const CONVENCOES = [
  {
    titulo: 'Inflação acumulada',
    texto:
      'As variações mensais do IPCA são encadeadas: fator = (1 + v₁/100) × (1 + v₂/100) × … O mês inicial e o mês final entram no cálculo; de janeiro de 2016 a dezembro de 2025 são 120 meses. O resultado é conferido com o número-índice oficial do IBGE.',
  },
  {
    titulo: 'Arredondamento',
    texto:
      'Os cálculos usam todas as casas decimais e só o resultado é arredondado: centavos para valores em reais e duas casas para percentuais (meio para cima).',
  },
  {
    titulo: 'Arquivos CSV',
    texto:
      'Separador ponto e vírgula, vírgula decimal, sem separador de milhar, codificação UTF-8 com BOM (abre direto no Excel e no LibreOffice). As primeiras linhas, iniciadas por #, trazem fonte, unidade, período e data de atualização. Células de valor vazias indicam observação ausente na fonte.',
  },
]

export const ETAPAS_PROJETO = [
  { titulo: 'Requisitos', texto: 'O que o sistema precisa fazer' },
  { titulo: 'Planejamento', texto: 'Como será construído' },
  { titulo: 'Tarefas', texto: 'Passos pequenos e verificáveis' },
]
