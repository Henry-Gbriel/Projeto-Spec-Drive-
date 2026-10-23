# Implementation Plan: Observatório do Real

**Branch**: `001-observatorio-do-real` | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-observatorio-do-real/spec.md`

## Summary

Site público de educação econômica que mostra indicadores oficiais (IBGE e Banco Central) com
fonte, unidade, período e atualização sempre visíveis. Três peças:

1. **Rotinas de dados em Python** (coleta → tratamento/validação → publicação), agendadas uma
   vez por dia no GitHub Actions, gravando em **Supabase PostgreSQL** nas camadas `bruto`,
   `tratado` e `publico`, com versionamento de revisões e preservação da última versão válida.
2. **API somente leitura em FastAPI**, que lê apenas a camada `publico` e calcula as regras
   econômicas (acumulado do IPCA, simulador, variações, base 100) com `Decimal`.
3. **Interface em React + TypeScript + Vite**, responsiva e acessível, seguindo as referências
   visuais, publicada como site estático.

A primeira entrega (MVP) cobre página inicial, IPCA e simulador de poder de compra (US1–US3) e o
catálogo inicial (US8 parcial).

## Technical Context

**Language/Version**: Python 3.12 (dados e API); TypeScript 5.x com React 19 (interface)

**Primary Dependencies**:
- Backend: FastAPI, Pydantic v2, httpx (clientes das fontes), psycopg 3 (acesso ao banco,
  SQL explícito, sem ORM), tenacity (novas tentativas), Typer (CLI das rotinas), PyYAML
  (catálogo).
- Interface: Vite, React Router, TanStack Query (cache e estados de carregamento/erro),
  Recharts (gráficos, com camada de acessibilidade) e CSS Modules com variáveis CSS (tokens
  das referências), sem framework de UI.

**Storage**: Supabase PostgreSQL (plano Free), schemas `bruto`, `tratado`, `publico`; migrações
SQL versionadas com Supabase CLI.

**Testing**: pytest (unitários de fórmulas, conectores com fixtures gravadas, integração com
Postgres local, contrato da API); Vitest + Testing Library (componentes e formatação pt-BR);
Playwright + axe-core (ponta a ponta, acessibilidade, larguras 360/768/1440 px); ruff, ESLint,
`tsc --noEmit`; gitleaks no CI.

**Target Platform**: navegadores modernos (desktop e celular); API em contêiner Linux; rotinas
em runner Linux do GitHub Actions.

**Project Type**: aplicação web (backend de dados + API + frontend estático).

**Performance Goals**: conteúdo útil em ≤ 3 s em 4G (SC-006); respostas da API servidas do cache
HTTP na maior parte das visitas (dados mudam no máximo uma vez por dia).

**Constraints**: custo mensal alvo R$ 0; credenciais só no servidor; WCAG 2.1 AA; sem
observações inventadas; cálculos reproduzíveis.

**Scale/Scope**: 7 páginas, ~12 séries, ~400 observações mensais por série (1994→hoje), tráfego
baixo (centenas a poucos milhares de visitas/mês). Banco previsto < 50 MB.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano atende | Situação |
|-----------|---------------------|----------|
| I. Orientado por especificações | spec → plan → tasks; este plano referencia FR/SC da spec; mudanças passam pela spec | ✅ |
| II. Qualidade e modularidade | Módulos separados: `coleta/`, `tratamento/`, `publicacao/`, `regras/` (fórmulas puras), `api/`; interface sem regra econômica (só formatação); ruff/ESLint obrigatórios; docs em português | ✅ |
| III. Transparência dos dados | Catálogo único (`dados/catalogo.yaml` → `tratado.indicador`) alimenta API, site e CSV; schema da API exige fonte/unidade/período/atualização; campo `natureza` real/ilustrativo; componente de cartão não renderiza sem metadados | ✅ |
| IV. Reprodutibilidade e testes | Payload bruto preservado e deduplicado por hash; versões com `versao_codigo` (git SHA); fórmulas puras com `Decimal` e casos de referência; testes obrigatórios para conectores, tratamento, merge de revisões e fórmulas | ✅ |
| V. Correlação ≠ causalidade | Textos do resumo gerados por modelos descritivos fixos; blocos "Andar junto não é causar" e "Mais moeda significa mais inflação?"; revisão de textos no checklist de PR | ✅ |
| VI. Acessibilidade e responsividade | Tabela alternativa para todo gráfico; cor + traço; axe no CI; testes em 360/768/1440 px; `prefers-reduced-motion` | ✅ |
| VII. Credenciais | Senhas só em segredos do GitHub Actions e do Cloud Run; `.env` no `.gitignore`; interface só conhece a URL pública da API; papéis com privilégio mínimo; RLS em todas as tabelas; gitleaks | ✅ |
| VIII. Simplicidade e custo | Planos gratuitos; SQL explícito sem ORM; um único pacote Python para rotinas e API; sem fila, cache distribuído ou orquestrador. Componentes extras justificados em Complexity Tracking | ✅ (com justificativas) |

**Pós-design (Phase 1)**: reavaliado após `data-model.md` e `contracts/`. Nenhuma violação nova;
a separação em três schemas e a API à parte são exigências do usuário e estão justificadas
abaixo.

## Fontes oficiais (validadas em 2026-10-22)

Ver [research.md](./research.md), R-01 a R-06, para endpoints, amostras de resposta e limites.

| Indicador | Fonte | Série | Unidade | Frequência | Entrega | Verificado |
|-----------|-------|-------|---------|------------|---------|------------|
| IPCA variação mensal | IBGE SIDRA | tabela 1737, variável 63 | % ao mês | mensal | 1 | ✅ |
| IPCA número-índice | IBGE SIDRA | tabela 1737, variável 2266 (dez/1993 = 100) | índice | mensal | 1 | ✅ |
| IPCA (conferência) | BCB SGS | 433 | % ao mês | mensal | 1 | ✅ |
| Dólar PTAX venda (média mensal) | BCB SGS | 3698 | R$/US$ | mensal | 2 | ✅ |
| Euro PTAX venda | BCB SGS | 21619 | R$/€ | diária → média mensal | 2 | ✅ |
| Selic meta | BCB SGS | 432 (descartar datas futuras) | % a.a. | diária → vigente no fim do mês | 2 | ✅ |
| Base monetária restrita | BCB SGS | 1788 | R$ mil → R$ bilhões | mensal | 3 | ✅ |
| Papel-moeda em circulação | BCB SGS | 1786 | R$ mil → R$ bilhões | mensal | 3 | ✅ |
| M1 / M2 / M3 / M4 (saldo) | BCB SGS | 27791 / 27810 / 27813 / 27815 | R$ mil → R$ bilhões | mensal | 3 | ✅ |
| Produção de cédulas e moedas | BCB Olinda `mecir_prog_anual_producao` | — | unidade a confirmar | anual | 3 | A VALIDAR (unidade; programa × realizado) |

Itens **A VALIDAR** não bloqueiam a Entrega 1; DEVEM ser confirmados antes de o indicador ser
ativado. Dados do BCB sob licença ODbL (citar a fonte).

## Arquitetura

```text
 IBGE SIDRA ─┐                     GitHub Actions (cron diário, 1 job)
 BCB SGS ────┼──> coleta ──> bruto ──> tratamento + validação ──> tratado ──> publicação ──> publico
 BCB PTAX ───┘     (httpx)     │              (Decimal, merge SCD2)                 │
                               └─ payload deduplicado por hash                       │
                                                                                    ▼
                         Navegador ──HTTPS──> Cloudflare Pages (React estático)
                              │
                              └──HTTPS──> API FastAPI (Cloud Run) ──papel api_leitura──> publico
