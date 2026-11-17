<!--
Sync Impact Report
- Version change: (template, sem versão) → 1.0.0
- Princípios definidos (primeira ratificação):
  - [PRINCIPLE_1_NAME] → I. Desenvolvimento Orientado por Especificações
  - [PRINCIPLE_2_NAME] → II. Qualidade de Código e Organização Modular
  - [PRINCIPLE_3_NAME] → III. Transparência e Procedência dos Dados (INEGOCIÁVEL)
  - [PRINCIPLE_4_NAME] → IV. Cálculos Reproduzíveis e Testados (INEGOCIÁVEL)
  - [PRINCIPLE_5_NAME] → V. Honestidade Analítica: Correlação Não É Causalidade
  - (novo) VI. Acessibilidade e Navegação Responsiva
  - (novo) VII. Proteção de Credenciais
  - (novo) VIII. Simplicidade e Baixo Custo
- Seções adicionadas: "Padrões de Dados e Apresentação de Indicadores",
  "Fluxo de Desenvolvimento e Portões de Qualidade", "Governança"
- Seções removidas: nenhuma
- Templates: nenhum template foi modificado (o escopo deste comando é apenas a constituição;
  plan/spec/tasks templates leem a constituição em tempo de execução).
- TODOs pendentes: nenhum
-->

# Constituição do Observatório do Real

## Core Principles

### I. Desenvolvimento Orientado por Especificações

Toda funcionalidade DEVE nascer de uma especificação escrita antes do código, seguindo o fluxo
Spec Kit: especificar → esclarecer → planejar → gerar tarefas → implementar.

- Nenhum código de produção DEVE ser mesclado sem uma especificação (`spec.md`), um plano
  (`plan.md`) e uma lista de tarefas (`tasks.md`) correspondentes.
- Mudanças de comportamento DEVEM atualizar primeiro a especificação; o código segue a especificação,
  nunca o contrário.
- Ambiguidades DEVEM ser resolvidas (via `/speckit-clarify`) ou registradas explicitamente como
  pendências antes do planejamento.

**Justificativa**: especificações tornam as decisões auditáveis e mantêm humanos e IA alinhados
sobre o que está sendo construído e por quê.

### II. Qualidade de Código e Organização Modular

- O código DEVE ser organizado em módulos com responsabilidade única e fronteiras claras,
  separando no mínimo: coleta de dados, transformação/cálculo, armazenamento e apresentação.
- Regras econômicas e transformações de dados NÃO DEVEM residir em componentes de interface.
- O código DEVE passar por formatador e linter automáticos configurados no repositório, sem
  avisos ignorados sem justificativa.
- Nomes, funções e módulos DEVEM ser legíveis e coesos; duplicação de regra de cálculo é proibida
  (uma regra, uma implementação).
- Toda a documentação do projeto (README, especificações, planos, comentários explicativos,
  mensagens ao usuário) DEVE ser escrita em português do Brasil. Identificadores de código PODEM
  seguir convenções em inglês quando a linguagem ou biblioteca assim recomendar.

**Justificativa**: módulos isolados são testáveis e substituíveis; documentação em português
garante que o público e os mantenedores compreendam o projeto.

### III. Transparência e Procedência dos Dados (INEGOCIÁVEL)

Todo indicador exibido ou exportado DEVE apresentar, de forma visível junto ao dado:

1. **Fonte oficial** (instituição e, quando houver, código da série — ex.: IBGE/SIDRA, BCB/SGS);
2. **Unidade de medida** (ex.: % a.a., R$ correntes, R$ constantes de uma data-base, índice);
3. **Período de referência** (ex.: mês/ano, trimestre, acumulado em 12 meses);
4. **Data de atualização** (quando o dado foi obtido da fonte, em formato ISO `AAAA-MM-DD`).

- Dados reais e dados ilustrativos (simulados, fictícios, de exemplo ou projeções) DEVEM ser
  diferenciados de forma explícita e inequívoca — rótulo textual obrigatório, não apenas cor.
- Dados ilustrativos NUNCA DEVEM ser apresentados como reais, nem misturados a séries reais sem
  identificação.
- Um indicador sem metadados completos NÃO DEVE ser publicado.

**Justificativa**: a credibilidade do Observatório depende de que qualquer pessoa possa verificar
de onde vem cada número e a que ele se refere.

### IV. Cálculos Reproduzíveis e Testados (INEGOCIÁVEL)

- Todo cálculo econômico (deflação, variação, acumulado, médias, conversões, índices) DEVE ser
  reproduzível: mesmas entradas e mesma versão do código DEVEM produzir o mesmo resultado.
- Os parâmetros de cálculo (data-base, índice deflator, janelas, arredondamento) DEVEM ser
  explícitos e documentados, nunca implícitos.
- Toda regra econômica e toda transformação de dados DEVE ter testes automatizados, incluindo
  casos com valores de referência conhecidos (conferidos com a fonte oficial ou calculados à mão)
  e casos de borda (dados ausentes, séries vazias, mudanças de unidade).
- Testes DEVEM ser escritos junto com (ou antes de) a regra que verificam e DEVEM passar antes
  da mesclagem.
- Dados brutos obtidos das fontes DEVEM ser preservados ou recuperáveis, separados dos dados
  transformados.

**Justificativa**: erros silenciosos em cálculos econômicos comprometem conclusões públicas;
reprodutibilidade e testes são a única forma de garantir confiança.

### V. Honestidade Analítica: Correlação Não É Causalidade

