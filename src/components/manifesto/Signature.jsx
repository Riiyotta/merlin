// Port of module 50047. Adds `is-visible` once the signature is 50% in view; the original CSS then
// draws the circle around "Yours" (manifesto-circle-draw, 1.6s ease-in-out; reduced motion shows it drawn).
import { useEffect, useRef, useState } from 'react'

export default function Signature() {
  const ref = useRef(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          io.disconnect()
        }
      },
      { threshold: 0.5 },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])

  return (
    <div ref={ref} className={`manifesto-signature${visible ? ' is-visible' : ''}`}>
      <span className="manifesto-circled-yours">
        Yours
        <svg viewBox="0 0 180 90" preserveAspectRatio="none" aria-hidden="true" focusable="false">
          <path pathLength="1" d="M155 17C126 1 55 6 22 28C-9 49 6 77 61 80C115 84 172 62 175 37C177 20 157 10 134 9" />
        </svg>
      </span>
      , Merlin
      <img
        alt=""
        loading="lazy"
        width={148}
        height={148}
        decoding="async"
        data-nimg="1"
        className="manifesto-signature-mark"
        style={{ color: 'transparent' }}
        sizes="(max-width: 600px) 112px, 148px"
        src="/assets/mark.webp"
      />
    </div>
  )
}
