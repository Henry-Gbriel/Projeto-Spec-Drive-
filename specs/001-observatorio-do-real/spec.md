# Feature Specification: Observatório do Real

**Feature Branch**: `001-observatorio-do-real`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Desenvolva o Observatório do Real, um site público de educação econômica apoiado por uma estrutura de engenharia de dados. Utilize as imagens das pastas observatorio-do-real/desktop e observatorio-do-real/celular como referências visuais. O site deve incluir: página inicial; painel de indicadores; simulador de poder de compra pelo IPCA; consulta de câmbio; exploração de base monetária e agregados monetários; comparação de indicadores; catálogo de dados e metodologia; contatos do autor por LinkedIn e e-mail. Os usuários devem conseguir selecionar períodos, consultar gráficos e tabelas, entender os indicadores e baixar dados em CSV. Diferencie inflação, desvalorização cambial, expansão monetária e produção física de cédulas. Especifique os estados de carregamento, ausência de dados, falha de atualização e entrada inválida. Não invente observações ausentes. Defina critérios de aceitação verificáveis e organize o escopo em entregas incrementais, começando pela página inicial, IPCA e simulador de poder de compra."

## Visão Geral e Referências Visuais

O Observatório do Real é um site público, gratuito e sem cadastro, que transforma séries
econômicas oficiais (Banco Central do Brasil e IBGE) em gráficos, tabelas e explicações em
linguagem simples. Por trás do site existe um fluxo de dados em quatro etapas — **coleta**,
**armazenamento**, **tratamento** e **apresentação** — que garante que cada número exibido tenha
origem rastreável.

As telas de referência (fora do repositório, em `observatorio-do-real/desktop` e
`observatorio-do-real/celular`) definem a identidade visual e a organização das páginas:

| Referência | Página / componente |
|------------|---------------------|
| `01-pagina-inicial` | Página inicial |
| `02-visao-geral` | Painel de indicadores (Visão geral) |
| `03-poder-de-compra` | Simulador de poder de compra pelo IPCA |
| `04-cambio` | Consulta de câmbio |
| `05-moeda-em-circulacao` | Moeda em circulação, base monetária e agregados |
| `06-comparar-indicadores` | Comparação de indicadores (base 100) |
| `07-dados-metodologia-sobre` | Catálogo de dados, metodologia e sobre o projeto |
| `08-componentes-e-estados` | Sistema visual: componentes e estados dos dados (somente desktop) |
| `09-componente-rodape`, `10-componente-navegacao` | Rodapé e navegação comuns |

As referências são o guia visual; quando houver divergência entre uma imagem e esta
especificação, prevalece esta especificação (ex.: os números das imagens são ilustrativos).

## Entregas Incrementais

| Entrega | Conteúdo | Histórias |
|---------|----------|-----------|
| **Entrega 1 — MVP** | Página inicial, navegação, rodapé com contatos, IPCA (gráfico, tabela, explicação, CSV) e simulador de poder de compra | US1, US2, US3 |
| **Entrega 2** | Painel de indicadores completo (IPCA, dólar, Selic, base monetária) e consulta de câmbio | US4, US5 |
| **Entrega 3** | Moeda em circulação, base monetária, agregados M1–M4 e produção física de cédulas e moedas | US6 |
| **Entrega 4** | Comparação de indicadores em base 100 e catálogo completo de dados e metodologia | US7, US8 |

Cada entrega é publicável sozinha. Páginas de entregas futuras NÃO aparecem como links ativos
na navegação até serem entregues (ver FR-005).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conhecer o projeto pela página inicial (Priority: P1) — Entrega 1

Uma pessoa curiosa sobre economia chega ao site e, na página inicial, entende o propósito do
Observatório, os temas disponíveis, de onde vêm os dados e como contatar o autor.

**Why this priority**: é a porta de entrada; sem ela, nenhuma outra página é encontrada.

**Independent Test**: abrir a página inicial em celular e desktop, percorrer as seções, seguir
os links para as páginas disponíveis e acionar os contatos do autor.

