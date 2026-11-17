# Quickstart: execução local e validação — Entrega 1

Guia para subir o Observatório localmente e provar, com cenários verificáveis, que a Entrega 1
(página inicial, IPCA e simulador) funciona. Detalhes de modelo e contratos estão em
[data-model.md](./data-model.md) e [contracts/](./contracts/); decisões em
[research.md](./research.md).

## Pré-requisitos

| Ferramenta | Versão | Uso |
|------------|--------|-----|
| Python | 3.12 | coleta, tratamento e API |
| uv | ≥ 0.5 | ambiente e dependências Python |
| Node.js | 22 LTS | interface |
| pnpm ou npm | atual | dependências da interface |
| Docker | atual | Postgres local (`docker-compose.yml`) |
| Supabase CLI (`npx supabase`) | ≥ 2.x | só para publicar as migrações no Supabase |

Nenhuma credencial real é necessária para rodar localmente.

## 1. Banco local

```bash
./infra/preparar-banco-local.sh      # Postgres 16 em Docker (porta 54329), papéis do Supabase
                                     # emulados e todas as migrações de supabase/migrations
```

Copie `backend/.env.example` para `backend/.env` e preencha com as URLs impressas pelo
script (o `.env` está no `.gitignore`). Alternativa mais pesada: `npx supabase start`.

| Variável | Usada por | Conteúdo |
|----------|-----------|----------|
| `COLETOR_DATABASE_URL` | rotinas de coleta | conexão do papel `coletor` |
| `API_DATABASE_URL` | API | conexão do papel `api_leitura` |
| `CORS_ORIGENS` | API | `http://localhost:5173,http://localhost:4173` |
| `VITE_API_URL` | interface | `http://localhost:8010` (público, não é segredo) |
| `VITE_AUTOR_LINKEDIN`, `VITE_AUTOR_EMAIL` | interface | contatos do rodapé (obrigatórios só no build de produção) |

## 2. Dados

```bash
cd backend
uv sync
uv run observatorio coletar --indicador ipca --carga-completa   # IPCA desde 1994 (SIDRA)
uv run observatorio coletar --todos                             # rotina diária completa
uv run observatorio situacao                                    # versões, coletas e avisos
uv run observatorio publicar --indicador ipca                   # regrava o publicado, sem coletar
```

**Esperado**: `publico.indicador_publicado` com `ipca` em `atualizado`; os demais indicadores do
catálogo em `aguardando_integracao` ou `em_definicao`.

## 3. API e interface

```bash
cd backend && uv run uvicorn observatorio.api.app:app --port 8010   # http://localhost:8010/docs
cd frontend && npm install && npm run dev                           # http://localhost:5173
```

## 4. Testes automatizados

```bash
cd backend && uv run ruff check && uv run ruff format --check && uv run pytest
cd backend && uv run pytest -m fontes_reais   # opcional: consulta IBGE e BCB de verdade
cd frontend && npm run lint && npm run typecheck && npm test
cd frontend && npx playwright install chromium && npx playwright test   # ponta a ponta + axe
```

As suítes de backend não acessam a internet: as respostas das fontes são simuladas com payloads
gravados em `backend/tests/fixtures/`. Os testes de integração criam um banco temporário no
Postgres do `docker-compose.yml` (ou em `TESTE_DATABASE_URL`). Os testes de ponta a ponta usam
respostas reais da API gravadas em `frontend/tests/e2e/fixtures/`.

## 5. Cenários de validação (Entrega 1)

| # | Cenário | Como verificar | Resultado esperado | Ref. |
|---|---------|----------------|--------------------|------|
| V1 | Casos de referência do simulador | `uv run pytest tests/unit/test_formulas.py -k referencia` | ≥ 10 casos com diferença ≤ R$ 0,01 em relação ao cálculo feito à mão | SC-001 |
| V2 | Acumulado do IPCA | `GET /v1/indicadores/ipca/resumo?inicio=2021-01&fim=2025-12` | `acumulado_percentual` igual ao produto encadeado da série oficial; `meses_considerados = 60` | SC-002, FR-022 |
| V3 | Mês não publicado | simulador com `fim` posterior ao último mês publicado | `periodo.fim_utilizado` = último mês publicado + `aviso_nao_publicado` | US3-3 |
| V4 | Entrada inválida | `valor=0`, `valor=abc`, `inicio>fim`, `inicio=1990-01` | HTTP 400 com `erros[].campo`; na interface, mensagem junto ao campo e foco nele | FR-028 |
| V5 | Lacuna | fixture com um mês ausente no meio | gráfico interrompido, tabela "sem dado", CSV vazio, resumo `situacao: lacuna`, simulador 422 | SC-004 |
| V6 | Falha de coleta | `uv run observatorio coletar --indicador ipca --simular-falha` | dados publicados inalterados; selo "Falha na atualização" com a data da última versão válida | SC-011 |
| V7 | Revisão | fixture com valor alterado para mês já existente | linha antiga fechada, nova vigente, versão com `n_revisadas = 1` | data-model |
| V8 | Idempotência | rodar `coletar --todos` duas vezes | 2ª execução: `sem_novidade`, nenhuma versão nova | data-model |
| V9 | CSV | baixar pelo site e abrir no LibreOffice/Excel pt-BR | acentos corretos, uma linha por mês, metadados no topo | SC-010, contracts/csv.md |
| V10 | Metadados | percorrer as páginas | fonte, unidade, período e atualização em todo cartão, gráfico e tabela | SC-003 |
| V11 | Responsividade | Playwright em 360, 768 e 1440 px | sem rolagem horizontal | SC-008 |
| V12 | Acessibilidade | axe + navegação só por teclado | zero violações A/AA; simulação concluída sem mouse | SC-007 |
| V13 | Acesso público ao banco | com a chave publicável, consultar `bruto.coleta` e `tratado.observacao` pela API de dados | acesso negado; somente `publico` com `publicado = true` é legível | Princípio VII |
| V14 | Segredos | `gitleaks detect` (CI) e inspeção do build da interface | nenhum segredo no repositório ou no JavaScript publicado | Princípio VII |

## 6. Publicação (resumo)

1. Supabase (nuvem): `supabase link` + `supabase db push`; criar senhas dos papéis `coletor` e
   `api_leitura`; desativar a API de dados (ou expor apenas `publico`).
2. Rotinas: segredo `COLETOR_DATABASE_URL` no GitHub Actions; workflow diário + manual.
3. API: imagem publicada no Cloud Run com segredo `API_DATABASE_URL`.
4. Interface: Cloudflare Pages com `VITE_API_URL` apontando para a API.
5. Rodar V2, V6, V10, V13 contra o ambiente publicado.

Detalhes e custos: [plan.md](./plan.md#publicação-custos-e-limitações).
