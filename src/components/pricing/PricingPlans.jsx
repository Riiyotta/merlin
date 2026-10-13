// section#plans (CLONE_SPEC_PAGES_A.md §2.1/§2.2). Card styling comes from 2abce9a6dc03269b.css.
import DownloadButton from '../shared/DownloadButton.jsx'
import { FiCheck } from '../hero/icons.jsx'
import { PLANS } from './pricingData.js'

export default function PricingPlans() {
  return (
    <section id="plans" className="pricing-plans" aria-label="Monthly plans">
      <div className="pricing-plan-grid">
        {PLANS.map((plan) => (
          <article key={plan.name} className={`pricing-plan pricing-plan-${plan.tone}`}>
            <h2>{plan.name}</h2>
            <p className="pricing-plan-description">{plan.description}</p>
            <div className="pricing-plan-price">
              <span>
                {'$'}
                {plan.price}
              </span>
              <span>/ month</span>
            </div>
            <DownloadButton
              variant={plan.variant}
              className="pricing-plan-cta"
              ariaLabel={`Get Merlin for Mac — ${plan.name} plan`}
            />
            <div className="pricing-plan-details">
              <p>
                <FiCheck aria-hidden="true" />
                <span>
                  <strong>{plan.credits}</strong> credits each month
                </span>
              </p>
              <p>
                <FiCheck aria-hidden="true" />
                All of Merlin, included
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
