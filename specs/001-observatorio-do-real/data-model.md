# Modelo de Dados: Observatório do Real

Banco: Supabase PostgreSQL. Três camadas, cada uma em um **schema** próprio:

| Schema | Camada | Quem escreve | Quem lê |
|--------|--------|--------------|---------|
| `bruto` | Dados brutos, exatamente como vieram da fonte | rotina de coleta (`coletor`) | rotina de tratamento |
| `tratado` | Séries padronizadas, validadas e versionadas | rotina de tratamento (`coletor`) | rotina de publicação |
| `publico` | Resultados prontos para consulta | rotina de publicação (`coletor`) | API (`api_leitura`) e, opcionalmente, papel `anon` |

Princípios aplicados: III (metadados obrigatórios), IV (dados brutos preservados, cálculos
reproduzíveis), VII (papéis com privilégio mínimo).

## Diagrama

```text
            bruto                         tratado                            publico
 ┌───────────────────────┐   ┌─────────────────────────────────┐   ┌─────────────────────────┐
 │ coleta ───< payload   │──>│ versao_serie ───< observacao     │──>│ indicador_publicado     │
 │   (1 por execução e   │   │      │            (histórico SCD2)│   │ observacao_publicada    │
 │    indicador)         │   │      └──< ocorrencia_validacao   │   │ (snapshot da versão     │
 └───────────────────────┘   │ indicador (catálogo/metadados)   │   │  publicada)             │
                             └─────────────────────────────────┘   └─────────────────────────┘
```

## Schema `tratado` — catálogo

### `tratado.indicador`

Registro de metadados único, usado pelo site, pela API e pelos CSV (FR-054). Mantido em arquivo
versionado no repositório (`dados/catalogo.yaml`) e sincronizado ao banco pela rotina.

| Campo | Tipo | Regras |
|-------|------|--------|
| `codigo` | text PK | `^[a-z0-9_]+$`; ex.: `ipca`, `ipca_indice`, `dolar_ptax` |
| `nome` | text | obrigatório |
| `descricao` | text | linguagem simples (FR-013) |
| `instituicao` | text | `IBGE` ou `Banco Central do Brasil` etc. (FR-050) |
| `codigo_serie` | text | ex.: `SIDRA 1737/v63`, `SGS 433` |
| `url_origem` | text | URL pública da fonte |
| `conector` | text | `sidra`, `sgs`, `olinda`, `manual` |
| `parametros_conector` | jsonb | ex.: `{"tabela":1737,"variavel":63}` |
| `unidade` | text | obrigatório (Princípio III) |
| `frequencia_fonte` | text | `diaria`, `mensal`, `anual`, `por_reuniao` |
| `frequencia_exibicao` | text | `mensal` ou `anual` |
| `agregacao_mensal` | text null | `media`, `fim_de_mes`, `vigente_fim_de_mes`; null se já mensal |
| `casas_decimais` | smallint | 0–6 |
| `natureza` | text | `real` \| `ilustrativo` — CHECK |
| `janela_revisao_meses` | smallint | quantos meses recentes são recoletados a cada execução |
| `situacao_catalogo` | text | `ativo`, `aguardando_integracao`, `em_definicao` |
| `entrega` | smallint | 1–4 |
| `versao_publicada_id` | bigint null FK → `versao_serie.id` | **ponteiro da versão publicada** |

## Schema `bruto`

### `bruto.coleta`

Uma linha por tentativa de coleta de um indicador.

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | bigint identity PK | |
| `indicador_codigo` | text FK | |
| `execucao_id` | uuid | agrupa as coletas de uma mesma execução da rotina |
| `iniciada_em` / `concluida_em` | timestamptz | |
| `status` | text | `sucesso`, `falha`, `sem_novidade` — CHECK |
| `url_requisitada` | text | sem segredos |
| `parametros` | jsonb | intervalo pedido (`data_inicial`, `data_final`) |
| `http_status` | int null | |
| `erro` | text null | mensagem técnica (não exibida ao público) |
| `payload_id` | bigint null FK | null em falha |

### `bruto.payload`

Conteúdo bruto preservado (FR-051), deduplicado por hash.

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | bigint identity PK | |
| `sha256` | char(64) UNIQUE | hash SHA-256 dos bytes recebidos, concatenados na ordem das requisições (separados por `\n`) |
| `conteudo` | jsonb | **lista** com o corpo JSON de cada resposta da fonte, na ordem das requisições, sem alteração de valores (uma requisição para o SIDRA; uma por bloco de até 10 anos nas séries diárias do SGS) |
| `tamanho_bytes` | int | |
| `recebido_em` | timestamptz | |

