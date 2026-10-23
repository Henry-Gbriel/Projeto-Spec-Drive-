-- Séries tratadas e versionadas, com histórico de revisões (SCD tipo 2).

CREATE TABLE tratado.versao_serie (
  id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  indicador_codigo  text NOT NULL REFERENCES tratado.indicador (codigo),
  coleta_id         bigint NOT NULL REFERENCES bruto.coleta (id),
  criada_em         timestamptz NOT NULL DEFAULT now(),
  status            text NOT NULL CHECK (status IN
                      ('em_tratamento', 'validada', 'rejeitada', 'publicada', 'substituida')),
  n_observacoes     integer NOT NULL DEFAULT 0,
  primeira_data     date,
  ultima_data       date,
  n_inseridas       integer NOT NULL DEFAULT 0,
  n_revisadas       integer NOT NULL DEFAULT 0,
  n_inalteradas     integer NOT NULL DEFAULT 0,
  hash_conteudo     char(64),
  versao_codigo     text NOT NULL
);

-- Só uma versão publicada por indicador.
CREATE UNIQUE INDEX versao_publicada_unica_idx
  ON tratado.versao_serie (indicador_codigo) WHERE status = 'publicada';

ALTER TABLE tratado.indicador
  ADD CONSTRAINT indicador_versao_publicada_fk
  FOREIGN KEY (versao_publicada_id) REFERENCES tratado.versao_serie (id);

CREATE TABLE tratado.observacao (
  id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  indicador_codigo  text NOT NULL REFERENCES tratado.indicador (codigo),
  data_referencia   date NOT NULL,
  valor             numeric(20, 6),
  situacao          text NOT NULL CHECK (situacao IN ('ok', 'ausente')),
  versao_inicio_id  bigint NOT NULL REFERENCES tratado.versao_serie (id),
  versao_fim_id     bigint REFERENCES tratado.versao_serie (id),
  CONSTRAINT observacao_ausente_sem_valor CHECK ((situacao = 'ausente') = (valor IS NULL))
);

COMMENT ON TABLE tratado.observacao IS
  'Nunca há UPDATE de valor: revisões fecham a linha antiga (versao_fim_id) e abrem outra';

-- No máximo um valor vigente por data (prevenção de duplicidade).
CREATE UNIQUE INDEX observacao_vigente_unica_idx
  ON tratado.observacao (indicador_codigo, data_referencia) WHERE versao_fim_id IS NULL;

CREATE TABLE tratado.ocorrencia_validacao (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  versao_id        bigint NOT NULL REFERENCES tratado.versao_serie (id),
  regra            text NOT NULL,
  severidade       text NOT NULL CHECK (severidade IN ('bloqueante', 'aviso')),
  data_referencia  date,
  detalhe          jsonb NOT NULL DEFAULT '{}'::jsonb
);
