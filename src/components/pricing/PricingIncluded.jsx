// section.pricing-included (CLONE_SPEC_PAGES_A.md §2.1/§2.2). Icons are the homepage section-label SVGs (6950 module 17712).
import { SectionIcon } from '../routines/SectionLabel.jsx'
import { FEATURES } from './pricingData.js'

export default function PricingIncluded() {
  return (
    <section className="pricing-included" aria-labelledby="included-title">
      <div className="pricing-section-intro">
        <h2 id="included-title">
          All the places
          <br />
          <span>your day takes you.</span>
        </h2>
        <p>The same thoughtful assistant, wherever the work happens. Every plan comes with all of this.</p>
      </div>
      <div className="pricing-feature-grid">
        {FEATURES.map((f) => (
          <article key={f.icon}>
            <SectionIcon section={f.icon} />
            <h3>{f.title}</h3>
            <p>{f.body}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
