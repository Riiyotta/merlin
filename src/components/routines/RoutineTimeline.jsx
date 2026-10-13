import { useEffect, useId, useRef, useState } from 'react'
import { useInView } from 'framer-motion'
import { useReducedMotion } from '../../lib/hero-reduced-motion.js'
import { FiCheck, FiClock, FiFileText, FiLoader, FiPause, FiPlay, FiRotateCcw, FiZap } from '../hero/icons.jsx'

// Port of `em` (page.split.js:48-51): the "Weekly studio update" routine walkthrough.
// Step counter 0..12 (2*5+2). Delays: step 0 -> 200ms, odd steps -> tool duration,
// even steps -> 120ms, step 11 -> 480ms. Plays only while >=10% in view, tab visible, not paused.
// Visual transitions (.rt-sequence, spinner, status swap) are driven by the original CSS.

const TOOLS = [
  {
    id: 'mail-search',
    app: 'Gmail',
    logo: 'gmail',
    action: 'Find this week’s project emails',
    result: '1 conversation found',
    duration: '0.8s',
    items: [
      {
        title: 'Launch review',
        meta: 'Sophie Hayes → Amira',
        text: 'The website direction looks good. Let’s review the deck alongside the latest designs on Monday.',
      },
    ],
  },
  {
    id: 'mail-read',
    app: 'Gmail',
    logo: 'gmail',
    action: 'Read the launch review conversation',
    result: '4 messages read',
    duration: '0.4s',
    items: [
      {
        title: 'Website direction approved',
        meta: 'Sophie Hayes · Latest reply',
        text: 'The direction is approved. Bring the launch deck and first page designs to Monday’s call so we can agree on the final details.',
      },
    ],
  },
  {
    id: 'notion-search',
    app: 'Notion',
    logo: 'notion',
    action: 'Find the Common Ground project',
    result: '1 project found',
    duration: '0.6s',
    items: [
      {
        title: 'Common Ground · Studio launch',
        meta: 'Project page',
        text: 'Launch plan, website direction, and the team’s latest updates.',
      },
    ],
  },
  {
    id: 'notion-read',
    app: 'Notion',
    logo: 'notion',
    action: 'Read the project notes',
    result: '3 updates collected',
    duration: '0.5s',
    items: [
      {
        title: 'First designs ready',
        meta: 'Leo · Website direction',
        text: 'The homepage designs are ready for review. The opening story follows the approved direction.',
      },
      { title: 'Launch copy', meta: 'Amira · Deliverables', text: 'Final copy still needs a review before it goes into the build.' },
      {
        title: 'Before Friday',
        meta: 'Launch checklist',
        text: 'Review the deck, confirm final copy, and choose a flight for the client visit.',
      },
    ],
  },
  {
    id: 'calendar',
    app: 'Calendar',
    logo: 'calendar',
    action: 'Check the next project meeting',
    result: '1 meeting found',
    duration: '0.3s',
    items: [
      {
        title: 'Launch catch-up with Sophie',
        meta: 'Monday, October 5 · 10:00–10:30 am',
        text: 'Sophie, Amira, and Leo · Review the deck, website designs, and final launch details.',
      },
    ],
  },
]

const LAST = 2 * TOOLS.length + 2