**Acceptance Scenarios**:

1. **Given** a página inicial aberta, **When** a pessoa a lê, **Then** encontra: chamada
   principal, apresentação do Observatório, fontes de dados (BCB e IBGE), os quatro temas
   (inflação, poder de compra, câmbio, moeda em circulação), as quatro etapas do fluxo de dados
   (coleta, armazenamento, tratamento, apresentação) e atalhos para as páginas disponíveis.
2. **Given** os cartões de temas com miniaturas de gráficos, **When** são exibidos, **Then** há
   o aviso textual "As miniaturas dos cards são ilustrações, não dados".
3. **Given** um tema cuja página ainda não foi entregue, **When** o cartão é exibido, **Then**
   ele aparece identificado como "Em breve" e não leva a uma página vazia ou quebrada.
4. **Given** o rodapé de qualquer página, **When** a pessoa aciona "LinkedIn", **Then** o perfil
   do autor abre em nova aba, e o link anuncia "(nova aba)"; **When** aciona "E-mail", **Then** o
   aplicativo de e-mail é aberto com o endereço do autor preenchido.
5. **Given** um celular de 360 px de largura, **When** a página é aberta, **Then** não há rolagem
   horizontal da página e a navegação entre páginas fica acessível (fileira de links rolável na
   horizontal, conforme a referência).

---

### User Story 2 - Entender a inflação pelo IPCA (Priority: P1) — Entrega 1

A pessoa escolhe um período e vê quanto os preços subiram pelo IPCA, em gráfico e tabela, com
explicação do que é o índice, e pode baixar os dados em CSV.

**Why this priority**: o IPCA é o indicador central do projeto e a base do simulador.

**Independent Test**: com a série real do IPCA carregada, selecionar cada período predefinido e
um período personalizado, conferir o acumulado com a calculadora oficial de referência, alternar
para a tabela e baixar o CSV.

**Acceptance Scenarios**:

1. **Given** o painel aberto, **When** nenhum período foi escolhido, **Then** o período padrão
   é "5 anos" terminando no último mês publicado, e o texto "Referência: mmm/aaaa a mmm/aaaa" mostra
   o intervalo exato.
2. **Given** o cartão do IPCA, **When** é exibido, **Then** mostra: inflação acumulada no período
   (em %), frase explicativa ("Alta de preços: o real comprou menos"), seta **e** texto indicando a
   direção (nunca apenas cor), período, fonte (IBGE, com código da série), unidade e data de
   atualização.
3. **Given** um período selecionado, **When** a pessoa abre "Ver valores em tabela", **Then** vê
   uma linha por mês com variação mensal (%), acumulado no período (%) e número-índice, com os
   mesmos valores do gráfico.
4. **Given** o gráfico, **When** a pessoa passa o mouse, toca ou navega por teclado sobre um ponto,
   **Then** vê mês/ano, valor e unidade.
5. **Given** a seção "O que é?", **When** expandida, **Then** explica em linguagem simples o que o
   IPCA mede e quem o calcula, e diferencia inflação de desvalorização cambial.
6. **Given** um período selecionado, **When** a pessoa aciona "Baixar CSV", **Then** recebe um
   arquivo com as observações do período, cabeçalho descritivo e metadados (ver FR-030).
7. **Given** um período cujo mês final ainda não foi publicado pelo IBGE, **When** o período é
   aplicado, **Then** um aviso informa "O IPCA de mmm/aaaa ainda não foi publicado pelo IBGE" e o
   cálculo termina no último mês disponível, indicado explicitamente.

---

### User Story 3 - Simular o poder de compra (Priority: P1) — Entrega 1

A pessoa informa um valor em reais e duas datas (mês/ano) e descobre quanto precisaria hoje para
comprar o mesmo que comprava antes, corrigido pelo IPCA, com a explicação do cálculo.

**Why this priority**: é a ferramenta que traduz a inflação para a vida cotidiana.

