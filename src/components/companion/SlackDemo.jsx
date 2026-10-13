// Slack demo (`eB`, page.split.js:74-75). 17s timeline, 14s reduced-motion still frame.
import { AnimatePresence, motion } from 'framer-motion'
import { FI } from '../../lib/companion-icons.js'
import MerlinMark, { MARK_SMALL_CLASS } from './MerlinMark.jsx'
import { AppLogo, DEMO_SPRING, DemoCursor, DemoPlayback, WindowLights, useDemoClock } from './playback.jsx'

const DRAFT = 'hey sophie, the launch deck is ready for friday. can you take a look at the opening before our call?'
const REWRITE =
  'Hi Sophie! The launch deck is ready for Friday. Could you take a look at the opening before our call? I’d love to hear what you think.'
const CAPTIONS = [
  { at: 0, label: 'Editing a Slack draft' },
  { at: 1400, label: 'Selecting the draft' },
  { at: 2900, label: 'Opening Companion with the selection' },
  { at: 4400, label: 'Asking for a warmer rewrite' },
  { at: 8200, label: 'Reviewing the suggestion' },
  { at: 12500, label: 'Rewrite inserted · Draft not sent' },
]
const RAIL = [
  [FI.V5Y, 'Home'],
  [FI.X6_, 'DMs'],
  [FI.zd, 'Activity'],
  [FI.Y19, 'Later'],
  [FI.$Ri, 'More'],
]

function Message({ name, index, time, children }) {
  return (
    <article className="slack-demo-message">
      <span className={`slack-demo-avatar avatar-${index}`}>{name[0]}</span>
      <div>
        <p>
          <strong>{name}</strong>
          <time>{time}</time>
        </p>
        <div>{children}</div>
      </div>
    </article>
  )
}

