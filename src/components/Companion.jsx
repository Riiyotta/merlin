// §8 Companion (`e1`, page.split.js:85).
import { useState } from 'react'
import { FI } from '../lib/companion-icons.js'
import { Reveal, useReducedMotion } from '../lib/companion-motion.jsx'
import MerlinMark from './companion/MerlinMark.jsx'
import SectionLabel from './companion/SectionLabel.jsx'
import CompanionShowcase from './companion/CompanionShowcase.jsx'

const HEADLINES = [
  ['No need to leave', 'what you’re doing.'],
  ['Stay in your flow.', 'Help is right here.'],
  ['Keep your focus.', 'Help comes to you.'],
]
const ARROW_PATH =
  'M5 19C22 4 41 8 43 23C46 40 21 35 31 22C45 5 71 20 78 37C84 50 85 62 84 73M73 63C78 68 81 73 84 77C89 73 94 68 99 62'

export default function Companion() {
  const reduced = useReducedMotion()
  const [index, setIndex] = useState(0)
  const [typed, setTyped] = useState(false)
  const lines = HEADLINES[index]

  // After the first "Rephrase word" click every character types in at 28ms/char (CSS companion-type-in).
  const renderLine = (text, offset) =>
    typed && !reduced
      ? Array.from(text).map((ch, i) => (
          <span key={i} className="companion-typed-character" style={{ animationDelay: `${(offset + i) * 28}ms` }}>
            {ch}
          </span>
        ))
      : text

  const askMerlin = (e) =>
    e.currentTarget
      .closest('section')
      ?.querySelector('.portfolio-companion-stage')
      ?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' })

  return (
    <section className="story-section companion-section" id="companion" aria-labelledby="companion-title">
      <div className="companion-heading">
        <div className="companion-title-group">
          <p className="story-bridge story-bridge-handwritten">
            <span>And when you’re working somewhere else…</span>
            <svg viewBox="0 0 112 86" fill="none" aria-hidden="true">
              <path d={ARROW_PATH} />
            </svg>
          </p>
          <SectionLabel />
          <div className="companion-selection-ui">
            <h2
              id="companion-title"
              className="companion-selected-title"
              aria-live="polite"
              aria-atomic="true"
              aria-label={lines.join(' ')}
            >
              <span key={`start-${index}`} aria-hidden="true" className="companion-selected-line companion-selected-start">
                {renderLine(lines[0], 0)}
              </span>
              <br />
              <span key={`end-${index}`} aria-hidden="true" className="companion-selected-line companion-selected-end">
                {renderLine(lines[1], lines[0].length)}
              </span>
            </h2>
            <div className="companion-selection-popover" role="group" aria-label="Selected text actions">
              <button type="button" className="companion-selection-action companion-selection-ask" onClick={askMerlin}>
                <span className="companion-selection-logo" aria-hidden="true">
                  <MerlinMark />
                </span>
                <span>Ask Merlin</span>
              </button>
              <span className="companion-selection-divider" aria-hidden="true" />
              <button
                type="button"
                className="companion-selection-action companion-selection-rephrase"
                onClick={() => {
                  setTyped(true)
                  setIndex((i) => (i + 1) % HEADLINES.length)
                }}
              >
                Rephrase word
              </button>
            </div>
          </div>
        </div>
        <div className="companion-introduction">
          <p>
            That sentence doesn’t sound quite like you. Highlight it and ask{' '}
            <span className="companion-inline-identity">
              <span className="companion-inline-icon companion-inline-merlin" aria-hidden="true">
                <MerlinMark />
              </span>
              Merlin
            </span>{' '}
            for another version. Put it back when it feels right.
          </p>
          <p>
            Or ask about a{' '}
            <span className="companion-inline-identity">
              <span className="companion-inline-icon" aria-hidden="true">
                <img src="/assets/google-chrome.svg" alt="" width={22} height={22} />
              </span>
              webpage
            </span>
            , a file in{' '}
            <span className="companion-inline-identity">
              <span className="companion-inline-icon" aria-hidden="true">
                <img src="/assets/finder.svg" alt="" width={22} height={22} />
              </span>
              Finder
            </span>
            , or what’s on your{' '}
            <span className="companion-inline-identity">
              <span className="companion-inline-icon companion-inline-screen" aria-hidden="true">
                <FI.ufi />
              </span>
              screen
            </span>
            , with your permission.
          </p>
        </div>
        <figure className="portfolio-companion-person">
          <img
            src="/assets/companion.webp"
            alt="A cyan felt character working from a comfortable armchair"
            width={1536}
            height={1024}
            loading="lazy"
          />
          <figcaption>
            A second pair of eyes.
            <br />
            Right when you need one.
          </figcaption>
        </figure>
      </div>
      <Reveal className="portfolio-companion-stage">
        <CompanionShowcase />
      </Reveal>
    </section>
  )
}