- Textos, títulos, gráficos e legendas NÃO DEVEM afirmar ou sugerir relação causal a partir de
  correlação, coincidência temporal ou sobreposição de séries.
- Ao exibir séries lado a lado ou correlações, a interface DEVE usar linguagem descritiva
  ("variaram juntas", "no mesmo período") e, quando pertinente, um aviso explícito de que
  correlação não implica causalidade.
- Afirmações causais só PODEM aparecer quando citarem estudo ou fonte metodológica que as
  sustente, com referência visível.
- Gráficos NÃO DEVEM usar escalas, eixos truncados ou recortes de período que distorçam a leitura
  sem indicação clara.

**Justificativa**: um observatório público tem responsabilidade de não induzir conclusões
equivocadas sobre a economia.

### VI. Acessibilidade e Navegação Responsiva

- A interface DEVE atender às diretrizes WCAG 2.1 nível AA: contraste adequado, navegação
  completa por teclado, foco visível, textos alternativos e rótulos semânticos.
- Gráficos DEVEM ter alternativa textual ou tabular dos dados e NÃO DEVEM depender apenas de cor
  para transmitir informação.
- O layout DEVE funcionar em telas de celular (a partir de 360 px), tablet e desktop, sem rolagem
  horizontal da página.

**Justificativa**: informação econômica pública deve ser acessível a todas as pessoas, em
qualquer dispositivo.

### VII. Proteção de Credenciais

- Chaves de API, tokens, senhas e demais segredos NUNCA DEVEM ser versionados no repositório
  nem expostos no código executado no navegador.
- Segredos DEVEM ser fornecidos por variáveis de ambiente ou pelo gerenciador de segredos da
  plataforma; o repositório DEVE conter apenas um arquivo de exemplo (ex.: `.env.example`) sem
  valores reais.
- Arquivos de segredos DEVEM constar no `.gitignore`; um vazamento DEVE resultar em revogação e
  rotação imediata da credencial.

**Justificativa**: credenciais expostas geram custos, abuso de serviços e perda de confiança.

### VIII. Simplicidade e Baixo Custo

- A solução mais simples que atenda à especificação DEVE ser preferida (YAGNI).
- Novas dependências, serviços pagos ou infraestrutura adicional DEVEM ser justificados no
  `plan.md`, na seção de complexidade, com alternativa mais simples considerada e descartada.
- DEVEM ser preferidos: fontes de dados públicas e gratuitas, hospedagem estática ou de camada
  gratuita, e armazenamento em arquivos (ex.: CSV/JSON/SQLite) antes de bancos de dados gerenciados.
- O custo mensal estimado de operação DEVE ser registrado no plano sempre que houver serviço
  externo envolvido.

**Justificativa**: o projeto deve ser sustentável e fácil de manter, entender e evoluir.

## Padrões de Dados e Apresentação de Indicadores

- Cada indicador DEVE possuir um registro de metadados (fonte, código da série, URL de origem,
  unidade, periodicidade, período de referência, data de atualização, natureza real/ilustrativa)
  mantido junto ao código ou aos dados, e consumido pela interface — nunca digitado manualmente
  na tela.
- Datas DEVEM seguir o formato ISO `AAAA-MM-DD` no armazenamento; a exibição PODE usar o formato
  brasileiro `DD/MM/AAAA`. Números DEVEM ser exibidos no padrão brasileiro (vírgula decimal).
- Valores monetários DEVEM indicar se estão em termos nominais (correntes) ou reais (constantes),
  com a data-base e o índice deflator quando reais.
- Falhas na coleta DEVEM ser sinalizadas ao usuário (ex.: "dado desatualizado desde …"), nunca
  mascaradas com valores antigos sem aviso.

## Fluxo de Desenvolvimento e Portões de Qualidade

Antes de qualquer mesclagem na branch principal, DEVEM ser verificados:

1. Existência de especificação, plano e tarefas para a mudança (Princípio I);
2. Formatação, lint e testes automatizados passando (Princípios II e IV);
3. Metadados completos e distinção real/ilustrativo em todo indicador novo ou alterado
   (Princípio III);
4. Revisão de textos e gráficos quanto a afirmações causais indevidas (Princípio V);
5. Verificação de acessibilidade e responsividade nas telas afetadas (Princípio VI);
6. Ausência de segredos no diff (Princípio VII);
7. Justificativa registrada para qualquer nova dependência ou custo (Princípio VIII).

O "Constitution Check" do `plan.md` DEVE avaliar explicitamente cada princípio; violações só são
aceitas se registradas na tabela de complexidade com justificativa.

## Governance

- Esta constituição prevalece sobre quaisquer outras práticas ou preferências do projeto.
- Emendas DEVEM ser propostas por meio de `/speckit-constitution`, com descrição da mudança,
  justificativa e impacto nos artefatos existentes, e registradas no histórico do Git.
- Versionamento semântico da constituição:
  - **MAJOR**: remoção ou redefinição incompatível de princípios ou regras de governança;
  - **MINOR**: novo princípio ou seção, ou ampliação material de orientação;
  - **PATCH**: esclarecimentos, redação e correções sem mudança de significado.
- Toda revisão de código e todo plano DEVEM verificar a conformidade com esta constituição.
  Complexidade adicional DEVE ser justificada.
- A conformidade DEVE ser reavaliada a cada nova funcionalidade e, no mínimo, a cada emenda.

**Version**: 1.0.0 | **Ratified**: 2026-10-22 | **Last Amended**: 2026-10-22