**Independent Test**: simular valores conhecidos e conferir com resultados de referência
calculados à mão a partir da série oficial; testar entradas inválidas.

**Acceptance Scenarios**:

1. **Given** valor R$ 100,00, data inicial e data final válidas, **When** a simulação é feita,
   **Then** o site mostra: valor corrigido, inflação acumulada (%), mudança no poder de compra (%),
   número de meses considerados, comparação visual "quantia nominal × valor que mantém o poder de
   compra" e a frase "A diferença não é ganho nem perda de dinheiro: é o quanto os preços subiram".
2. **Given** um resultado, **When** a pessoa abre "Como o cálculo funciona", **Then** vê os passos
   com os números reais da simulação: meses usados, fator acumulado (4 casas decimais) e a conta
   valor × fator = resultado.
3. **Given** uma data final ainda não publicada, **When** a simulação é feita, **Then** o cálculo
   usa o último mês disponível e exibe aviso com os dois meses (o pedido e o usado).
4. **Given** entrada inválida (valor vazio, zero, negativo, não numérico, com mais de duas casas
   decimais, data inicial posterior à final, data inicial anterior ao início da série ou posterior
   ao último mês publicado), **When** a pessoa tenta simular, **Then** nenhum resultado é exibido, uma
   mensagem junto ao campo explica o problema e como corrigir, e o foco vai para o campo com erro.
5. **Given** data inicial igual à data final, **When** a simulação é feita, **Then** o fator usa
   apenas a variação desse mês, conforme a regra de cálculo (FR-022).
6. **Given** o valor digitado no padrão brasileiro ("1.500,00"), **When** a simulação é feita,
   **Then** é interpretado como mil e quinhentos reais.

---

### User Story 4 - Ver o painel de indicadores (Priority: P2) — Entrega 2

A pessoa vê, em um só lugar, IPCA acumulado, variação do dólar (PTAX), Selic meta e quantidade de
moeda (base monetária) para o período escolhido, com histórico e um resumo em texto.

**Why this priority**: amplia o MVP com uma visão integrada dos principais números.

**Independent Test**: selecionar períodos e verificar que os quatro cartões, o histórico com abas e
o resumo do período usam o mesmo intervalo e as mesmas fontes.

**Acceptance Scenarios**:

1. **Given** um período (12 meses, 3 anos, 5 anos, 10 anos ou personalizado), **When** aplicado,
   **Then** os quatro cartões, o gráfico e o resumo são atualizados para o mesmo intervalo.
2. **Given** o histórico, **When** a pessoa alterna as abas (Inflação, Dólar, Selic, Base
   monetária), **Then** o gráfico mostra a série escolhida com título, unidade, fonte e período.
3. **Given** o bloco "Resumo do período", **When** exibido, **Then** o texto é gerado a partir dos
   números do período e só usa linguagem descritiva, sem relações de causa entre indicadores.
4. **Given** o bloco "Dois jeitos de o real perder valor", **When** exibido, **Then** diferencia
   inflação (perda de poder de compra dentro do país, IPCA) de desvalorização cambial (mais reais
   por moeda estrangeira).

---

### User Story 5 - Consultar o câmbio (Priority: P2) — Entrega 2

A pessoa acompanha quantos reais são necessários para comprar um dólar e um euro, por período, e
entende como ler a cotação.

**Why this priority**: o câmbio é o segundo modo mais conhecido de "o real perder valor".

**Independent Test**: escolher períodos e moedas, conferir início, fim, mínimo, máximo e variação
com a série oficial PTAX, e baixar o CSV.

**Acceptance Scenarios**:

1. **Given** período e moedas (dólar, euro ou ambas) selecionados, **When** aplicados, **Then**
   cada moeda tem cartão com cotação no fim do período, variação %, valor inicial, mínimo/máximo,
   fonte (BCB, PTAX venda) e atualização.
