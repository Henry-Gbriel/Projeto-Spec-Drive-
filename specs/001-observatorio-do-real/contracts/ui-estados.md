# Contrato: estados de dados na interface (FR-040 a FR-042)

Todo bloco que exibe dados (cartão de indicador, gráfico, tabela, resultado do simulador, item do
catálogo) usa o componente `EstadoDados` e está **sempre em exatamente um** dos estados abaixo.
Referência visual: `08-componentes-e-estados.png` (seção "Estados dos dados").

| Estado | Condição de entrada | O que aparece | Acessibilidade |
|--------|---------------------|---------------|----------------|
| `carregando` | requisição em andamento, sem dado em cache | esqueleto com pulsação suave (desligada com `prefers-reduced-motion`) | `aria-busy="true"` no bloco e texto oculto "Carregando dados de {indicador}" |
| `pronto` | resposta 200 com observações | dados + metadados (fonte, unidade, período, atualização) | gráfico com tabela alternativa |
| `sem_dados` | resposta 200 com `observacoes` vazio | ícone + "Sem dados — não há valores para o período escolhido." | texto, não só ícone |
| `nao_publicado` | `periodo.aviso_nao_publicado` preenchido | dados até `fim_utilizado` **e** aviso azul: "O {indicador} de {mês} ainda não foi publicado pelo {fonte}. Mostramos até {mês usado}." | `role="note"` |
| `lacuna` | `situacao: "lacuna"` ou 422 com `meses_ausentes` | gráfico com interrupção; cartão sem número-síntese; texto "Não calculado: falta o dado de {meses}." | lista dos meses em texto |
| `falha_atualizacao` | `atualizacao.situacao = "falha_atualizacao"` | dados da última versão válida **e** selo vermelho "Falha na atualização" + "Mostramos a versão de {data}." | selo com texto |
| `erro` | falha de rede ou 5xx, sem dado em cache | caixa de falha: "Não foi possível carregar os dados agora. Tente novamente em instantes." + botão "Tentar novamente" | foco no botão após erro |
| `entrada_invalida` | validação local ou 400 com `erros[]` | resultado não é exibido; mensagem junto ao campo | `aria-invalid="true"`, `aria-describedby` para a mensagem, foco no primeiro campo inválido |
| `nao_integrado` | 409 ou catálogo com `aguardando_integracao`/`em_definicao` | selo azul "Aguardando integração" ou amarelo "Em definição"; botão CSV desabilitado com "Disponível após a integração com a fonte." | botão com `aria-disabled` |

Regras:

- Estados combináveis: `pronto` pode vir com `nao_publicado` e/ou `falha_atualizacao`
  (avisos sobrepostos aos dados). Os demais são exclusivos.
- Selo `Ilustrativo` aparece **somente** quando `indicador.natureza = "ilustrativo"`.
- Nenhum estado exibe número que não veio da API.
- Cada estado tem teste de componente (Vitest) e ao menos um teste ponta a ponta com resposta
  simulada (Playwright).

## Validação de entrada do simulador (lado da interface)

A interface valida antes de chamar a API, com as mesmas regras do servidor (o servidor continua
sendo a autoridade):

| Campo | Regra | Mensagem |
|-------|-------|----------|
| valor | obrigatório | "Informe um valor em reais." |
| valor | formato `1.500,00` ou `1500,00` ou `1500` | "Use apenas números, com vírgula para os centavos. Exemplo: 1.500,00" |
| valor | > 0 | "O valor deve ser maior que zero." |
| valor | ≤ 2 casas decimais | "Use no máximo dois dígitos de centavos." |
| valor | ≤ R$ 9.999.999.999.999,99 | "Valor acima do limite do simulador." |
| data inicial | ≥ primeiro mês da série | "O IPCA está disponível a partir de {mês}." |
| data inicial | ≤ último mês publicado | "Ainda não há IPCA publicado para {mês}." |
| datas | inicial ≤ final | "A data inicial deve ser anterior ou igual à data final." |
| data final | > último mês publicado | **não é erro**: usa o último mês publicado e mostra aviso (US3-3) |
