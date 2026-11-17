---

description: "Lista de tarefas do Observatório do Real"
---

# Tasks: Observatório do Real

**Input**: Documentos de design em `specs/001-observatorio-do-real/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: INCLUÍDOS. A constituição (Princípio IV) exige testes automatizados para toda regra
econômica e transformação de dados, e a spec define critérios verificáveis (SC-001 a SC-012).
Testes de cada história são escritos antes da implementação e devem falhar primeiro.

**Organization**: tarefas agrupadas por história de usuário. As Fases 1 a 6 formam a
**Entrega 1 (MVP)**. As Fases 7 a 10 cobrem as Entregas 2 a 4 e começam por uma tarefa de
validação das fontes marcadas como **A VALIDAR** em `research.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa pendente)
- **[Story]**: história da spec (US1 a US8)
- Caminhos: `backend/src/observatorio/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`,
  `supabase/migrations/`, `dados/`

## Convenções para todas as tarefas

- Documentação, comentários, mensagens ao usuário e nomes de domínio em **português do Brasil**.
- Valores econômicos sempre em `decimal.Decimal` no Python; nunca `float`.
- Nenhuma tarefa pode estimar, interpolar ou repetir observações ausentes (FR-012).
- Nenhum segredo em código ou em arquivo versionado; só em `.env` (ignorado) e em segredos de
  CI/hospedagem (Princípio VII).

---

## Phase 1: Setup (infraestrutura compartilhada)

**Purpose**: estrutura do repositório, ferramentas e CI.

- [X] T001 Criar a estrutura de diretórios do plano na raiz: `dados/`, `dados/manuais/`, `supabase/migrations/`, `backend/src/observatorio/{coleta,tratamento,publicacao,regras,repositorio,api}/`, `backend/tests/{fixtures,unit,integration,contract}/`, `frontend/`, `docs/referencias-visuais/{desktop,celular}/`, `.github/workflows/`
- [X] T002 Copiar as imagens de `~/Downloads/observatorio-do-real/desktop/*.png` e `~/Downloads/observatorio-do-real/celular/*.png` para `docs/referencias-visuais/desktop/` e `docs/referencias-visuais/celular/`, e criar `docs/referencias-visuais/README.md` com a tabela página ↔ imagem da seção "Visão Geral e Referências Visuais" de `specs/001-observatorio-do-real/spec.md`
- [X] T003 Inicializar o projeto Python com uv em `backend/pyproject.toml` (Python 3.12; dependências: fastapi, uvicorn[standard], pydantic>=2, pydantic-settings, httpx, tenacity, psycopg[binary,pool]>=3, typer, pyyaml; dev: pytest, pytest-cov, respx, ruff, schemathesis ou openapi-core) e script de console `observatorio = "observatorio.cli:app"`
- [X] T004 [P] Configurar ruff (lint + format, `line-length = 100`, regras E, F, I, B, UP, DTZ, S) em `backend/pyproject.toml` e pytest com marcador `fontes_reais` (desligado por padrão) e `integracao`
- [X] T005 [P] Inicializar a interface com Vite + React 19 + TypeScript estrito em `frontend/` (`npm create vite@latest`), adicionando react-router, @tanstack/react-query, recharts; dev: vitest, @testing-library/react, @testing-library/user-event, jsdom, @playwright/test, @axe-core/playwright, openapi-typescript, eslint, eslint-plugin-jsx-a11y, prettier
- [X] T006 [P] Configurar ESLint (incluindo `jsx-a11y` recomendado), Prettier, `tsc --noEmit` e scripts `lint`, `typecheck`, `test`, `test:e2e`, `gerar:tipos` em `frontend/package.json`
- [X] T007 [P] Inicializar o Supabase CLI na raiz (`supabase init`) gerando `supabase/config.toml`; no `config.toml`, deixar a API de dados expondo apenas o schema `publico` no ambiente local
- [X] T008 [P] Criar `.gitignore` na raiz cobrindo `.env`, `.env.*` (exceto `.env.example`), `.venv/`, `node_modules/`, `dist/`, `supabase/.temp/`, `*.dump`, `playwright-report/`, `test-results/`
- [X] T009 [P] Criar `backend/.env.example` com `COLETOR_DATABASE_URL=`, `API_DATABASE_URL=`, `CORS_ORIGENS=http://localhost:5173`, `AMBIENTE=local` (sem valores reais) e `frontend/.env.example` com `VITE_API_URL=http://localhost:8000`
- [X] T010 Criar o workflow de CI em `.github/workflows/ci.yml`: jobs `backend` (uv sync, ruff check, ruff format --check, pytest com Postgres via `supabase start`), `frontend` (npm ci, lint, typecheck, vitest, build, playwright com axe), `segredos` (gitleaks) e `contrato` (compara o OpenAPI servido pela API com `specs/001-observatorio-do-real/contracts/api-openapi.yaml`)
- [X] T011 [P] Reescrever `README.md` em português: propósito, arquitetura (diagrama do plan.md), execução local (link para `specs/001-observatorio-do-real/quickstart.md`), fontes oficiais, custos e como reativar o agendamento do GitHub Actions após 60 dias sem atividade

---

## Phase 2: Foundational (pré-requisitos bloqueantes)

**Purpose**: banco, catálogo, pipeline de dados do IPCA, base da API e casca da interface. As
histórias US1, US2, US3 e US8 dependem desta fase.

**⚠️ CRITICAL**: nenhuma história começa antes do fim desta fase.

### Banco de dados (Supabase PostgreSQL)