2. **Given** o gráfico, **When** exibido, **Then** cada moeda tem cor **e** padrão de traço
   distintos e rótulo no fim da linha; a unidade é "reais por unidade de moeda estrangeira, média
   mensal".
3. **Given** nenhuma moeda marcada, **When** a pessoa desmarca a última, **Then** o site mantém ao
   menos uma marcada ou mostra o estado "Selecione ao menos uma moeda".
4. **Given** o bloco "Como ler a cotação", **When** exibido, **Then** explica que alta da cotação
   significa desvalorização do real diante daquela moeda, com exemplo numérico.
5. **Given** a pergunta "Câmbio é o mesmo que inflação?", **When** expandida, **Then** explica a
   diferença entre os dois conceitos.

---

### User Story 6 - Explorar moeda em circulação, base monetária e agregados (Priority: P3) — Entrega 3

A pessoa entende quanto dinheiro existe na economia e diferencia produção física de cédulas,
dinheiro em circulação e expansão monetária.

**Why this priority**: conteúdo educativo importante, mas com séries mais complexas.

**Independent Test**: alternar entre as séries (em circulação, base monetária, agregados M1–M4),
conferir valores com o BCB e verificar a seção de produção de cédulas com anos não publicados.

**Acceptance Scenarios**:

1. **Given** o bloco "Três ideias que costumam ser confundidas", **When** exibido, **Then**
   diferencia: produção física de cédulas e moedas (unidade: milhões de unidades), dinheiro em
   circulação (R$ bilhões) e expansão monetária (variação %, sobre R$ bilhões).
2. **Given** o aviso "Fabricar cédulas não é, por si só, criar dinheiro", **When** exibido,
   **Then** explica que novas cédulas em grande parte substituem cédulas gastas.
3. **Given** as séries históricas, **When** a pessoa alterna as abas, **Then** cada série mostra
   unidade (R$ bilhões, saldo de fim de mês), fonte, período e atualização.
4. **Given** a seção de produção física, **When** um ano ainda não tem dado publicado, **Then** o
   ano aparece como "Não publicado", com marcação vazia, nunca com estimativa.
5. **Given** o bloco "Mais moeda significa mais inflação?", **When** exibido, **Then** afirma que a
   relação não é direta e lista outros fatores, sem afirmar causalidade.
6. **Given** o glossário, **When** a pessoa expande Base monetária, M1, M2, M3 e M4, **Then** cada
   termo tem definição em linguagem simples.

---

### User Story 7 - Comparar indicadores em base 100 (Priority: P3) — Entrega 4

A pessoa escolhe até quatro indicadores e um período e vê como eles evoluíram a partir do mesmo
ponto de partida, sem ser induzida a ver causa onde há só movimento conjunto.

**Why this priority**: recurso analítico avançado que depende das séries das entregas anteriores.

**Independent Test**: selecionar combinações de indicadores, conferir que todos começam em 100 no
mês inicial e que a tabela de valores originais confere com as séries.

**Acceptance Scenarios**:

1. **Given** a lista (IPCA número-índice, dólar, euro, Selic meta, base monetária, M2), **When** a
   pessoa marca indicadores, **Then** o contador mostra "n de 4" e um quinto não pode ser marcado
   (com mensagem explicativa).
2. **Given** indicadores e período escolhidos, **When** aplicados, **Then** cada série é dividida
   pelo seu valor no mês inicial e multiplicada por 100, e todas partem de 100.
3. **Given** o gráfico, **When** exibido, **Then** abaixo há a tabela "Valores e unidades
   originais" com indicador, unidade, valor inicial, valor final e base 100 no fim.
4. **Given** a página, **When** exibida, **Then** há os blocos "O que é base 100?" e "Andar junto
   não é causar", visíveis sem interação.
5. **Given** um indicador sem valor no mês inicial do período, **When** aplicado, **Then** esse
   indicador não é exibido e um aviso explica o motivo, sem preencher o valor ausente.

---

