// /pricing (CLONE_SPEC_PAGES_A.md §2). Route CSS order lives in src/styles/pricing.css.
import '../styles/pricing.css'
import HeroNav from '../components/hero/HeroNav.jsx'
import Footer from '../components/Footer.jsx'
import PricingPlans from '../components/pricing/PricingPlans.jsx'
import PricingIncluded from '../components/pricing/PricingIncluded.jsx'
import PricingFaq from '../components/pricing/PricingFaq.jsx'
import { usePageMeta } from '../components/pricing/usePageMeta.js'

export default function PricingPage() {
  usePageMeta(
    'Plans | Merlin',
    'Choose your Merlin plan: Pro, Ultra, or Max. Your AI assistant for Mac, with room for the work you want to do.',
    'https://www.merlin.computer/pricing',
  )

  return (
    <main className="merlin-story site-layout pricing-page" id="top">
      <a href="#plans" className="skip-link">
        Skip to plans
      </a>
      <section className="story-hero" aria-labelledby="pricing-title">
        <HeroNav />
        {/* Server-rendered title: no hero-title-chroma sweep on this route (§1). */}
        <h1 id="pricing-title">
          <span className="hero-title-line">Make room for</span>
          <span className="hero-title-line hero-title-muted">the rest of your day.</span>
        </h1>
        <div className="hero-bottom">
          <p>
            Your ideas. Your to-dos. Your time back.
            <br />
            Choose how much Merlin you need along the way.
          </p>
        </div>
      </section>
      <div className="site-container">
        <PricingPlans />
        <PricingIncluded />
        <PricingFaq />
      </div>
      <Footer />
    </main>
  )
}
