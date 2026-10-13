import { useState } from 'react'
import { motion } from 'framer-motion'
import { useReducedMotion } from '../../lib/hero-reduced-motion.js'

// Detail panels opened from the hero notification cards. Ported from page.split.js:18-31
// (deck slides `A`, deck `L`, helpers `T`, meeting `O`, project `E`, email `F`, wrapper `H`).
// Only the three ids used on the homepage (meeting, project, email) are included.

const SLIDES = [
  {
    file: '01-introduction',
    title: 'Studio introduction',
    alt: 'Common Ground. Good design. Shared ambition. Strategy, identity and digital experiences. Studio launch October 9. Review draft for Sophie, Amira and Leo.',
  },
  {
    file: '02-services',
    title: 'Three services',
    alt: 'Three services. One studio. Strategy: find the story worth telling. Identity: give the story a distinct voice. Digital experiences: bring it to life online. From the first idea to the first impression.',
  },
  {
    file: '03-work',
    title: 'Selected work',
    alt: 'The work makes it real. Field Coffee: strategy, identity and packaging, with the line For a slower kind of morning. Forme Studio: identity and website, with the line Room to be yourself. Illustrative project mockups.',
  },
  {
    file: '04-website',
    title: 'Website review',
    alt: "The same story, online. Leo's first designs, ready for review. Compare the homepage story with the deck. Illustrative Common Ground homepage: Good design. Shared ambition. An independent brand and digital studio. Explore our work. Field Coffee and Forme Studio.",
  },
  {
    file: '05-readiness',
    title: 'Launch readiness',
    alt: "What's ready. What's next. Website direction: approved. Homepage designs: ready for review. Launch copy: needs final review. Launch deck: first draft. From Sophie's email and the project notes.",
  },
  {
    file: '06-decisions',
    title: 'Review decisions',
    alt: "Let's agree the final details. Monday October 5 at 10am: Sophie, Amira and Leo. Before Friday: review deck and final copy. October 9: launch target. Does the deck match the website? What still needs changing? Are we ready for October 9?",
  },
]

// next/image `fill` output style
const FILL_STYLE = {
  position: 'absolute',
  height: '100%',
  width: '100%',
  left: 0,
  top: 0,
  right: 0,
  bottom: 0,
  color: 'transparent',
}

function LaunchDeck() {
  const [index, setIndex] = useState(0)
  const reduced = useReducedMotion()
  const step = (delta) => setIndex((i) => Math.max(0, Math.min(SLIDES.length - 1, i + delta)))
  return (
    <div
      className="cg-deck"
      role="region"
      aria-label="Common Ground launch deck"
      onKeyDown={(e) => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          e.preventDefault()
          e.stopPropagation()
          step(e.key === 'ArrowRight' ? 1 : -1)
        }
      }}
    >
      <div className="cg-slide" role="group" aria-roledescription="slide" aria-label={`${index + 1} of 6: ${SLIDES[index].title}`}>
        {SLIDES.map((slide, i) => (
          <motion.div
            key={slide.file}
            className="cg-image-frame"
            aria-hidden={index !== i}
            initial={false}
            animate={{ opacity: +(index === i), x: reduced || index === i ? 0 : i < index ? -16 : 16 }}
            transition={{ duration: 0.2 * !reduced, ease: [0.22, 1, 0.36, 1] }}
            style={{ zIndex: +(index === i) }}
          >
            <img
              src={`/assets/launch-deck-${slide.file}.png`}
              alt={slide.alt}
              loading="eager"
              decoding="async"
              data-nimg="fill"
              draggable={false}
              style={FILL_STYLE}
            />
          </motion.div>
        ))}
      </div>
      <nav className="cg-navigation" aria-label="Slide navigation">
        <button type="button" onClick={() => step(-1)} disabled={index === 0} aria-label="Previous slide">
          <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="m11.5 5-5 5 5 5" />
          </svg>
        </button>
        <div className="cg-pages">
          {SLIDES.map((slide, i) => (
            <button
              key={slide.file}
              type="button"
              onClick={() => setIndex(i)}
              aria-label={`Slide ${i + 1}: ${slide.title}`}
              aria-current={index === i ? 'step' : undefined}
            >
              <span />
            </button>
          ))}
        </div>
        <button type="button" onClick={() => step(1)} disabled={index === 5} aria-label="Next slide">
          <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="m8.5 5 5 5-5 5" />
          </svg>
        </button>
      </nav>
      <span className="hnd-sr-only" role="status">
        Slide {index + 1} of 6: {SLIDES[index].title}
      </span>
    </div>
  )
}

