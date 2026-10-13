// e6: meeting landscape with transcript window, Transcript/Notes switch and audio player.
// Ported from reference/source/page.split.js:86-88.
import { useId, useRef, useState } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { FiRrl, FijH2, FiYrT, Fiaze, FiGHw } from './icons.jsx'

const TRANSCRIPT = [
  { name: 'Amira', initials: 'A', time: 134, text: 'Let’s keep the launch focused. We can start with the three services, and give each one a little room to breathe.' },
  { name: 'Sophie', initials: 'SH', time: 143, text: 'That feels right. Could we put together a short deck before Friday? Something that tells the story simply.' },
  { name: 'Leo', initials: 'L', time: 151, text: 'I’ll bring the revised website direction on Wednesday. Then we can look at everything together.' },
]

const TASKS = [
  { owner: 'Amira', title: 'Prepare the launch deck', detail: 'Introduce the three services, the studio story, and the approved website direction.', due: 'Thu, Oct 8' },
  { owner: 'Leo', title: 'Share the revised website designs', detail: 'Bring the homepage and service pages together for the team’s review.', due: 'Wed, Oct 7' },
  { owner: 'Sophie', title: 'Review the deck and final copy', detail: 'Collect feedback in one place and confirm the last changes before launch.', due: 'Thu, Oct 8' },
]

const TABS = [
  { name: 'Transcript', Icon: FiRrl },
  { name: 'Notes', Icon: FijH2 },
]

