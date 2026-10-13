// Tabbed demo switcher (`eX` + `eJ`, page.split.js:80-85).
import { useCallback, useEffect, useId, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { FI } from '../../lib/companion-icons.js'
import { useReducedMotion } from '../../lib/companion-motion.jsx'
import { AppLogo, PlaybackPortalContext } from './playback.jsx'
import PhotoshopDemo from './PhotoshopDemo.jsx'
import SlackDemo from './SlackDemo.jsx'
import ChromeDemo from './ChromeDemo.jsx'

const ARROW_PATH =
  'M5 19C22 4 41 8 43 23C46 40 21 35 31 22C45 5 71 20 78 37C84 50 85 62 84 73M73 63C78 68 81 73 84 77C89 73 94 68 99 62'

const EXAMPLES = [
  { name: 'Photoshop', logo: '/assets/photoshop.png', description: 'Removing a background in Photoshop.', focus: 430 },
  { name: 'Slack', logo: '/assets/slack.png', description: 'Rewriting a reply in your own words.', focus: 265 },
  { name: 'Chrome', logo: '/assets/google-chrome.svg', description: 'Turning an article into ideas to try.', focus: 380 },
]

export default function CompanionShowcase() {
  const [active, setActive] = useState(0)
  const [portalTarget, setPortalTarget] = useState(null)
  const reduced = useReducedMotion()
  const [detailed, setDetailed] = useState(false)
  const id = useId()
  const stageRef = useRef(null)
  const tabRefs = useRef([])
  const example = EXAMPLES[active]
  const next = useCallback(() => setActive((i) => (i + 1) % EXAMPLES.length), [])

  useEffect(() => {
    if (stageRef.current) stageRef.current.scrollLeft = detailed ? example.focus : 0
  }, [detailed, example.focus])

  const onTabKeyDown = (e, index) => {
    const target =
      e.key === 'ArrowRight'
        ? (index + 1) % EXAMPLES.length
        : e.key === 'ArrowLeft'
          ? (index + EXAMPLES.length - 1) % EXAMPLES.length
          : e.key === 'Home'
            ? 0
            : e.key === 'End'
              ? EXAMPLES.length - 1
              : null
    if (target === null) return
    e.preventDefault()
    setActive(target)
    tabRefs.current[target]?.focus()
  }

  return (
    <PlaybackPortalContext.Provider value={portalTarget}>
      <div className="companion-context-note">
        <h3
          key={active}
          className="companion-context-title"
          style={{ fontFamily: "'caveat', 'caveat Fallback'" }}
          aria-live="polite"
          aria-atomic="true"
          aria-label={example.description}
        >
          <span aria-hidden="true">
            {example.description.split(' ').map((word, i) => (
              <motion.span
                key={i}
                className="companion-context-word"
                initial={!reduced && { opacity: 0, y: 8, rotate: -2 }}
                animate={{ opacity: 1, y: 0, rotate: 0 }}
                transition={{ duration: reduced ? 0 : 0.35, delay: reduced ? 0 : 0.055 * i, ease: 'easeOut' }}
              >
                {word}
                {' '}
              </motion.span>
            ))}
          </span>
        </h3>
        <svg className="companion-context-arrow" viewBox="0 0 112 86" fill="none" aria-hidden="true">
          <motion.path
            key={active}
            d={ARROW_PATH}
            initial={!reduced && { pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: reduced ? 0 : 0.65, delay: reduced ? 0 : 0.2 }}
          />
        </svg>
      </div>
      <div className="companion-showcase">
        <div
          role="tabpanel"
          id={`${id}-panel`}
          aria-labelledby={`${id}-tab-${active}`}
          className="companion-example-panel"
        >
          <div className="companion-example-heading">
            <button
              type="button"
              className="companion-detail-toggle"
              aria-pressed={detailed}
              aria-controls={`${id}-stage`}
              onClick={() => setDetailed(!detailed)}
            >
              {detailed ? <FI.eDi /> : <FI.mkN />}
              {detailed ? 'Fit the screen' : 'See the details'}
            </button>
          </div>
          <div
            className={`companion-stage ${detailed ? 'companion-stage-detailed' : ''}`}
            id={`${id}-stage`}
            ref={stageRef}
            tabIndex={detailed ? 0 : undefined}
            aria-label={detailed ? `${example.name} demo. Scroll horizontally to explore the full app.` : undefined}
          >
            <div key={active} className="companion-stage-inner">
              {active === 0 ? (
                <PhotoshopDemo onComplete={next} />
              ) : active === 1 ? (
                <SlackDemo workspace={{ name: 'Common Ground' }} onComplete={next} />
              ) : (
                <ChromeDemo onComplete={next} />
              )}
            </div>
          </div>
          {detailed && (
            <p className="companion-pan-hint">
              Scroll across to explore the app <FI.dyV />
            </p>
          )}
        </div>
        <div className="companion-switch">
          <div role="tablist" aria-label="Companion app examples">
            {EXAMPLES.map(({ name, logo }, i) => (
              <button
                key={name}
                type="button"
                role="tab"
                id={`${id}-tab-${i}`}
                ref={(el) => {
                  tabRefs.current[i] = el
                }}
                aria-label={name}
                title={name}
                aria-selected={active === i}
                aria-controls={`${id}-panel`}
                tabIndex={active === i ? 0 : -1}
                onKeyDown={(e) => onTabKeyDown(e, i)}
                onClick={() => setActive(i)}
              >
                {active === i && (
                  <motion.span
                    className="companion-app-indicator"
                    layoutId={`${id}-app-indicator`}
                    transition={reduced ? { duration: 0 } : { type: 'spring', stiffness: 380, damping: 32 }}
                    aria-hidden="true"
                  />
                )}
                <AppLogo src={logo} size={20} />
                <span className="companion-app-name">{name}</span>
              </button>
            ))}
          </div>
          <div className="companion-footer-playback" ref={setPortalTarget} />
        </div>
      </div>
    </PlaybackPortalContext.Provider>
  )
}