**Prevenção de duplicidade**: `INSERT ... ON CONFLICT (sha256) DO NOTHING`. Se o hash já existe,
a coleta é registrada com `status = 'sem_novidade'` apontando para o payload existente e o
tratamento não gera nova versão.

## Schema `tratado` — séries

### `tratado.versao_serie`

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | bigint identity PK | |
| `indicador_codigo` | text FK | |
| `coleta_id` | bigint FK | coleta que originou a versão |
| `criada_em` | timestamptz | |
| `status` | text | ver máquina de estados abaixo |
| `n_observacoes` | int | |
| `primeira_data` / `ultima_data` | date | |
| `n_inseridas` / `n_revisadas` / `n_inalteradas` | int | resultado do merge |
| `hash_conteudo` | char(64) | hash das observações vigentes após o merge |
| `versao_codigo` | text | versão do código de tratamento (git SHA), para reprodutibilidade |

**Máquina de estados**

```text
em_tratamento ──> validada ──> publicada ──> substituida
      │               │
      └──> rejeitada <┘   (falha de validação bloqueante)
```

- Só uma versão por indicador fica `publicada` (índice único parcial
  `WHERE status = 'publicada'`).
- Uma versão `rejeitada` nunca é publicada; a publicada anterior continua no ar (FR-053).

### `tratado.observacao`

Histórico de valores por data de referência, com controle de revisões em estilo SCD tipo 2.

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | bigint identity PK | |
| `indicador_codigo` | text FK | |
| `data_referencia` | date | séries mensais: dia 01; diárias: a própria data |
| `valor` | numeric(20,6) null | null ⇒ ausente na fonte |
| `situacao` | text | `ok` \| `ausente` — CHECK (`ausente` ⇔ `valor IS NULL`) |
| `versao_inicio_id` | bigint FK | versão em que este valor passou a valer |
| `versao_fim_id` | bigint null FK | versão que o substituiu (null = vigente) |

Restrições:

- `UNIQUE (indicador_codigo, data_referencia) WHERE versao_fim_id IS NULL` — no máximo um valor
  vigente por data (**prevenção de duplicidade**).
- Nunca há `UPDATE` de `valor`; revisões fecham a linha antiga e abrem outra.

### `tratado.ocorrencia_validacao`

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | bigint PK | |
| `versao_id` | bigint FK | |
| `regra` | text | ex.: `lacuna`, `fora_do_intervalo`, `data_duplicada_na_fonte`, `queda_de_cobertura` |
| `severidade` | text | `bloqueante` \| `aviso` |
| `data_referencia` | date null | |
| `detalhe` | jsonb | |

## Schema `publico`

Tabelas de leitura, regravadas pela rotina de publicação **dentro de uma transação** que também
move o ponteiro `versao_publicada_id`. Assim a API sempre lê um snapshot consistente.

### `publico.indicador_publicado`

Projeção de `tratado.indicador` mais o estado de atualização:
`codigo`, `nome`, `descricao`, `instituicao`, `codigo_serie`, `url_origem`, `unidade`,
`frequencia`, `casas_decimais`, `natureza`, `situacao` (`atualizado`, `aguardando_integracao`,
`em_definicao`, `falha_atualizacao`), `periodo_inicio`, `periodo_fim`,
`ultima_atualizacao_valida`, `ultima_tentativa`, `mensagem_publica`, `versao_id`, `publicado`
(boolean).

### `publico.observacao_publicada`

`indicador_codigo`, `data_referencia` (já na frequência de exibição), `valor`, `situacao`.
PK `(indicador_codigo, data_referencia)`. Inclui uma linha `ausente` para cada mês sem dado
entre a primeira e a última data, para a interface mostrar a lacuna (FR-012).

## Fluxo de atualização incremental

Para cada indicador ativo, a rotina diária executa:

1. **Coleta**: pede à fonte o intervalo
   `[última data vigente − janela_revisao_meses, hoje]`. Na primeira carga, ou no primeiro dia de
   cada mês (**recarga completa** mensal), pede todo o histórico em blocos permitidos pela fonte.
   Grava `bruto.coleta` e `bruto.payload` (deduplicado por hash).
