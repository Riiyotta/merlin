import { FiArchive, FiArrowLeft, FiCornerUpLeft, FiMoreHorizontal, FiTrash2 } from './hero/icons.jsx'
import RoutineTimeline from './routines/RoutineTimeline.jsx'
import SectionLabel from './routines/SectionLabel.jsx'

// Port of `ex` (page.split.js:52): "First, a little context." + Gmail preview + Routines row.

const APPS = [
  { name: 'Gmail', logo: '/assets/gmail.png' },
  { name: 'Calendar', logo: '/assets/calendar.png' },
  { name: 'Slack', logo: '/assets/slack.png' },
  { name: 'Notion', logo: '/assets/notion.png' },
  { name: 'Granola', logo: '/assets/granola.png' },
  { name: 'Linear', logo: '/assets/linear.png' },
]

// next/font caveat instance family (`ed().style.fontFamily`)
const CAVEAT = "'caveat', 'caveat Fallback'"

// Static Merlin face mark (component `t`, page.split.js:5) as rendered in the live DOM, viewBox "22 22 56 66".
function MerlinMark() {
  return (
    <svg viewBox="22 22 56 66" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M 28 52 C 24 40 24 24 38 26 C 44 27 42 36 42 42 C 42 48 46 52 50 52 C 54 52 58 48 58 42 C 58 36 56 27 62 26 C 76 24 76 40 72 52"
        stroke="currentColor"
        strokeWidth="6.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <g>
        <g>
          <circle
            cx="38"
            cy="66"
            r="4.5"
            fill="currentColor"
            style={{ transform: 'scale(1)', transformOrigin: '38px 66px', transition: 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
          />
        </g>
      </g>
      <g>
        <g>
          <circle
            cx="62"
            cy="66"
            r="4.5"
            fill="currentColor"
            style={{ transform: 'scale(1)', transformOrigin: '62px 66px', transition: 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
          />
        </g>
      </g>
      <path
        d="M 39 79 Q 50 88 61 79"
        stroke="currentColor"
        strokeWidth="5"
        strokeLinecap="round"
        fill="none"
        style={{ transition: 'd 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
      />
    </svg>
  )
}

export default function Routines() {
  const source = APPS[0]
  return (
    <section className="story-section routines-section story-context" id="routines" aria-labelledby="context-heading">
      <div className="story-context-intro" id="chat">
        <h2 id="context-heading" aria-label="First, a little context.">
          First, a little
          <span className="context-heading-line">
            <span className="context-apps" role="group" aria-label="Connected apps">
              {APPS.map(({ name, logo }) => (
                <span className="context-app-tile" title={name} key={name}>
                  <span>
                    <img src={logo} alt={name} data-brand={name.toLowerCase()} width={25} height={25} />
                  </span>
                </span>
              ))}
            </span>
            <em>context.</em>
          </span>
        </h2>
        <div className="portfolio-context-copy">
          <p>
            The conversation is in{' '}
            <span className="context-inline-identity">
              <img className="context-inline-slack" src="/assets/slack.png" alt="" width={20} height={20} />
              Slack
            </span>
            . The plan is in{' '}
            <span className="context-inline-identity">
              <img className="context-inline-notion" src="/assets/notion.png" alt="" width={20} height={20} />
              Notion
            </span>
            .{' '}
            <span className="context-inline-identity">
              <span className="context-inline-initials" aria-hidden="true">
                SH
              </span>
              Sophie’s
            </span>{' '}
            email is in your{' '}
            <span className="context-inline-identity">
              <img className="context-inline-gmail" src="/assets/gmail.png" alt="" width={20} height={20} />
              inbox
            </span>
            .
          </p>
          <p>Connect the tools you use, and Merlin can help you bring it all together.</p>
        </div>
      </div>
      <div className="context-connections">
        <div className="context-source" id="context-source-preview">
          <div className="context-source-content" key={source.name}>
            <header className="context-source-header">
              <span className="context-source-brand">
                <img src={source.logo} alt="" width={20} height={20} />
                <span>{source.name}</span>
              </span>
            </header>
            <div className="context-email-toolbar" aria-hidden="true">
              <span className="context-email-back">
                <FiArrowLeft />
                <span>Inbox</span>
              </span>
              <span className="context-email-tool-group context-email-tools-organize">
                <span className="context-email-tool">
                  <FiArchive />
                </span>
                <span className="context-email-tool">
                  <FiTrash2 />
                </span>
                <span className="context-email-tool">
                  <FiMoreHorizontal />
                </span>
              </span>
              <span className="context-email-tool-divider" />
              <span className="context-email-reply">
                <FiCornerUpLeft />
                <span>Reply</span>
              </span>
            </div>
            <article className="context-email" aria-label="Received email from Sophie about the launch review">
              <header className="context-email-envelope">
                <div className="context-email-subject-line">
                  <h3 className="context-email-title">A quick catch-up before launch</h3>
                  <span className="context-email-inbox">Inbox</span>
                </div>
                <div className="context-email-author">
                  <span className="context-email-avatar" aria-hidden="true">
                    SH
                  </span>
                  <div>
                    <div className="context-email-sender">
                      <span className="context-email-author-name">Sophie Hayes</span>
                      <span className="context-email-author-address">&lt;sophie@commonground.example&gt;</span>
                    </div>
                  </div>
                  <span className="context-email-label">9:41 AM</span>
                </div>
              </header>
              <div className="context-email-message">
                <p>Hi Amira,</p>
                <p>The launch is looking good. Can we talk through the deck before next Friday?</p>
                <p>
                  I’ve added my notes to the project page. It would be great to see the latest website direction alongside
                  the slides, so we can make sure everything tells the same story.
                </p>
                <p>
                  Does Monday at 10 work for you and Leo? We can use the time to agree on the last few details before
                  October 9.
                </p>
                <p>
                  Thanks!
                  <br />
                  Sophie
                </p>
              </div>
            </article>
          </div>
        </div>
      </div>
      <div className="routine-columns">
        <SectionLabel section="routine" label="Routines" />
        <div className="context-routine-note">
          <span style={{ fontFamily: CAVEAT }}>Then, make it a routine.</span>
          <svg viewBox="0 0 112 86" fill="none" aria-hidden="true">
            <path d="M5 19C22 4 41 8 43 23C46 40 21 35 31 22C45 5 71 20 78 37C84 50 85 62 84 73M73 63C78 68 81 73 84 77C89 73 94 68 99 62" />
          </svg>
        </div>
        <p className="routine-intro-copy">Tell Merlin what needs doing, and when. It’ll take it from there.</p>
        <div className="routines-workspace-wrap">
          <RoutineTimeline />
        </div>
        <figure className="routine-intro-quote">
          <img src="/assets/studio.webp" alt="" width={1536} height={1024} loading="lazy" />
          <figcaption>
            From morning briefings to Friday updates, set a routine once.{' '}
            <span className="routine-inline-merlin">
              <span aria-hidden="true">
                <MerlinMark />
              </span>
              Merlin
            </span>{' '}
            keeps it moving, so you have one less thing to remember.
          </figcaption>
        </figure>
      </div>
    </section>
  )
}