### User Story 8 - Consultar o catálogo de dados e a metodologia (Priority: P2/P3) — Entrega 1 (parcial) e Entrega 4 (completa)

A pessoa confere, para cada indicador, fonte oficial, unidade, frequência, período disponível e
última atualização, baixa a série completa em CSV e entende o caminho de cada número.

**Why this priority**: concretiza a transparência exigida pela constituição. Na Entrega 1, o
catálogo já existe com o IPCA; as demais entradas aparecem com o selo "Aguardando integração" ou
"Em definição" até que suas séries sejam entregues.

**Independent Test**: para cada entrada do catálogo, conferir os metadados com a fonte e baixar o
CSV; verificar o estado das entradas ainda não integradas.

**Acceptance Scenarios**:

1. **Given** o catálogo, **When** exibido, **Then** lista IPCA, câmbio PTAX (dólar e euro), Selic
   meta, base monetária, agregados M1 a M4 e produção de cédulas e moedas, cada um com descrição,
   fonte oficial com link, unidade, frequência, período disponível, última atualização e selo de
   estado (Atualizado, Aguardando integração, Em definição, Falha na atualização).
2. **Given** um indicador integrado, **When** a pessoa aciona "Baixar CSV", **Then** recebe a série
   completa; **Given** um indicador não integrado, **Then** o botão aparece indisponível com o texto
   "Disponível após a integração com a fonte".
3. **Given** a seção "O caminho de cada número", **When** exibida, **Then** descreve coleta,
   armazenamento, tratamento e apresentação, e declara que meses não publicados são identificados e
   nunca preenchidos com estimativas.
4. **Given** a seção "Sobre o projeto", **When** exibida, **Then** apresenta o projeto, o autor e o
   desenvolvimento orientado por especificações (requisitos, planejamento, tarefas).

---

### Edge Cases

- **Mês ainda não publicado**: o período ou a simulação terminam no último mês disponível, com
  aviso explícito do mês pedido e do mês usado. Nenhum valor é estimado.
- **Lacuna no meio da série** (mês ausente na fonte): o gráfico mostra interrupção na linha, a
  tabela mostra "sem dado" e cálculos que dependem do mês ausente (acumulados, base 100, simulador)
  não são realizados, com mensagem que nomeia o mês ausente.
- **Período sem nenhuma observação**: estado "Sem dados — não há valores para o período escolhido",
  sem gráfico vazio enganoso.
- **Falha na atualização**: se a coleta mais recente falhar, o site continua exibindo a última
  versão válida, com selo "Falha na atualização" e a data da última atualização bem-sucedida.
- **Nenhuma versão válida disponível**: o bloco mostra o estado de falha, sem números.
- **Período personalizado inválido**: início posterior ao fim, datas fora da série ou campos vazios
  impedem a aplicação e exibem mensagem junto ao campo.
- **Revisão da fonte**: se a fonte revisar valores passados, a nova versão substitui a anterior e a
  data de atualização reflete a revisão; a versão anterior permanece recuperável.
- **Mudança de unidade ou metodologia da fonte** (ex.: troca de base do número-índice): a série
  tratada é mantida na unidade documentada no catálogo; a mudança é registrada na metodologia.
- **Valores muito grandes no simulador** (ex.: R$ 1.000.000.000,00): o resultado é exibido com
  separadores brasileiros, sem notação científica e sem quebrar o layout.
- **Movimento reduzido**: quem prefere menos movimento não vê animações de pulsação nos estados de
  carregamento.
- **Navegador com recursos limitados ou conexão lenta**: o conteúdo textual e as explicações continuam legíveis; o
  estado de carregamento aparece enquanto os dados chegam.

## Requirements *(mandatory)*

### Functional Requirements

**Estrutura, navegação e contatos**

- **FR-001**: O site MUST ser público, gratuito, sem cadastro e todo em português do Brasil.
- **FR-002**: O site MUST ter as páginas: Início, Visão geral (painel), Poder de compra, Câmbio,
  Moeda em circulação, Comparar indicadores e Sobre e metodologia (catálogo).