- [X] T012 Criar `supabase/migrations/0001_schemas_e_papeis.sql`: schemas `bruto`, `tratado`, `publico`; papéis de login `coletor` e `api_leitura` (`NOLOGIN` na migração; senha definida fora do repositório com `ALTER ROLE ... LOGIN PASSWORD` documentado no quickstart); `REVOKE ALL` de `public`, `anon` e `authenticated` em `bruto` e `tratado`; `GRANT USAGE` e DML em `bruto`, `tratado`, `publico` para `coletor`; `GRANT USAGE` + `SELECT` em `publico` para `api_leitura`, `anon` e `authenticated`
- [X] T013 Criar `supabase/migrations/0002_tratado_indicador.sql` com `tratado.indicador` conforme `data-model.md`: `codigo` text PK com CHECK `codigo ~ '^[a-z0-9_]+$'`; `nome`, `descricao`, `instituicao`, `url_origem`, `unidade` NOT NULL; `codigo_serie`; `conector` CHECK em (`sidra`, `sgs`, `olinda`, `manual`); `parametros_conector` jsonb; `frequencia_fonte` CHECK em (`diaria`, `mensal`, `anual`, `por_reuniao`); `frequencia_exibicao` CHECK em (`mensal`, `anual`); `agregacao_mensal` CHECK em (`media`, `fim_de_mes`, `vigente_fim_de_mes`) ou NULL; `casas_decimais` smallint CHECK 0–6; `natureza` CHECK em (`real`, `ilustrativo`); `janela_revisao_meses` smallint; `situacao_catalogo` CHECK em (`ativo`, `aguardando_integracao`, `em_definicao`); `entrega` smallint CHECK 1–4; `versao_publicada_id` bigint NULL (FK adicionada em T015)
- [X] T014 Criar `supabase/migrations/0003_bruto.sql`: `bruto.payload` (`id` identity PK, `sha256` char(64) UNIQUE NOT NULL, `conteudo` jsonb NOT NULL, `tamanho_bytes` int, `recebido_em` timestamptz) e `bruto.coleta` (`id` identity PK, `indicador_codigo` FK, `execucao_id` uuid, `iniciada_em`, `concluida_em`, `status` CHECK em (`sucesso`, `falha`, `sem_novidade`), `url_requisitada`, `parametros` jsonb, `http_status` int NULL, `erro` text NULL, `payload_id` FK NULL) com índice em `(indicador_codigo, iniciada_em DESC)`
- [X] T015 Criar `supabase/migrations/0004_tratado_series.sql`: `tratado.versao_serie` (campos de `data-model.md`; `status` CHECK em (`em_tratamento`, `validada`, `rejeitada`, `publicada`, `substituida`); índice único parcial `(indicador_codigo) WHERE status = 'publicada'`; `versao_codigo` text NOT NULL); `tratado.observacao` (`valor` numeric(20,6) NULL; `situacao` CHECK em (`ok`, `ausente`) e CHECK `(situacao = 'ausente') = (valor IS NULL)`; `versao_inicio_id` FK NOT NULL; `versao_fim_id` FK NULL; índice único parcial `(indicador_codigo, data_referencia) WHERE versao_fim_id IS NULL`); `tratado.ocorrencia_validacao` (`severidade` CHECK em (`bloqueante`, `aviso`)); FK `tratado.indicador.versao_publicada_id → tratado.versao_serie.id`
- [X] T016 Criar `supabase/migrations/0005_publico.sql`: `publico.indicador_publicado` (colunas de `data-model.md`, `situacao` CHECK em (`atualizado`, `aguardando_integracao`, `em_definicao`, `falha_atualizacao`), `publicado` boolean NOT NULL DEFAULT false, índice em `publicado`) e `publico.observacao_publicada` (PK `(indicador_codigo, data_referencia)`, `valor` numeric(20,6) NULL, `situacao` CHECK em (`ok`, `ausente`) com a mesma regra de nulidade)
- [X] T017 Criar `supabase/migrations/0006_rls.sql`: `ENABLE ROW LEVEL SECURITY` em **todas** as tabelas dos três schemas; política `SELECT` em `publico.indicador_publicado` para `anon, authenticated, api_leitura` com `USING (publicado = true)`; política `SELECT` em `publico.observacao_publicada` com `USING (EXISTS (SELECT 1 FROM publico.indicador_publicado i WHERE i.codigo = indicador_codigo AND i.publicado))`; políticas `ALL` para `coletor` nos três schemas; nenhuma política para `anon`/`authenticated` em `bruto`/`tratado`
- [X] T018 [P] Escrever teste de integração em `backend/tests/integration/test_seguranca_banco.py`: (a) toda tabela de `bruto`, `tratado`, `publico` tem `relrowsecurity = true`; (b) conectado como `anon`, `SELECT` em `bruto.coleta` e `tratado.observacao` falha ou retorna 0 linhas; (c) como `api_leitura`, linhas de `publico` com `publicado = false` não aparecem; (d) `api_leitura` não consegue `INSERT` em nenhum schema (cenário V13 do quickstart)
- [X] T019 [P] Escrever teste de integração em `backend/tests/integration/test_restricoes.py` cobrindo: CHECK de `natureza`, regra `ausente ⇔ valor IS NULL`, unicidade de observação vigente por data, unicidade de `sha256` e unicidade de versão `publicada` por indicador

### Catálogo

- [X] T020 Criar `dados/catalogo.yaml` com **todos** os indicadores da spec e os metadados de `research.md`: `ipca` (SIDRA tabela 1737, variável 63, "% ao mês", mensal, 2 casas, `janela_revisao_meses: 3`, `situacao_catalogo: ativo`, entrega 1, `url_origem: https://sidra.ibge.gov.br/tabela/1737`); `ipca_indice` (variável 2266, "número-índice (dez/1993 = 100)", 2 casas, ativo, entrega 1); `dolar_ptax` (SGS 3698, média mensal de venda, R$/US$), `euro_ptax` (SGS 21619, diária, `agregacao_mensal: media`, R$/€), `selic_meta` (SGS 432, `agregacao_mensal: vigente_fim_de_mes`, % a.a.) (`aguardando_integracao`, entrega 2); `base_monetaria` (SGS 1788), `papel_moeda_circulacao` (SGS 1786), `m1` (SGS 27791), `m2` (27810), `m3` (27813), `m4` (27815), todos em R$ mil na fonte e exibidos em R$ bilhões (`aguardando_integracao`, entrega 3); `producao_cedulas_moedas` (`em_definicao`, `conector: olinda`, serviço `mecir_prog_anual_producao`, entrega 3); todos com `natureza: real` e descrição em linguagem simples
- [X] T021 Implementar `backend/src/observatorio/catalogo.py`: carregar e validar `dados/catalogo.yaml` com Pydantic (mesmas regras dos CHECKs de T013) e sincronizar com `tratado.indicador` e `publico.indicador_publicado` (upsert por `codigo`; indicadores não ativos ficam com `publicado = true` e `situacao` igual a `situacao_catalogo`, sem observações, para o catálogo exibir o selo)
- [X] T022 [P] Teste unitário em `backend/tests/unit/test_catalogo.py`: rejeita `codigo` fora de `^[a-z0-9_]+$`, `natureza` inválida, `casas_decimais` fora de 0–6 e indicador sem `unidade` ou `instituicao`

### Configuração e acesso ao banco

- [X] T023 [P] Implementar `backend/src/observatorio/config.py` com pydantic-settings lendo `COLETOR_DATABASE_URL`, `API_DATABASE_URL`, `CORS_ORIGENS`, `AMBIENTE` do ambiente/`.env`; nunca registrar URLs com senha em log (mascarar)
- [X] T024 Implementar `backend/src/observatorio/repositorio/conexao.py`: pool psycopg 3 para o coletor (modo sessão) e pool mínimo para a API com `prepare_threshold=None` e `sslmode=require` fora do ambiente local (research R-07)

### Regras econômicas puras (Decimal)

- [X] T025 [P] Escrever testes em `backend/tests/unit/test_formulas.py` **antes** da implementação: fator e acumulado (FR-022) com ≥ 10 casos de referência calculados à mão a partir de valores reais do SIDRA gravados em `backend/tests/fixtures/sidra_1737_v63.json` (incluindo mês único, 12 meses, jan/2016–dez/2025 = 120 meses e um período > 10 anos); conferência pelo número-índice `I_b / I_{a−1}` dentro de 0,01 p.p.; valor corrigido em centavos com ROUND_HALF_UP; mudança no poder de compra `(1/F − 1) × 100`; equivalente `V / F`; lacuna ⇒ exceção `LacunaNaSerie` com a lista de meses ausentes; nenhum uso de `float` (SC-001, SC-002)
- [X] T026 Implementar `backend/src/observatorio/regras/ipca.py`: `fator_acumulado(variacoes, inicio, fim)`, `acumulado_percentual(fator)`, `simular_poder_de_compra(valor, variacoes, inicio, fim)` retornando os campos de `Simulacao` do contrato; precisão de contexto 28; arredondamento só na saída
- [X] T027 [P] Implementar `backend/src/observatorio/regras/periodo.py`: resolução de períodos `12m`, `3a`, `5a`, `10a` e personalizado `AAAA-MM` terminando no último mês publicado; cálculo de `fim_utilizado` e do texto `aviso_nao_publicado` ("O IPCA de set/2026 ainda não foi publicado pelo IBGE. O cálculo usa ago/2026."), com testes em `backend/tests/unit/test_periodo.py`
- [X] T028 [P] Implementar `backend/src/observatorio/regras/formatacao.py` com nomes de meses abreviados em português (`jan/2016`) para mensagens, com teste em `backend/tests/unit/test_formatacao.py`

