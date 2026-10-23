# Observatório do Real

Site público de educação econômica que transforma dados oficiais do **IBGE** e do **Banco
Central do Brasil** em gráficos, tabelas e explicações em linguagem simples, sempre com
fonte, unidade, período e data de atualização visíveis.

Projeto de aprendizado prático de **Spec-Driven Development**: toda funcionalidade nasce de
uma especificação, um plano e uma lista de tarefas (`specs/`), seguindo a constituição em
`.specify/memory/constitution.md`.

## O que já está disponível (Entrega 1)

- **Página inicial** com os temas, as fontes e o caminho dos dados.
- **Painel do IPCA**: inflação acumulada por período, gráfico, tabela, explicação e CSV.
- **Simulador de poder de compra**: corrige um valor pelo IPCA, com o cálculo passo a passo.
- **Catálogo de dados e metodologia**: todos os indicadores, situação de cada um e download.

Próximas entregas: câmbio e painel completo (2), moeda em circulação e agregados (3),
comparação em base 100 (4). Veja `specs/001-observatorio-do-real/spec.md`.

## Arquitetura

```text
 IBGE SIDRA ─┐                     GitHub Actions (cron diário)
 BCB SGS ────┼──> coleta ──> bruto ──> tratamento + validação ──> tratado ──> publicação ──> publico
             │     (httpx)     │              (Decimal, revisões SCD2)               │
             │                 └─ conteúdo bruto deduplicado por hash                 │
                                                                                     ▼
                         Navegador ──> site estático (React + Vite)
                              └──────> API somente leitura (FastAPI) ──papel api_leitura──> publico
```

| Pasta | Conteúdo |
|-------|----------|
| `backend/` | Pacote Python `observatorio`: conectores, tratamento, publicação, regras econômicas, API e CLI |
| `frontend/` | Interface React + TypeScript |
| `supabase/migrations/` | Schemas `bruto`, `tratado`, `publico`, papéis e políticas RLS |
| `dados/catalogo.yaml` | Metadados de todos os indicadores (fonte única) |
| `docs/` | Referências visuais, publicação, desempenho e validação |
| `specs/001-observatorio-do-real/` | Especificação, plano, pesquisa, contratos e tarefas |

## Rodar localmente

Pré-requisitos: Python 3.12, [uv](https://docs.astral.sh/uv/), Node.js 22, Docker.

```bash
./infra/preparar-banco-local.sh          # Postgres local (porta 54329) com as migrações
cp backend/.env.example backend/.env     # preencha com as URLs impressas pelo script

cd backend
uv sync
uv run observatorio coletar --todos      # baixa o IPCA real do IBGE (e confere com o BCB)
uv run observatorio situacao
uv run uvicorn observatorio.api.app:app --port 8010    # API em http://localhost:8010/docs

cd ../frontend
npm install
VITE_API_URL=http://localhost:8010 npm run dev           # site em http://localhost:5173
```

Guia completo e cenários de validação: `specs/001-observatorio-do-real/quickstart.md`.

## Testes

```bash
cd backend  && uv run ruff check && uv run ruff format --check && uv run pytest
cd frontend && npm run lint && npm run typecheck && npm test && npx playwright test
```

- Backend: regras econômicas contra valores de referência, conectores com respostas reais
  gravadas, integração com Postgres (revisões, falhas, segurança) e contrato da API.
- Interface: componentes, ponta a ponta em 360/768/1440 px e acessibilidade (axe, WCAG 2.1 AA).
- `uv run pytest -m fontes_reais` consulta as fontes oficiais de verdade.

## Publicação e custos

Custo-alvo **US$ 0/mês**: Supabase Free, GitHub Actions, Render Free (API) e
Cloudflare Pages. Passo a passo em [`docs/publicacao.md`](docs/publicacao.md).

### Reativar a coleta agendada

Em repositórios públicos, o GitHub desativa agendamentos após 60 dias sem atividade. Para
reativar: **Actions → Coleta diária → Enable workflow** (e rode uma vez manualmente).

## Fontes e licença dos dados

- IPCA: IBGE, SIDRA tabela 1737 (variáveis 63 e 2266). Conferência: BCB SGS 433.
- Séries do Banco Central: Sistema Gerenciador de Séries Temporais (SGS), licença ODbL.

O Observatório não estima valores ausentes: meses não publicados ou sem dado aparecem
identificados como tal.