const formatTime = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`

export function MeetingLandscape() {
  const id = useId()
  const audioRef = useRef(null)
  const tabRefs = useRef([])
  const reduced = useReducedMotion()
  const [tab, setTab] = useState(1)
  const [playing, setPlaying] = useState(false)
  const [time, setTime] = useState(0)
  const [duration, setDuration] = useState(125.805688)
  const [error, setError] = useState(false)
  const [done, setDone] = useState(TASKS.map(() => false))

  const togglePlay = async () => {
    const audio = audioRef.current
    if (!audio) return
    if (!audio.paused) {
      audio.pause()
      return
    }
    setError(false)
    if (audio.ended) audio.currentTime = 0
    try {
      await audio.play()
    } catch {
      setError(true)
    }
  }

  const onDuration = (e) => {
    const d = e.currentTarget.duration
    if (Number.isFinite(d) && d > 0) setDuration(d)
  }

  const progress = duration > 0 ? Math.min(1, time / duration) : 0

  return (
    <div className="meeting-landscape">
      <audio
        ref={audioRef}
        src="/assets/merlin-introduction.mp3"
        preload="metadata"
        onLoadedMetadata={onDuration}
        onDurationChange={onDuration}
        onTimeUpdate={(e) => setTime(e.currentTarget.currentTime)}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onEnded={() => setPlaying(false)}
        onError={() => {
          setPlaying(false)
          setError(true)
        }}
      />
      <img
        className="meeting-landscape-art"
        src="/assets/meeting-scene.webp"
        alt="Two handmade felt characters talking over tea in a sunlit garden studio"
        width={1536}
        height={1024}
        loading="lazy"
      />
      <div className="transcript-window">
        <div className="transcript-chrome">
          <span className="transcript-window-dots" aria-hidden="true">
            <i />
            <i />
            <i />
          </span>
        </div>
        <div className="transcript-paper">
          <div className="transcript-paper-toolbar">
            <div className="transcript-call-people">
              <span className="transcript-meeting-symbol">
                <img src="/assets/google-meet.png" alt="Google Meet" width={18} height={18} />
              </span>
              <div className="transcript-call-avatars">
                <img src="/assets/meeting.webp" alt="Sophie" width={28} height={28} />
                <img src="/assets/companion.webp" alt="Leo" width={28} height={28} />
              </div>
            </div>
            <div className="transcript-switch" role="tablist" aria-label="Meeting content">
              <motion.span
                className="transcript-switch-selection"
                aria-hidden="true"
                initial={false}
                animate={{ x: tab === 0 ? '0%' : '100%' }}
                transition={reduced ? { duration: 0 } : { type: 'spring', stiffness: 550, damping: 38, mass: 0.7 }}
              />
              {TABS.map(({ name, Icon }, i) => (
                <button
                  key={name}
                  ref={(el) => {
                    tabRefs.current[i] = el
                  }}
                  type="button"
                  role="tab"
                  id={`${id}-tab-${i}`}
                  aria-selected={tab === i}
                  aria-controls={`${id}-panel`}
                  tabIndex={tab === i ? 0 : -1}
                  onClick={() => setTab(i)}
                  onKeyDown={(e) => {
                    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) return
                    e.preventDefault()
                    const next = e.key === 'Home' ? 0 : e.key === 'End' ? 1 : 1 - i
                    setTab(next)
                    tabRefs.current[next]?.focus()
                  }}
                >
                  <Icon aria-hidden="true" />
                  <span>{name}</span>
                </button>
              ))}
            </div>
          </div>
          <div className="transcript-heading">
            <h3>
              Launch catch-up<span>Monday, October 5</span>
            </h3>
          </div>
          <div className="transcript-participants">
            <span className="transcript-presence" /> <strong>Amira, Sophie &amp; Leo</strong> <span>·</span> Google Meet
          </div>
          <div className="transcript-body" id={`${id}-panel`} role="tabpanel" aria-labelledby={`${id}-tab-${tab}`} tabIndex={0}>
            <motion.div
              key={tab}
              initial={!reduced && { opacity: 0.4, y: 3 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: reduced ? 0 : 0.16, ease: [0.23, 1, 0.32, 1] }}
            >
              {tab === 0 ? (
                <div className="transcript-lines">
                  {TRANSCRIPT.map((line) => (
                    <div className="transcript-line" key={line.time}>
                      <div className="transcript-speaker">
                        <span className="transcript-speaker-avatar" aria-hidden="true">{line.initials}</span>
                        <strong>{line.name}</strong>
                        <time>{formatTime(line.time)}</time>
                      </div>
                      <p>{line.text}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="transcript-notes">
                  <h4>Meeting summary</h4>
                  <p>
                    The team aligned on a focused October 9 launch for Common Ground. The first release will introduce the studio’s three core services, with a clear story across the website and launch deck.
                  </p>
                  <p>
                    Leo will share the revised designs on Wednesday. Amira will build the deck around the approved direction, leaving Thursday for Sophie’s feedback and final copy changes.
                  </p>
                  <h4>Key decisions</h4>
                  <ul className="transcript-decisions">
                    <li><strong>Keep the scope small.</strong> Give each service room to breathe; save additional offerings for a later release.</li>
                    <li><strong>Tell one story.</strong> Use the same positioning and visual direction in the deck and on the website.</li>
                    <li><strong>Review before Friday.</strong> Resolve design and copy feedback before the October 9 launch.</li>
                  </ul>
                  <div className="transcript-actions-heading">
                    <h4>Action items</h4>
                    <span>{done.filter(Boolean).length} of {TASKS.length} done</span>
                  </div>
                  {TASKS.map((task, i) => (
                    <button
                      key={task.title}
                      className="transcript-task"
                      type="button"
                      aria-pressed={done[i]}
                      onClick={() => setDone((d) => d.map((v, j) => (j === i ? !v : v)))}
                    >
                      <span aria-hidden="true">{done[i] && <FiYrT />}</span>
                      <div className="transcript-task-copy">
                        <strong>{task.title}</strong>
                        <small>{task.detail}</small>
                        <span>
                          {task.owner}
                          <span aria-hidden="true"> · </span>
                          <time>{task.due}</time>
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </motion.div>
          </div>
          <div className="transcript-player" data-playing={playing}>
            <button
              className="transcript-play"
              type="button"
              aria-label={playing ? 'Pause Merlin audio' : 'Play Merlin audio'}
              aria-pressed={playing}
              onClick={togglePlay}
            >
              <span className="transcript-play-symbol">
                <motion.span
                  className="transcript-control-icon"
                  initial={false}
                  animate={{ opacity: playing ? 0 : 1, scale: playing ? 0.6 : 1, filter: playing && !reduced ? 'blur(3px)' : 'blur(0px)' }}
                  transition={{ duration: reduced ? 0 : 0.16 }}
                >
                  <Fiaze />
                </motion.span>
                <motion.span
                  className="transcript-control-icon"
                  initial={false}
                  animate={{ opacity: playing ? 1 : 0, scale: playing ? 1 : 0.6, filter: playing || reduced ? 'blur(0px)' : 'blur(3px)' }}
                  transition={{ duration: reduced ? 0 : 0.16 }}
                >
                  <FiGHw />
                </motion.span>
              </span>
            </button>
            <div className="transcript-timeline">
              <div className="transcript-wave-track">
                <div className="transcript-wave" aria-hidden="true">
                  {Array.from({ length: 64 }, (_, i) => (
                    <i key={i} className={i / 64 < progress ? 'is-played' : ''} style={{ height: 5 + ((13 * i + 3) % 17) }} />
                  ))}
                </div>
                <span className="transcript-playhead" aria-hidden="true" style={{ left: `${100 * progress}%` }} />
                <input
                  type="range"
                  min={0}
                  max={duration || 1}
                  step={0.1}
                  value={time}
                  disabled={!duration}
                  onChange={(e) => {
                    const t = Number(e.target.value)
                    if (audioRef.current) audioRef.current.currentTime = t
                    setTime(t)
                  }}
                  aria-label="Merlin audio position"
                  aria-valuetext={`${formatTime(time)} of ${formatTime(duration)}`}
                />
              </div>
              <div className="transcript-player-times">
                <time>{formatTime(time)}</time>
                <span>{duration ? formatTime(duration) : '—:—'}</span>
              </div>
              {error && <span className="transcript-audio-error" role="status">Couldn’t play the audio. Please try again.</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