### Pipeline de dados (coleta → tratamento → validação → publicação)

- [X] T029 [P] Gravar fixtures reais em `backend/tests/fixtures/`: `sidra_1737_v63.json` e `sidra_1737_v2266.json` (de jul/1994 a set/2026, obtidas de `https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/63/p/199407-202609` e `.../v/2266/...`), `sgs_433.json`, e variantes sintéticas derivadas: `sidra_com_lacuna.json` (um mês com `"V":"..."`), `sidra_revisada.json` (um valor alterado), `sidra_data_duplicada.json`, `sidra_esquema_invalido.json`
- [X] T030 [P] Escrever testes do conector em `backend/tests/unit/test_coleta_sidra.py` com respx: ignora o primeiro elemento (cabeçalho), converte `D3C` `AAAAMM` em `AAAA-MM-01`, converte `V` em `Decimal`, transforma `"..."`, `"-"`, `"X"` em `ausente`, aplica 3 tentativas com espera exponencial e timeout de 30 s e falha com erro claro após isso
- [X] T031 Implementar o conector `backend/src/observatorio/coleta/sidra.py` (`https://apisidra.ibge.gov.br/values/t/{tabela}/n1/all/v/{variavel}/p/{AAAAMM}-{AAAAMM}`) e a interface comum `backend/src/observatorio/coleta/base.py` (`Conector.coletar(indicador, data_inicial, data_final) -> RespostaBruta` com bytes, URL e status HTTP)
- [X] T032 [P] Implementar o conector `backend/src/observatorio/coleta/sgs.py` (`https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial=dd/mm/aaaa&dataFinal=dd/mm/aaaa`, divisão em blocos de no máximo 10 anos para séries diárias; resposta `{"erro":{"statusCode":404}}` para janela sem dados tratada como `sem_novidade`, não como falha), usado na Entrega 1 só para a conferência do IPCA pelo SGS 433, com testes em `backend/tests/unit/test_coleta_sgs.py`
- [X] T033 Implementar `backend/src/observatorio/repositorio/bruto.py`: gravar `bruto.payload` com `INSERT ... ON CONFLICT (sha256) DO NOTHING` e `bruto.coleta`; quando o hash já existe, registrar a coleta como `sem_novidade` apontando para o payload existente
- [X] T034 [P] Escrever testes em `backend/tests/unit/test_validacao.py` para cada regra de `data-model.md`: `esquema_invalido`, `data_duplicada_na_fonte`, `queda_de_cobertura`, `serie_vazia`, `fora_do_intervalo` (IPCA mensal fora de −5 % a +100 %) como **bloqueantes**; `lacuna`, `revisao_grande` (> 1 %), `valor_nao_numerico`, `data_futura` (descartada) e `divergencia_fontes` (SIDRA × SGS 433) como **avisos**
- [X] T035 Implementar `backend/src/observatorio/tratamento/padronizacao.py` (datas e unidades padronizadas, sem corrigir valores silenciosamente) e `backend/src/observatorio/tratamento/validacao.py` (regras de T034, gravando `tratado.ocorrencia_validacao`)
- [X] T036 [P] Escrever testes de integração em `backend/tests/integration/test_merge_revisoes.py`: inserção inicial; reexecução sem mudança ⇒ nenhuma versão nova (idempotência, V8); valor alterado ⇒ linha antiga com `versao_fim_id` preenchido e nova vigente, `n_revisadas = 1` (V7); datas vigentes fora do intervalo coletado intocadas; data vigente sumida dentro do intervalo ⇒ `queda_de_cobertura` e rollback
- [X] T037 Implementar `backend/src/observatorio/tratamento/merge.py`: merge SCD2 descrito em `data-model.md` ("Nunca há `UPDATE` de `valor`; revisões fecham a linha antiga e abrem outra"), com contagens `n_inseridas`, `n_revisadas`, `n_inalteradas`, `hash_conteudo` e `versao_codigo` (git SHA lido de `GITHUB_SHA` ou `git rev-parse`), usando `pg_advisory_xact_lock` por indicador
- [X] T038 [P] Escrever testes de integração em `backend/tests/integration/test_publicacao_e_falhas.py`: publicação gera linhas `ausente` para meses sem dado entre a primeira e a última data; troca de versão é atômica; falha de coleta (conector levanta erro) ou validação bloqueante mantém `publico.observacao_publicada` idêntica e muda só `situacao = 'falha_atualizacao'`, `ultima_tentativa` e `mensagem_publica` (V6, SC-011)
- [X] T039 Implementar `backend/src/observatorio/publicacao/publicar.py`: em uma transação, regravar `publico.observacao_publicada` e `publico.indicador_publicado` do indicador, marcar a versão como `publicada`, a anterior como `substituida` e mover `tratado.indicador.versao_publicada_id`; e `registrar_falha(indicador, mensagem)` que só altera o estado de atualização
- [X] T040 Implementar o orquestrador `backend/src/observatorio/rotina.py`: para cada indicador `ativo`, calcular a janela `[última data vigente − janela_revisao_meses, hoje]` (carga completa na primeira execução, com `--carga-completa` ou no dia 1 do mês), executar coleta → tratamento → validação → merge → publicação, isolando falhas por indicador e retornando código de saída ≠ 0 se algum falhar
- [X] T041 Implementar a CLI `backend/src/observatorio/cli.py` com Typer: `observatorio coletar [--indicador X | --todos] [--carga-completa] [--simular-falha]`, `observatorio situacao` (tabela com versão publicada, última coleta, avisos) e `observatorio sincronizar-catalogo`
- [X] T042 Criar o workflow `.github/workflows/coleta-diaria.yml`: `schedule: cron '17 9 * * *'`, `workflow_dispatch`, `concurrency: coleta` sem cancelamento, segredo `COLETOR_DATABASE_URL`, `uv run observatorio sincronizar-catalogo && uv run observatorio coletar --todos`
- [X] T043 [P] Criar o workflow `.github/workflows/backup-semanal.yml`: `pg_dump --data-only --schema=bruto --schema=tratado --schema=publico` (sem papéis) com o segredo `COLETOR_DATABASE_URL`, enviado como artefato com retenção de 90 dias

### Base da API (FastAPI)

- [X] T044 Implementar `backend/src/observatorio/api/app.py`: aplicação FastAPI com título e versão do contrato, apenas métodos `GET`, CORS restrito a `CORS_ORIGENS`, cabeçalho `Cache-Control: public, max-age=3600` e `ETag` baseado em `versao_id` nas rotas de dados
- [X] T045 [P] Implementar `backend/src/observatorio/api/erros.py`: respostas RFC 9457 `application/problem+json` em português com `type`, `title`, `status`, `detail`, `erros[{campo, mensagem}]` e `meses_ausentes`, conforme `components.schemas.Problema` do contrato
- [X] T046 [P] Implementar `backend/src/observatorio/api/esquemas.py` com modelos Pydantic espelhando `Indicador`, `Atualizacao`, `PeriodoReferencia`, `Observacao`, `Serie`, `Resumo`, `Simulacao`, `Problema` do contrato; valores decimais serializados como string (ex.: `"0.4500"`)
- [X] T047 Implementar `backend/src/observatorio/repositorio/publico.py`: consultas de leitura em `publico` (indicador por código, catálogo, observações por intervalo, último mês publicado) com o papel `api_leitura`, uma ida ao banco por requisição
- [X] T048 Implementar `GET /v1/saude` em `backend/src/observatorio/api/rotas/saude.py` e o teste de contrato `backend/tests/contract/test_contrato_openapi.py`, que valida as respostas de todas as rotas implementadas contra `specs/001-observatorio-do-real/contracts/api-openapi.yaml`

