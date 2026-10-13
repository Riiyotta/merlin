// Inline Feather icons used on the blog (CLONE_SPEC_PAGES_B.md §0.2).
const svgProps = {
  stroke: 'currentColor',
  fill: 'none',
  strokeWidth: '2',
  viewBox: '0 0 24 24',
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  'aria-hidden': 'true',
  height: '1em',
  width: '1em',
  xmlns: 'http://www.w3.org/2000/svg',
}

export function ArrowUpRight() {
  return (
    <svg {...svgProps}>
      <line x1="7" y1="17" x2="17" y2="7" />
      <polyline points="7 7 17 7 17 17" />
    </svg>
  )
}

export function ArrowLeft() {
  return (
    <svg {...svgProps}>
      <line x1="19" y1="12" x2="5" y2="12" />
      <polyline points="12 19 5 12 12 5" />
    </svg>
  )
}
