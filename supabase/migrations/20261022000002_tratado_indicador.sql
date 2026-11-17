-- Catálogo de indicadores: registro único de metadados (FR-054, Princípio III).
-- Fonte de verdade: dados/catalogo.yaml, sincronizado pela rotina.

CREATE TABLE tratado.indicador (
  codigo               text PRIMARY KEY CHECK (codigo ~ '^[a-z0-9_]+$'),
  nome                 text NOT NULL,
  descricao            text NOT NULL,
  instituicao          text NOT NULL,
  codigo_serie         text,
  url_origem           text NOT NULL,
  conector             text NOT NULL CHECK (conector IN ('sidra', 'sgs', 'olinda', 'manual')),
  parametros_conector  jsonb NOT NULL DEFAULT '{}'::jsonb,
  unidade              text NOT NULL,
  frequencia_fonte     text NOT NULL
                       CHECK (frequencia_fonte IN ('diaria', 'mensal', 'anual', 'por_reuniao')),
  frequencia_exibicao  text NOT NULL CHECK (frequencia_exibicao IN ('mensal', 'anual')),
  agregacao_mensal     text
                       CHECK (agregacao_mensal IN ('media', 'fim_de_mes', 'vigente_fim_de_mes')),
  casas_decimais       smallint NOT NULL CHECK (casas_decimais BETWEEN 0 AND 6),
  natureza             text NOT NULL CHECK (natureza IN ('real', 'ilustrativo')),
  janela_revisao_meses smallint NOT NULL DEFAULT 3 CHECK (janela_revisao_meses >= 0),
  situacao_catalogo    text NOT NULL
                       CHECK (situacao_catalogo IN ('ativo', 'aguardando_integracao', 'em_definicao')),
  entrega              smallint NOT NULL CHECK (entrega BETWEEN 1 AND 4),
  limite_inferior      numeric,
  limite_superior      numeric,
  ordem                smallint NOT NULL DEFAULT 0,
  versao_publicada_id  bigint
);

COMMENT ON COLUMN tratado.indicador.versao_publicada_id IS
  'Ponteiro da versão publicada; só muda dentro da transação de publicação';
COMMENT ON COLUMN tratado.indicador.limite_inferior IS
  'Limite plausível usado pela regra de validação fora_do_intervalo';
