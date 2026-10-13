import { useEffect, useId, useRef, useState } from 'react'
import { flushSync } from 'react-dom'
import { useInView } from 'framer-motion'
import { useReducedMotion } from '../../lib/hero-reduced-motion.js'
import { flipScene, snapshotScene } from '../../lib/hero-flip.js'
import { FiChevronRight, FiRotateCcw, FiVolume2, FiVolumeX } from './icons.jsx'
import NotificationDetail from './NotificationDetail.jsx'

// Port of `et` (page.split.js:33-44): notification stack over the hero landscape.
// Sequence: starts at >=60% in view + tab visible, first card after 180ms, then every 430ms (3 total),
// each arrival FLIP-animated by src/lib/hero-flip.js. Optional two-tone sine ping.

const NOTIFICATIONS = [
  { id: 'meeting', title: 'Your 10am meeting brief is ready.', description: 'Sophie’s notes, in one place.' },
  { id: 'project', title: 'Your launch deck has a first draft.', description: 'Six slides, ready to review.' },
  { id: 'email', title: 'I drafted your reply to Sophie.', description: 'Launch dates and next steps, ready for review.' },
]

export default function HeroNotifications() {
  const sceneRef = useRef(null)
  const sceneId = useId()
  const flightRef = useRef(null)
  const [busy, setBusy] = useState(false)
  const lastOpenedRef = useRef(null)
  const inView = useInView(sceneRef, { amount: 0.6 })
  const reduced = useReducedMotion()
  const [count, setCount] = useState(0)
  const [openId, setOpenId] = useState(null)
  const [readIds, setReadIds] = useState([])
  const [replayKey, setReplayKey] = useState(0)
  const [soundOn, setSoundOn] = useState(false)
  const [tabVisible, setTabVisible] = useState(true)
  const audioRef = useRef(null)
  const soundRef = useRef(false)

  function ping() {
    const ctx = audioRef.current
    if (!soundRef.current || !ctx || ctx.state !== 'running') return
    const now = ctx.currentTime
    ;[880, 1174.66].forEach((freq, i) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      const at = now + 0.095 * i
      osc.type = 'sine'
      osc.frequency.value = freq
      gain.gain.setValueAtTime(0, at)
      gain.gain.linearRampToValueAtTime(0.055, at + 0.012)
      gain.gain.exponentialRampToValueAtTime(1e-4, at + 0.48)
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.start(at)
      osc.stop(at + 0.5)
      osc.onended = () => {
        osc.disconnect()
        gain.disconnect()
      }
    })
  }

  async function toggleSound() {
    if (soundRef.current) {
      soundRef.current = false
      setSoundOn(false)
      audioRef.current?.suspend().catch(() => {})
      return
    }
    try {
      if (!audioRef.current) audioRef.current = new AudioContext()
      await audioRef.current.resume()
      soundRef.current = true
      setSoundOn(true)
      ping()
    } catch (e) {
      soundRef.current = false
      setSoundOn(false)
    }
  }

  function transition(update, focusSelector, arrival = false) {
    const scene = `[data-hn-scene="${sceneId}"]`
    const before = snapshotScene(scene)
    flightRef.current?.abort()
    const controller = new AbortController()
    flightRef.current = controller
    const run = flipScene(before, scene, controller.signal, reduced, arrival, () => {
      flushSync(() => {
        setBusy(true)
        update()
      })
    })
    if (focusSelector) sceneRef.current?.querySelector(focusSelector)?.focus({ preventScroll: true })
    run
      .catch(() => {})
      .finally(() => {
        if (flightRef.current === controller) {
          flightRef.current = null
          setBusy(false)
        }
      })
  }

  function close() {
    transition(() => setOpenId(null), '[data-front="true"]')
  }

  function open(id) {
    transition(() => {
      lastOpenedRef.current = id
      setReadIds((ids) => (ids.includes(id) ? ids : [...ids, id]))
      setOpenId(id)
    }, '.hnd-close')
  }

  function replay() {
    setReadIds([])
    const flight = flightRef.current
    flightRef.current = null
    flight?.abort()
    lastOpenedRef.current = null
    setBusy(false)
    setOpenId(null)
    setCount(0)
    setReplayKey((k) => k + 1)
  }

  useEffect(() => {
    const onVisibility = () => setTabVisible(!document.hidden)
    onVisibility()
    document.addEventListener('visibilitychange', onVisibility)
    return () => {
      document.removeEventListener('visibilitychange', onVisibility)
      const flight = flightRef.current
      flightRef.current = null
      flight?.abort()
      audioRef.current?.close().catch(() => {})
      audioRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!inView || !tabVisible || busy || openId || count >= NOTIFICATIONS.length) return
    const timer = window.setTimeout(
      () => {
        transition(() => setCount((c) => c + 1), undefined, true)
        ping()
      },
      count === 0 ? 180 : 430,
    )
    return () => window.clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inView, tabVisible, count, replayKey, busy, openId])

  const arrived = NOTIFICATIONS.slice(0, count)
  const unread = arrived.filter((n) => !readIds.includes(n.id)).length
  const stacked = arrived.filter((n) => n.id !== openId)
  const anchor = arrived.findIndex((n) => n.id === (openId ?? lastOpenedRef.current))
  const order =
    anchor < 0
      ? arrived.map((n) => n.id).reverse()
      : [...arrived.slice(anchor + +!!openId), ...arrived.slice(0, anchor)].filter((n) => n.id !== openId).map((n) => n.id)
  const openTitle = NOTIFICATIONS.find((n) => n.id === openId)?.title

  return (
    <div
      ref={sceneRef}
      data-hn-scene={sceneId}
      aria-busy={busy}
      className={`hero-notifications${openId ? ' hn-is-open' : ''}`}
      role="region"
      aria-label="Merlin notification preview"
      onKeyDown={(e) => {
        if (e.key === 'Escape' && openId) {
          e.preventDefault()
          close()
        }
      }}
    >
      <div className="hn-workspace" style={{ paddingBottom: 12 * Math.max(0, stacked.length - 1) }}>
        <div className="hn-stack">
          <span className="hn-counter" role="status" aria-live="polite" aria-atomic="true" style={{ opacity: +(unread > 0) }}>
            <span aria-hidden="true">{unread}</span>
            <span className="hn-sr-only">{unread} unread notifications</span>
          </span>
          {stacked.map((n) => {
            const depth = order.indexOf(n.id)
            return (
              <button
                key={`${replayKey}-${n.id}`}
                type="button"
                className={`hn-card${depth > 0 ? ' hn-card-behind' : ''}`}
                aria-label={`Open ${n.title}`}
                aria-expanded={false}
                tabIndex={depth === 0 ? 0 : -1}
                data-hn-surface={n.id}
                data-front={depth === 0}
                onClick={() => open(n.id)}
                style={{
                  zIndex: NOTIFICATIONS.length - depth,
                  width: `${100 - 4.5 * depth}%`,
                  left: `${2.25 * depth}%`,
                  top: depth > 0 ? 12 * depth : undefined,
                }}
              >
                <span className="hn-card-body">
                  <span className="hn-icon" aria-hidden="true">
                    <img
                      alt=""
                      loading="lazy"
                      width={40}
                      height={40}
                      decoding="async"
                      data-nimg="1"
                      src="/assets/merlin-dock.png"
                      style={{ color: 'transparent' }}
                    />
                  </span>
                  <span className="hn-content">
                    <span className="hn-title">{n.title}</span>
                    <span className="hn-description">{n.description}</span>
                  </span>
                  <FiChevronRight className="hn-open-arrow" aria-hidden="true" />
                </span>
              </button>
            )
          })}
        </div>
        {openId && (
          <div
            key={`detail-${replayKey}-${openId}`}
            id="hn-detail-panel"
            data-hn-surface={openId}
            className="hn-detail-shell"
            role="region"
            aria-label={openTitle}
            style={{ zIndex: 20 }}
          >
            <div className="hn-detail-content">
              <NotificationDetail id={openId} onClose={close} />
            </div>
          </div>
        )}
      </div>
      <div className="hn-controls">
        <button onClick={toggleSound} aria-pressed={soundOn} aria-label="Notification sound">
          {soundOn ? <FiVolume2 aria-hidden="true" /> : <FiVolumeX aria-hidden="true" />}
          Sound {soundOn ? 'on' : 'off'}
        </button>
        <button onClick={replay} aria-label="Replay notification animation">
          <FiRotateCcw aria-hidden="true" />
          Replay
        </button>
      </div>
    </div>
  )
}
