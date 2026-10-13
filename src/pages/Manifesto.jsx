// /manifesto (CLONE_SPEC_PAGES_A.md §4). Body text is PLACEHOLDER prose, not Merlin's essay;
// see src/components/manifesto/copy.js. Headings and signature are verbatim from the spec.
import '../styles/manifesto.css'
import HeroNav from '../components/hero/HeroNav.jsx'
import Footer from '../components/Footer.jsx'
import Mention from '../components/manifesto/Mention.jsx'
import TimeOfDayCopy from '../components/manifesto/TimeOfDayCopy.jsx'
import Signature from '../components/manifesto/Signature.jsx'
import { usePageMeta } from '../components/pricing/usePageMeta.js'
import { HANDWRITING, P3, P4, P5, P6, P8 } from '../components/manifesto/copy.js'

function Photo({ src, alt }) {
  return (
    <figure className="manifesto-photo">
      <img
        alt={alt}
        loading="lazy"
        width={1536}
        height={1024}
        decoding="async"
        data-nimg="1"
        style={{ color: 'transparent' }}
        sizes="(max-width: 600px) calc(100vw - 48px), (max-width: 1023px) 82vw, 880px"
        src={src}
      />
    </figure>
  )
}

export default function Manifesto() {
  usePageMeta(
    'The Merlin manifesto',
    'Why we’re building Merlin: an AI assistant for your Mac that helps across your apps, browser, meetings, and projects, giving you more time for life.',
    'https://www.merlin.computer/manifesto',
  )

  return (
    <main className="merlin-story site-layout manifesto-page" id="top">
      <a className="skip-link" href="#manifesto">
        Read the manifesto
      </a>
      <div className="site-container">
        <header className="manifesto-navigation">
          <HeroNav />
        </header>
      </div>
      <article id="manifesto" className="manifesto-poster" aria-labelledby="manifesto-title">
        <section className="manifesto-poster-opening">
          <div className="manifesto-handwriting manifesto-handwriting-time" aria-hidden="true">
            {HANDWRITING.time}
          </div>
          <div className="manifesto-poster-copy">
            <h1 id="manifesto-title">
              Less managing.
              <br />
              More living.
            </h1>
            <TimeOfDayCopy part="opening" />
          </div>
          <div className="manifesto-handwriting manifesto-handwriting-back" aria-hidden="true">
            {HANDWRITING.back}
          </div>
        </section>
        <Photo
          src="/assets/companion.webp"
          alt="Merlin sitting comfortably in an armchair with a laptop in a sunlit room."
        />
        <section className="manifesto-poster-understanding" aria-labelledby="manifesto-understanding-title">
          <div className="manifesto-poster-copy">
            <h2 id="manifesto-understanding-title">
              We know that day.
              <br />
              We’ve lived it too.
            </h2>
            <p>{P3}</p>
            <p>{P4}</p>
            <p>
              {P5[0]}
              <Mention kind="meeting">meeting</Mention>
              {P5[1]}
            </p>
          </div>
          <span className="manifesto-handwritten-note" aria-hidden="true">
            {HANDWRITING.noteUnderstanding}
          </span>
        </section>
        <Photo
          src="/assets/meeting-scene.webp"
          alt="Merlin sharing tea and a conversation with a friend at a sunny garden studio table."
        />
        <section className="manifesto-poster-action" aria-labelledby="manifesto-action-title">
          <div className="manifesto-poster-copy">
            <h2 id="manifesto-action-title">
              And there it is.
              <br />A little room.
            </h2>
            <p>
              {P6[0]}
              <Mention kind="browser">browser</Mention>
              {P6[1]}
            </p>
            <TimeOfDayCopy part="return" />
          </div>
          <span className="manifesto-handwritten-note" aria-hidden="true">
            {HANDWRITING.noteAction}
          </span>
        </section>
        <Photo
          src="/assets/hero-beach-reading.webp"
          alt="Merlin enjoying a book under a beach umbrella beside the sea at sunset."
        />
        <section className="manifesto-poster-ending" aria-labelledby="manifesto-ending-title">
          <div className="manifesto-poster-copy">
            <p>{P8}</p>
            <TimeOfDayCopy part="finish" />
            <h2 id="manifesto-ending-title">
              Your time.
              <br />
              Yours to spend.
            </h2>
          </div>
          <Signature />
        </section>
      </article>
      <Footer />
    </main>
  )
}
