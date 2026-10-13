// Chrome demo (`eK`, page.split.js:76-77). 18.5s timeline, 15s reduced-motion still frame.
import { AnimatePresence, motion } from 'framer-motion'
import { FI } from '../../lib/companion-icons.js'
import { EASE_OUT_EXPO } from '../../lib/companion-motion.jsx'
import MerlinMark, { MARK_SMALL_CLASS } from './MerlinMark.jsx'
import { DEMO_SPRING, DemoCursor, DemoPlayback, WindowLights, useDemoClock } from './playback.jsx'

const TAKEAWAYS = [
  'keep tomorrow’s first hour meeting-free for one important task.',
  'check messages at set times, instead of every time one lands.',
  'end the day by writing down your next step. less figuring things out in the morning.',
]

function PageMark({ size = 14 }) {
  return (
    <span className="chrome-demo-page-mark" style={{ width: size, height: size, fontSize: 0.7 * size }} aria-hidden="true">
      f
    </span>
  )
}

export default function ChromeDemo({ onComplete }) {
  const playback = useDemoClock(18500, 15000, onComplete)
  const { t, reduced, playing, viewport, scale, setTime } = playback
  const companionOpen = t >= 3300
  const prompt = 'what should i actually try from this?'.slice(0, Math.floor(Math.max(0, t - 4300) / 58))
  const done = t >= 13900
  const caption =
    t < 1900
      ? 'Article open in Chrome'
      : t < 3300
        ? 'Opening Companion with Option + Space'
        : t < 7000
          ? 'Page title and URL attached'
          : t < 8800
            ? 'Reading the article'
            : done
              ? 'Takeaways ready'
              : 'Summarizing the article'
  const keysDown = t >= 2700
  const keyAnim = { y: keysDown ? 2 : 0, backgroundColor: keysDown ? '#57575d' : '#323237' }

  return (
    <div className="companion-demo chrome-demo">
      <div
        ref={viewport}
        className="slack-demo-viewport chrome-demo-viewport"
        aria-label="Animated example of asking Merlin about a page in Chrome"
      >
        <div className="slack-demo-scene chrome-demo-scene" style={{ transform: `scale(${scale})` }}>
          <div className="chrome-demo-tabs" aria-hidden="true">
            <WindowLights />
            <div className="chrome-demo-tab">
              <FI.Y19 />
              <span>Reading list</span>
              <FI.yGN />
            </div>
            <div className="chrome-demo-tab is-active">
              <PageMark />
              <span>A little room to focus • Fieldnotes</span>
              <FI.yGN />
            </div>
            <div className="chrome-demo-tab">
              <FI.CKj />
              <span>Weekend plans</span>
              <FI.yGN />
            </div>
            <FI.GGD />
            <FI.fK4 />
          </div>
          <div className="chrome-demo-address" aria-hidden="true">
            <FI.kRp />
            <FI.dyV />
            <FI.jTZ />
            <div className="chrome-demo-omnibox">
              <FI.ou6 />
              <span>
                fieldnotes.example<span className="chrome-demo-url-path">/journal/a-little-room-to-focus</span>
              </span>
              <FI.usP />
            </div>
            <span className="chrome-demo-profile">A</span>
            <FI.ZZB />
          </div>
          <div className="chrome-demo-page">
            <header className="chrome-demo-site-header">
              <span>
                <PageMark size={21} /> fieldnotes
              </span>
              <nav>
                Journal <span>About</span> <span>Newsletter ↗</span>
              </nav>
            </header>
            <motion.div
              className="chrome-demo-page-scroll"
              animate={{ y: t >= 1600 ? -24 : 0 }}
              transition={{ duration: reduced ? 0 : 0.8, ease: EASE_OUT_EXPO }}
            >
              <div className="chrome-demo-article">
                <div className="chrome-demo-article-kicker">
                  WORK, A LITTLE BETTER <span>06 MIN READ</span>
                </div>
                <div className="chrome-demo-editorial">
                  <div>
                    <h2>
                      A little room
                      <br />
                      to focus.
                    </h2>
                    <p>
                      You don’t need a better to-do list.
                      <br />
                      You need a little less in the way.
                    </p>
                    <div className="chrome-demo-byline">
                      <span>JL</span>
                      <div>
                        Jamie Lee<small>September 10 · Work &amp; life</small>
                      </div>
                    </div>
                  </div>
                  <div className="chrome-demo-illustration" aria-hidden="true">
                    <div className="chrome-demo-sun" />
                    <div className="chrome-demo-window" />
                    <div className="chrome-demo-book">
                      <span>
                        one thing
                        <br />
                        at a time.
                      </span>
                    </div>
                    <div className="chrome-demo-cup" />
                    <div className="chrome-demo-pencil" />
                    <span className="chrome-demo-illustration-caption">MAKE SPACE FOR THE GOOD WORK.</span>
                  </div>
                </div>
                <div className="chrome-demo-article-body">
                  <aside>
                    IN THIS ARTICLE<span>{'01   Start with space'}</span>
                    <span>{'02   Batch the noise'}</span>
                    <span>{'03   Leave a breadcrumb'}</span>
                  </aside>
                  <div>
                    <h3>01. Start with space.</h3>
                    <p>
                      Protect the first hour of your day for one important task. Keep meetings out of that hour. Your
                      best attention deserves more than an inbox.
                    </p>
                    <h3>02. Batch the noise.</h3>
                    <p>
                      Choose a few times to check messages. Turning every notification into a task makes it harder to
                      finish anything.
                    </p>
                    <h3>03. Leave a breadcrumb.</h3>
                    <p>Before you stop for the day, write down your next step. Tomorrow starts with a little less friction.</p>
                  </div>
                </div>
              </div>
            </motion.div>
            <div className="chrome-demo-scrollbar" aria-hidden="true">
              <span />
            </div>
          </div>
          <AnimatePresence>
            {!companionOpen && (
              <motion.div
                key="chrome-shortcut"
                className="chrome-demo-hotkey"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: t >= 1800 ? 1 : 0, y: 0 }}
                exit={{ opacity: 0, y: 5 }}
                transition={{ duration: reduced ? 0 : 0.25 }}
                aria-hidden="true"
              >
                <span>Open Companion</span>
                <motion.kbd animate={keyAnim}>⌥</motion.kbd>
                <motion.kbd animate={keyAnim}>space</motion.kbd>
              </motion.div>
            )}
            {companionOpen && (
              <motion.div
                key="chrome-companion"
                className="slack-demo-companion chrome-demo-companion"
                initial={{ opacity: 0, y: 12, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={reduced ? { duration: 0 } : DEMO_SPRING}
              >
                <div className="slack-demo-companion-prompt">
                  <FI.yGN />
                  <span>{prompt || <em>Ask Merlin anything…</em>}</span>
                  <motion.kbd animate={{ backgroundColor: t >= 6650 && t < 7050 ? '#65656f' : '#ffffff0c' }}>⏎</motion.kbd>
                </div>
                <motion.div
                  className="slack-demo-context"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: t >= 3850 ? 1 : 0 }}
                  transition={{ duration: reduced ? 0 : 0.2 }}
                >
                  <span title="fieldnotes.example/journal/a-little-room-to-focus">
                    <PageMark size={12} /> A little room to focus · fieldnotes.example
                  </span>
                </motion.div>
                {t >= 7000 && t < 8800 && (
                  <div className="slack-demo-answer">
                    <span className="slack-demo-thinking">
                      reading this page<span>…</span>
                    </span>
                  </div>
                )}
                {t >= 8800 && (
                  <div className="slack-demo-answer chrome-demo-answer">
                    <p>three small things worth trying:</p>
                    <ol>
                      {TAKEAWAYS.map((item, i) => {
                        const typed = item.slice(0, Math.floor(Math.max(0, t - 9300 - 1100 * i) / 15))
                        return typed && <li key={item}>{typed}</li>
                      })}
                    </ol>
                    {done && (
                      <span className="chrome-demo-source">
                        <PageMark size={11} /> from the article you’re reading
                      </span>
                    )}
                  </div>
                )}
                {done && (
                  <motion.footer initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <MerlinMark className={MARK_SMALL_CLASS} />
                    <FI.nxz />
                    <span>
                      Open in Merlin <FI.HaR />
                    </span>
                  </motion.footer>
                )}
              </motion.div>
            )}
          </AnimatePresence>
          {!companionOpen && (
            <button
              type="button"
              onClick={() => setTime(3300)}
              className="chrome-demo-dock"
              aria-label="Open companion in this demo"
            >
              <MerlinMark />
            </button>
          )}
          {!reduced && t < 2100 && (
            <motion.div
              className="slack-demo-cursor"
              aria-hidden="true"
              animate={{ x: 624, y: t >= 1000 ? 369 : 294 }}
              transition={{ duration: playing ? 0.6 : 0 }}
            >
              <DemoCursor />
            </motion.div>
          )}
        </div>
      </div>
      <DemoPlayback playback={playback} caption={caption} done={done} />
      <p className="sr-only">
        Example: while reading an article in Chrome, press Option + Space. Merlin picks up the page title and URL. Ask
        what to try from the article, then read the takeaways beside the page. No text is inserted and no page is
        changed.
      </p>
    </div>
  )
}