```

- Toda escrita no banco acontece pelas rotinas (papel `coletor`). A API só lê.
- Fórmulas ficam em `backend/src/observatorio/regras/`, funções puras usadas pela publicação e
  pela API. A interface não recalcula números, apenas formata.

## Fórmulas (regras econômicas)

Todas com `decimal.Decimal` (precisão de 28 dígitos), arredondamento apenas na saída.

| Regra | Fórmula | Arredondamento | Ref. |
|-------|---------|----------------|------|
| Fator IPCA de *a* a *b* (inclusive) | `F = ∏_{m=a}^{b} (1 + v_m / 100)` com `v_m` = variação mensal (%) | nenhum (precisão completa) | FR-022 |
| Inflação acumulada | `(F − 1) × 100` | 2 casas, ROUND_HALF_UP | FR-022 |
| Meses considerados | `n = meses(a..b)` | — | FR-022 |
| Valor corrigido | `V × F` | centavos, ROUND_HALF_UP | FR-026 |
| Mudança no poder de compra | `(1/F − 1) × 100` | 2 casas | FR-026 |
| Equivalente no início | `V / F` | centavos | FR-026 |
| Variação de série de nível | `(x_b / x_a − 1) × 100` | 1–2 casas (catálogo) | FR-023 |
| Base 100 | `100 × x_t / x_a` | 1 casa | US7 |
| Média mensal (euro PTAX) | média aritmética das cotações diárias de venda do mês (dólar usa a média oficial SGS 3698) | precisão da fonte + 2 | research R-02 |
| Selic vigente no fim do mês | meta vigente no último dia do mês | — | research R-03 |

Conferência cruzada: o fator pelo número-índice (`I_b / I_{a−1}`, SIDRA variável 2266) deve
coincidir com o produto das variações com diferença relativa ≤ 0,01 % (`|F_var / F_índice − 1| ≤ 10⁻⁴`).
A tolerância é relativa porque as variações mensais publicadas têm 2 casas: de jul/1994 a
set/2026 a diferença absoluta chega a 0,016 p.p. num acumulado de 797,71 % (medido em
2026-10-22). Regra de lacuna: se algum `v_m` do intervalo estiver ausente, nada é
calculado e os meses ausentes são informados (FR-012).

## Atualização incremental, revisões e duplicidades

Resumo (detalhes em [data-model.md](./data-model.md#fluxo-de-atualização-incremental)):

- **Incremental**: cada indicador recoleta só a janela recente (`janela_revisao_meses`: IPCA 3,
  câmbio 2, Selic 2, agregados monetários 24). Recarga completa no dia 1 de cada mês.
- **Revisões**: comparação valor a valor; diferença fecha a linha vigente e abre outra (SCD2),
  com histórico recuperável e contagem `n_revisadas`.
- **Duplicidades**: hash SHA-256 do payload (`UNIQUE`), índice único parcial de observação
  vigente por data, e rejeição de payload com data repetida.
- **Falha**: rollback da versão em tratamento; `publico` mantém os dados anteriores e só muda o
  selo para "Falha na atualização" (FR-053, SC-011).
- **Concorrência**: `pg_advisory_xact_lock` por indicador e `concurrency` no workflow impedem
  duas rotinas simultâneas (no pooler em modo sessão, porta 5432).

## Segurança e acesso (Supabase)

- Papéis próprios: `coletor` (escreve) e `api_leitura` (`SELECT` em `publico`). `service_role` e
  chave secreta do Supabase não são usados pela aplicação.
- **RLS ativado em todas as tabelas**; políticas `SELECT` só em `publico`, com
  `USING (publicado = true)` para `anon`, `authenticated` e `api_leitura`. Sem políticas em
  `bruto`/`tratado` ⇒ negado.
- **API de dados do Supabase desativada** (a interface fala só com a FastAPI). Se for reativada,
  expor apenas o schema `publico`.
- Segredos: `COLETOR_DATABASE_URL` (GitHub Actions), `API_DATABASE_URL` (Cloud Run Secret
  Manager). A interface recebe apenas `VITE_API_URL`, que é pública.
- API: somente `GET`; CORS restrito ao domínio do site; limites de tamanho de período; sem logs
  de dados pessoais (não há).

## Project Structure

### Documentation (this feature)

```text
specs/001-observatorio-do-real/
├── plan.md              # este arquivo
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── api-openapi.yaml # contrato HTTP da API
│   ├── csv.md           # formato dos arquivos CSV
│   └── ui-estados.md    # contrato dos estados de dados na interface
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
dados/
└── catalogo.yaml                 # metadados de todos os indicadores (fonte única)

