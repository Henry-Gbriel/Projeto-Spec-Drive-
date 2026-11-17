# Contrato: arquivos CSV (FR-030, FR-031)

Gerados por `GET /v1/indicadores/{codigo}/serie.csv` a partir da camada `publico`, ou seja, dos
mesmos dados mostrados no site.

## Formato

| Item | Valor | Motivo |
|------|-------|--------|
| Codificação | UTF-8 **com BOM** | Faz o Excel em pt-BR reconhecer os acentos |
| Separador | `;` | A vírgula é o separador decimal no Brasil |
| Separador decimal | `,` | Padrão brasileiro (FR-024) |
| Separador de milhar | nenhum | Evita ambiguidade na leitura automática |
| Quebra de linha | `\r\n` | RFC 4180 |
| Aspas | `"` só quando o campo contém `;`, aspas ou quebra de linha | RFC 4180 |
| Nome do arquivo | `{codigo}_{AAAA-MM}_{AAAA-MM}.csv` ou `{codigo}_completo.csv` | |

## Estrutura

1. **Bloco de metadados**: linhas que começam com `#`, no formato `# chave: valor`, nesta ordem:
   `indicador`, `descricao`, `fonte`, `codigo_serie`, `url_origem`, `unidade`, `frequencia`,
   `natureza` (`real`/`ilustrativo`), `periodo_referencia`, `atualizado_em` (ISO 8601),
   `gerado_em`, `observacao` (texto fixo: "Células de valor vazias indicam observação ausente
   na fonte; o Observatório não estima valores.").
2. **Cabeçalho**: `data;valor;unidade;situacao`.
3. **Linhas**: uma por data de referência, em ordem crescente.
   - `data`: `AAAA-MM-DD` (séries mensais usam o dia 01).
   - `valor`: com a precisão da fonte e vírgula decimal; **vazio** quando ausente.
   - `situacao`: `ok` ou `ausente`.

## Exemplo (trecho; valores apenas ilustram o formato)

```text
# indicador: IPCA — variação mensal
# fonte: IBGE
# codigo_serie: SIDRA tabela 1737, variável 63
# unidade: % ao mês
# natureza: real
# periodo_referencia: 2025-01 a 2025-03
# atualizado_em: 2026-10-22T09:15:00-03:00
data;valor;unidade;situacao
2025-01-01;0,16;% ao mês;ok
2025-02-01;1,31;% ao mês;ok
2025-03-01;;% ao mês;ausente
```

## Regras verificáveis

- O número de linhas de dados é igual ao número de meses do período (SC-010).
- Nenhuma célula de `valor` é preenchida para uma linha `ausente` (SC-004).
- O arquivo abre com os acentos corretos no LibreOffice Calc e no Excel em pt-BR (teste manual
  descrito no quickstart).
