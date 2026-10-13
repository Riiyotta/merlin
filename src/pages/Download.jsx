// /download and /download?start=1 (CLONE_SPEC_PAGES_A.md §3). No homepage chrome on this route.
import '../styles/download.css'
import InstallIntro from '../components/download/InstallIntro.jsx'
import { usePageMeta } from '../components/pricing/usePageMeta.js'

const STEPS = [
  {
    n: '01',
    title: 'Open your download',
    img: '/assets/open-download.png',
    body: (
      <>
        Find the Merlin <strong>.dmg</strong> file in your <strong>Downloads</strong> folder and double-click it.
      </>
    ),
  },
  {
    n: '02',
    title: 'Move to Applications',
    img: '/assets/move-to-applications.png',
    body: (
      <>
        Drag the <strong>Merlin icon</strong> into the <strong>Applications</strong> folder beside it.
      </>
    ),
  },
  {
    n: '03',
    title: 'Open Merlin',
    img: '/assets/launch-merlin.png',
    body: (
      <>
        Open <strong>Merlin</strong> from Applications, and sign in to get started.
      </>
    ),
  },
]

export default function DownloadPage() {
  usePageMeta(
    'Download Merlin for Mac',
    'Get Merlin for Mac. Open your download, move Merlin to Applications, and open the app.',
    'https://www.merlin.computer/download',
  )

  return (
    <main className="install-page">
      <header className="install-header">
        <a className="install-brand" aria-label="Merlin home" href="/">
          <img
            alt=""
            loading="lazy"
            width={112}
            height={112}
            decoding="async"
            data-nimg="1"
            className=""
            style={{ color: 'transparent' }}
            src="/assets/merlin-dock.png"
          />
          merlin.computer
        </a>
      </header>
      <section className="install-intro" aria-labelledby="install-title">
        <InstallIntro />
      </section>
      <ol className="install-steps" aria-label="Install Merlin in three steps">
        {STEPS.map((step) => (
          <li key={step.n}>
            <div className="install-step-heading">
              <span>{step.n}</span>
              <h2>{step.title}</h2>
            </div>
            <div className="install-art">
              <img
                alt=""
                loading="lazy"
                width={1448}
                height={1086}
                decoding="async"
                data-nimg="1"
                style={{ color: 'transparent' }}
                sizes="(max-width: 620px) 90vw, (max-width: 1400px) 30vw, 380px"
                src={step.img}
              />
            </div>
            <p>{step.body}</p>
          </li>
        ))}
      </ol>
    </main>
  )
}