### Casca da interface

- [X] T049 Criar os tokens de design em `frontend/src/estilos/tokens.css` a partir de `docs/referencias-visuais/desktop/08-componentes-e-estados.png`: fundo `#0A0B0B`, verde profundo `#0C1F17`, azul-escuro `#0B1426`, amarelo `#F5D33A`, cards `#111413`, área clara `#E9ECEA`, texto de apoio `#A3ABA7`, linhas `#1E2321`; cores e traços das séries (IPCA verde contínuo, Dólar azul tracejado, Euro amarelo pontilhado, Selic roxo traço-ponto, Base monetária laranja pontilhado); tipografia Inter Tight 300/700/800 e Instrument Serif itálico (Google Fonts); foco do teclado com contorno amarelo visível; contraste ≥ 4,5:1 para texto
- [X] T050 [P] Criar `frontend/src/estilos/global.css` com reset, `prefers-reduced-motion` desligando animações, utilitário `.somente-leitor-de-tela` e layout fluido sem rolagem horizontal de 360 px a 1440 px
- [X] T051 [P] Gerar os tipos da API com `openapi-typescript` a partir de `specs/001-observatorio-do-real/contracts/api-openapi.yaml` em `frontend/src/servicos/api-tipos.ts` e implementar o cliente `frontend/src/servicos/api.ts` (base `import.meta.env.VITE_API_URL`, tratamento de `application/problem+json`)
- [X] T052 [P] Implementar `frontend/src/formatacao/numeros.ts` e `frontend/src/formatacao/datas.ts` (vírgula decimal, ponto de milhar, `R$`, `mmm/aaaa`, `dd/mm/aaaa`, sem notação científica) e `frontend/src/formatacao/valorEmReais.ts` (converte "1.500,00", "1500,00" e "1500" para "1500.00"), com testes em `frontend/tests/unit/formatacao.test.ts`
- [X] T053 Implementar o componente `frontend/src/componentes/EstadoDados.tsx` com os estados de `contracts/ui-estados.md` (`carregando`, `pronto`, `sem_dados`, `nao_publicado`, `lacuna`, `falha_atualizacao`, `erro`, `entrada_invalida`, `nao_integrado`), texto + ícone em cada estado, `aria-busy` no carregamento e botão "Tentar novamente" com foco, e testes em `frontend/tests/unit/EstadoDados.test.tsx`
- [X] T054 [P] Implementar `frontend/src/componentes/Selo.tsx` (Ilustrativo, Aguardando integração, Em definição, Atualizado, Falha na atualização) — o selo "Ilustrativo" só aparece com `natureza = "ilustrativo"` — e `frontend/src/componentes/TermoExplicado.tsx` (`<details>` "O que é?")
- [X] T055 Configurar rotas e provedores em `frontend/src/app/App.tsx` e `frontend/src/main.tsx` (React Router, QueryClient com `staleTime` de 1 h) e o arquivo `frontend/public/_redirects` do Cloudflare Pages para a SPA

**Checkpoint**: `uv run observatorio coletar --indicador ipca --carga-completa` publica o IPCA
real; `GET /v1/saude` responde; a interface abre com tokens e estados.

---

## Phase 3: User Story 1 — Conhecer o projeto pela página inicial (Priority: P1) 🎯 MVP

**Goal**: página inicial, navegação e rodapé com contatos do autor, conforme
`docs/referencias-visuais/*/01-pagina-inicial.png`, `09-componente-rodape.png` e
`10-componente-navegacao.png`.

**Independent Test**: abrir `/` em 360, 768 e 1440 px, percorrer as seções, seguir os links
disponíveis, ver os temas futuros como "Em breve" e acionar LinkedIn (nova aba) e e-mail.

### Tests for User Story 1

- [X] T056 [P] [US1] Teste ponta a ponta em `frontend/tests/e2e/inicio.spec.ts`: seções presentes (chamada principal, apresentação, fontes BCB/IBGE, quatro temas, quatro etapas do fluxo de dados), aviso "As miniaturas dos cards são ilustrações, não dados", temas não entregues com "Em breve" e sem link ativo, LinkedIn com `target="_blank"`, `rel="noopener noreferrer"` e texto "(nova aba)", e-mail com `mailto:`; sem rolagem horizontal em 360/768/1440 px; zero violações axe A/AA
- [X] T057 [P] [US1] Teste de componente em `frontend/tests/unit/Navegacao.test.tsx`: link da página atual com `aria-current="page"`; páginas de entregas futuras não aparecem como links ativos (FR-005)

### Implementation for User Story 1

- [X] T058 [P] [US1] Criar `frontend/src/conteudo/site.ts` com os dados do autor (nome "Henry Gabriel Santos Silva", `linkedin` e `email` lidos de `VITE_AUTOR_LINKEDIN` e `VITE_AUTOR_EMAIL`, que são públicos e não são segredos; se ausentes, o build de produção falha com mensagem clara) e a lista de páginas com `entrega` e `disponivel`
- [X] T059 [P] [US1] Implementar `frontend/src/app/Navegacao.tsx`: logotipo "Observatório do Real", links do cabeçalho com destaque da página atual, botão "Explorar dados" e, no celular, fileira de links com rolagem horizontal própria (sem rolagem da página)
- [X] T060 [P] [US1] Implementar `frontend/src/app/Rodape.tsx`: logotipo, frase "Engenharia de dados a serviço do conhecimento sobre o Brasil.", "Desenvolvido por Henry Gabriel Santos Silva.", links das páginas disponíveis, botões LinkedIn "(nova aba)" e E-mail, e a linha de fontes ("Fontes: Banco Central do Brasil e IBGE.") — sem o texto provisório "Nesta etapa, os números exibidos são dados ilustrativos"
- [X] T061 [US1] Implementar `frontend/src/app/Layout.tsx` com link "Pular para o conteúdo", `<header>`, `<main id="conteudo">` e `<footer>`
- [X] T062 [US1] Implementar `frontend/src/paginas/Inicio.tsx` seguindo `01-pagina-inicial.png`: chamada "Conhecer nossa moeda é compreender o nosso Brasil.", bloco "O observatório" com fontes BCB · IBGE e "Abertos, CSV", faixa "Ordem e progresso também se constroem com conhecimento.", "Quatro caminhos para entender o real" (Inflação, Poder de compra, Câmbio, Moeda em circulação; miniaturas decorativas com `aria-hidden` e o aviso de ilustração; "Em breve" para Câmbio e Moeda), "Do dado público ao conhecimento" (Coleta, Armazenamento, Tratamento, Apresentação) e "Pelo Brasil e pelo conhecimento de toda a sociedade" com atalhos para as páginas disponíveis
- [X] T063 [US1] Ajustar a responsividade de `Inicio.tsx`, `Navegacao.tsx` e `Rodape.tsx` conforme `docs/referencias-visuais/celular/01-pagina-inicial.png`, `09-componente-rodape.png` e `10-componente-navegacao.png` (cards empilhados em uma coluna no celular)

**Checkpoint**: US1 funciona sozinha (as páginas de dados podem ainda estar indisponíveis).

---

## Phase 4: User Story 2 — Entender a inflação pelo IPCA (Priority: P1) 🎯 MVP

**Goal**: cartão, gráfico, tabela, explicação e CSV do IPCA com seleção de período (rota
`/visao-geral` mostrando só o IPCA na Entrega 1, conforme `02-visao-geral.png`).

