-- Schemas das três camadas e papéis com privilégio mínimo (data-model.md, Princípio VII).
--
-- Os papéis são criados SEM login. Para habilitar o login, defina a senha fora do repositório
-- (SQL Editor do Supabase ou psql), por exemplo:
--   ALTER ROLE coletor WITH LOGIN PASSWORD '<senha forte>';
--   ALTER ROLE api_leitura WITH LOGIN PASSWORD '<senha forte>';

CREATE SCHEMA IF NOT EXISTS bruto;
CREATE SCHEMA IF NOT EXISTS tratado;
CREATE SCHEMA IF NOT EXISTS publico;

COMMENT ON SCHEMA bruto IS 'Dados brutos exatamente como vieram das fontes oficiais';
COMMENT ON SCHEMA tratado IS 'Séries padronizadas, validadas e versionadas';
COMMENT ON SCHEMA publico IS 'Resultados publicados para consulta pela API';

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'coletor') THEN
    CREATE ROLE coletor NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'api_leitura') THEN
    CREATE ROLE api_leitura NOLOGIN;
  END IF;
END
$$;

-- Ninguém além do coletor enxerga as camadas internas.
REVOKE ALL ON SCHEMA bruto, tratado FROM PUBLIC, anon, authenticated;
REVOKE ALL ON SCHEMA publico FROM PUBLIC;

GRANT USAGE, CREATE ON SCHEMA bruto, tratado, publico TO coletor;
GRANT USAGE ON SCHEMA publico TO api_leitura, anon, authenticated;

-- Privilégios padrão para tabelas e sequências criadas pelas próximas migrações.
ALTER DEFAULT PRIVILEGES IN SCHEMA bruto, tratado, publico
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO coletor;
ALTER DEFAULT PRIVILEGES IN SCHEMA bruto, tratado, publico
  GRANT USAGE, SELECT ON SEQUENCES TO coletor;
ALTER DEFAULT PRIVILEGES IN SCHEMA publico
  GRANT SELECT ON TABLES TO api_leitura, anon, authenticated;
-- O Supabase concede privilégios padrão a anon/authenticated no schema public; aqui nada é
-- concedido a eles em bruto/tratado.
ALTER DEFAULT PRIVILEGES IN SCHEMA bruto, tratado
  REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;