export default function SlackDemo({ workspace, onComplete }) {
  const playback = useDemoClock(17000, 14000, onComplete)
  const { reduced, t, playing, setTime, scale, viewport } = playback
  const name = workspace?.name || 'Acme Studio'
  const inserted = t >= 12500
  const caption = [...CAPTIONS].reverse().find((c) => t >= c.at)
  const prompt = 'make this a little warmer'.slice(0, Math.floor(Math.max(0, t - 4900) / 65))
  const answer = REWRITE.slice(0, Math.floor(Math.max(0, t - 8200) / 10))
  const cursor =
    t < 900
      ? { x: 720, y: 431 }
      : t < 1400
        ? { x: 284, y: 390 }
        : t < 2500
          ? { x: 730, y: 390 }
          : t < 3400
            ? { x: 700, y: 390 }
            : t < 4400
              ? { x: 363, y: 334 }
              : t < 11800
                ? { x: 700, y: 302 }
                : t < 12500
                  ? { x: 551, y: 329 }
                  : { x: 760, y: 451 }
  const pressed = (t >= 4080 && t < 4300) || (t >= 12200 && t < 12400)

  return (
    <div className="companion-demo">
      <div
        ref={viewport}
        className="slack-demo-viewport"
        aria-label="Animated example of rewriting a Slack draft with Merlin"
      >
        <div className="slack-demo-scene" style={{ transform: `scale(${scale})` }}>
          <div className="slack-demo-titlebar" aria-hidden="true">
            <WindowLights />
            <FI.kRp />
            <FI.dyV />
            <FI.Ohp />
            <div className="slack-demo-search">
              <FI.CKj /> Search {name}
              <span>⌘ K</span>
            </div>
            <FI.lrG />
          </div>
          <div className="slack-demo-layout">
            <aside className="slack-demo-rail" aria-hidden="true">
              <div className="slack-demo-workspace">{name.charAt(0).toUpperCase()}</div>
              {RAIL.map(([Icon, label]) => (
                <div key={label} className={label === 'Home' ? 'is-active' : ''}>
                  <Icon />
                  <span>{label}</span>
                </div>
              ))}
              <div className="slack-demo-rail-bottom">
                <FI.GGD />
                <span className="slack-demo-me">
                  A<i />
                </span>
              </div>
            </aside>
            <aside className="slack-demo-sidebar" aria-hidden="true">
              <header>
                <strong>{name}</strong>
                <FI.fK4 />
                <FI.SG1 />
              </header>
              <div className="slack-demo-sidebar-top">
                <p>
                  ▤ <span>Threads</span>
                </p>
                <p>
                  ◷ <span>Drafts &amp; sent</span>
                  <b>1</b>
                </p>
              </div>
              <div className="slack-demo-section">
                <FI.fK4 /> Channels <FI.GGD />
              </div>
              {['general', 'design', 'product', 'engineering', 'launch'].map((c) => (
                <div key={c} className={`slack-demo-channel ${c === 'design' ? 'is-active' : ''}`}>
                  <FI.Qz2 />
                  {c}
                  {c === 'product' && <b>3</b>}
                </div>
              ))}
              <div className="slack-demo-section">
                <FI.fK4 /> Direct messages <FI.GGD />
              </div>
              {['Sophie Hayes', 'Noah Williams', 'Lena Park'].map((p, i) => (
                <div key={p} className="slack-demo-dm">
                  <span className={`slack-demo-avatar avatar-${i}`}>
                    {p[0]}
                    <i />
                  </span>
                  {p}
                </div>
              ))}
              <div className="slack-demo-section">
                <FI.GGD /> Add teammates
              </div>
            </aside>
            <section className="slack-demo-conversation">
              <header className="slack-demo-channel-header">
                <FI.Qz2 />
                <strong>design</strong>
                <FI.fK4 />
                <div>
                  <span>SH</span>
                  <span>NW</span>
                  <span>LP</span>
                </div>
                <FI.ppo />
                <FI.$Ri />
              </header>
              <div className="slack-demo-tabs">
                <span>
                  <FI.X6_ /> Messages
                </span>
                <span>▧ Files</span>
                <span>＋</span>
              </div>
              <div className="slack-demo-messages">
                <div className="slack-demo-date">
                  <span>
                    Today <FI.fK4 />
                  </span>
                </div>
                <Message name="Sophie Hayes" index={0} time="9:42 AM">
                  The new launch deck is ready for a look 👀
                  <div className="slack-demo-reactions">
                    <span>🙌 3</span>
                    <span>👀 2</span>
                  </div>
                </Message>
                <Message name="Noah Williams" index={1} time="9:47 AM">
                  These are looking great! Just polishing the transitions.
                  <div className="slack-demo-thread">
                    2 replies <span>Last reply 4 minutes ago</span>
                  </div>
                </Message>
                <Message name="Lena Park" index={2} time="9:51 AM">
                  Quick one: is the review still on Friday? I can have the accessibility notes ready tomorrow.
                </Message>
              </div>
              <div className={`slack-demo-composer ${inserted ? 'is-inserted' : ''}`}>
                <div className="slack-demo-format" aria-hidden="true">
                  <b>B</b>
                  <i>I</i>
                  <s>S</s>
                  <span>⌁</span>
                  <span>☷</span>
                  <span>☰</span>
                  <span>〈/〉</span>
                </div>
                <div className="slack-demo-draft">
                  <span
                    style={{
                      backgroundSize:
                        t >= 1400 && t < 12500 ? `${Math.min(100, (t - 1400) / 9)}% 100%` : '0% 100%',
                    }}
                  >
                    {inserted ? REWRITE : DRAFT}
                  </span>
                </div>
                <div className="slack-demo-compose-tools" aria-hidden="true">
                  <FI.GGD />
                  <FI.WAO />
                  <span>Aa</span>
                  <FI._mV />
                  <span className="slack-demo-compose-spacer" />
                  <FI.kGk />
                  <FI.fK4 />
                </div>
              </div>
              <div className="slack-demo-enter-hint">
                {inserted ? 'Draft ready. Nothing sent.' : 'Shift + Enter to add a new line'}
              </div>
            </section>
          </div>
          <AnimatePresence>
            {t >= 2900 && t < 4400 && (
              <motion.div
                key="selection-actions"
                className="slack-demo-pill"
                initial={{ opacity: 0, y: 6, scale: 0.94 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.97 }}
                transition={DEMO_SPRING}
              >
                <button type="button" onClick={() => setTime(4400)}>
                  <FI.usP /> Ask Merlin
                </button>
                <span />
                <button type="button" onClick={() => setTime(4900)}>
                  Make it clearer
                </button>
              </motion.div>
            )}
            {t >= 4400 && t < 12500 && (
              <motion.div
                key="slack-companion"
                className="slack-demo-companion"
                initial={{ opacity: 0, y: 10, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 6, scale: 0.98 }}
                transition={DEMO_SPRING}
              >
                <div className="slack-demo-companion-prompt">
                  <FI.yGN />
                  <span>{prompt || <em>What should I do with this?</em>}</span>
                  <kbd>⏎</kbd>
                </div>
                <div className="slack-demo-context">
                  <span>
                    <AppLogo src="/assets/slack.png" size={12} /> Slack
                  </span>
                  <span>▤ Selection · {DRAFT.split(' ').length} words</span>
                </div>
                {t >= 6900 && (
                  <div className="slack-demo-answer">
                    {t >= 8200 ? (
                      <p>
                        {answer}
                        <span className={t < 9900 ? 'slack-demo-caret' : ''} />
                      </p>
                    ) : (
                      <span className="slack-demo-thinking">
                        Merlin is thinking<span>…</span>
                      </span>
                    )}
                  </div>
                )}
                {t >= 10400 && (
                  <motion.footer initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <MerlinMark className={MARK_SMALL_CLASS} />
                    <button type="button" onClick={() => setTime(12500)}>
                      Insert in Slack <kbd>⌘⏎</kbd>
                    </button>
                    <span>Open in Merlin ↗</span>
                  </motion.footer>
                )}
              </motion.div>
            )}
          </AnimatePresence>
          {!reduced && t < 14000 && (
            <motion.div
              className="slack-demo-cursor"
              aria-hidden="true"
              animate={{ x: cursor.x, y: cursor.y, scale: pressed ? 0.83 : 1 }}
              transition={{ duration: playing ? 0.55 : 0 }}
            >
              <DemoCursor />
            </motion.div>
          )}
        </div>
      </div>
      <DemoPlayback playback={playback} caption={caption.label} done={inserted} />
      <p className="sr-only">
        Example: select a draft in Slack, click Ask Merlin, ask for a warmer rewrite, then choose Insert in Slack. The
        reply replaces the selected draft but is not sent.
      </p>
    </div>
  )
}
