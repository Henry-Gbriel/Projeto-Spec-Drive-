# Research: Observatório do Real

Decisões da Phase 0. Fontes oficiais consultadas **ao vivo em 2026-10-22**. Itens ainda não
confirmados estão marcados **A VALIDAR** e DEVEM ser confirmados antes de serem ativados.

## R-01 — IPCA (Entrega 1) ✅ verificado

- **Decision**: fonte primária **IBGE SIDRA, tabela 1737, Brasil (`n1/all`)**:
  - variável **63** — "IPCA - Variação mensal", unidade `%` (código de unidade 2);
  - variável **2266** — "IPCA - Número-índice (base: dezembro de 1993 = 100)", unidade
    "Número-índice" (código 30), usada para a **conferência cruzada** do fator acumulado e para a
    coluna de número-índice da tabela.
  - Endpoint: `https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/{63|2266}/p/{períodos}`
    com `p` = `all`, `last N`, `first N` ou lista `AAAAMM,AAAAMM` / intervalo `AAAAMM-AAAAMM`.
  - Resposta: lista JSON cujo **primeiro elemento é o cabeçalho** (descrição das colunas) e os
    demais são observações. Campos usados: `V` (valor, string com ponto decimal), `D3C`
    (período `AAAAMM`), `D2C` (variável), `MN` (unidade). Valores não disponíveis vêm como
    texto (`"..."`, `"-"`, `"X"`), tratados como `ausente`.
  - Amostra real (2026-10-22): `{"V":"0.82","D2C":"63","D3C":"202609","D3N":"setembro 2026"}`;
    número-índice set/2026 = `7695.8200000000000`; jun/1994 = `857.29`; jul/1994 = `915.93`.
  - Número-índice disponível desde dez/1979. Último mês publicado na consulta: **set/2026**.
