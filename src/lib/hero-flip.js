// Notification-stack FLIP engine, ported 1:1 from the original homepage chunk
// (reference/source/page.split.js:31-32 helpers + `en`, :43 snapshot logic in `R`).
// Uses the Web Animations API; every surface (card / detail shell / counter) is measured
// before and after a React commit, then animated from its old box to its new box.

const ZERO = { cx: 0, cy: 0, width: 0, height: 0, radius: 0 }
const STEP = 1 / 240
const clamp = (v, min, max) => Math.min(max, Math.max(min, v))
const flights = new WeakMap()

const DETAIL = { stiffness: 480, duration: 560 }
const DEFAULT = { stiffness: 620, duration: 480 }
const ARRIVAL = { stiffness: 580, duration: 500 }

// Critically damped curve sampled at 120fps, normalised so the last frame lands at 1.
const CURVES = new Map(
  [DETAIL, DEFAULT, ARRIVAL].map((cfg) => [
    cfg,
    (() => {
      const w = Math.sqrt(cfg.stiffness)
      const f = (t) => 1 - (1 + w * t) * Math.exp(-w * t)
      const end = f(cfg.duration / 1000)
      const count = Math.ceil(cfg.duration / (1000 / 120))
      return Array.from({ length: count + 1 }, (_, i) => {
        const offset = i / count
        return { offset, progress: f((offset * cfg.duration) / 1000) / end }
      })
    })(),
  ]),
)

const lerp = (a, b, t) => a + (b - a) * t
const surfaces = (scene) =>
  document.querySelectorAll(`${scene} [data-hn-surface], ${scene} .hn-counter`)
const surfaceKey = (node) => node.dataset.hnSurface ?? 'counter'
const contentOf = (node) => node.querySelector(':scope > .hn-card-body, :scope > .hn-detail-content')
const kindOf = (node) =>
  node.classList.contains('hn-detail-shell') ? 'detail' : node.classList.contains('hn-counter') ? 'counter' : 'card'
const boxOf = (rect, radius) => ({
  cx: rect.left + rect.width / 2,
  cy: rect.top + rect.height / 2,
  width: rect.width,
  height: rect.height,
  radius,
})
const radiusOf = (value, width, height, scale = 1) =>
  Math.min(value.includes('%') ? (parseFloat(value) / 100) * width : parseFloat(value) * scale, Math.min(width, height) / 2)

// Velocity of an in-flight animation at `time`, so interrupted flights hand momentum on.
function velocityAt(frames, duration, time) {
  if (time <= 0 || time >= duration) return { ...ZERO }
  const p = time / duration
  const i = Math.max(1, frames.findIndex((f) => f.offset >= p))
  const a = frames[i - 1]
  const b = frames[i]
  const dt = ((b.offset - a.offset) * duration) / 1000
  return Object.fromEntries(Object.keys(ZERO).map((k) => [k, (b[k] - a[k]) / dt]))
}

// Spring simulation used for interrupted / morphing flights (card <-> detail).
function simulate(from, to, isDetail, velocity) {
  const cur = { ...from }
  const vel = { ...(velocity ?? ZERO) }
  const k = {
    cx: isDetail ? 900 : 1100,
    cy: isDetail ? 900 : 1100,
    width: isDetail ? 760 : 960,
    height: isDetail ? 640 : 840,
    radius: 900,
  }
  for (const key of Object.keys(cur)) {
    const diff = to[key] - cur[key]
    if (diff) {
      if (vel[key] * diff > 0) vel[key] = Math.sign(diff) * Math.min(Math.abs(vel[key]), Math.sqrt(k[key]) * Math.abs(diff))
    } else vel[key] = 0
  }
  const bulgeWindow = isDetail ? 0.38 : 0.3
  const resized = Math.abs(from.width - to.width) + Math.abs(from.height - to.height) > 1
  const bulge = !velocity && resized ? (isDetail ? 0.32 : 0.22) : 0
  let d = 0
  let t = 0
  let settled = 0
  const frames = [{ ...from, offset: 0 }]
  for (let step = 1; step <= 240; step++) {
    t = step * STEP
    for (const key of Object.keys(cur)) {
      const w = Math.sqrt(k[key])
      const x0 = cur[key] - to[key]
      const r = vel[key] + w * x0
      const e = Math.exp(-w * STEP)
      cur[key] = to[key] + (x0 + r * STEP) * e
      vel[key] = (vel[key] - w * r * STEP) * e
    }
    const target = (1 - clamp(t / bulgeWindow, 0, 1)) ** 3 * bulge
    d += clamp(target - d, -(5 * STEP), 5 * STEP)
    const width = Math.max(1, cur.width)
    const height = Math.max(1, cur.height)
    const maxR = Math.min(width, height) / 2
    const extra = Math.min(100, Math.max(0, maxR - cur.radius)) * d
    const radius = clamp(cur.radius + extra, 0, maxR)
    if (step % 2 === 0) frames.push({ cx: cur.cx, cy: cur.cy, width, height, radius, offset: t })
    settled =
      Object.keys(to).every((key) => Math.abs(cur[key] - to[key]) < 0.12 && Math.abs(vel[key]) < 2) && d < 0.001
        ? settled + STEP
        : 0
    if (t > 0.32 && settled >= 0.04) break
  }
  const ms = Math.ceil(1000 * t)
  frames.push({ ...to, offset: t + STEP })
  const total = t + STEP
  frames.forEach((f) => {
    f.offset /= total
  })
  return { frames, duration: ms + 1000 * STEP }
}