function Company() {
  return (
    <span className="hnd-company">
      <span aria-hidden="true">cg</span>Common Ground
    </span>
  )
}

function MeetingBrief() {
  return (
    <>
      <div className="hnd-context">
        <span className="hnd-source">
          <img className="hnd-app-mark" src="/assets/calendar.png" alt="" width={16} height={16} />
          Today · 10:00–10:30
        </span>
      </div>
      <h2>You’re ready for Sophie.</h2>
      <p className="hnd-intro hnd-story">
        You’re meeting{' '}
        <span className="hnd-person">
          <span className="hnd-initials" aria-hidden="true">
            SH
          </span>
          Sophie
        </span>{' '}
        at <Company /> to go over the launch. I gathered the notes so you can pick up where you left off.
      </p>
      <div className="hnd-section">
        <h3>Bring these into the room</h3>
        <ol className="hnd-brief">
          <li>
            <strong>The landing page is ready.</strong>
            <span>Sophie approved the copy yesterday. The team is waiting on the final images.</span>
          </li>
          <li>
            <strong>There’s one date to agree on.</strong>
            <span>The proposed launch is October 9. Ask if the customer emails can go out that morning.</span>
          </li>
        </ol>
      </div>
      <div className="hnd-mail-footer">
        <button type="button" className="hnd-join">
          <img src="/assets/google-meet.png" alt="" width={16} height={16} />
          Join meeting
        </button>
      </div>
    </>
  )
}

function ProjectDeck() {
  return (
    <>
      <div className="hnd-context">
        <Company />
        <span>Launch presentation</span>
      </div>
      <LaunchDeck />
    </>
  )
}

function EmailDraft() {
  const [sent, setSent] = useState(false)
  return (
    <>
      <div className="hnd-context">
        <span className="hnd-source">
          <img className="hnd-gmail-mark" src="/assets/gmail.png" alt="" width={16} height={16} />
          Gmail
        </span>
        <span className={`hnd-draft-status${sent ? ' is-sent' : ''}`}>{sent ? 'Sent' : 'Draft'}</span>
      </div>
      <h2>Re: A quick catch-up before launch</h2>
      <div className="hnd-email">
        <div className="hnd-email-to">
          <span className="hnd-mail-to-label">To</span>
          <span className="hnd-mail-token">
            <span className="hnd-mail-avatar" aria-hidden="true">
              SH
            </span>
            <span className="hnd-mail-recipient">
              <strong>Sophie Hayes</strong>
            </span>
          </span>
        </div>
        <div className="hnd-draft">
          <p>Hi Sophie,</p>
          <p>
            Monday at 10 works for me. I’ll bring the latest deck so we can review your notes and the website direction
            together before the October 9 launch.
          </p>
          <p>
            Thanks,
            <br />
            Amira
          </p>
        </div>
      </div>
      <div className="hnd-mail-footer">
        <button type="button" className="hnd-local-action" onClick={() => setSent(true)} disabled={sent}>
          {sent ? 'Sent' : 'Send'}
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            {sent ? (
              <path d="m5 12 4 4L19 6" />
            ) : (
              <>
                <path d="m22 3-9.5 18-2.2-7.3L3 11.5 22 3z" />
                <path d="M22 3 10.3 13.7" />
              </>
            )}
          </svg>
        </button>
      </div>
    </>
  )
}

const DETAIL_CLASS = { email: ' hnd-mail-detail', meeting: ' hnd-meet-detail', project: ' hnd-project-detail' }

export default function NotificationDetail({ id, onClose }) {
  return (
    <section className={`notification-detail${DETAIL_CLASS[id] ?? ''}`} aria-label="Notification details">
      <button type="button" className="hnd-close" aria-label="Close notification details" onClick={onClose}>
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <path d="m6 6 8 8M14 6l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </button>
      <div className="hnd-content" key={id}>
        {id === 'meeting' ? <MeetingBrief /> : id === 'project' ? <ProjectDeck /> : <EmailDraft />}
      </div>
    </section>
  )
}