- **Espelho para conferência**: **BCB SGS 433** (IPCA variação mensal, %):
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=dd/mm/aaaa&dataFinal=dd/mm/aaaa`
  ou `/dados/ultimos/N`. Resposta: `[{"data":"01/09/2026","valor":"0.82"}]`. Valores conferem com
  o SIDRA nos meses consultados (jul–set/2026: 0.07, −0.32, 0.82).
- **Rationale**: o IBGE é o produtor oficial do IPCA (constituição, Princípio III: fonte oficial).
  O SGS é usado só como verificação: divergência entre as duas fontes gera ocorrência
  `divergencia_fontes` (aviso) e é exibida no log de validação, não ao público.
- **Calendário oficial**: `servicodados.ibge.gov.br/api/v3/calendario/9256` (IPCA) informa as
  próximas divulgações (out/2026 em 12/11/2026; nov/2026 em 11/12/2026). Uso opcional para o texto
  "próxima divulgação prevista em ...".
- **Calendário**: o IPCA de um mês é divulgado pelo IBGE por volta do dia 10 do mês seguinte. O
  sistema **não depende do calendário**: "último mês publicado" é a maior data presente na versão
  publicada. A rotina diária capta a divulgação no mesmo dia ou no seguinte.
- **Revisões**: o IPCA praticamente não é revisado; janela de revisão de 3 meses é suficiente e a
  recarga completa mensal cobre qualquer exceção.
- **Simulador**: aceita datas a partir de **jul/1994** (Plano Real). Os meses anteriores
  (hiperinflação, outras moedas) ficam fora do simulador, mas podem existir na série.
- **Alternatives considered**: API v3 de agregados do IBGE (`servicodados.ibge.gov.br`) — mesma
  informação, resposta mais aninhada e não respondeu na verificação; SGS 433 como primária —
  é um espelho, não a fonte produtora.

## R-02 — Câmbio PTAX (Entrega 2) ✅ verificado

- **Decision**:
  - **Dólar**: **SGS 3698** — dólar venda, **média mensal** (R$/US$, desde 02/1953), série
    oficial pronta; dispensa calcular a média. Conferido: set/2026 = 5,1447, igual à média das
    cotações de fechamento da PTAX (Olinda) do mês. SGS 3697 é a média de **compra** (não usar).
  - **Euro**: **SGS 21619** — euro venda **diária** (R$/€, desde 31/12/1998); a rotina calcula a
    média mensal (média aritmética dos dias úteis do mês). SGS 21620 é compra (não usar).
  - Alternativa equivalente: API Olinda PTAX (`CotacaoMoedaPeriodo`, filtro
    `tipoBoletim eq 'Fechamento'`, datas `'MM-DD-AAAA'`).
- **Limite do SGS (confirmado)**: séries **diárias** exigem `dataInicial`/`dataFinal` e aceitam no
  máximo **10 anos por consulta** (desde 26/03/2025); resposta de erro: "O sistema aceita uma
  janela de consulta de, no máximo, 10 anos em séries de periodicidade diária". Séries mensais
  retornam o histórico completo. `/dados/ultimos/N` funciona para todas. Janela sem dados
  responde `{"erro":{"statusCode":404,...}}` ⇒ tratar como "sem novidade", não como falha.
- **Licença**: dados do BCB publicados sob ODbL (Open Data Commons Open Database License) ⇒
  citar a fonte no site e nos CSV.

## R-03 — Selic meta (Entrega 2) ✅ verificado

- **Decision**: **SGS 432** (meta Selic, % a.a., diária, desde 05/03/1999); exibição mensal com o
  valor vigente no último dia do mês.
- **Atenção**: a série traz **datas futuras** (ex.: 03/11/2026 e 04/11/2026 na consulta de
  22/10/2026) ⇒ o tratamento descarta datas posteriores a hoje (regra de validação
  `data_futura`, aviso).

## R-04 — Base monetária, meio circulante e agregados (Entrega 3) ✅ verificado

Todas mensais, saldo de fim de período, unidade **R$ mil** (exibição em R$ bilhões: ÷ 1.000.000).

| Indicador | SGS | Início |
|-----------|-----|--------|
| Base monetária restrita | 1788 | 02/1946 |
| Papel-moeda em circulação (componente da base) | 1786 | 02/1980 |
| Papel-moeda em poder do público | 27789 | 2002 (início exato não confirmado) |
| M1 (saldo) | 27791 | 01/2002 |
| M2 / M3 / M4 (saldo) | 27810 / 27813 / 27815 | 2001–2002 (primeiras linhas nulas ⇒ `ausente`) |

- **Correções**: 27788 é M1 **média dos dias úteis** (não usar); 1786 é papel-moeda **em
  circulação**, diferente do papel-moeda **em poder do público** (27789).
- **Defasagem**: em 22/10/2026 o último mês disponível era ago/2026 (~7–8 semanas).
- **Revisões**: o BCB revisa os meses recentes ⇒ `janela_revisao_meses: 24`.
- Metadados do SGS: não há endpoint de metadados; usar o catálogo CKAN
  `dadosabertos.bcb.gov.br/api/3/action/package_search?fq=codigo_sgs:N` para conferência manual.

## R-05 — Produção física de cédulas e moedas (Entrega 3) — PARCIALMENTE VERIFICADO

- **Fonte estruturada encontrada**: API Olinda do BCB
  `olinda.bcb.gov.br/olinda/servico/mecir_prog_anual_producao/versao/v1/odata/TodosDadosProducao?$format=json`
  ("Quantidades produzidas por ano e espécie", Sismecir, ODbL), 2010–2026, por ano, espécie e
  denominação. Ex.: `{"DESC_ano":"2026","DESC_deno":"100.00","DESC_especie":"CÉDULAS","DESC_quant_produzida":"418560"}`.
- **A VALIDAR antes de ativar**: (1) a **unidade** (não informada; parece milhares de peças);
  (2) se os números são o **programa anual** (planejado) ou a produção **realizada** — o nome do
  serviço contém "prog_anual" e já existe 2026 completo. Enquanto não houver confirmação
  documental, o indicador fica `em_definicao` e **não** é publicado (Princípio III).
- **Decision**: conector `olinda` para este serviço; carga manual (`dados/manuais/`) só como
  último recurso, com a URL do documento oficial por ano.
- Relacionado: `mecir_dinheiro_em_circulacao` (`informacoes_diarias`, desde 1994-10-03, D+1,
  quantidade e valor por denominação) pode complementar a página de moeda; consultar por data
  com `$filter`, nunca o histórico inteiro de uma vez.

## R-06 — Princípio "não inventar observações"

- **Decision**: lacunas viram linhas `ausente` (`valor = null`) na camada `publico`; nenhum
  preenchimento, interpolação ou repetição. Cálculos que atravessam lacunas não são feitos e
  retornam os meses ausentes.

## R-07 — Acesso ao Supabase e políticas

- **Decision**: a interface fala **só com a FastAPI**. A API de dados do Supabase (PostgREST) é
  **desativada** no painel; RLS fica ativado em todas as tabelas como defesa em profundidade,
  com políticas `SELECT` somente em `publico` e `USING (publicado = true)`.
- Papéis próprios de login (`coletor`, `api_leitura`) com privilégio mínimo; a chave secreta
  (`sb_secret_…`, antes `service_role`) não é usada. As chaves legadas JWT estão previstas para
  descontinuação até o fim de 2026 ⇒ desativá-las.
- Tabelas criadas por migração SQL **não** recebem RLS automaticamente ⇒ cada migração ativa RLS
  explicitamente; teste de integração verifica que toda tabela tem `relrowsecurity = true`.
- **Conexões**: conexão direta é só IPv6 ⇒ usar o pooler (IPv4). Rotinas e migrações: modo
  **sessão** (porta 5432). API em contêiner com escala a zero: modo **transação** (porta 6543),
  que **não suporta prepared statements** ⇒ psycopg 3 com `prepare_threshold=None`, pool mínimo
  e `sslmode=require`; sem `SET` de sessão nem advisory locks na API.
- **Alternatives considered**: interface lendo o Supabase direto com a chave publicável — rejeitada
  (duplicaria fórmulas em TypeScript e ampliaria a superfície exposta).

## R-08 — Banco: Supabase Free

- 500 MB, 5 GB de tráfego/mês, 2 projetos ativos, **pausa após 7 dias de baixa atividade**,
  **sem backups automáticos**. Pro: US$ 25/mês. Fonte: <https://supabase.com/pricing>,
  <https://supabase.com/docs/guides/platform/free-project-pausing>.
- **Decision**: Free. A rotina diária gera atividade (não há garantia documentada de que impeça a
  pausa ⇒ monitorar). Backup semanal com `pg_dump --data-only` dos três schemas (somente dados
  públicos de origem oficial, sem papéis/senhas) como artefato do GitHub Actions.

## R-09 — API: hospedagem

- **Decision**: **Google Cloud Run**, cobrança por requisição, `min-instances=0`, região Tier 1
  (`us-east1`). Cota gratuita: 2 mi requisições, 180 mil vCPU-s e 360 mil GiB-s por mês. Exige
  conta de faturamento ⇒ alerta de orçamento em US$ 1. Fonte:
  <https://cloud.google.com/run/pricing>.
- **Alternatives considered**: Render Free (sem cartão, mas dorme após 15 min e a partida a frio
  leva ~1 min, o que viola SC-006 — mantida como alternativa documentada); Fly.io (sem plano
  gratuito para novas contas); Railway (crédito de US$ 1/mês); Vercel Hobby (uso não comercial e
  partida a frio); Koyeb (uma instância, regiões fora da América do Sul, exigência de cartão
  incerta).
- **Observação de latência**: banco em `sa-east-1` e API em `us-east1` somam ~120 ms por consulta;
  aceitável com cache HTTP de 1 h e consultas agregadas (uma ida ao banco por requisição).

## R-10 — Rotinas: GitHub Actions

- Repositório público: minutos ilimitados em runners padrão; privado: 2.000 min/mês (suficiente).
- Cron pode atrasar ou pular execuções; **agendamentos são desativados após 60 dias sem atividade
  no repositório público**. Fonte:
  <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows>.
- **Decision**: cron `17 9 * * *` (06h17 em Brasília), `workflow_dispatch`, `concurrency` para
  impedir execuções simultâneas, rotina idempotente, notificação por e-mail em falha (padrão do
  GitHub). Commits regulares mantêm o agendamento ativo; o README registra como reativar.

## R-11 — Interface: hospedagem

- **Decision**: **Cloudflare Pages Free** (uso comercial permitido, 500 builds/mês, arquivos até
  25 MiB). Fonte: <https://developers.cloudflare.com/pages/platform/limits/>.
- **Alternatives considered**: GitHub Pages (não comercial; SPA exige contorno de 404),
  Vercel Hobby (não comercial), Netlify Free (cota de créditos apertada).

## R-12 — Ferramentas

| Área | Decisão | Motivo |
|------|---------|--------|
| Pacotes Python | uv | rápido, lockfile, ambiente reprodutível |
| Qualidade Python | ruff (lint + formatação) | uma só ferramenta |
| Acesso ao banco | psycopg 3 com SQL explícito | simplicidade (Princípio VIII); controle de transações |
| HTTP das fontes | httpx + tenacity (3 tentativas, espera exponencial, timeout 30 s) | fontes oficiais às vezes oscilam |
| Testes Python | pytest; fixtures gravadas das respostas reais; Postgres local do Supabase CLI | sem internet nos testes; integração real com SQL |
| Interface | React 19 + TypeScript + Vite; React Router; TanStack Query | cache e estados de carregamento/erro prontos |
| Gráficos | Recharts (camada de acessibilidade) + tabela alternativa sempre presente | declarativo; acessibilidade complementada pela tabela |
| Estilo | CSS Modules + variáveis CSS com os tokens das referências | sem dependência de framework de UI |
| Tipos da API | `openapi-typescript` gerando tipos de `contracts/api-openapi.yaml` | contrato único entre API e interface |
| Testes da interface | Vitest + Testing Library; Playwright + `@axe-core/playwright` | componentes, ponta a ponta, acessibilidade |
| Segredos | gitleaks no CI | Princípio VII |

## R-13 — Fórmula do acumulado (convenção)

- **Decision**: acumulado de *a* a *b* **inclusive** = produto das variações mensais de *a* a *b*
  (equivale a `I_b / I_{a−1}` pelo número-índice). Ex.: jan/2016 a dez/2025 = 120 meses.
- **Rationale**: é a leitura natural de "inflação entre jan/2016 e dez/2025" e permite conferir
  com o número-índice oficial. A convenção é declarada na página de metodologia e no passo a
  passo do simulador.
- **Alternatives considered**: excluir o mês inicial (`I_b / I_a`), adotado por algumas
  calculadoras quando o valor é "do fim do mês inicial"; rejeitado para manter consistência com
  o FR-022 da spec.
