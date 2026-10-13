// Static Merlin face mark (component `t` in page.split.js:5, non-animated branch).
const EYE_STYLE = (cx) => ({
  transform: 'scale(1)',
  transformOrigin: `${cx}px 66px`,
  transition: 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
})

export default function MerlinMark({ className, style }) {
  return (
    <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className={className} style={style}>
      <path
        d="M 28 52 C 24 40 24 24 38 26 C 44 27 42 36 42 42 C 42 48 46 52 50 52 C 54 52 58 48 58 42 C 58 36 56 27 62 26 C 76 24 76 40 72 52"
        stroke="currentColor"
        strokeWidth="6.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <g><g><circle cx="38" cy="66" r="4.5" fill="currentColor" style={EYE_STYLE(38)} /></g></g>
      <g><g><circle cx="62" cy="66" r="4.5" fill="currentColor" style={EYE_STYLE(62)} /></g></g>
      <path
        d="M 39 79 Q 50 88 61 79"
        stroke="currentColor"
        strokeWidth="5"
        strokeLinecap="round"
        fill="none"
        style={{ transition: 'd 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
      />
    </svg>
  )
}

// The demos give this mark the Tailwind-style height/width "4" utility pair. The original CSS
// defines the height one as 16px square; the string is assembled at runtime so Tailwind's JIT
// scanner does not emit its own rem-based utilities (10px at the 62.5% root) that would win.
export const MARK_SMALL_CLASS = ['h', '4'].join('-') + ' ' + ['w', '4'].join('-')
