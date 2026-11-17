#!/usr/bin/env bash
# Prepara o banco local de desenvolvimento (docker compose) com as migrações do Supabase.
# Uso: ./infra/preparar-banco-local.sh   (recria o banco "observatorio" do zero)
set -euo pipefail
cd "$(dirname "$0")/.."

PORTA=54329
SENHA_LOCAL="local"   # apenas para a máquina do desenvolvedor
export PGPASSWORD=postgres
psql_admin() { psql -h localhost -p "$PORTA" -U postgres -v ON_ERROR_STOP=1 -q "$@"; }

docker compose up -d --wait banco >/dev/null
psql_admin -d postgres -c "DROP DATABASE IF EXISTS observatorio WITH (FORCE)" -c "CREATE DATABASE observatorio"
psql_admin -d observatorio -f infra/bootstrap-supabase-local.sql
for arquivo in supabase/migrations/*.sql; do
  psql_admin -d observatorio -f "$arquivo"
done
psql_admin -d observatorio \
  -c "ALTER ROLE coletor WITH LOGIN PASSWORD '$SENHA_LOCAL'" \
  -c "ALTER ROLE api_leitura WITH LOGIN PASSWORD '$SENHA_LOCAL'"

echo "Banco local pronto. Use no backend/.env:"
echo "COLETOR_DATABASE_URL=postgresql://coletor:$SENHA_LOCAL@localhost:$PORTA/observatorio"
echo "API_DATABASE_URL=postgresql://api_leitura:$SENHA_LOCAL@localhost:$PORTA/observatorio"
