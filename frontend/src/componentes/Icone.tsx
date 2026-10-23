/** Ícones em SVG embutido. Decorativos por padrão (o significado sempre vem em texto). */

const CAMINHOS = {
  relogio: 'M12 7v5l3 2M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z',
  alerta:
    'M12 9v4m0 4h.01M10.3 3.9 2 18a2 2 0 0 0 1.7 3h16.6a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z',
  info: 'M12 16v-5m0-3h.01M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z',
  vazio: 'M4 4v16h16M8 16h.01M12 16h.01M16 16h.01',
  'seta-cima': 'M12 19V5m-6 6 6-6 6 6',
  'seta-baixo': 'M12 5v14m6-6-6 6-6-6',
  'seta-direita': 'M5 12h14m-6-6 6 6-6 6',
  download: 'M12 4v11m-5-5 5 5 5-5M5 20h14',
  email: 'M4 6h16v12H4zM4 7l8 6 8-6',
  linkedin: 'M4 4h16v16H4zM8 10v6M8 7.5v.01M12 16v-3.5a2 2 0 0 1 4 0V16M12 10v6',
  check: 'M5 12.5 10 17l9-10',
  atualizar: 'M20 12a8 8 0 1 1-2.3-5.7M20 4v4h-4',
} as const

export type NomeIcone = keyof typeof CAMINHOS

interface Props {
  nome: NomeIcone
  tamanho?: number
  className?: string
}

export function Icone({ nome, tamanho = 16, className }: Props) {
  return (
    <svg
      className={className}
      width={tamanho}
      height={tamanho}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d={CAMINHOS[nome]} />
    </svg>
  )
}
