// §11 Footer (6950 chunk, module 42077). Bird flight/drift loops are pure CSS in the original stylesheet.
import { useState } from 'react'
import { FI } from '../lib/companion-icons.js'
import { useReducedMotion } from '../lib/companion-motion.jsx'
import FooterClock from './footer/FooterClock.jsx'

function Wordmark() {
  const [sweeping, setSweeping] = useState(false)
  const reduced = useReducedMotion()
  const start = () => {
    if (!reduced) setSweeping(true)
  }
  return (
    <a
      href="#top"
      className={`closing-wordmark hero-site-name${sweeping && !reduced ? ' hero-site-sweep' : ''}`}
      aria-label="merlin.computer — back to top"
      onMouseEnter={start}
      onFocus={start}
      onAnimationEnd={() => setSweeping(false)}
    >
      merlin.computer
    </a>
  )
}

export default function Footer() {
  return (
    <footer className="closing-footer">
      <div className="closing-sky" aria-hidden="true">
        {[1, 2, 3].map((n) => (
          <div key={n} className={`closing-bird-track closing-bird-track-${n}`}>
            <div className="closing-bird">
              <div className="closing-bird-drift">
                <div className="closing-bird-shape" />
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="closing-main">
        <FooterClock />
        <div className="closing-beach" aria-hidden="true" />
      </div>
      <div className="closing-footer-links">
        <div className="closing-brand">
          <Wordmark />
          <span className="closing-copyright">© {new Date().getFullYear()} merlin computing inc</span>
        </div>
        <nav aria-label="Footer">
          <a href="/pricing">Pricing</a>
          <a href="/manifesto">Manifesto</a>
          <a href="/blog">Blog</a>
          <a href="/privacy">Privacy</a>
          <a href="/terms">Terms</a>
          <a href="mailto:team@merlin.computer">
            Contact <FI.qdV aria-hidden="true" />
          </a>
        </nav>
      </div>
    </footer>
  )
}
