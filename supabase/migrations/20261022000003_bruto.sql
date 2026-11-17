-- Camada bruta: respostas das fontes preservadas sem alteração (FR-051, Princípio IV).

CREATE TABLE bruto.payload (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  sha256         char(64) NOT NULL UNIQUE,
  conteudo       jsonb NOT NULL,
  tamanho_bytes  integer NOT NULL,
  recebido_em    timestamptz NOT NULL DEFAULT now()
);

COMMENT ON COLUMN bruto.payload.sha256 IS
  'Hash dos bytes recebidos; evita guardar o mesmo conteúdo duas vezes';

CREATE TABLE bruto.coleta (
  id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  indicador_codigo  text NOT NULL REFERENCES tratado.indicador (codigo),
  execucao_id       uuid NOT NULL,
  iniciada_em       timestamptz NOT NULL DEFAULT now(),
  concluida_em      timestamptz,
  status            text NOT NULL CHECK (status IN ('sucesso', 'falha', 'sem_novidade')),
  url_requisitada   text,
  parametros        jsonb NOT NULL DEFAULT '{}'::jsonb,
  http_status       integer,
  erro              text,
  payload_id        bigint REFERENCES bruto.payload (id)
);

CREATE INDEX coleta_indicador_data_idx ON bruto.coleta (indicador_codigo, iniciada_em DESC);
