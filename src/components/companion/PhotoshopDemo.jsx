// Photoshop demo (`e$`, page.split.js:79). 22s timeline, 21s reduced-motion still frame.
import { AnimatePresence, motion } from 'framer-motion'
import { FI } from '../../lib/companion-icons.js'
import { EASE_OUT_EXPO } from '../../lib/companion-motion.jsx'
import MerlinMark, { MARK_SMALL_CLASS } from './MerlinMark.jsx'
import { AppLogo, DEMO_SPRING, DemoCursor, DemoPlayback, WindowLights, useDemoClock } from './playback.jsx'

const ART = '/assets/mark.webp'
const PROMPT = 'how do i remove this background?'
const ANSWER =
  'click remove background in the bar below your artwork. photoshop adds a mask, so you can bring back any edges it misses.'
const TOOLS = [FI.PfQ, FI.KFS, FI._cq, FI.mfX, FI.fZZ, FI.Jwm, FI.FrA, FI.MRc, FI._wx, FI.$Ri]

export default function PhotoshopDemo({ onComplete }) {
  const playback = useDemoClock(22000, 21000, onComplete)
  const { t, reduced, viewport, scale, setTime } = playback
  const companionOpen = t >= 3200
  const captured = t >= 10400
  const answering = t >= 12200
  const answer = ANSWER.slice(0, Math.floor(Math.max(0, t - 12200) / 22))
  const removed = t >= 18700
  const caption =
    t < 2000
      ? 'Artwork open in Photoshop'
      : t < 6700
        ? 'Asking how to remove the background'
        : t < 10400
          ? 'Waiting for screen permission'
          : t < 12200
            ? 'Approved screenshot attached'
            : t < 18700
              ? 'Reviewing the tool instructions'
              : 'Background removed in Photoshop'
  const cursor =
    t < 9600 ? { x: 510, y: 335 } : t < 11200 ? { x: 520, y: 311 } : t < 17200 ? { x: 785, y: 364 } : { x: 357, y: 424 }

  return (
    <div className="companion-demo photoshop-demo">
      <div
        ref={viewport}
        className="slack-demo-viewport photoshop-demo-viewport"
        aria-label="Animated example of Merlin looking at Photoshop with permission"
      >
        <div className="slack-demo-scene photoshop-demo-scene" style={{ transform: `scale(${scale})` }}>
          <div className="photoshop-demo-menu" aria-hidden="true">
            <WindowLights />
            <strong>Photoshop</strong>
            {['File', 'Edit', 'Image', 'Layer', 'Type', 'Select', 'Filter', 'View', 'Window', 'Help'].map((m) => (
              <span key={m}>{m}</span>
            ))}
          </div>
          <div className="photoshop-demo-options" aria-hidden="true">
            <FI.PfQ />
            <FI.fK4 />
            <span>Auto-Select</span>
            <span className="photoshop-demo-field">
              Layer <FI.fK4 />
            </span>
            <i />
            <span>Show Transform Controls</span>
            <span className="photoshop-demo-options-spacer" />
            <span className="photoshop-demo-share">Share</span>
            <FI.CKj />
          </div>
          <div className="photoshop-demo-document" aria-hidden="true">
            merlin-studio.psd @ 50% (Artwork, RGB/8) <FI.yGN />
          </div>
          <div className="photoshop-demo-tools" aria-hidden="true">
            {TOOLS.map((Tool, i) => (
              <span key={i} className={i === 0 ? 'is-selected' : ''}>
                <Tool />
              </span>
            ))}
            <div className="photoshop-demo-swatches">
              <i />
              <i />
            </div>
          </div>
          <div className="photoshop-demo-ruler" aria-hidden="true">
            0<span>100</span>
            <span>200</span>
            <span>300</span>
            <span>400</span>
            <span>500</span>
            <span>600</span>
          </div>
          <div className="photoshop-demo-artboard">
            <motion.div
              className="photoshop-demo-art-background"
              animate={{ opacity: removed ? 0 : 1 }}
              transition={{ duration: reduced ? 0 : 0.75 }}
            />
            <img src={ART} alt="Hand-stitched cyan felt Merlin artwork on a warm pink background" draggable={false} />
          </div>
          <div className="photoshop-demo-context-bar">
            <span aria-hidden="true">⠿</span>
            <span className="photoshop-demo-select-subject">Select subject</span>
            <button
              type="button"
              onClick={() => setTime(18700)}
              disabled={!answering || removed}
              className={t >= 16200 && !removed ? 'is-guided' : ''}
              aria-label="Remove background in this demo"
            >
              {removed ? (
                <>
                  <FI.YrT /> Background removed
                </>
              ) : (
                <>
                  <FI.fZZ /> Remove background
                </>
              )}
            </button>
            <FI.ou6 />
            <FI.$Ri />
          </div>
          <aside className="photoshop-demo-properties" aria-hidden="true">
            <header>
              Properties <FI.$Ri />
            </header>
            <div className="photoshop-demo-property-body">
              <p>
                <FI.fZZ /> Pixel Layer
              </p>
              <strong>Transform</strong>
              <div className="photoshop-demo-transform">
                <span>
                  W <b>1200 px</b>
                </span>
                <span>
                  H <b>1200 px</b>
                </span>
                <span>
                  X <b>0 px</b>
                </span>
                <span>
                  Y <b>0 px</b>
                </span>
              </div>
              <strong>Align and Distribute</strong>
              <div className="photoshop-demo-align">{'⊢   ⊥   ⊣   ⊤   ⊞   ⋮'}</div>
            </div>
            <header className="photoshop-demo-layer-tabs">
              Layers <span>Channels</span>
              <span>Paths</span>
            </header>
            <div className="photoshop-demo-layer-options">
              <span>
                Normal <FI.fK4 />
              </span>
              Opacity: 100%
            </div>
            <div className="photoshop-demo-layer">
              <FI.Vap />
              <span className="photoshop-demo-layer-thumb">
                <img src={ART} alt="" />
              </span>
              {removed && (
                <span className="photoshop-demo-mask">
                  <img src={ART} alt="" />
                </span>
              )}
              <span>Artwork</span>
              {!removed && <FI.F5$ />}
            </div>
            <div className="photoshop-demo-layer-bottom">
              <FI.s_k />
              <span>fx</span>
              <FI.fZZ />
              <FI.GGD />
            </div>
          </aside>
          <div className="photoshop-demo-status" aria-hidden="true">
            <span>50%</span>
            <span>1200 px × 1200 px (72 ppi)</span>
            <span>Adobe Photoshop</span>
          </div>
          <AnimatePresence>
            {t >= 2000 && !companionOpen && (
              <motion.div
                key="photoshop-shortcut"
                className="chrome-demo-hotkey photoshop-demo-hotkey"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: reduced ? 0 : 0.2 }}
                aria-hidden="true"
              >
                <span>Open Companion</span>
                <kbd>⌥</kbd>
                <kbd>space</kbd>
              </motion.div>
            )}
            {companionOpen && (
              <motion.div
                key="photoshop-companion"
                className="slack-demo-companion photoshop-demo-companion"
                initial={{ opacity: 0, y: 12, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={reduced ? { duration: 0 } : DEMO_SPRING}
              >
                <div className="slack-demo-companion-prompt">
                  <FI.yGN />
                  <span>
                    {PROMPT.slice(0, Math.floor(Math.max(0, t - 3800) / 65)) || <em>Ask Merlin anything…</em>}
                  </span>
                  <kbd>⏎</kbd>
                </div>
                <div className="slack-demo-context">
                  <span>
                    <AppLogo src="/assets/photoshop.png" size={12} /> Adobe Photoshop
                  </span>
                  {captured && (
                    <span>
                      <FI.fZZ /> Screenshot
                    </span>
                  )}
                </div>
                {t >= 6700 && t < 10400 && (
                  <div className="photoshop-demo-screen-ask">
                    <p>Mind if I take a look at your screen?</p>
                    <span>
                      I’ll capture the screen you’re looking at so I can answer properly. Nothing is captured unless you
                      approve.
                    </span>
                    <div>
                      <button
                        type="button"
                        onClick={() => setTime(10400)}
                        aria-label="Approve the simulated screenshot in this demo"
                        className={t >= 9900 ? 'is-pressed' : ''}
                      >
                        Take a look
                      </button>
                      <span>Not now</span>
                    </div>
                  </div>
                )}
                {captured && !answering && (
                  <div className="slack-demo-answer">
                    <span className="slack-demo-thinking">
                      taking a look<span>…</span>
                    </span>
                  </div>
                )}
                {answering && (
                  <div className="slack-demo-answer photoshop-demo-answer">
                    <p>{answer}</p>
                  </div>
                )}
                {t >= 15800 && (
                  <footer>
                    <MerlinMark className={MARK_SMALL_CLASS} />
                    <FI.nxz />
                    <span>
                      Open in Merlin <FI.HaR />
                    </span>
                  </footer>
                )}
              </motion.div>
            )}
            {captured && t < 11000 && !reduced && (
              <motion.div
                key="approved-capture-flash"
                className="photoshop-demo-capture-flash"
                initial={{ opacity: 0.14 }}
                animate={{ opacity: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
                aria-hidden="true"
              />
            )}
          </AnimatePresence>
          {!reduced && (
            <motion.div
              className="slack-demo-cursor"
              animate={cursor}
              transition={{ duration: playback.playing ? 0.6 : 0, ease: EASE_OUT_EXPO }}
              aria-hidden="true"
            >
              <DemoCursor />
            </motion.div>
          )}
        </div>
      </div>
      <DemoPlayback playback={playback} caption={caption} done={removed} />
      <p className="sr-only">
        Scripted example: open Merlin in Photoshop and ask how to remove a background. Approve the sample screen
        request. Merlin sees the screenshot and explains which tool to use. The demo user clicks Remove Background and
        Photoshop adds a mask. This demo never captures your screen or changes your files.
      </p>
    </div>
  )
}