**Independent Test**: com o IPCA real publicado, aplicar 12 m, 3 a, 5 a, 10 a e um período
personalizado; conferir o acumulado com o cálculo manual (V2); abrir a tabela; baixar o CSV (V9);
simular lacuna e falha (V5, V6).

### Tests for User Story 2

- [X] T064 [P] [US2] Testes de contrato e de API em `backend/tests/contract/test_rotas_ipca.py`: `GET /v1/indicadores`, `/v1/indicadores/ipca`, `/v1/indicadores/ipca/serie`, `/v1/indicadores/ipca/resumo` (padrão `5a`; `inicio`/`fim`; `inicio > fim` ⇒ 400 com `erros[].campo`; código inexistente ⇒ 404; indicador `aguardando_integracao` ⇒ 409; mês final não publicado ⇒ `fim_utilizado` e `aviso_nao_publicado`; lacuna ⇒ `situacao: "lacuna"` com `meses_ausentes`)
- [X] T065 [P] [US2] Testes do CSV em `backend/tests/unit/test_csv.py` conforme `contracts/csv.md`: UTF-8 com BOM, separador `;`, vírgula decimal, sem separador de milhar, `\r\n`, bloco de metadados com as chaves na ordem do contrato, cabeçalho `data;valor;unidade;situacao`, uma linha por mês do período, valor vazio para `ausente`, nome `ipca_AAAA-MM_AAAA-MM.csv` ou `ipca_completo.csv` (SC-010)
- [X] T066 [P] [US2] Teste ponta a ponta em `frontend/tests/e2e/ipca.spec.ts` com respostas simuladas: período padrão "5 anos" e texto "Referência: mmm/aaaa a mmm/aaaa"; troca de período atualiza cartão, gráfico e tabela; "Ver valores em tabela" mostra os mesmos valores do gráfico; leitura de ponto por teclado; estados `carregando`, `sem_dados`, `nao_publicado`, `lacuna`, `falha_atualizacao`; download do CSV; axe sem violações

### Implementation for User Story 2

- [X] T067 [US2] Implementar `GET /v1/indicadores` e `GET /v1/indicadores/{codigo}` em `backend/src/observatorio/api/rotas/indicadores.py`, lendo `publico.indicador_publicado` (metadados completos: fonte, unidade, frequência, casas decimais, natureza, período disponível, atualização)
- [X] T068 [US2] Implementar `GET /v1/indicadores/{codigo}/serie` em `backend/src/observatorio/api/rotas/series.py`: resolve período com `regras/periodo.py`, devolve uma `Observacao` por mês (incluindo `ausente`) e `derivadas` com o acumulado no período e o número-índice para o IPCA; 409 se não integrado
- [X] T069 [US2] Implementar `GET /v1/indicadores/{codigo}/resumo` em `backend/src/observatorio/api/rotas/series.py` usando `regras/ipca.py` (acumulado, fator, meses considerados) e retornando `situacao: "lacuna"` sem números quando houver mês ausente
- [X] T070 [US2] Implementar `backend/src/observatorio/api/csv.py` e a rota `GET /v1/indicadores/{codigo}/serie.csv` conforme `contracts/csv.md` (com período ou série completa), com `Content-Disposition` de anexo
- [X] T071 [P] [US2] Implementar `frontend/src/componentes/SeletorPeriodo.tsx` (12 meses, 3 anos, 5 anos, 10 anos, Personalizado com mês/ano de início e fim; validação local `inicio ≤ fim` com mensagem junto ao campo; botões com `aria-pressed`) conforme `08-componentes-e-estados.png`
- [X] T072 [P] [US2] Implementar `frontend/src/componentes/CartaoIndicador.tsx`: título, número-síntese, unidade, seta **e** frase de direção (nunca só cor), linhas Período / Fonte / Atualização, selo só se ilustrativo, "O que é?"; o componente não renderiza números se faltar fonte, unidade, período ou atualização (Princípio III)
- [X] T073 [P] [US2] Implementar `frontend/src/componentes/Grafico.tsx` com Recharts (`accessibilityLayer`), título, unidade visível, eixos com rótulos em pt-BR, dica com mês/ano + valor + unidade, linha interrompida em `ausente` (`connectNulls={false}`), cor + traço da série pelos tokens, rodapé "Fonte · período de referência" e `frontend/src/componentes/TabelaAlternativa.tsx` ("Ver valores em tabela", `<table>` com `<caption>` e `<th scope>`)
- [X] T074 [P] [US2] Implementar `frontend/src/componentes/BotaoCsv.tsx` (link para `serie.csv` com o período atual; desabilitado com "Disponível após a integração com a fonte." quando não integrado)
- [X] T075 [P] [US2] Escrever `frontend/src/conteudo/glossario.ts` com "O que é IPCA?" (índice oficial de inflação do Brasil, calculado pelo IBGE, mede a variação de preços de produtos e serviços consumidos pelas famílias) e o bloco "Dois jeitos de o real perder valor" (inflação × desvalorização cambial), revisando o texto para não afirmar causalidade (FR-014, FR-015)
- [X] T076 [US2] Implementar `frontend/src/paginas/VisaoGeral.tsx` na versão da Entrega 1: cabeçalho "Painel de indicadores", `SeletorPeriodo`, `CartaoIndicador` do IPCA, "Histórico do período" com `Grafico` + `TabelaAlternativa` + `BotaoCsv`, bloco "Dois jeitos de o real perder valor"; dados via TanStack Query e `EstadoDados`
- [X] T077 [US2] Ajustar `VisaoGeral.tsx` à referência `docs/referencias-visuais/celular/02-visao-geral.png` (seletor de período quebrando linha, gráfico com altura reduzida, tabela com rolagem horizontal **interna** ao bloco)

**Checkpoint**: US1 + US2 funcionam; o IPCA real aparece com metadados, tabela e CSV.

---

## Phase 5: User Story 3 — Simular o poder de compra (Priority: P1) 🎯 MVP

**Goal**: simulador conforme `03-poder-de-compra.png` (desktop e celular), com cálculo no
servidor e explicação passo a passo.

**Independent Test**: casos de referência com diferença ≤ R$ 0,01 (V1); data final não publicada
(V3); entradas inválidas (V4); simulação completa só com teclado.

### Tests for User Story 3

- [X] T078 [P] [US3] Testes de API em `backend/tests/contract/test_simulador.py`: `GET /v1/simulador/poder-de-compra` com `valor=100.00&inicio=2016-01&fim=2025-12` (`meses_considerados = 120`); `inicio = fim` (um mês); `fim` posterior ao último publicado ⇒ `fim_utilizado` + aviso; 400 para `valor` vazio, `0`, negativo, `abc`, 3 casas decimais, acima de `9999999999999.99`, `inicio > fim`, `inicio < 1994-07`, `inicio` posterior ao último mês publicado (mensagens de `contracts/ui-estados.md`); 422 com `meses_ausentes` quando houver lacuna
- [X] T079 [P] [US3] Teste ponta a ponta em `frontend/tests/e2e/simulador.spec.ts`: valor "1.500,00" interpretado como 1500; resultado com valor corrigido, inflação acumulada, mudança no poder de compra, meses, barras comparativas e a frase "A diferença ... não é ganho nem perda de dinheiro: é o quanto os preços subiram"; entrada inválida não mostra resultado, mostra mensagem junto ao campo com `aria-invalid` e move o foco; fluxo inteiro só com teclado; axe sem violações; 360 px sem rolagem horizontal

### Implementation for User Story 3

