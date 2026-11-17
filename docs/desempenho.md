# Desempenho — Entrega 1 (SC-006)

Meta: conteúdo útil em até 3 s numa conexão móvel 4G típica.

Medição em 2026-10-22 com Lighthouse 12 (perfil móvel padrão: Moto G Power emulado,
4G lento simulado — mais pessimista que um 4G típico), build de produção servido por
`vite preview` e API local com o IPCA real.

| Página | Desempenho | Acessibilidade | FCP | LCP | TBT |
|--------|-----------:|---------------:|----:|----:|----:|
| `/` | 100 | 100 | 1,5 s | 1,5 s | 60 ms |
| `/visao-geral` | 96 | 100 | 1,6 s | 1,8 s | 70 ms |
| `/poder-de-compra` | 99 | 100 | 1,5 s | 1,9 s | 0 ms |
| `/sobre` | 94 | 100 | 1,5 s | 1,8 s | 30 ms |

**Resultado: meta atendida** (LCP ≤ 1,9 s em todas as páginas).

## O que foi necessário

A primeira medição mostrou LCP de 3,6 s nas páginas de dados. Duas mudanças resolveram:

1. **Gráficos sob demanda**: a biblioteca de gráficos (~110 kB comprimidos) é baixada à
   parte (`React.lazy` em `VisaoGeral.tsx`); cartão, título e textos aparecem antes.
   Separar páginas inteiras piorou o LCP (4,0 s), por isso a divisão é só no gráfico.
2. **Fontes sem bloqueio**: a folha do Google Fonts carrega com `media="print"` →
   `all`; o texto aparece com a fonte do sistema até a fonte chegar.

## Como repetir

```bash
cd frontend
VITE_API_URL=http://localhost:8010 VITE_AUTOR_LINKEDIN=... VITE_AUTOR_EMAIL=... npx vite build
npx vite preview --port 4173 &
npx lighthouse http://localhost:4173/visao-geral --only-categories=performance,accessibility
```

Observação: em produção a primeira visita após um período sem acessos pode levar alguns
segundos a mais por causa da partida a frio da API no Cloud Run (plan.md, limitações). A
página e o cartão continuam aparecendo; os dados entram com o estado "carregando".
