// Section: Meetings + Projects (CLONE_SPEC.md §7). Ported from reference/source/page.split.js:86-88 (e4, e3, e5, e6, e8, e7, e9).
import { useEffect, useRef } from 'react'
import { MeetingLabelIcon, ProjectLabelIcon } from './meetings/icons.jsx'
import { ArtifactIcons } from './meetings/ArtifactIcons.jsx'
import { MeetingLandscape } from './meetings/MeetingLandscape.jsx'

const PROJECT_FILES = [
  { type: 'pdf', name: 'Launch report.pdf', metadata: '6 pages', edited: 'Edited 2 hours ago', title: 'Launch report', detail: 'COMMON GROUND', accent: 'rose' },
  { type: 'spreadsheet', name: 'Launch budget.xlsx', metadata: '3 sheets', edited: 'Edited 2 hours ago', title: 'Launch budget', detail: 'BUDGET / OCTOBER', accent: 'green' },
  { type: 'website', name: 'Studio website.html', metadata: 'Website', edited: 'Edited yesterday', title: 'A fresh start.', detail: 'COMMON GROUND STUDIO', accent: 'blue' },
  { type: 'deck', name: 'Launch deck.pptx', metadata: '12 slides', edited: 'Edited yesterday', title: 'Good things ahead.', detail: 'THE LAUNCH STORY', accent: 'amber' },
]

function ProjectFolders() {
  return (
    <div className="project-folder-landscape">
      <div className="project-folder-grid">
        {PROJECT_FILES.map((f) => (
          <figure key={f.type} className={`project-folder-item project-folder-${f.accent}`}>
            <span className="project-capsule-icon">
              <ArtifactIcons type={f.type} />
            </span>
            <figcaption>
              <strong>{f.name}</strong>
              <span>{f.metadata} · {f.edited}</span>
            </figcaption>
            <div className="project-folder-art" aria-hidden="true">
              <div className="project-folder-sheet project-folder-sheet-back">
                <span>✓</span>
                <i />
                <i />
              </div>
              <div className="project-folder-sheet project-folder-sheet-middle">
                <ArtifactIcons type={f.type} />
              </div>
              <div className={`project-folder-sheet project-folder-sheet-front project-file-${f.type}`}>
                <small>{f.detail}</small>
                <strong>{f.title}</strong>
                {f.type === 'spreadsheet' ? (
                  <div className="project-file-cells">
                    {Array.from({ length: 12 }, (_, i) => <i key={i} />)}
                  </div>
                ) : (
                  <div className="project-file-lines">
                    <i />
                    <i />
                    <i />
                  </div>
                )}
              </div>
            </div>
          </figure>
        ))}
      </div>
    </div>
  )
}

export default function Meetings() {
  const ref = useRef(null)

  // Mirror the landscape height into --meeting-card-height (ResizeObserver), as the original does.
  useEffect(() => {
    const section = ref.current
    const landscape = section?.querySelector('.meeting-landscape')
    if (!section || !landscape) return
    const update = () => section.style.setProperty('--meeting-card-height', `${landscape.getBoundingClientRect().height}px`)
    update()
    const ro = new ResizeObserver(update)
    ro.observe(landscape)
    return () => ro.disconnect()
  }, [])

  return (
    <section ref={ref} className="story-section meetings-section projects-section story-handoff" id="meetings" aria-labelledby="handoff-heading">
      <div className="story-pair-intro">
        <h2 id="handoff-heading">
          One{' '}
          <span className="story-meeting-logos" aria-hidden="true">
            <img src="/assets/google-meet.png" alt="" width={44} height={44} />
            <img src="/assets/zoom-camera.svg" alt="" width={44} height={44} />
          </span>{' '}
          conversation.
          <br />
          <em>
            Something to <ArtifactIcons /> show for it.
          </em>
        </h2>
        <div className="story-meeting-intro-copy">
          <p>
            Focus on your call with{' '}
            <span className="context-inline-identity">
              <span className="context-inline-initials" aria-hidden="true">SH</span>
              Sophie
            </span>
            . Merlin takes care of the notes and next steps.
          </p>
          <p>
            Then turn your ideas into{' '}
            <span className="story-inline-artifact"><ArtifactIcons type="pdf" />PDFs</span>,{' '}
            <span className="story-inline-artifact"><ArtifactIcons type="deck" />decks</span>,{' '}
            <span className="story-inline-artifact"><ArtifactIcons type="spreadsheet" />spreadsheets</span>, and{' '}
            <span className="story-inline-artifact"><ArtifactIcons type="website" />websites</span>. All from the same conversation.
          </p>
        </div>
      </div>
      <div className="story-pair-grid">
        <article className="story-meeting-panel">
          <header>
            <div className="story-section-label story-section-label-meeting">
              <MeetingLabelIcon />
              <span>Meetings</span>
            </div>
            <h3>
              Be there for the call.{' '}
              <span className="handoff-title-highlight handoff-title-highlight-green">Merlin handles the notes.</span>
            </h3>
            <p>Record with Merlin. After the call, come back to what you decided and what happens next.</p>
          </header>
          <MeetingLandscape />
        </article>
        <article className="story-project-panel" id="projects">
          <header>
            <div className="story-section-label story-section-label-project">
              <ProjectLabelIcon />
              <span>Projects</span>
            </div>
            <h3>
              You bring the ideas.{' '}
              <span className="handoff-title-highlight handoff-title-highlight-orange">Merlin brings them to life.</span>
            </h3>
            <p>Reports, spreadsheets, decks, and websites. Everything you need to move the project forward, together in one place.</p>
          </header>
          <ProjectFolders />
        </article>
      </div>
    </section>
  )
}