- [X] T080 [US3] Implementar `GET /v1/simulador/poder-de-compra` em `backend/src/observatorio/api/rotas/simulador.py`: validações de FR-025/FR-028 com erros por campo, regra "data final > último publicado não é erro", cálculo com `regras/ipca.simular_poder_de_compra`, resposta `Simulacao` incluindo `passos` (variações usadas) e metadados do indicador
- [X] T081 [P] [US3] Implementar `frontend/src/paginas/poder-de-compra/FormularioSimulacao.tsx`: campo "Valor em reais" com prefixo R$ e dica "Use vírgula para os centavos. Exemplo: 1.500,00"; "Data inicial" e "Data final" (mês/ano) com limites da série; validação local de `contracts/ui-estados.md`; `aria-describedby` e foco no primeiro campo inválido; bloco Índice / Fonte / Atualização
- [X] T082 [P] [US3] Implementar `frontend/src/paginas/poder-de-compra/ResultadoSimulacao.tsx`: frase "Para manter o poder de compra de R$ X de mmm/aaaa, em mmm/aaaa você precisaria de", valor corrigido em destaque, cartões "Inflação acumulada" (seta + texto, número de meses) e "Mudança no poder de compra" (com o equivalente no início), barras "Quantia nominal × valor que mantém o poder de compra" com rótulos em texto, aviso de mês não publicado
- [X] T083 [P] [US3] Implementar `frontend/src/paginas/poder-de-compra/ComoFunciona.tsx`: passos 01–03 com os números reais da simulação (meses usados, fator com 4 casas, conta `valor × fator = resultado`) e "O que é IPCA?" do glossário
- [X] T084 [US3] Compor `frontend/src/paginas/PoderDeCompra.tsx` (cabeçalho "Quanto você precisaria hoje para comprar o que comprava antes?", formulário, resultado em região `aria-live="polite"`, metodologia) e ajustar ao layout celular de `docs/referencias-visuais/celular/03-poder-de-compra.png`

**Checkpoint**: US1, US2 e US3 funcionam de forma independente.

---

## Phase 6: User Story 8 (parcial) — Catálogo de dados e metodologia (Entrega 1)

**Goal**: página "Sobre e metodologia" com o catálogo completo de indicadores (IPCA integrado,
demais com selo), "O caminho de cada número" e "Sobre o projeto", conforme
`07-dados-metodologia-sobre.png`.

**Independent Test**: conferir metadados de cada entrada com `dados/catalogo.yaml`; baixar a série
completa do IPCA; ver botões desabilitados nos indicadores não integrados.

### Tests for User Story 8 (Entrega 1)

- [X] T085 [P] [US8] Teste ponta a ponta em `frontend/tests/e2e/catalogo.spec.ts`: 12 entradas do catálogo (as de `dados/catalogo.yaml`) com descrição, fonte com link, unidade, frequência, período, atualização e selo; IPCA com CSV completo; demais com botão desabilitado e "Disponível após a integração com a fonte."; seção de metodologia declara que meses não publicados nunca são preenchidos com estimativas; axe sem violações

### Implementation for User Story 8 (Entrega 1)

- [X] T086 [P] [US8] Implementar `frontend/src/componentes/ItemCatalogo.tsx` com os campos e o selo de situação (FR-042) e o `BotaoCsv` da série completa
- [X] T087 [P] [US8] Escrever `frontend/src/conteudo/metodologia.ts`: etapas Coleta, Armazenamento, Tratamento, Apresentação; convenção do acumulado (meses inicial e final incluídos, research R-13); formato do CSV (`;`, vírgula decimal, UTF-8 com BOM); política de falha ("o observatório mantém a última versão válida e avisa na tela") e de lacunas
- [X] T088 [US8] Implementar `frontend/src/paginas/Sobre.tsx` com "Catálogo de indicadores" (dados de `GET /v1/indicadores`), "O caminho de cada número", "Sobre o projeto" (projeto independente, desenvolvimento Spec-Driven: requisitos, planejamento, tarefas) e "Detalhes técnicos para visitantes interessados" (`<details>`), ajustada a `docs/referencias-visuais/celular/07-dados-metodologia-sobre.png`

**Checkpoint**: Entrega 1 completa.

---

## Phase 6b: Publicação da Entrega 1

- [X] T089 Criar `backend/Dockerfile` (Python 3.12 slim, uv, usuário não root, `uvicorn observatorio.api.app:app --host 0.0.0.0 --port $PORT`) e `backend/.dockerignore` excluindo `.env` e `tests/`
- [X] T090 Documentar em `docs/publicacao.md` os passos 1–5 da seção "Publicação, custos e limitações" do `plan.md`: projeto Supabase em `sa-east-1`, `supabase db push`, senhas de `coletor`/`api_leitura` via `ALTER ROLE` no SQL Editor, **desativar a API de dados** e as chaves legadas; segredo `COLETOR_DATABASE_URL` (pooler modo sessão, 5432) no GitHub; Cloud Run em `us-east1` com `min-instances=0`, segredo `API_DATABASE_URL` (pooler modo transação, 6543) e alerta de orçamento de US$ 1; Cloudflare Pages com `VITE_API_URL`, `VITE_AUTOR_LINKEDIN`, `VITE_AUTOR_EMAIL`
- [ ] T091 Executar a publicação conforme `docs/publicacao.md` após o usuário fornecer o LinkedIn e o e-mail do autor e as contas (Supabase, Google Cloud, Cloudflare) e validar no ambiente publicado os cenários V2, V6, V10, V13 e V14 de `quickstart.md`

---

## Phase 7: User Story 4 — Painel de indicadores completo (Priority: P2) — Entrega 2

**Goal**: quatro cartões (IPCA, dólar, Selic, base monetária), histórico com abas e resumo do
período (`02-visao-geral.png`).

**Independent Test**: um período muda os quatro cartões, as abas e o resumo; o resumo não afirma
causalidade.

- [ ] T092 [US4] Reconferir com chamada real os códigos já verificados em `research.md` (R-02 a R-04: SGS 3698, 432, 1788) e gravar fixtures em `backend/tests/fixtures/sgs_3698.json`, `sgs_432.json`, `sgs_1788.json`; se algo divergir, atualizar `research.md` e a tabela de fontes de `plan.md` antes de seguir
- [ ] T093 [P] [US4] Testes em `backend/tests/unit/test_agregacao_mensal.py`: média mensal das cotações diárias de venda; Selic vigente no último dia do mês; saldo de fim de mês; mês sem nenhuma cotação ⇒ `ausente`
- [ ] T094 [US4] Implementar `backend/src/observatorio/tratamento/agregacao.py` (`media`, `fim_de_mes`, `vigente_fim_de_mes`) e a conversão R$ mil → R$ bilhões em `tratamento/padronizacao.py`, e ativar `dolar_ptax`, `selic_meta` e `base_monetaria` em `dados/catalogo.yaml` (`janela_revisao_meses`: 2, 2 e 24)
- [ ] T095 [P] [US4] Testes de variação de séries de nível em `backend/tests/unit/test_formulas.py` (`(x_b / x_a − 1) × 100`, mínimo, máximo) e de `GET /v1/painel` em `backend/tests/contract/test_painel.py`
- [ ] T096 [US4] Implementar `backend/src/observatorio/regras/variacao.py` e `GET /v1/painel` em `backend/src/observatorio/api/rotas/painel.py`
- [ ] T097 [P] [US4] Implementar `frontend/src/paginas/visao-geral/ResumoDoPeriodo.tsx` com modelos de texto fixos e descritivos ("Os preços medidos pelo IPCA subiram X% no acumulado; no mesmo período, o dólar passou de ... para ...") sem conectivos causais, e teste em `frontend/tests/unit/ResumoDoPeriodo.test.tsx` que falha se o texto contiver "por causa", "causou", "devido a", "provocou", "levou a"
- [ ] T098 [US4] Estender `frontend/src/paginas/VisaoGeral.tsx` para quatro cartões e abas Inflação / Dólar / Selic / Base monetária, e ativar a página na navegação; teste e2e em `frontend/tests/e2e/visao-geral.spec.ts`