- **FR-003**: Todas as páginas MUST ter o mesmo cabeçalho de navegação, com destaque visual e
  semântico para a página atual, e o mesmo rodapé.
- **FR-004**: O rodapé MUST conter os contatos do autor — LinkedIn (abre em nova aba, avisando
  isso) e e-mail —, os links das páginas, a frase de fontes de dados e o nome do autor.
- **FR-005**: Páginas ainda não entregues MUST NOT aparecer como links ativos; seus atalhos MUST
  aparecer identificados como "Em breve".

**Transparência dos indicadores**

- **FR-010**: Todo indicador, cartão, gráfico, tabela e arquivo CSV MUST exibir fonte oficial,
  unidade, período de referência e data de atualização.
- **FR-011**: Dados ilustrativos MUST ser identificados por rótulo textual ("Ilustrativo",
  "Dados ilustrativos"); dados reais MUST NOT carregar esse rótulo; os dois MUST NOT ser
  misturados numa mesma série.
- **FR-012**: O site MUST NOT inventar, interpolar, estimar ou repetir observações ausentes; meses
  ausentes ou não publicados MUST ser identificados como tal.
- **FR-013**: Cada indicador MUST ter explicação em linguagem simples ("O que é?") acessível na
  própria página.
- **FR-014**: O site MUST diferenciar, com textos explícitos, quatro conceitos: inflação (alta
  geral de preços, IPCA), desvalorização cambial (mais reais por moeda estrangeira), expansão
  monetária (crescimento da quantidade de moeda, base monetária e agregados) e produção física de
  cédulas e moedas (unidades fabricadas, não valor novo na economia).
- **FR-015**: Textos, títulos e resumos MUST NOT afirmar causalidade entre indicadores; onde séries
  aparecem juntas, MUST haver aviso de que movimento conjunto não comprova causa.

**Períodos, gráficos e tabelas**

- **FR-020**: Páginas com séries MUST permitir escolher período entre 12 meses, 3 anos, 5 anos,
  10 anos e personalizado (mês/ano inicial e final); o padrão MUST ser 5 anos até o último mês
  publicado.
- **FR-021**: Todo gráfico MUST ter alternativa em tabela com os mesmos valores, título, unidade,
  eixo com rótulos, leitura de ponto por ponteiro, toque e teclado, e séries distinguidas por cor
  **e** padrão de traço.
- **FR-022**: A inflação acumulada entre o mês inicial *a* e o mês final *b* (inclusive) MUST ser
  calculada pelo encadeamento das variações mensais do IPCA de *a* até *b*:
  fator = ∏ (1 + variação mensal/100); acumulado (%) = (fator − 1) × 100. O número de meses
  considerados MUST ser exibido.
- **FR-023**: Variações percentuais de séries de nível (câmbio, base monetária, agregados) MUST
  ser calculadas como (valor final / valor inicial − 1) × 100, informando quais observações foram
  usadas.
- **FR-024**: Números MUST ser exibidos no padrão brasileiro (vírgula decimal, ponto de milhar,
  "R$"), com casas decimais documentadas por indicador; datas na tela em "mmm/aaaa" ou "dd/mm/aaaa".

**Simulador de poder de compra**

- **FR-025**: O simulador MUST receber valor em reais (padrão brasileiro, até 2 casas decimais,
  maior que zero) e mês/ano inicial e final.
- **FR-026**: O resultado MUST mostrar valor corrigido (valor × fator, arredondado a centavos
  somente na exibição), inflação acumulada, mudança no poder de compra
  ((1/fator − 1) × 100), equivalente do valor original em reais do mês inicial (valor / fator) e
  número de meses.
- **FR-027**: O simulador MUST explicar o cálculo passo a passo com os números da simulação.
- **FR-028**: Entradas inválidas MUST impedir o cálculo e exibir mensagem junto ao campo, em texto,
  associada ao campo para tecnologias assistivas.

