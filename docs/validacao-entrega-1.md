# Validação da Entrega 1 — 2026-10-22

Cenários de `specs/001-observatorio-do-real/quickstart.md`, executados localmente (Postgres 16
em Docker, IPCA real coletado do IBGE em 2026-10-22, último mês publicado: set/2026).

| # | Cenário | Como foi verificado | Resultado |
|---|---------|---------------------|-----------|
| V1 | Casos de referência do simulador | `tests/unit/test_formulas.py`: 12 casos, valores esperados calculados à parte com `fractions.Fraction` sobre a série oficial | ✅ diferença ≤ R$ 0,01 em todos |
| V2 | Acumulado do IPCA | `GET /v1/indicadores/ipca/resumo?inicio=2021-01&fim=2025-12` na API local com dados reais | ✅ `33.14`, 60 meses (igual ao cálculo exato) |
| V3 | Mês não publicado | `tests/contract/test_simulador.py`, e2e `simulador.spec.ts` | ✅ termina em set/2026 com aviso |
| V4 | Entrada inválida | 11 casos na API (400 por campo) + e2e (mensagem junto ao campo, `aria-invalid`, foco) | ✅ |
| V5 | Lacuna | integração (`test_publicacao_e_falhas.py`), API (422 com `meses_ausentes`), e2e (linha interrompida, "sem dado") | ✅ nada estimado |
| V6 | Falha de coleta | `observatorio coletar -i ipca --simular-falha` no banco local | ✅ código de saída 1; 393 observações preservadas; selo "Falha na atualização"; volta a "atualizado" na coleta seguinte |
| V7 | Revisão | `test_merge_revisoes.py::test_revisao_fecha_linha_antiga_e_abre_nova` | ✅ linha antiga fechada, `n_revisadas = 1`, aviso `revisao_grande` |
| V8 | Idempotência | coleta real repetida + `test_reexecucao_sem_mudanca_nao_cria_versao` | ✅ `sem_mudancas`, nenhuma versão nova, payload não duplicado |
| V9 | CSV | API real: `ipca_2025-01_2025-12.csv`, BOM UTF-8 (`EF BB BF`), 12 linhas de dados; formato coberto por `tests/unit/test_csv.py` | ✅ automático · ⏳ abertura manual no Excel/LibreOffice pendente (não há planilha instalada nesta máquina) |
| V10 | Metadados | e2e `transversais.spec.ts` (cartão, gráfico, tabela, simulador) | ✅ |
| V11 | Responsividade | e2e em 360, 768 e 1440 px nas 4 páginas | ✅ sem rolagem horizontal |
| V12 | Acessibilidade | axe (WCAG 2.1 A/AA) em todas as páginas, desktop e celular; fluxos só com teclado; Lighthouse acessibilidade 100 | ✅ zero violações |
| V13 | Acesso público ao banco | `tests/integration/test_seguranca_banco.py` | ✅ `anon`/`authenticated` sem acesso a `bruto`/`tratado`; só `publicado = true`; `api_leitura` não escreve |
| V14 | Segredos | `.env` ignorado pelo Git; busca no build por `postgres://`, `password`, `sb_secret`, `service_role` | ✅ única ocorrência é a lista de tipos de campo do React (`type="password"`), não um segredo · gitleaks roda no CI |

## Suítes automatizadas

| Suíte | Resultado |
|-------|-----------|
| Backend (`pytest`: unitários, integração, contrato) | 173 aprovados |
| Fontes oficiais reais (`pytest -m fontes_reais`) | 3 aprovados |
| Interface (Vitest) | 61 aprovados |
| Ponta a ponta (Playwright, desktop + celular 360 px) | 78 aprovados |
| ruff, Prettier, ESLint, `tsc` | sem erros |

## Bugs encontrados pelos testes e corrigidos

- Contrato OpenAPI com YAML inválido (descrição com dois-pontos sem aspas).
- Cabeçalho `User-Agent` com acentos (HTTP só aceita ASCII).
- Navegação interna quebrava a página: `window.scrollTo` devolve Promise no Chromium atual e o
  efeito do React a tratava como função de limpeza.
- Nome acessível do logotipo diferente do texto visível (WCAG 2.5.3).
- Banco indisponível gerava erro 500 genérico; agora responde 503 em `problem+json`.
- Desempenho: LCP de 3,6 s nas páginas de dados reduzido para ≤ 1,9 s (`docs/desempenho.md`).

## Convergência (2026-10-23)

Correções das tarefas T119–T128 (`/speckit-converge`):

- Testes da variação de séries de nível com valores de referência (Constitution IV).
- Data de atualização no gráfico e unidade + atualização na legenda da tabela (Constitution III).
- Falha antes da primeira publicação aparece como "Falha na atualização" (FR-040).
- Prettier verificado no CI; conteúdo mínimo sem JavaScript (`<noscript>`).
- Teste com R$ 1.000.000.000,00 em 360 px; política de mudança de unidade na metodologia.
- Teste de contrato compara os campos das respostas, não só os caminhos.
- Formato de `bruto.payload` documentado; comando `observatorio publicar`.

## Pendências para publicar

- LinkedIn e e-mail do autor (variáveis `VITE_AUTOR_LINKEDIN` e `VITE_AUTOR_EMAIL`).
- Contas no Supabase, Google Cloud e Cloudflare; passo a passo em `docs/publicacao.md`.
- Repetir V2, V6, V10, V13 e V14 no ambiente publicado.