---

## Phase 8: User Story 5 — Consultar o câmbio (Priority: P2) — Entrega 2

**Goal**: página de câmbio com dólar e euro (`04-cambio.png`).

**Independent Test**: períodos e moedas atualizam cartões e gráfico; valores conferem com a PTAX;
CSV de cada moeda.

- [ ] T099 [US5] Reconferir com chamada real o SGS 21619 (euro venda diário, consulta em blocos de até 10 anos), gravar `backend/tests/fixtures/sgs_21619.json` e ativar `euro_ptax` em `dados/catalogo.yaml`
- [ ] T100 [P] [US5] Teste e2e em `frontend/tests/e2e/cambio.spec.ts`: cartões com cotação final, variação, início, mín./máx., fonte "Banco Central do Brasil (PTAX, venda)"; desmarcar a última moeda mantém uma marcada ou mostra "Selecione ao menos uma moeda"; cor + traço distintos e rótulo no fim da linha
- [ ] T101 [P] [US5] Escrever em `frontend/src/conteudo/glossario.ts` "Como ler a cotação" (exemplo US$ 1 = R$ 4,00 → R$ 5,00, alta de 25%), "O que é a PTAX?" e "Câmbio é o mesmo que inflação?"
- [ ] T102 [US5] Implementar `frontend/src/paginas/Cambio.tsx` com `SeletorPeriodo`, seleção de moedas, dois `CartaoIndicador`, `Grafico` de duas séries com `TabelaAlternativa` e `BotaoCsv`, layout celular de `04-cambio.png`, e ativar a página na navegação

---

## Phase 9: User Story 6 — Moeda em circulação, base monetária e agregados (Priority: P3) — Entrega 3

**Goal**: página "Moeda em circulação" (`05-moeda-em-circulacao.png`).

**Independent Test**: abas de séries históricas com unidade e fonte; produção física com anos
"Não publicado"; glossário.

- [ ] T103 [US6] Reconferir SGS 1786, 27791, 27810, 27813, 27815 (R$ mil) e gravar fixtures; para a produção física, confirmar em documentação oficial do BCB a **unidade** e se `mecir_prog_anual_producao` é programa planejado ou produção realizada, registrando a conclusão em R-05 de `research.md` (sem confirmação, o indicador continua `em_definicao` e não é publicado)
- [ ] T104 [P] [US6] Implementar o conector `backend/src/observatorio/coleta/olinda.py` para `https://olinda.bcb.gov.br/olinda/servico/mecir_prog_anual_producao/versao/v1/odata/TodosDadosProducao?$format=json` (campos `DESC_ano`, `DESC_deno`, `DESC_especie`, `DESC_quant_produzida` como strings; soma por ano e espécie), com fixture e teste em `backend/tests/unit/test_coleta_olinda.py` (anos sem linha viram `ausente`)
- [ ] T105 [P] [US6] Teste de conversão de unidade para R$ bilhões em `backend/tests/unit/test_padronizacao.py` e ativação de `papel_moeda_circulacao`, `m1`–`m4` e `producao_cedulas_moedas` em `dados/catalogo.yaml` com `janela_revisao_meses: 24` para agregados
- [ ] T106 [P] [US6] Escrever em `frontend/src/conteudo/glossario.ts` "Três ideias que costumam ser confundidas", "Fabricar cédulas não é, por si só, criar dinheiro", "Mais moeda significa mais inflação?" (sem afirmar causalidade) e os verbetes Base monetária, M1, M2, M3, M4
- [ ] T107 [US6] Implementar `frontend/src/paginas/Moeda.tsx` com séries históricas em abas (Em circulação, Base monetária, Agregados M1–M4), gráfico de barras da produção física com "Não publicado" (borda tracejada, sem valor), glossário e layout celular; ativar na navegação; teste e2e em `frontend/tests/e2e/moeda.spec.ts`

---

## Phase 10: User Story 7 e User Story 8 (completa) — Comparação e catálogo (Priority: P3) — Entrega 4

**Goal**: comparação em base 100 (`06-comparar-indicadores.png`) e catálogo com todas as séries
integradas.

**Independent Test**: todas as séries começam em 100; tabela de valores originais confere;
indicador sem valor inicial é omitido com aviso.

- [ ] T108 [P] [US7] Testes em `backend/tests/unit/test_base100.py` (`100 × x_t / x_a`, 1 casa; série sem valor no mês inicial vai para `omitidos`) e em `backend/tests/contract/test_comparacao.py` (mais de 4 indicadores ⇒ 400)
- [ ] T109 [US7] Implementar `backend/src/observatorio/regras/base100.py` e `GET /v1/comparacao` em `backend/src/observatorio/api/rotas/comparacao.py`
- [ ] T110 [US7] Implementar `frontend/src/paginas/Comparar.tsx`: lista de indicadores com contador "n de 4" e bloqueio do quinto com mensagem, `SeletorPeriodo`, gráfico base 100 com linha de partida = 100, tabela "Valores e unidades originais", blocos "O que é base 100?" e "Andar junto não é causar" sempre visíveis; ativar na navegação; teste e2e em `frontend/tests/e2e/comparar.spec.ts`
- [ ] T111 [US8] Atualizar `frontend/src/paginas/Sobre.tsx` e `dados/catalogo.yaml` para que todas as séries integradas tenham CSV completo e selo "Atualizado", e repetir `frontend/tests/e2e/catalogo.spec.ts` com o catálogo completo

---

## Phase 11: Polish & Cross-Cutting Concerns

- [X] T112 [P] Teste `frontend/tests/e2e/responsividade.spec.ts` percorrendo todas as páginas disponíveis em 360, 768 e 1440 px e falhando se `document.documentElement.scrollWidth > innerWidth` (SC-008)
- [X] T113 [P] Teste `frontend/tests/e2e/acessibilidade.spec.ts` com axe em todas as páginas disponíveis e navegação só por teclado nos fluxos principais (SC-007)
- [X] T114 [P] Teste `frontend/tests/e2e/metadados.spec.ts` que verifica, em todo cartão, gráfico e tabela, a presença de fonte, unidade, período e atualização (SC-003)
- [X] T115 [P] Teste opcional `backend/tests/integration/test_fontes_reais.py` (marcador `fontes_reais`) que consulta SIDRA e SGS de verdade, e job semanal no `ci.yml` que o executa sem bloquear PRs
- [X] T116 Medir o tempo até conteúdo útil da Entrega 1 com Lighthouse em perfil móvel 4G e registrar o resultado em `docs/desempenho.md` (meta ≤ 3 s, SC-006)
- [X] T117 Revisar todos os textos em `frontend/src/conteudo/` e páginas quanto a afirmações causais (SC-012) e registrar a revisão no checklist do PR
- [X] T118 Executar todos os cenários V1–V14 de `specs/001-observatorio-do-real/quickstart.md` e registrar os resultados em `docs/validacao-entrega-1.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependências.
- **Foundational (Fase 2)**: depende da Fase 1 e **bloqueia todas as histórias**.
- **US1 (Fase 3)**: depende só da Fase 2 (tokens, layout, rotas).
- **US2 (Fase 4)** e **US3 (Fase 5)**: dependem da Fase 2 (IPCA publicado, regras, base da API).
  US3 reutiliza `TermoExplicado` e o glossário de US2 (T075), mas é testável sozinha.
- **US8 parcial (Fase 6)**: depende da Fase 2 e de `BotaoCsv` (T074).
- **Publicação (Fase 6b)**: depende das Fases 3–6 e dos dados do autor e contas fornecidos pelo
  usuário.
- **Entregas 2–4 (Fases 7–10)**: dependem da Entrega 1 publicada; cada fase começa pela tarefa de
  validação das fontes (T092, T099, T103).
- **Polish (Fase 11)**: T112–T114 podem rodar a cada entrega; T116–T118 ao fechar a Entrega 1.

### Within Each User Story

- Testes primeiro (devem falhar), depois regras → repositório → rotas → componentes → página.
- Conteúdo textual (`frontend/src/conteudo/`) pode ser escrito em paralelo aos componentes.

### Parallel Opportunities

- Fase 1: T004–T009 e T011 em paralelo.
- Fase 2: migrações em sequência (T012 → T017); em paralelo a elas: T022, T023, T025, T027, T028,
  T029, T030, T032, T034, T049–T052.
- Após a Fase 2: US1, US2, US3 e US8 parcial podem avançar em paralelo.

---

## Parallel Example: User Story 2

```bash
# Testes primeiro, em paralelo:
Task: "T064 Testes de contrato em backend/tests/contract/test_rotas_ipca.py"
Task: "T065 Testes do CSV em backend/tests/unit/test_csv.py"
Task: "T066 Teste e2e em frontend/tests/e2e/ipca.spec.ts"