**Download de dados**

- **FR-030**: Cada série integrada MUST poder ser baixada em CSV, tanto o recorte do período
  escolhido quanto a série completa (no catálogo). O arquivo MUST conter colunas de data
  (AAAA-MM-DD), valor e unidade, e informar fonte, código da série, natureza (real/ilustrativo) e
  data de atualização. Observações ausentes MUST aparecer como vazias, nunca preenchidas.
- **FR-031**: O CSV MUST abrir corretamente em planilhas brasileiras comuns (separador e
  codificação documentados na página de metodologia).

**Estados dos dados**

- **FR-040**: Todo bloco de dados MUST ter os estados: **Carregando** (esqueleto com indicação
  textual para leitores de tela; pulsação desligada para quem prefere menos movimento), **Sem
  dados** ("Não há valores para o período escolhido"), **Falha na atualização** (mostra a última
  versão válida e avisa; sem versão válida, mostra só o aviso), **Ainda não publicado** (mês mais
  recente não divulgado pela fonte) e **Entrada inválida** (mensagem junto ao campo).
- **FR-041**: Cada estado MUST ser comunicado por texto e ícone, não apenas por cor.
- **FR-042**: O catálogo MUST exibir, por indicador, um selo de situação: Atualizado, Aguardando
  integração, Em definição ou Falha na atualização.

**Engenharia de dados**

- **FR-050**: As séries MUST ser obtidas apenas de fontes oficiais (IBGE para IPCA; Banco Central
  do Brasil para câmbio PTAX, Selic, base monetária, agregados e meio circulante; publicações
  oficiais do BCB e da Casa da Moeda para produção de cédulas).
- **FR-051**: Os dados brutos coletados MUST ser preservados com data de coleta, separados dos dados
  tratados, permitindo refazer qualquer número exibido.
- **FR-052**: O tratamento MUST padronizar datas e unidades, detectar lacunas e valores fora do
  padrão e registrar o que encontrou, sem corrigir dados silenciosamente.
- **FR-053**: A atualização das séries MUST ocorrer automaticamente ao menos uma vez por dia; uma
  falha MUST manter a última versão válida publicada.
- **FR-054**: Cada indicador MUST ter registro de metadados (nome, descrição, fonte, código da
  série, link de origem, unidade, frequência, período disponível, última atualização, natureza,
  situação) usado tanto pelo site quanto pelos arquivos CSV.

**Acessibilidade e responsividade**

- **FR-060**: Todas as páginas MUST atender WCAG 2.1 AA: navegação completa por teclado com foco
  visível, contraste mínimo, estrutura de títulos, textos alternativos e rótulos de formulário.
- **FR-061**: O layout MUST funcionar de 360 px a telas largas sem rolagem horizontal da página; no
  celular, os cartões empilham em uma coluna e a navegação vira uma fileira rolável.

### Key Entities

- **Indicador**: conceito econômico acompanhado (ex.: IPCA, dólar PTAX). Atributos: nome,
  descrição simples, fonte oficial, código da série, link de origem, unidade, frequência, casas
  decimais, natureza (real/ilustrativo), situação de integração.
- **Série**: sequência temporal de observações de um indicador, em uma versão.
- **Observação**: valor de uma série em uma data de referência; pode estar "ausente" ou "não
  publicada", nunca estimada.
- **Coleta**: registro de uma busca na fonte — data/hora, resultado (sucesso/falha), dados brutos
  obtidos.
- **Versão da série**: resultado do tratamento de uma coleta bem-sucedida; a mais recente válida é
  a publicada.
- **Período de referência**: intervalo mês/ano inicial e final escolhido pelo usuário.
- **Simulação**: valor, mês inicial, mês final pedido, mês final usado, fator, resultados.
- **Conceito do glossário**: termo (IPCA, PTAX, Selic, base monetária, M1–M4, base 100) e
  explicação simples.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Para 100% dos casos de referência (ao menos 10 combinações de valor e período,
  incluindo mês único, 12 meses e mais de 10 anos), o simulador difere em no máximo R$ 0,01 do
  valor calculado à mão a partir da série oficial do IPCA.