2. **Tratamento**: converte o payload em observações padronizadas (data, valor `Decimal`,
   unidade), agrega para mensal quando necessário, e cria `versao_serie` em `em_tratamento`.
3. **Merge**: para cada data recebida, compara com a observação vigente:
   - inexistente → insere (`n_inseridas`);
   - igual → nada (`n_inalteradas`);
   - diferente → fecha a vigente (`versao_fim_id`) e insere a nova (`n_revisadas`) — **revisão**.
   Datas vigentes **fora** do intervalo coletado não são tocadas. Datas que estavam vigentes,
   estão **dentro** do intervalo e desapareceram da fonte geram ocorrência `queda_de_cobertura`
   (bloqueante): a fonte não "apaga" histórico sem revisão humana.
4. **Validação** (regras na tabela abaixo). Bloqueante ⇒ `rejeitada` e a transação de merge é
   desfeita (rollback); avisos ficam registrados.
5. **Publicação**: em uma transação, regrava `publico.*` do indicador, marca a versão como
   `publicada`, a anterior como `substituida` e move `versao_publicada_id`.
6. **Falha** em qualquer etapa: registra `coleta.status = 'falha'` (ou versão `rejeitada`),
   atualiza apenas `publico.indicador_publicado.situacao = 'falha_atualizacao'`,
   `ultima_tentativa` e `mensagem_publica`; **as observações publicadas não mudam**.

Idempotência: rodar a rotina duas vezes seguidas não cria versões novas (hash do payload igual ⇒
`sem_novidade`; merge sem diferenças ⇒ versão não é criada).

## Regras de validação

| Regra | Severidade | Descrição |
|-------|-----------|-----------|
| `esquema_invalido` | bloqueante | campos esperados ausentes ou com tipo errado |
| `data_duplicada_na_fonte` | bloqueante | mesma data duas vezes no payload |
| `queda_de_cobertura` | bloqueante | datas vigentes sumiram da fonte |
| `serie_vazia` | bloqueante | payload sem observações quando eram esperadas |
| `fora_do_intervalo` | bloqueante | valor fora de limites plausíveis do indicador (ex.: IPCA mensal fora de −5 % a +100 %) |
| `lacuna` | aviso | mês faltando entre a primeira e a última data |
| `revisao_grande` | aviso | revisão com diferença relativa > 1 % |
| `valor_nao_numerico` | aviso | valor da fonte vazio ou "..." ⇒ vira `ausente` |
| `data_futura` | aviso | data posterior a hoje (ex.: Selic meta no SGS 432) ⇒ descartada |
| `divergencia_fontes` | aviso | IPCA do SIDRA difere do SGS 433 no mesmo mês |

## Papéis e acesso (Supabase)

| Papel | Tipo | Permissões |
|-------|------|-----------|
| `coletor` | papel de login próprio, usado só pela rotina | `USAGE` e DML em `bruto`, `tratado`, `publico` |
| `api_leitura` | papel de login próprio, usado só pela API | `USAGE` + `SELECT` em `publico`; nada em `bruto`/`tratado` |
| `anon`, `authenticated` | papéis da API de dados do Supabase | sem acesso a `bruto`/`tratado`; `SELECT` em `publico` **somente** onde `publicado = true` (RLS) |
| `service_role` | Supabase | não é usado pela aplicação |

- **RLS ativado em todas as tabelas** dos três schemas.
- `publico.*`: política `SELECT` para `anon, authenticated, api_leitura` com
  `USING (publicado = true)` (em `observacao_publicada`, via `EXISTS` no indicador publicado).
- `bruto.*` e `tratado.*`: nenhuma política para `anon`/`authenticated` ⇒ acesso negado.
- A API de dados do Supabase expõe apenas o schema `publico` (ou nenhum; ver research.md, R-07).
- Senhas dos papéis ficam apenas nos segredos do servidor e das rotinas (Princípio VII).

## Mapeamento para as entidades da especificação

| Entidade (spec) | Onde fica |
|-----------------|-----------|
| Indicador | `tratado.indicador` → `publico.indicador_publicado` |
| Série / Versão da série | `tratado.versao_serie` |
| Observação | `tratado.observacao` → `publico.observacao_publicada` |
| Coleta | `bruto.coleta` + `bruto.payload` |
| Período de referência | parâmetro da API (não persistido) |
| Simulação | calculada na API (não persistida; site sem dados pessoais) |
| Conceito do glossário | conteúdo da interface (`frontend/src/conteudo/glossario.ts`) |
