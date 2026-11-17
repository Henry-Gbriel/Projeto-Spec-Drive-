-- Row Level Security em TODAS as tabelas (defesa em profundidade; research R-07).
-- Tabelas criadas por migração não recebem RLS automaticamente no Supabase.

ALTER TABLE bruto.payload ENABLE ROW LEVEL SECURITY;
ALTER TABLE bruto.coleta ENABLE ROW LEVEL SECURITY;
ALTER TABLE tratado.indicador ENABLE ROW LEVEL SECURITY;
ALTER TABLE tratado.versao_serie ENABLE ROW LEVEL SECURITY;
ALTER TABLE tratado.observacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE tratado.ocorrencia_validacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE publico.indicador_publicado ENABLE ROW LEVEL SECURITY;
ALTER TABLE publico.observacao_publicada ENABLE ROW LEVEL SECURITY;

-- Coletor: acesso completo às três camadas.
CREATE POLICY coletor_tudo ON bruto.payload FOR ALL TO coletor USING (true) WITH CHECK (true);
CREATE POLICY coletor_tudo ON bruto.coleta FOR ALL TO coletor USING (true) WITH CHECK (true);
CREATE POLICY coletor_tudo ON tratado.indicador FOR ALL TO coletor USING (true) WITH CHECK (true);
CREATE POLICY coletor_tudo ON tratado.versao_serie FOR ALL TO coletor USING (true) WITH CHECK (true);
CREATE POLICY coletor_tudo ON tratado.observacao FOR ALL TO coletor USING (true) WITH CHECK (true);
CREATE POLICY coletor_tudo ON tratado.ocorrencia_validacao
  FOR ALL TO coletor USING (true) WITH CHECK (true);
CREATE POLICY coletor_tudo ON publico.indicador_publicado
  FOR ALL TO coletor USING (true) WITH CHECK (true);
CREATE POLICY coletor_tudo ON publico.observacao_publicada
  FOR ALL TO coletor USING (true) WITH CHECK (true);

-- Público (API e, se reativada, API de dados do Supabase): só o que foi publicado.
CREATE POLICY leitura_publicada ON publico.indicador_publicado
  FOR SELECT TO anon, authenticated, api_leitura
  USING (publicado = true);

CREATE POLICY leitura_publicada ON publico.observacao_publicada
  FOR SELECT TO anon, authenticated, api_leitura
  USING (EXISTS (
    SELECT 1 FROM publico.indicador_publicado i
    WHERE i.codigo = indicador_codigo AND i.publicado
  ));

-- Sem políticas para anon/authenticated em bruto e tratado: acesso negado.
-- Garantia extra para tabelas já existentes (os privilégios padrão valem só para as novas).
REVOKE ALL ON ALL TABLES IN SCHEMA bruto, tratado FROM PUBLIC, anon, authenticated, api_leitura;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA publico
  FROM PUBLIC, anon, authenticated, api_leitura;
GRANT SELECT ON ALL TABLES IN SCHEMA publico TO api_leitura, anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA bruto, tratado, publico TO coletor;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA bruto, tratado, publico TO coletor;