supabase/
├── config.toml
├── migrations/                   # schemas, tabelas, papéis, grants, RLS
└── seed.sql                      # nada além do catálogo inicial

backend/
├── pyproject.toml                # uv; um pacote para rotinas e API
├── .env.example
├── src/observatorio/
│   ├── config.py                 # leitura de variáveis de ambiente
│   ├── catalogo.py               # carrega e sincroniza dados/catalogo.yaml
│   ├── coleta/                   # conectores: sidra.py, sgs.py, olinda.py
│   ├── tratamento/               # padronização, agregação mensal, validações, merge SCD2
│   ├── publicacao/               # regrava publico.* em transação
│   ├── regras/                   # fórmulas puras (Decimal): ipca.py, variacao.py, base100.py
│   ├── repositorio/              # SQL explícito com psycopg
│   ├── api/                      # app.py, rotas, esquemas Pydantic, CSV, erros RFC 9457
│   └── cli.py                    # observatorio coletar | situacao | publicar
└── tests/
    ├── fixtures/                 # respostas reais gravadas das fontes
    ├── unit/                     # fórmulas, conectores, validações, CSV
    ├── integration/              # merge/revisões/falhas contra Postgres local
    └── contract/                 # API x contracts/api-openapi.yaml

frontend/
├── package.json
├── vite.config.ts
├── public/
└── src/
    ├── app/                      # rotas, layout, navegação, rodapé
    ├── paginas/                  # Inicio, VisaoGeral, PoderDeCompra, Cambio, Moeda, Comparar, Sobre
    ├── componentes/              # CartaoIndicador, Grafico, TabelaAlternativa, SeletorPeriodo,
    │                             # EstadoDados, Selo, TermoExplicado, BotaoCsv
    ├── servicos/                 # cliente da API (tipos gerados do OpenAPI)
    ├── formatacao/               # números, moeda e datas pt-BR
    ├── conteudo/                 # textos educativos e glossário
    └── estilos/                  # tokens das referências (cores, tipografia)
