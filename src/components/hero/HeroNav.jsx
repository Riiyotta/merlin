import { useCallback, useEffect, useRef, useState } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { useReducedMotion } from '../../lib/hero-reduced-motion.js'

// Port of the hero corner nav (6950 chunk, module 63154).
// The dot rides a spring {stiffness:170, damping:15, mass:.8} to the hovered/focused link with a
// perpendicular "bend" of up to -8px shaped 4n(1-n) over travel and scale 1 + .35*4n(1-n).

const SPRING = { stiffness: 170, damping: 15, mass: 0.8 }
// Current route, read once per load (site links are full page loads). Trailing slash stripped so /pricing/ matches /pricing.
const PATHNAME = window.location.pathname.replace(/\/+$/, '') || '/'

function useNavDot({ axis, bend = 16, lead, size = 5, reduced = false }) {
  const trackRef = useRef(null)
  const [showing, setShowing] = useState(false)
  const target = useMotionValue(0)
  const main = useSpring(target, SPRING)
  const bendOffset = useMotionValue(0)
  const scale = useMotionValue(1)
  const crossTarget = useMotionValue(0)
  const cross = useSpring(crossTarget, SPRING)
  const crossWithBend = useTransform(() => cross.get() + bendOffset.get())
  const fromRef = useRef(0)
  const toRef = useRef(0)
  const bendRef = useRef(0)
  const rafRef = useRef(0)

  const runBend = useCallback(() => {
    cancelAnimationFrame(rafRef.current)
    const tick = () => {
      const from = fromRef.current
      const to = toRef.current
      const distance = to - from
      if (Math.abs(distance) < 1) {
        bendOffset.set(0)
        return
      }
      const pos = main.get()
      const n = Math.max(0, Math.min(1, (pos - from) / distance))
      const shape = 4 * n * (1 - n)
      bendOffset.set(bendRef.current * shape)
      scale.set(1 + 0.35 * shape)
      if (Math.abs(pos - to) > 0.3 || Math.abs(bendOffset.get()) > 0.3) {
        rafRef.current = requestAnimationFrame(tick)
      } else {
        bendOffset.set(0)
        scale.set(1)
      }
    }
    rafRef.current = requestAnimationFrame(tick)
  }, [main, bendOffset, scale])

  const move = useCallback(
    (el) => {
      const track = trackRef.current
      if (!track) return
      const t = track.getBoundingClientRect()
      const r = el.getBoundingClientRect()
      const along = axis === 'x' ? r.left - t.left + r.width / 2 - size / 2 : r.top - t.top + r.height / 2 - size / 2
      const across = lead === undefined ? 0 : axis === 'x' ? r.bottom - t.top + lead : r.left - t.left - lead - size
      if (!showing || reduced) {
        cancelAnimationFrame(rafRef.current)
        target.jump(along)
        main.jump(along)
        crossTarget.jump(across)
        cross.jump(across)
        bendOffset.set(0)
        scale.set(1)
        setShowing(true)
        return
      }
      crossTarget.set(across)
      const current = main.get()
      fromRef.current = current
      toRef.current = along
      bendRef.current = Math.min(Math.abs(bend), 0.14 * Math.abs(along - current)) * Math.sign(bend)
      target.set(along)
      runBend()
    },
    [axis, bend, lead, size, showing, reduced, target, main, crossTarget, cross, bendOffset, scale, runBend],
  )

  useEffect(() => () => cancelAnimationFrame(rafRef.current), [])

  return {
    trackRef,
    showing,
    move,
    style: axis === 'x' ? { x: main, y: crossWithBend, scale } : { y: main, x: crossWithBend, scale },
  }
}

export default function HeroNav() {
  const reduced = useReducedMotion()
  const dot = useNavDot({ axis: 'y', bend: -8, lead: 10, size: 6, reduced })
  const currentRef = useRef(null)

  useEffect(() => {
    const sync = () => {
      if (currentRef.current) dot.move(currentRef.current)
    }
    sync()
    window.addEventListener('resize', sync)
    return () => window.removeEventListener('resize', sync)
  }, [dot.move])

  const [sweeping, setSweeping] = useState(false)
  const sweepTimer = useRef()
  const sweep = () => {
    if (sweeping || reduced) return
    setSweeping(true)
    sweepTimer.current = window.setTimeout(() => setSweeping(false), 900)
  }
  useEffect(() => () => window.clearTimeout(sweepTimer.current), [])

  const linkProps = (href) => ({
    href,
    ref: PATHNAME === href ? currentRef : undefined,
    'aria-current': PATHNAME === href ? 'page' : undefined,
    onMouseEnter: (e) => dot.move(e.currentTarget),
    onFocus: (e) => dot.move(e.currentTarget),
  })

  return (
    <nav
      ref={dot.trackRef}
      className="hero-corner-nav"
      aria-label="Main navigation"
      onMouseLeave={() => {
        const focused = dot.trackRef.current?.querySelector('a:focus-visible')
        if (focused || currentRef.current) dot.move(focused ?? currentRef.current)
      }}
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget) && currentRef.current) dot.move(currentRef.current)
      }}
    >
      {dot.showing && <motion.span className="hero-nav-dot" aria-hidden="true" style={dot.style} />}
      <a
        {...linkProps('/')}
        className="hero-site-name hero-site-brand"
        onMouseEnter={(e) => {
          dot.move(e.currentTarget)
          sweep()
        }}
        onFocus={(e) => {
          dot.move(e.currentTarget)
          sweep()
        }}
      >
        <img
          className="hero-site-icon"
          src="/assets/merlin-dock-32.png"
          alt=""
          loading="lazy"
          width={20}
          height={20}
          decoding="async"
          data-nimg="1"
          style={{ color: 'transparent' }}
        />
        <span className={`hero-site-name${sweeping ? ' hero-site-sweep' : ''}`}>merlin.computer</span>
      </a>
      <div className="hero-corner-links">
        <a {...linkProps('/pricing')}>Pricing</a>
        <a {...linkProps('/manifesto')}>Manifesto</a>
      </div>
    </nav>
  )
}
