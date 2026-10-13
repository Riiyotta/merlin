// Decoding headline (`sn`, page.split.js:89). Char i resolves once frame >= 10 + i.
export const HEADLINE_LINES = ['Personal work.', 'Private by design.']
export const FINAL_FRAME = 10 + HEADLINE_LINES.join('').length
const GLYPHS = '01A9F3C7#8E2B6D4'

export default function DecodingHeadline({ frame }) {
  let offset = 0
  return (
    <h2 id="privacy-heading" aria-label={HEADLINE_LINES.join(' ')}>
      {HEADLINE_LINES.map((line, lineIndex) => {
        const chars = Array.from(line).map((ch, i) => {
          const index = offset + i
          const shown = frame >= 10 + index || ch === ' '
          return (
            <span key={i} className="privacy-code-character">
              <span style={{ opacity: shown ? 1 : 0 }}>{ch === ' ' ? ' ' : ch}</span>
              {!shown && (
                <span className="privacy-code-glyph">{GLYPHS[(7 * frame + 3 * index) % GLYPHS.length]}</span>
              )}
            </span>
          )
        })
        offset += line.length
        return (
          <span
            key={line}
            className={`privacy-headline-line ${lineIndex ? 'privacy-headline-accent' : ''}`}
            aria-hidden="true"
          >
            {chars}
          </span>
        )
      })}
    </h2>
  )
}