└── tests/                        # Vitest e Playwright (e2e/ + a11y)

docs/referencias-visuais/         # cópia das imagens desktop/ e celular/
.github/workflows/
├── ci.yml                        # lint, tipos, testes, gitleaks, build
├── coleta-diaria.yml             # cron diário + workflow_dispatch
└── backup-semanal.yml            # pg_dump dos dados (sem papéis)
```

**Structure Decision**: aplicação web com `backend/` (um único pacote Python que contém as
rotinas e a API, compartilhando `regras/` e `repositorio/`) e `frontend/` (SPA estática).
Migrações em `supabase/` e catálogo em `dados/` ficam na raiz por serem usados pelas duas
partes.

## Execução local e testes

Ver [quickstart.md](./quickstart.md). Resumo: `supabase start` (Postgres local em Docker) →
`uv run observatorio coletar` → `uv run fastapi dev` → `npm run dev`. Testes de backend não
acessam a internet (fixtures gravadas); um teste opcional marcado `fontes_reais` verifica as
fontes de verdade e roda semanalmente no CI, sem bloquear PRs.

**Portões de CI** (constituição, "Fluxo de Desenvolvimento"): ruff, pytest, ESLint, `tsc`,
Vitest, Playwright + axe, gitleaks, build da interface, verificação de que o contrato OpenAPI
servido bate com `contracts/api-openapi.yaml`.

## Publicação, custos e limitações

Custo-alvo: **US$ 0/mês** (preços consultados em 2026-10-22; detalhes e fontes em
[research.md](./research.md), R-08 a R-11).

| Componente | Serviço / plano | Custo | Limites relevantes | Mitigação |
|------------|-----------------|-------|--------------------|-----------|
| Banco | Supabase Free | US$ 0 | 500 MB, 5 GB de tráfego/mês, 2 projetos; **pausa após 7 dias sem atividade**; **sem backup automático**; conexão direta só IPv6 | rotina diária gera atividade; backup semanal com `pg_dump` (dados públicos) como artefato do Actions; conexões pelo pooler IPv4 |
| Rotinas | GitHub Actions (repositório público) | US$ 0 | cron pode atrasar ou pular execuções; **agendamentos desativados após 60 dias sem atividade no repositório** | horário fora de :00; rotina idempotente com janela de revisão; `workflow_dispatch`; alerta por e-mail em falha |
| API | Google Cloud Run (cobrança por requisição, `min-instances=0`) | US$ 0 dentro da cota (2 mi req., 180 mil vCPU-s/mês) | exige conta de faturamento com cartão; partida a frio de alguns segundos; cota gratuita em regiões Tier 1 (ex.: `us-east1`) | alerta de orçamento em US$ 1; cache HTTP de 1 h; interface mostra estado `carregando` |
| API (alternativa) | Render Free | US$ 0 | dorme após 15 min; **partida a frio ~1 min** | aceitável só se não houver cartão; viola SC-006 na primeira visita |
| Interface | Cloudflare Pages Free | US$ 0 | 500 builds/mês, 25 MiB por arquivo | — |
| Domínio | opcional (`.com.br` no Registro.br) | ~R$ 40/ano | — | pode usar `*.pages.dev` e `*.run.app` |
| **Total** | | **US$ 0/mês** (+ domínio opcional) | | |

**Gatilhos para sair do gratuito**: banco > 400 MB, tráfego > 4 GB/mês, ou pausas recorrentes ⇒
Supabase Pro (US$ 25/mês). Cloud Run acima da cota cobra por uso (centavos para este volume).

**Limitações aceitas**:

- Dados atualizados no máximo uma vez por dia; o IPCA sai uma vez por mês.
- Sem backup ponto-a-ponto (PITR) no plano Free; recuperação = migrações + último `pg_dump` +
  nova coleta completa das fontes (todas as séries são públicas e recuperáveis).
- Produção física de cédulas depende de publicações não estruturadas (carga manual, Entrega 3).
- Primeira visita após inatividade pode levar alguns segundos a mais (partida a frio da API).

**Passos de publicação**:

1. Supabase: criar projeto (região `sa-east-1`), `supabase link`, `supabase db push`, definir
   senhas dos papéis `coletor` e `api_leitura`, **desativar a API de dados** e desativar as
   chaves legadas.
2. GitHub: segredos `COLETOR_DATABASE_URL` (pooler, modo sessão, porta 5432) e workflows
   `coleta-diaria.yml` (cron `17 9 * * *` UTC), `ci.yml`, `backup-semanal.yml`.
3. Cloud Run: imagem `backend/` (FastAPI + Uvicorn), segredo `API_DATABASE_URL` (pooler, modo
   transação, porta 6543, `prepare_threshold=None`), `CORS_ORIGENS` com o domínio do site.
4. Cloudflare Pages: build `frontend/` (`npm run build`), variável `VITE_API_URL`.
5. Validar no ambiente publicado os cenários V2, V6, V10, V13 do [quickstart](./quickstart.md).

## Entregas e prioridade

| Entrega | Escopo técnico |
|---------|----------------|
| **1 (MVP)** | Migrações completas (três schemas, papéis, RLS); catálogo com todos os indicadores (só IPCA ativo); conector SIDRA + conferência pelo SGS 433; tratamento, validação, merge e publicação; API: `saude`, `indicadores`, `serie`, `serie.csv`, `resumo`, `simulador`; interface: layout, navegação, rodapé com contatos, Início, IPCA (cartão, gráfico, tabela, CSV, "O que é?"), Poder de compra, Sobre e metodologia (catálogo parcial); CI e publicação |
| 2 | Conectores SGS e PTAX; dólar, euro, Selic, base monetária; `GET /v1/painel`; páginas Visão geral e Câmbio |
| 3 | Meio circulante, agregados M1–M4, produção física (carga manual versionada); página Moeda em circulação |
| 4 | `GET /v1/comparacao`; página Comparar; catálogo completo |

## Complexity Tracking

| Item | Por que é necessário | Alternativa mais simples rejeitada porque |
|------|----------------------|-------------------------------------------|
| API FastAPI separada do site estático | Pedido do usuário; mantém credenciais fora do navegador e centraliza as fórmulas testadas em Python | Ler o Supabase direto do navegador exporia o banco e duplicaria regras em TypeScript |
| Três schemas (`bruto`, `tratado`, `publico`) | Pedido do usuário; Princípio IV (dados brutos preservados) e VII (público só vê o publicado) | Uma tabela única não permite rollback nem restringir o acesso ao que foi publicado |
| Histórico SCD2 de observações | Revisões das fontes precisam ser rastreáveis e reproduzíveis | Sobrescrever valores perde a auditoria exigida pelo Princípio IV |
| Cloud Run (exige conta de faturamento) | Partida a frio de segundos, compatível com SC-006, dentro da cota gratuita | Render Free é mais simples, mas a partida a frio de ~1 min viola SC-006 (mantido como alternativa) |
