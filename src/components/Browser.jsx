// Section: Browser tasks (CLONE_SPEC.md §6). Ported from reference/source/page.split.js:59-64 (eC, eA).
import { useEffect, useRef, useState } from 'react'
import { useReducedMotion } from 'framer-motion'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { BrowserLabelIcon, SiQYV, SisE_ } from './browser/icons.jsx'
import { BrowserPreview } from './browser/MockSites.jsx'

gsap.registerPlugin(ScrollTrigger)

const EXAMPLES = [
  { name: 'Qatar Airways', Logo: SiQYV, favicon: '', description: 'I can help you compare flights on', detail: 'and find the right one for your trip.' },
  { name: 'DoorDash', favicon: '/assets/doordash.png', description: 'I can help you find lunch on', detail: 'and get an order ready that everyone will love.' },
  { name: 'Instacart', Logo: SisE_, favicon: '', description: 'I can help you tick off your grocery list on', detail: 'and get your basket ready for checkout.' },
  { name: 'Ashby', favicon: '/assets/ashby.png', description: 'I can help you fill out your application on', detail: 'so it’s ready for you to review and submit.' },
]

// Slot pose for offset d = slotIndex - activeIndex (spec §6 Motion).
function pose(slot, active) {
  const d = slot - active
  const n = Math.abs(d)
  if (d === 0) return { yPercent: 0, rotateX: 0, scaleX: 1, scaleY: 1, opacity: 1, zIndex: 4, '--step-opacity': 0 }
  return {
    yPercent: Math.sign(d) * (63 + (n - 1) * 9),
    rotateX: 62 * Math.sign(d),
    scaleX: 0.94 - (n - 1) * 0.06,
    scaleY: 0.26,
    opacity: n === 1 ? 1 : 0.58,
    zIndex: 3 - n,
    '--step-opacity': 1,
  }
}

export default function Browser() {
  const sectionRef = useRef(null)
  const stageRef = useRef(null)
  const goToRef = useRef(null)
  const [active, setActive] = useState(0)
  const reduced = useReducedMotion()
  const current = EXAMPLES[active]

  useEffect(() => {
    if (!sectionRef.current || !stageRef.current) return
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      let bump
      const cards = gsap.utils.toArray('.bs-card', sectionRef.current)
      const slots = gsap.utils.toArray('.bs-card-slot', sectionRef.current)
      let landed = 0
      let last = 0
      let direction = 1

      slots.forEach((slot, i) => gsap.set(slot, { ...pose(i, 0), transformOrigin: '50% 50%' }))
      gsap.set(cards, { y: 0, scale: 1 })

      const tl = gsap.timeline({
        defaults: { duration: 1, ease: 'none' },
        onUpdate() {
          const p = this.progress() * (cards.length - 1)
          const idx = Math.round(p)
          if (p !== last) direction = p > last ? 1 : -1
          last = p
          setActive(idx)
          if (landed >= 0 && Math.abs(p - landed) > 0.04) {
            bump?.kill()
            gsap.set(cards, { y: 0, scale: 1 })
            landed = -1
          }
          if (Math.abs(p - idx) < 0.005 && landed !== idx) {
            bump?.kill()
            gsap.set(cards, { y: 0, scale: 1 })
            landed = idx
            bump = gsap
              .timeline()
              .to(cards[idx], { y: 9 * direction, scale: 0.985, duration: 0.1, ease: 'power2.out' })
              .to(cards[idx], { y: 0, scale: 1, duration: 0.7, ease: 'elastic.out(1, 0.5)' })
          }
        },
        scrollTrigger: {
          trigger: sectionRef.current,
          pin: stageRef.current,
          start: 'top top',
          end: () => '+=' + Math.max(320, 0.325 * window.innerHeight * (EXAMPLES.length - 1)),
          scrub: true,
          anticipatePin: 1,
          invalidateOnRefresh: true,
          snap: { snapTo: 'labelsDirectional', inertia: false, delay: 0.1, duration: { min: 0.12, max: 0.25 } },
        },
      })

      tl.addLabel('card-0', 0)
      for (let k = 1; k < cards.length; k++) {
        const at = k - 1
        slots.forEach((slot, i) => {
          tl.fromTo(slot, pose(i, k - 1), { ...pose(i, k), immediateRender: false }, at)
        })
        tl.addLabel(`card-${k}`, k)
      }

      goToRef.current = (index) => {
        const st = tl.scrollTrigger
        if (st) window.scrollTo({ top: st.start + ((st.end - st.start) * index) / (cards.length - 1), behavior: 'instant' })
      }

      return () => {
        bump?.kill()
        goToRef.current = null
      }
    })
    return () => mm.revert()
  }, [])

  const show = (i) => {
    const index = Math.max(0, Math.min(EXAMPLES.length - 1, i))
    if (goToRef.current) {
      goToRef.current(index)
    } else {
      sectionRef.current?.querySelectorAll('.bs-card')[index]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      setActive(index)
    }
  }

  return (
    <section ref={sectionRef} className="browser-showcase" id="browser" aria-labelledby="browser-showcase-heading">
      <div className="bs-boundary">
        <div className="bs-stage" ref={stageRef}>
          <div className="bs-copy">
            <div className="story-section-label story-section-label-browser">
              <BrowserLabelIcon />
              <span>Browser tasks</span>
            </div>
            <h2 id="browser-showcase-heading">
              {'If it happens in a browser, '}
              <span>Merlin can help.</span>
            </h2>
            <p aria-live="polite" aria-atomic="true">
              {current.description}{' '}
              <span className={`bs-inline-brand bs-inline-brand-${active}`}>
                {current.Logo ? <current.Logo aria-hidden="true" /> : <img src={current.favicon} alt="" width={16} height={16} />}
                {current.name}
              </span>{' '}
              {current.detail}
            </p>
          </div>
          <div className="bs-deck">
            {EXAMPLES.map((ex, i) => (
              <div className="bs-card-slot" key={ex.name}>
                <article
                  className={`bs-card bs-card-${i}`}
                  aria-label={ex.name}
                  aria-hidden={(!reduced && i !== active) || undefined}
                  ref={(el) => {
                    if (!el) return
                    if (reduced || i === active) el.removeAttribute('inert')
                    else el.setAttribute('inert', '')
                  }}
                >
                  <div className="bs-card-brand">
                    {ex.Logo ? <ex.Logo aria-hidden="true" /> : <img src={ex.favicon} alt="" width={21} height={21} />}
                    {ex.name}
                  </div>
                  <BrowserPreview exampleIndex={i} />
                </article>
              </div>
            ))}
          </div>
          <div className="bs-pagination" aria-label="Browser examples">
            {EXAMPLES.map((ex, i) => (
              <button key={ex.name} aria-label={`Show ${ex.name}`} aria-current={active === i ? 'step' : undefined} onClick={() => show(i)}>
                <span />
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
