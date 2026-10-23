-- Camada pública: snapshot da versão publicada, lido pela API.

CREATE TABLE publico.indicador_publicado (
  codigo                     text PRIMARY KEY,
  nome                       text NOT NULL,
  descricao                  text NOT NULL,
  instituicao                text NOT NULL,
  codigo_serie               text,
  url_origem                 text NOT NULL,
  unidade                    text NOT NULL,
  frequencia                 text NOT NULL,
  casas_decimais             smallint NOT NULL,
  natureza                   text NOT NULL CHECK (natureza IN ('real', 'ilustrativo')),
  situacao                   text NOT NULL CHECK (situacao IN
                               ('atualizado', 'aguardando_integracao', 'em_definicao',
                                'falha_atualizacao')),
  periodo_inicio             date,
  periodo_fim                date,
  ultima_atualizacao_valida  timestamptz,
  ultima_tentativa           timestamptz,
  mensagem_publica           text,
  versao_id                  bigint,
  entrega                    smallint NOT NULL,
  ordem                      smallint NOT NULL DEFAULT 0,
  publicado                  boolean NOT NULL DEFAULT false
);

CREATE INDEX indicador_publicado_publicado_idx ON publico.indicador_publicado (publicado);

CREATE TABLE publico.observacao_publicada (
  indicador_codigo  text NOT NULL REFERENCES publico.indicador_publicado (codigo),
  data_referencia   date NOT NULL,
  valor             numeric(20, 6),
  situacao          text NOT NULL CHECK (situacao IN ('ok', 'ausente')),
  PRIMARY KEY (indicador_codigo, data_referencia),
  CONSTRAINT observacao_publicada_ausente_sem_valor CHECK ((situacao = 'ausente') = (valor IS NULL))
);
