# Publicação — Entrega 1

Passo a passo para publicar banco, rotinas, API e site com custo-alvo de **US$ 0/mês**
(custos e limites em `specs/001-observatorio-do-real/plan.md`, seção "Publicação, custos e
limitações").

> **Antes de começar**, tenha em mãos: o endereço do LinkedIn e o e-mail do autor, e contas
> no Supabase, no Google Cloud (com faturamento ativo, exigido pelo Cloud Run) e na
> Cloudflare. Nenhuma senha ou chave entra no repositório (Princípio VII).

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

## 3. API (Google Cloud Run)

```bash
cd backend
gcloud auth login
gcloud config set project <projeto>
gcloud services enable run.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com

# Segredo com a URL do modo transação (senha do api_leitura)
printf '%s' '<API_DATABASE_URL>' | gcloud secrets create api-database-url --data-file=-

gcloud run deploy observatorio-api \
  --source . \
  --region us-east1 \
  --allow-unauthenticated \
  --min-instances 0 --max-instances 2 \
  --memory 512Mi --cpu 1 \
  --set-secrets API_DATABASE_URL=api-database-url:latest \
  --set-env-vars AMBIENTE=producao,CORS_ORIGENS=https://<dominio-do-site>
```

Depois, em **Faturamento → Orçamentos e alertas**, crie um alerta de **US$ 1**.

Verifique: `curl https://<url-da-api>/v1/saude` → `{"status":"ok","banco":"ok"}`.

## 4. Site (Cloudflare Pages)

1. **Workers & Pages → Create → Pages → Connect to Git**, escolha o repositório.
2. Configuração de build:
   - Diretório raiz: `frontend`
   - Comando: `npm ci && npm run build`
   - Saída: `dist`
3. Variáveis de ambiente (públicas, embutidas no JavaScript — **nunca** segredos):
   - `VITE_API_URL=https://<url-da-api>`
   - `VITE_AUTOR_LINKEDIN=https://www.linkedin.com/in/<perfil>`
   - `VITE_AUTOR_EMAIL=<e-mail>`

   O build falha de propósito se alguma delas faltar.
4. Volte ao passo 3 e ajuste `CORS_ORIGENS` com o domínio final do site.

## 5. Validação no ambiente publicado

Rode os cenários do `specs/001-observatorio-do-real/quickstart.md`:

| Cenário | Como |
|---------|------|
| V2 | `GET /v1/indicadores/ipca/resumo?inicio=2021-01&fim=2025-12` → `acumulado_percentual` 33.14 |
| V6 | **Actions → Coleta diária** com falha simulada (ou `observatorio coletar -i ipca --simular-falha` localmente apontando para produção): o site mostra "Falha na atualização" e os dados continuam |
| V10 | Percorrer as páginas: fonte, unidade, período e atualização visíveis |
| V13 | Com a Data API desativada, nenhuma tabela é acessível pela URL do Supabase |
| V14 | Buscar no JavaScript publicado por `postgres`, `password`, `sb_secret`: nada encontrado |
