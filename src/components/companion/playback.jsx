// Demo clock (`eR`, page.split.js:67-70) and playback controls (`eP`, page.split.js:71-72).
import { createContext, useContext, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { useInView } from 'framer-motion'
import { useReducedMotion } from '../../lib/companion-motion.jsx'
import { FI, IO } from '../../lib/companion-icons.js'

// Value: undefined -> inline caption/player; null -> nothing yet; Element -> portal target.
export const PlaybackPortalContext = createContext(undefined)

export const DEMO_SPRING = { type: 'spring', stiffness: 440, damping: 34, mass: 0.8 }

export function useDemoClock(duration = 17000, reducedTime = 14000, onComplete) {
  const reduced = useReducedMotion()
  const [time, setTime] = useState(0)
  const [playing, setPlaying] = useState(true)
  const [scale, setScale] = useState(1)
  const viewport = useRef(null)
  const inView = useInView(viewport, { amount: 0.15 })
  const finished = time >= duration

  useEffect(() => {
    const el = viewport.current
    if (!el) return
    const measure = () => setScale(el.clientWidth / 840)
    measure()
    const ro = new ResizeObserver(measure)
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  useEffect(() => {
    if (!inView || reduced || !playing || finished) return
    let last = performance.now()
    const id = window.setInterval(() => {
      const now = performance.now()
      const delta = document.hidden ? 0 : now - last
      last = now
      setTime((t) => Math.min(duration, t + delta))
    }, 40)
    return () => clearInterval(id)
  }, [inView, playing, reduced, finished, duration])

  useEffect(() => {
    if (!finished || !playing || reduced || !onComplete) return
    const check = () => {
      if (!document.hidden) onComplete()
    }
    check()
    document.addEventListener('visibilitychange', check)
    return () => document.removeEventListener('visibilitychange', check)
  }, [finished, playing, reduced, onComplete])

  const t = reduced ? reducedTime : time
  return {
    reduced,
    t,
    playing,
    setPlaying,
    setTime,
    scale,
    viewport,
    restart: () => {
      setTime(0)
      setPlaying(true)
    },
    complete: t >= duration,
    duration,
  }
}

export function DemoPlayback({ playback, caption, done }) {
  const { reduced, t, complete, playing, setPlaying, restart, duration } = playback
  const portalTarget = useContext(PlaybackPortalContext)

  if (portalTarget !== undefined) {
    if (!portalTarget || reduced) return null
    return createPortal(
      <button
        type="button"
        className="companion-footer-play-button"
        onClick={() => (complete ? restart() : setPlaying(!playing))}
        aria-label={complete ? 'Replay demo' : playing ? 'Pause demo' : 'Play demo'}
      >
        {complete ? <FI.cO3 /> : playing ? <IO.FML /> : <IO.vWc />}
      </button>,
      portalTarget,
    )
  }

  return (
    <>
      <div className="companion-demo-playback">
        <div className="companion-demo-caption">
          {done && <span className="is-done" aria-hidden="true">✓</span>}
          <p>{caption}</p>
        </div>
        <div className="companion-demo-player">
          <span>demo</span>
          {!reduced && (
            <>
              <button
                type="button"
                onClick={() => (complete ? restart() : setPlaying(!playing))}
                aria-label={complete ? 'Play demo again' : playing ? 'Pause demo' : 'Play demo'}
              >
                {!complete && playing ? <IO.FML /> : <IO.vWc />}
              </button>
              <button type="button" onClick={restart} aria-label="Restart demo">
                <FI.cO3 />
              </button>
            </>
          )}
        </div>
      </div>
      <div className="companion-demo-progress" aria-hidden="true">
        <span style={{ width: `${(t / duration) * 100}%` }} />
      </div>
    </>
  )
}

export function DemoCursor(props) {
  return (
    <svg width="22" height="27" viewBox="0 0 22 27" {...props}>
      <path
        d="M2 1v21l5.4-5 4.2 8 4-2-4.3-7.9 7.1-.8Z"
        fill="#161616"
        stroke="white"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function WindowLights() {
  return (
    <div className="slack-demo-lights">
      <i />
      <i />
      <i />
    </div>
  )
}

export function AppLogo({ src, size = 18, draggable }) {
  const isChrome = src === '/assets/google-chrome.svg'
  return (
    <img
      src={src}
      width={size}
      height={size}
      alt=""
      aria-hidden="true"
      draggable={isChrome ? false : draggable}
      style={isChrome ? { flexShrink: 0 } : { objectFit: 'contain', flexShrink: 0 }}
    />
  )
}