# Componentes de interface em paralelo (arquivos diferentes):
Task: "T071 SeletorPeriodo.tsx"
Task: "T072 CartaoIndicador.tsx"
Task: "T073 Grafico.tsx + TabelaAlternativa.tsx"
Task: "T074 BotaoCsv.tsx"
Task: "T075 conteudo/glossario.ts"
```

## Parallel Example: User Story 3

```bash
Task: "T078 Testes de API em backend/tests/contract/test_simulador.py"
Task: "T079 Teste e2e em frontend/tests/e2e/simulador.spec.ts"
# depois, em paralelo:
Task: "T081 FormularioSimulacao.tsx"
Task: "T082 ResultadoSimulacao.tsx"
Task: "T083 ComoFunciona.tsx"
```

---

## Implementation Strategy

### MVP primeiro (Entrega 1)

1. Fase 1 (Setup) → Fase 2 (Foundational): o IPCA real já é coletado, validado e publicado.
2. Fase 3 (US1) → **validar**: página inicial navegável.
3. Fase 4 (US2) → **validar** V2, V5, V6, V9.
4. Fase 5 (US3) → **validar** V1, V3, V4.
5. Fase 6 (US8 parcial) → Fase 6b (publicação) → Fase 11 (T112–T118).

### Entregas incrementais

- Entrega 2: Fases 7 e 8 (começando por T092 e T099).
- Entrega 3: Fase 9 (começando por T103).
- Entrega 4: Fase 10.
- Cada entrega é publicada sozinha; páginas não entregues continuam como "Em breve".

---

## Notes

- [P] = arquivos diferentes, sem dependência de tarefa pendente.
- Faça commit a cada tarefa ou grupo lógico; mensagens em português.
- Pare em qualquer checkpoint para validar a história de forma independente.
- Pendências do usuário: LinkedIn e e-mail do autor e contas de Supabase, Google Cloud e
  Cloudflare (bloqueiam só T091).

## Phase 12: Convergence

- [X] T119 CRITICAL: Escrever testes para `resumir_nivel` em `backend/tests/unit/test_variacao.py` (valores de referência `(x_b / x_a − 1) × 100` arredondado a 2 casas, mínimo e máximo, lacuna ⇒ `LacunaNaSerie`, série vazia e valor inicial zero ⇒ `ValueError`, nenhum uso de `float`) e um teste de contrato do resumo de série de nível em `backend/tests/contract/test_rotas_ipca.py` usando `ipca_indice` per Constitution IV (contradicts)
- [X] T120 CRITICAL: Exibir a data de atualização no rodapé do `Grafico` e a unidade e a data de atualização na legenda (`<caption>`) da `TabelaAlternativa` em `frontend/src/paginas/VisaoGeral.tsx` (usando `textoAtualizacao` de `frontend/src/componentes/Metadados.tsx`), e estender `frontend/tests/e2e/transversais.spec.ts` para exigir "Atualização" no gráfico e na tabela per Constitution III / FR-010 / SC-003 (partial)
- [X] T121 Exibir o estado `falha_sem_versao` (com `atualizacao.mensagem`) em vez de "Aguardando integração" quando a API responder 409 e o indicador estiver com `situacao: "falha_atualizacao"`: consultar `useIndicador` em `frontend/src/paginas/VisaoGeral.tsx` e `frontend/src/paginas/PoderDeCompra.tsx`, ajustar `estadoDoErro` em `frontend/src/componentes/EstadoDados.tsx` e cobrir com teste e2e em `frontend/tests/e2e/ipca.spec.ts` per FR-040 / Edge "Nenhuma versão válida disponível" (partial)
- [X] T122 Adicionar `npx prettier --check .` (script `formatar:verificar` em `frontend/package.json`) ao job `frontend` de `.github/workflows/ci.yml` per Constitution II (partial)
- [X] T123 Adicionar a `frontend/index.html` um bloco `<noscript>` com o nome do projeto, uma explicação curta, as fontes (IBGE e BCB), o link da API pública de CSV do IPCA e os contatos, legível sem JavaScript per Edge "Navegador com recursos limitados" (partial)
- [X] T124 Adicionar teste e2e em `frontend/tests/e2e/simulador.spec.ts` simulando R$ 1.000.000.000,00 (resposta gravada de `/v1/simulador/poder-de-compra?valor=1000000000.00&inicio=1994-07&fim=2026-09`) e verificando separadores brasileiros, ausência de notação científica e nenhuma rolagem horizontal em 360 px per Edge "Valores muito grandes no simulador" (partial)
- [X] T125 Incluir em `frontend/src/conteudo/metodologia.ts` (POLITICAS) como mudanças de base, unidade ou metodologia das fontes são tratadas e registradas (a série tratada mantém a unidade do catálogo; a mudança é anotada na metodologia) per Edge "Mudança de unidade ou metodologia da fonte" (partial)
- [X] T126 Estender `backend/tests/contract/test_contrato_openapi.py` para comparar, rota a rota, os campos obrigatórios das respostas 200 do OpenAPI servido pela API com os de `specs/001-observatorio-do-real/contracts/api-openapi.yaml` per plan: portões de CI (partial)
- [X] T127 Documentar em `specs/001-observatorio-do-real/data-model.md` (seção `bruto.payload`) que `conteudo` guarda a lista dos corpos JSON das respostas, na ordem das requisições (uma por bloco de consulta), e que o `sha256` é calculado sobre os bytes recebidos concatenados per data-model: bruto.payload (contradicts)
- [X] T128 Implementar o comando `observatorio publicar --indicador CODIGO` em `backend/src/observatorio/cli.py`, que regrava `publico.*` a partir da versão vigente sem coletar (útil após correção manual ou mudança de catálogo), com teste de integração em `backend/tests/integration/test_publicacao_e_falhas.py` per plan: CLI `coletar | situacao | publicar` (partial)
- [ ] T129 Abrir um CSV baixado da API (`ipca_completo.csv`) no LibreOffice Calc e no Excel em pt-BR, confirmar acentos, vírgula decimal e uma linha por mês, e registrar o resultado no cenário V9 de `docs/validacao-entrega-1.md` per FR-031 / quickstart V9 (partial)