export default function RoutineTimeline() {
  const ref = useRef(null)
  const inView = useInView(ref, { amount: 0.1 })
  const reduced = useReducedMotion()
  const uid = useId()
  const [step, setStep] = useState(0)
  const [playing, setPlaying] = useState(true)
  const [tabVisible, setTabVisible] = useState(true)
  const shown = reduced ? LAST : step
  const done = shown === LAST

  useEffect(() => {
    const onVisibility = () => setTabVisible(!document.hidden)
    onVisibility()
    document.addEventListener('visibilitychange', onVisibility)
    return () => document.removeEventListener('visibilitychange', onVisibility)
  }, [])

  useEffect(() => {
    if (!inView || !tabVisible || !playing || reduced || done) return
    const tool = TOOLS[Math.floor(step / 2)]
    const delay =
      step === 0 ? 200 : step === LAST - 1 ? 480 : step % 2 === 1 ? 1000 * Number.parseFloat(tool.duration) : 120
    const timer = window.setTimeout(() => setStep((s) => s + 1), delay)
    return () => window.clearTimeout(timer)
  }, [inView, tabVisible, playing, reduced, done, step])

  return (
    <div
      ref={ref}
      className={`routine-timeline${playing && inView && tabVisible ? '' : ' rt-paused'}`}
      aria-label="Weekly studio update routine walkthrough"
    >
      <div className="rt-run-eyebrow">
        <FiClock />
        Every Friday · 4:00 pm
        {!reduced && (
          <button
            type="button"
            className="rt-playback"
            onClick={
              done
                ? () => {
                    setStep(0)
                    setPlaying(true)
                  }
                : () => setPlaying((p) => !p)
            }
            aria-label={done ? 'Replay routine' : playing ? 'Pause routine' : 'Resume routine'}
          >
            {done ? <FiRotateCcw /> : playing ? <FiPause /> : <FiPlay />}
            {done ? 'Replay' : playing ? 'Pause' : 'Resume'}
          </button>
        )}
      </div>
      <ol className="rt-feed rt-tool-feed">
        <li className="rt-entry rt-update rt-trigger">
          <span className="rt-node rt-node-purple">
            <FiZap />
          </span>
          <div>
            <strong>Weekly studio update started</strong>
            <span className="rt-run-time">4:00 pm</span>
          </div>
        </li>
        {TOOLS.map((tool, i) => {
          const visible = shown >= 2 * i + 1
          const complete = shown >= 2 * i + 2
          const showResult = complete && i === 0
          return (
            <li
              key={tool.id}
              className={`rt-entry rt-tool-entry rt-sequence ${visible ? 'is-visible' : ''} ${
                complete ? 'is-complete' : visible ? 'is-running' : ''
              }`}
              aria-hidden={!visible}
            >
              <span className="rt-node rt-node-tool">
                <img src={`/assets/${tool.logo}.png`} alt={tool.app} width={15} height={15} />
              </span>
              <div className="rt-tool-toggle">
                <span className="rt-tool-label">
                  <strong>{tool.action}</strong>
                  <span className="rt-status-swap">
                    <span aria-hidden={complete}>Working…</span>
                    <span aria-hidden={!complete}>{tool.result}</span>
                  </span>
                </span>
                <span className="rt-tool-meta">
                  <span className="rt-status-icon" aria-hidden="true">
                    <FiLoader className="rt-spinner" />
                    <FiCheck className="rt-check" />
                  </span>
                  <span className="rt-duration">{complete ? tool.duration : ''}</span>
                </span>
              </div>
              {(showResult || (!complete && i === 0)) && (
                <div
                  className={`rt-tool-results${showResult ? '' : ' rt-result-pending'}`}
                  aria-hidden={!showResult}
                  id={`${uid}-${tool.id}`}
                >
                  {tool.items.map((item, j) => (
                    <article key={item.title} className={`rt-card ${tool.items.length > 1 && j === 0 ? 'rt-card-stack' : ''}`}>
                      <h4>{item.title}</h4>
                      <small>{item.meta}</small>
                      <p>{item.text}</p>
                    </article>
                  ))}
                </div>
              )}
            </li>
          )
        })}
        <li className={`rt-entry rt-update rt-synthesis rt-sequence ${shown >= LAST - 1 ? 'is-visible' : ''}`} aria-hidden={shown < LAST - 1}>
          <span className="rt-node rt-node-purple">
            <FiZap />
          </span>
          <div>
            <strong>Pulling decisions and loose ends together</strong>
            <span className="rt-tool-complete">
              {done ? <FiCheck /> : <FiLoader className="rt-spinner" />}
              {done ? 'Done' : 'Working…'}
            </span>
          </div>
        </li>
        <li className={`rt-entry rt-card-entry rt-sequence ${done ? 'is-visible' : ''}`} aria-hidden={!done}>
          <span className="rt-node rt-node-blue">
            <FiFileText />
          </span>
          <article className="rt-card rt-card-stack rt-final-update">
            <header>
              <h4>Your Friday update, ready.</h4>
              <span className="rt-badge">
                <FiCheck />
                Prepared for you
              </span>
            </header>
            <p>The website direction is approved, and Leo’s first designs are ready for a look.</p>
            <ul>
              <li>Review the deck with Sophie and Leo on Monday at 10.</li>
              <li>Give the final launch copy one more read.</li>
              <li>Choose a flight for the client visit on October 9.</li>
            </ul>
            <div className="rt-card-sources">
              <img src="/assets/gmail.png" alt="Gmail" width={15} height={15} />
              <img src="/assets/notion.png" alt="Notion" width={15} height={15} />
              <img src="/assets/calendar.png" alt="Calendar" width={15} height={15} />
              <span>Based on the emails, project notes, and calendar above</span>
            </div>
          </article>
        </li>
      </ol>
      <span className="rt-announcement" role="status">
        {done ? 'Weekly studio update complete. Your Friday update is ready.' : ''}
      </span>
    </div>
  )
}