// Snapshot every surface in the scene (the "First" in FLIP).
export function snapshotScene(scene) {
  return new Map(
    Array.from(surfaces(scene), (node) => {
      const style = getComputedStyle(node)
      const content = contentOf(node)
      const rect = node.getBoundingClientRect()
      const flight = flights.get(node)
      const scale = node.offsetWidth ? rect.width / node.offsetWidth : 1
      return [
        surfaceKey(node),
        {
          rect,
          radius: radiusOf(style.borderTopLeftRadius, rect.width, rect.height, scale),
          opacity: Number(style.opacity),
          contentOpacity: content ? Number(getComputedStyle(content).opacity) : 1,
          kind: kindOf(node),
          velocity: flight
            ? velocityAt(flight.frames, flight.duration, Number(flight.animation.currentTime ?? 0))
            : undefined,
        },
      ]
    }),
  )
}

// Commit the React change, measure the new layout and animate from the snapshot (Last, Invert, Play).
export async function flipScene(before, scene, signal, reduced, arrival, commit) {
  const animations = []
  const tracked = []
  const cancel = () => {
    animations.forEach((a) => a.cancel())
    tracked.forEach(({ node, flight }) => {
      if (flights.get(node) === flight) flights.delete(node)
    })
  }
  const finish = () =>
    animations.forEach((a) => {
      try {
        a.finish()
      } catch (e) {
        /* ignore */
      }
    })
  signal.addEventListener('abort', cancel, { once: true })
  window.addEventListener('resize', finish)
  try {
    if (signal.aborted) return
    commit()
    if (reduced || signal.aborted) return
    const after = Array.from(surfaces(scene), (node) => ({
      node,
      to: node.getBoundingClientRect(),
      style: getComputedStyle(node),
    }))
    const hasDetail = after.some(({ node }) => kindOf(node) === 'detail')
    const curve = arrival ? ARRIVAL : hasDetail ? DETAIL : DEFAULT
    const startTime = document.timeline.currentTime
    const animate = (el, keyframes, options) => {
      const anim = el.animate(keyframes, options)
      if (typeof startTime === 'number') anim.startTime = startTime
      animations.push(anim)
      return anim
    }
    after.forEach(({ node, to, style }) => {
      if (!to.width || !to.height) return
      const prev = before.get(surfaceKey(node))
      const kind = kindOf(node)
      const morph = prev && prev.kind !== kind
      const radius = radiusOf(style.borderTopLeftRadius, to.width, to.height)
      const opacity = Number(style.opacity)
      const end = boxOf(to, radius)
      const start = prev
        ? boxOf(prev.rect, prev.radius)
        : { ...end, cy: end.cy - 32 - 0.02 * to.height, width: 0.96 * to.width, height: 0.96 * to.height }
      const { frames, duration } =
        prev && kind !== 'counter' && !arrival && (morph || prev.velocity)
          ? simulate(start, end, kind === 'detail', prev.velocity)
          : {
              duration: curve.duration,
              frames: CURVES.get(curve).map(({ offset, progress }) => ({
                offset,
                cx: lerp(start.cx, end.cx, progress),
                cy: lerp(start.cy, end.cy, progress),
                width: lerp(start.width, end.width, progress),
                height: lerp(start.height, end.height, progress),
                radius: lerp(start.radius, end.radius, progress),
              })),
            }
      const timing = { duration, easing: 'linear', fill: 'both' }
      const keyframes = frames.map(({ offset, cx, cy, width, height, radius: r }) => {
        const sx = width / to.width
        const sy = height / to.height
        return {
          offset,
          transform: `translate3d(${cx - width / 2 - to.left}px, ${cy - height / 2 - to.top}px, 0) scale(${sx}, ${sy})`,
          borderRadius: `${r / sx}px / ${r / sy}px`,
        }
      })
      const flight = { animation: animate(node, keyframes, timing), frames, duration }
      flights.set(node, flight)
      tracked.push({ node, flight })
      if (!prev || prev.opacity !== opacity) {
        animate(node, [{ opacity: prev?.opacity ?? 0 }, { opacity }], { duration: 130, easing: 'ease-out', fill: 'both' })
      }
      const content = contentOf(node)
      if (content) {
        animate(
          content,
          frames.map(({ offset, width, height }) => ({
            offset,
            transform: `scale(${to.width / width}, ${to.height / height})`,
          })),
          timing,
        )
        if (morph || (prev && prev.contentOpacity < 1)) {
          animate(content, [{ opacity: morph ? 0 : prev.contentOpacity }, { opacity: 1 }], {
            duration: kind === 'detail' ? 190 : 130,
            delay: morph ? (kind === 'detail' ? 55 : 25) : 0,
            easing: 'cubic-bezier(.2,.7,.2,1)',
            fill: 'both',
          })
        }
      }
    })
    await Promise.all(animations.map((a) => a.finished.catch(() => {})))
  } finally {
    cancel()
    signal.removeEventListener('abort', cancel)
    window.removeEventListener('resize', finish)
  }
}
