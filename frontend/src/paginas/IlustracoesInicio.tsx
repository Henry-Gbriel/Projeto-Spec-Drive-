// Ilustrações decorativas da página inicial (referência: docs/referencias-visuais/*/01-pagina-inicial.png).
// Não representam dados: ficam ocultas para leitores de tela.

// Contorno simplificado do Brasil em (longitude, latitude).
const CONTORNO: [number, number][] = [
  [-73.9, -7.3],
  [-72.5, -5],
  [-70, -4.2],
  [-69.5, -1],
  [-69.9, 1.2],
  [-67, 2],
  [-64, 4],
  [-60.7, 5.2],
  [-59.8, 4.2],
  [-57, 1.9],
  [-54, 2.2],
  [-51.6, 4.3],
  [-50, 1.8],
  [-49.9, -0.5],
  [-48, -1],
  [-44.5, -2.5],
  [-41, -2.9],
  [-38, -3.8],
  [-35.3, -5.2],
  [-34.8, -7.3],
  [-35.3, -9.5],
  [-37.2, -11],
  [-38.9, -13.4],
  [-39.2, -17.7],
  [-40.8, -20.9],
  [-41.8, -22.9],
  [-44.6, -23.4],
  [-48, -25.4],
  [-48.6, -28.5],
  [-50.3, -30.6],
  [-52.5, -33.7],
  [-53.4, -33.7],
  [-55.6, -30.8],
  [-57.6, -30.2],
  [-55.7, -27.4],
  [-54.6, -25.6],
  [-54.3, -24],
  [-55.6, -22.6],
  [-57.9, -22],
  [-58.2, -20],
  [-57.5, -18],
  [-58.4, -16.3],
  [-60.2, -16.2],
  [-60.5, -13.7],
  [-62.2, -13.1],
  [-65.3, -11.5],
  [-65.4, -9.8],
  [-68, -10.7],
  [-70.6, -11],
  [-70.5, -9.4],
  [-72.8, -9.4],
]

// Brasília e cinco capitais ligadas a ela.
const CENTRO: [number, number] = [-47.9, -15.8]
const CIDADES: [number, number][] = [
  [-60, -3.1], // Manaus
  [-34.9, -8.05], // Recife
  [-43.2, -22.9], // Rio de Janeiro
  [-46.6, -23.5], // São Paulo
  [-51.2, -30], // Porto Alegre
]

const ESCALA = 10
const projetar = ([lon, lat]: [number, number]): [number, number] => [
  (lon + 75) * ESCALA,
  (6 - lat) * ESCALA,
]
const POLIGONO = CONTORNO.map(projetar)

function dentro([x, y]: [number, number]): boolean {
  let resultado = false
  for (let i = 0, j = POLIGONO.length - 1; i < POLIGONO.length; j = i++) {
    const [xi, yi] = POLIGONO[i] as [number, number]
    const [xj, yj] = POLIGONO[j] as [number, number]
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) resultado = !resultado
  }
  return resultado
}

const PASSO = 11
const PONTOS: [number, number][] = []
for (let y = PASSO / 2; y < 410; y += PASSO) {
  for (let x = PASSO / 2; x < 430; x += PASSO) {
    if (dentro([x, y])) PONTOS.push([x, y])
  }
}

export function MapaPontilhado({ className }: { className?: string }) {
  const [cx, cy] = projetar(CENTRO)
  return (
    <svg
      viewBox="0 0 430 410"
      className={className}
      aria-hidden="true"
      focusable="false"
      data-testid="mapa-pontilhado"
    >
      <g fill="var(--cor-amarelo)" opacity="0.45">
        {PONTOS.map(([x, y]) => (
          <circle key={`${x}-${y}`} cx={x} cy={y} r="1.3" />
        ))}
      </g>
      <g stroke="var(--cor-amarelo)" strokeWidth="1" strokeDasharray="3 4" opacity="0.7">
        {CIDADES.map(projetar).map(([x, y]) => (
          <line key={`l-${x}-${y}`} x1={cx} y1={cy} x2={x} y2={y} />
        ))}
      </g>
      <g fill="var(--cor-amarelo)">
        {[CENTRO, ...CIDADES].map(projetar).map(([x, y]) => (
          <g key={`c-${x}-${y}`}>
            <circle cx={x} cy={y} r="7" fill="none" stroke="var(--cor-amarelo)" opacity="0.5" />
            <circle cx={x} cy={y} r="3" />
          </g>
        ))}
      </g>
    </svg>
  )
}

export function LosangoBandeira({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 1000 400"
      preserveAspectRatio="xMidYMid slice"
      className={className}
      aria-hidden="true"
      focusable="false"
      data-testid="losango-bandeira"
    >
      <g fill="none" stroke="rgba(61, 220, 151, 0.22)" strokeWidth="1.5">
        <polygon points="500,-70 880,200 500,470 120,200" />
        <circle cx="500" cy="200" r="150" />
      </g>
    </svg>
  )
}