- **SC-002**: Para 100% dos períodos testados, a inflação acumulada exibida confere, com a mesma
  quantidade de casas decimais, com o acumulado calculado a partir da série oficial.
- **SC-003**: 100% dos cartões, gráficos, tabelas e arquivos CSV exibem fonte, unidade, período e
  data de atualização (verificação por inspeção de todas as páginas entregues).
- **SC-004**: 0 observações inventadas: em testes com séries contendo lacunas e meses não
  publicados, nenhum gráfico, tabela, cálculo ou CSV apresenta valor para o mês ausente.
- **SC-005**: Os cinco estados (carregando, sem dados, falha, não publicado, entrada inválida) são
  reproduzíveis e exibidos corretamente em todas as páginas com dados.
- **SC-006**: A página inicial e as páginas da Entrega 1 mostram conteúdo útil em até 3 segundos
  numa conexão móvel 4G típica.
- **SC-007**: Verificação automática e manual de acessibilidade sem nenhuma falha de nível A ou AA
  nas páginas entregues; todas as tarefas principais concluídas só com teclado.
- **SC-008**: Nenhuma página apresenta rolagem horizontal em larguras de 360, 768 e 1440 px.
- **SC-009**: Em teste com ao menos 5 pessoas sem formação em economia, ao menos 4 conseguem, sem
  ajuda e em até 2 minutos, simular o poder de compra e explicar com suas palavras a diferença entre
  inflação e desvalorização cambial.
- **SC-010**: Todo arquivo CSV baixado abre em planilha comum com acentos e números corretos e
  contém exatamente as observações do período escolhido.
- **SC-011**: Uma falha simulada na coleta mantém o site publicado com a última versão válida e o
  selo "Falha na atualização" em 100% dos blocos afetados.
- **SC-012**: Nenhum texto do site afirma causalidade entre indicadores (verificado por revisão de
  todos os textos em cada entrega).

## Assumptions

- **Dados reais na Entrega 1**: o IPCA e o simulador da Entrega 1 usam a série real do IBGE. Os
  números das imagens de referência são ilustrativos; dados ilustrativos só podem aparecer em
  protótipos ou miniaturas decorativas, sempre rotulados.
- **Contatos**: o autor é Henry Gabriel Santos Silva; o endereço do LinkedIn e o e-mail serão
  fornecidos antes da publicação (as referências mostram marcadores provisórios). A publicação da
  Entrega 1 depende desses dois valores.
- **Frequência das séries**: IPCA mensal; câmbio PTAX diário, exibido como média mensal; Selic meta
  por reunião do Copom, exibida no valor vigente ao fim de cada mês; base monetária e agregados como
  saldo de fim de mês; produção de cédulas anual.
- **Conta de referência do simulador**: o acumulado inclui as variações do mês inicial e do mês
  final (FR-022), em linha com a prática de calculadoras oficiais de correção por índice; essa
  convenção será documentada na metodologia.
- **Histórico disponível**: as séries cobrem ao menos desde julho de 1994 (Plano Real), quando a
  fonte oferecer; o simulador aceita datas a partir desse marco.
- **Sem contas de usuário**: o site não coleta dados pessoais nem exige login; não há área
  administrativa pública.
- **Custo baixo**: o site e a atualização dos dados devem operar em serviços gratuitos ou de baixo
  custo, conforme a constituição; a escolha fica para o plano.
- **Fora do escopo**: projeções e previsões, opiniões de política econômica, dados de outras
  moedas além de dólar e euro, comparação entre países, idiomas além do português e aplicativo
  móvel nativo.
- **Referências visuais**: as imagens estão fora do repositório (em
  `~/Downloads/observatorio-do-real`); recomenda-se copiá-las para o projeto para que o plano e a
  implementação as referenciem de forma versionada.
