# Publicação — Entrega 1

Passo a passo para publicar banco, rotinas, API e site com custo de **US$ 0/mês**
(custos e limites em `specs/001-observatorio-do-real/plan.md`, seção "Publicação, custos e
limitações"). Hospedagem da API: **Render Free** (decisão de 2026-10-23, research R-09).

> **Antes de começar**, tenha em mãos: o endereço do LinkedIn e o e-mail do autor, e contas
> gratuitas no Supabase, no Render e na Cloudflare (todas podem usar login do GitHub). Nenhuma
> senha ou chave entra no repositório (Princípio VII).

**Ordem recomendada:** 0 → 1 → 2 → 3 → 4 → 5. A API e o site precisam do banco pronto; o
CORS da API precisa do endereço do site.

## 0. Repositório

1. Torne o repositório **público** (Settings → General → Danger Zone → Change visibility):
   minutos ilimitados no GitHub Actions. Nenhum segredo está no código.
2. Mescle a branch `dev` na `main` por pull request: a coleta agendada e o Render usam a `main`.

## 1. Banco (Supabase)

1. Crie um projeto no plano **Free**, região **South America (São Paulo) `sa-east-1`**.
2. Na raiz do repositório:

   ```bash
   npx supabase login
   npx supabase link --project-ref <ref-do-projeto>
   npx supabase db push            # aplica supabase/migrations
   ```

3. No **SQL Editor** do painel, habilite o login dos papéis com senhas fortes geradas por você
   (guarde-as num gerenciador de senhas; elas não vão para o Git):

   ```sql
   ALTER ROLE coletor WITH LOGIN PASSWORD '<senha forte 1>';
   ALTER ROLE api_leitura WITH LOGIN PASSWORD '<senha forte 2>';
   ```

4. Em **Settings → API**: **desative a Data API** (o site só fala com a FastAPI). Se um dia
   for reativada, deixe exposto apenas o schema `publico`.
5. Em **Settings → API Keys**: desative as chaves legadas (`anon`/`service_role`). A
   aplicação não usa nenhuma chave do Supabase.
6. Em **Database → Connect → Connection pooler**, copie as duas URLs (IPv4):
   - **modo sessão, porta 5432** → usada pelas rotinas (`COLETOR_DATABASE_URL`, usuário
     `coletor.<ref>`);
   - **modo transação, porta 6543** → usada pela API (`API_DATABASE_URL`, usuário
     `api_leitura.<ref>`).

## 2. Rotinas de coleta (GitHub Actions)

1. Em **Settings → Secrets and variables → Actions**, crie o segredo
   `COLETOR_DATABASE_URL` com a URL do modo sessão (com a senha do `coletor`).
2. Rode a carga inicial: **Actions → Coleta diária → Run workflow** marcando
   "Recoletar o histórico completo".
3. A partir daí, a coleta roda todo dia às 06h17 (Brasília). O backup semanal
   (`backup-semanal.yml`) usa o mesmo segredo.

> Em repositório público, o GitHub desativa agendamentos após 60 dias sem atividade no
> repositório. Para reativar: **Actions → Coleta diária → Enable workflow**.

## 3. API (Render Free)

1. No Render: **New → Blueprint**, conecte o repositório. O arquivo `render.yaml` cria o serviço
   `observatorio-api` (Docker, plano Free, branch `main`, verificação em `/v1/saude`).
2. Quando o Render pedir as variáveis marcadas como secretas, informe:
   - `API_DATABASE_URL`: a URL do **modo transação (porta 6543)** com a senha do `api_leitura`;
   - `CORS_ORIGENS`: por enquanto `https://observatorio-do-real.pages.dev` (ajuste no passo 4
     se o endereço do site for outro).
3. Aguarde o primeiro deploy e verifique:
   `curl https://<servico>.onrender.com/v1/saude` → `{"status":"ok","banco":"ok"}`.

> **Limitação do plano Free:** após 15 min sem acessos o serviço dorme; a primeira requisição
> seguinte leva cerca de 1 minuto. O site avisa o visitante enquanto espera. Para eliminar
> isso no futuro: plano pago do Render ou migração para o Google Cloud Run (ver research R-09).

## 4. Site (Cloudflare Pages)

1. **Workers & Pages → Create → Pages → Connect to Git**, escolha o repositório.
2. Configuração de build:
   - Diretório raiz: `frontend`
   - Comando: `npm ci && npm run build`
   - Saída: `dist`
3. Variáveis de ambiente (públicas, embutidas no JavaScript — **nunca** segredos):
   - `VITE_API_URL=https://<servico>.onrender.com`
   - `VITE_AUTOR_LINKEDIN=https://www.linkedin.com/in/<perfil>`
   - `VITE_AUTOR_EMAIL=<e-mail>`

   O build falha de propósito se alguma delas faltar.
4. Se o endereço final do site for diferente do usado no passo 3, atualize `CORS_ORIGENS` no
   painel do Render (Environment) e salve: o serviço é reiniciado.

## 5. Validação no ambiente publicado

Rode os cenários do `specs/001-observatorio-do-real/quickstart.md`:

| Cenário | Como |
|---------|------|
| V2 | `GET /v1/indicadores/ipca/resumo?inicio=2021-01&fim=2025-12` → `acumulado_percentual` 33.14 |
| V6 | `observatorio coletar -i ipca --simular-falha` com `COLETOR_DATABASE_URL` de produção: o site mostra "Falha na atualização" e os dados continuam; rode a coleta normal em seguida |
| V10 | Percorrer as páginas: fonte, unidade, período e atualização visíveis |
| V13 | Com a Data API desativada, nenhuma tabela é acessível pela URL do Supabase |
| V14 | Buscar no JavaScript publicado por `postgres`, `password`, `sb_secret`: nada encontrado |
