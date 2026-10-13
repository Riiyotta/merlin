// §9 Privacy (`si`, page.split.js:90-92).
import { useEffect, useRef, useState } from 'react'
import { useInView } from 'framer-motion'
import { FI } from '../lib/companion-icons.js'
import { Reveal, useReducedMotion } from '../lib/companion-motion.jsx'
import DecodingHeadline, { FINAL_FRAME } from './privacy/DecodingHeadline.jsx'

export default function Privacy() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.18 })
  const reduced = useReducedMotion()
  const [frame, setFrame] = useState(0)

  useEffect(() => {
    if (!inView || reduced) return
    let current = 0
    const id = window.setInterval(() => {
      if (document.hidden) return
      setFrame((current += 1))
      if (current >= FINAL_FRAME) window.clearInterval(id)
    }, 55)
    return () => window.clearInterval(id)
  }, [inView, reduced])

  return (
    <section ref={ref} className="privacy-scene" id="privacy" aria-labelledby="privacy-heading">
      <div className="privacy-layout">
        <Reveal className="privacy-intro">
          <a className="privacy-eyebrow" href="/privacy">
            Privacy and control <FI.fOo aria-hidden="true" />
          </a>
          <DecodingHeadline frame={reduced ? FINAL_FRAME : frame} />
          <p className="privacy-intro-copy">
            Your work is personal. You choose what to share with Merlin and when to step in. We never sell your personal
            information.
          </p>
        </Reveal>
        <Reveal className="privacy-trust-cards">
          <article className="privacy-trust-card">
            <svg viewBox="0 0 200 200" fill="none" aria-hidden="true">
              {[36, 24, 12, 0].map((y, i) => (
                <path
                  key={y}
                  className="privacy-animated-layer"
                  style={{ animationDelay: `${-0.35 * i}s` }}
                  d="m30 76 70-36 70 36v15l-70 36-70-36Z"
                  transform={`translate(0 ${y})`}
                />
              ))}
              <path className="privacy-card-accent" d="m77 78 16 9 30-17" />
            </svg>
            <h3>Independently audited security</h3>
            <p>Merlin’s security controls undergo independent assessment through a SOC 2 Type II audit.</p>
          </article>
          <article className="privacy-trust-card">
            <svg viewBox="0 0 200 200" fill="none" aria-hidden="true">
              <path d="m36 59 97-22 31 21v98l-97 22-31-21Z" />
              <path d="m36 59 31 21 97-22M67 80v98M84 93l60-14M84 117l60-14M84 141l60-14" />
              <g className="privacy-card-accent">
                <path className="privacy-slider privacy-slider-one" d="M104 83v11" />
                <path className="privacy-slider privacy-slider-two" d="M131 101v11" />
                <path className="privacy-slider privacy-slider-three" d="M98 127v11" />
              </g>
            </svg>
            <h3>Your approval comes first</h3>
            <p>Merlin asks before sending emails or invites. You’re in control.</p>
          </article>
          <article className="privacy-trust-card">
            <svg viewBox="0 0 200 200" fill="none" aria-hidden="true">
              {[18, 9, 0].map((o, i) => (
                <path
                  key={o}
                  className="privacy-shield-ring"
                  style={{ animationDelay: `${-0.65 * i}s` }}
                  d="m100 35 53 20v45c0 30-24 50-53 64-29-14-53-34-53-64V55Z"
                  transform={`translate(${o / 2} ${-o / 2})`}
                />
              ))}
              <rect x="82" y="88" width="36" height="29" rx="4" />
              <path d="M89 88v-9a11 11 0 0 1 22 0v9" />
              <path className="privacy-card-accent" d="M100 99v8" />
            </svg>
            <h3>No model training</h3>
            <p>Neither Merlin nor our AI providers use your data to train models.</p>
          </article>
          <article className="privacy-trust-card">
            <svg viewBox="0 0 200 200" fill="none" aria-hidden="true">
              <rect x="30" y="55" width="48" height="90" rx="6" />
              <rect x="122" y="55" width="48" height="90" rx="6" />
              <path d="M40 70h28M40 80h20M132 70h28M132 80h20M78 100h44" />
              <circle className="privacy-transit-signal" cx="80" cy="100" r="2" fill="#50c7d8" stroke="none" />
              <rect x="88" y="89" width="24" height="23" rx="3" fill="#000" />
              <path d="M93 89v-7a7 7 0 0 1 14 0v7" />
              <path className="privacy-card-accent" d="M100 97v7M49 129h10M141 129h10" />
            </svg>
            <h3>Protected in storage and transit</h3>
            <p>Your data is encrypted when stored and as it moves between systems.</p>
          </article>
        </Reveal>
      </div>
    </section>
  )
}
