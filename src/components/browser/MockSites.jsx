// Mock destination pages shown inside the browser-showcase cards.
// Ported from reference/source/page.split.js:53-59 (ef, ey, ew, ek, eM).
import { useEffect, useRef, useState } from 'react'
import {
  FiJXP, FidyV, FiCKj, Fiou6, FifK4, FiYrT, FiND1, FiHzC, FiiHs, Fiicx, FiOhp, FikRp, FijH2, FiF5_, Fi_Ri,
  SiQYV, SiNy7, SisE_,
} from './icons.jsx'

const QA_FLIGHTS = [
  { time: '08:05', arrival: '16:50', price: 548, number: 'QR 10', duration: '6h 45m' },
  { time: '14:15', arrival: '23:00', price: 576, number: 'QR 4', duration: '6h 45m' },
  { time: '21:55', arrival: '06:40 +1', price: 529, number: 'QR 16', duration: '6h 45m' },
]

function QatarPage({ selected, onSelect }) {
  return (
    <div className="destination-page qa-page">
      <header className="qa-header">
        <img src="/assets/qatar-logo.webp" alt="Qatar Airways" />
        <div className="qa-nav">
          <span>Explore</span>
          <span>Book</span>
          <span>Experience</span>
          <span>Privilege Club</span>
        </div>
        <span className="qa-account"><FiJXP /> Log in</span>
      </header>
      <div className="qa-progress">
        <b>1 <span>Flights</span></b>
        <i />
        <span>{'2   Passenger details'}</span>
        <i />
        <span>{'3   Add-ons'}</span>
        <i />
        <span>{'4   Payment'}</span>
      </div>
      <div className="qa-search-summary">
        <div>
          <small>Return trip</small>
          <strong>London <FidyV /> Doha</strong>
        </div>
        <div>
          <small>Departure / Return</small>
          <strong>9 Oct – 12 Oct 2026</strong>
        </div>
        <div>
          <small>Passengers / Class</small>
          <strong>1 Adult · Economy</strong>
        </div>
        <FiCKj />
      </div>
      <main className="qa-results">
        <h3>Select your outbound flight</h3>
        <p>London Heathrow (LHR) to Doha (DOH) <span>Friday, 9 October 2026</span></p>
        <div className="qa-dates">
          {['Wed, 7 Oct', 'Thu, 8 Oct', 'Fri, 9 Oct', 'Sat, 10 Oct', 'Sun, 11 Oct'].map((d, i) => (
            <div key={d} className={i === 2 ? 'current' : ''}>
              <span>{d}</span>
              <b>GBP {[562, 551, 529, 548, 567][i]}</b>
            </div>
          ))}
        </div>
        <div className="qa-result-count">
          <span>3 flights available · All times are local</span>
          <span><Fiou6 />{' Direct flights   ·   Sort by departure '}<FifK4 /></span>
        </div>
        <div className="qa-flight-list">
          {QA_FLIGHTS.map((f, i) => (
            <button
              key={f.number}
              type="button"
              className={'qa-flight ' + (selected === i ? 'chosen' : '')}
              aria-pressed={selected === i}
              onClick={() => onSelect(i)}
            >
              <span className="qa-flight-info">
                <span className="qa-airline"><SiQYV /> Qatar Airways <small>{f.number} · Boeing 777</small></span>
                <span className="qa-flight-times">
                  <span><b>{f.time}</b><small>LHR</small></span>
                  <span className="qa-flight-path"><small>{f.duration}</small><i /><small>Non-stop</small></span>
                  <span><b>{f.arrival}</b><small>DOH</small></span>
                </span>
                <span className="qa-flight-details">Flight details <FifK4 /> <span>Cabin baggage included</span></span>
              </span>
              <span className="qa-fare">
                <small>Economy</small>
                <span>from <b>GBP {f.price}</b></span>
                <span className="qa-select">
                  {selected === i ? <><FiYrT /> Selected</> : <>Select <FifK4 /></>}
                </span>
              </span>
            </button>
          ))}
        </div>
      </main>
    </div>
  )
}

const DD_RESTAURANTS = [
  { name: 'Market Kitchen', kind: 'Healthy · Bowls · Salads', time: '25–35 min', rating: '4.8', image: 'grain-bowls', price: '$0 delivery fee' },
  { name: 'Little Garden', kind: 'Vegetarian · Mediterranean', time: '30–40 min', rating: '4.7', image: 'green-bowl', price: '$0 delivery fee' },
  { name: 'Rice & Co.', kind: 'Asian · Rice bowls · Healthy', time: '20–30 min', rating: '4.9', image: 'veggie-bowls', price: '$1.49 delivery fee' },
]

function DoorDashPage({ selected, onSelect }) {
  const [query, setQuery] = useState('')
  const [saved, setSaved] = useState([])
  const results = DD_RESTAURANTS.filter((r) => `${r.name} ${r.kind}`.toLowerCase().includes(query.toLowerCase()))
  return (
    <div className="destination-page dd-page">
      <header className="dd-header">
        <FiND1 />
        <span className="dd-wordmark"><SiNy7 /> DOORDASH</span>
        <span className="dd-service">Delivery <span>Pickup</span></span>
        <span className="dd-address"><FiHzC /> Studio <FifK4 /></span>
        <label className="destination-search">
          <FiCKj />
          <input aria-label="Search restaurants" placeholder="Search DoorDash" value={query} onChange={(e) => setQuery(e.target.value)} />
        </label>
        <span className="dd-cart"><FiiHs /> 0</span>
      </header>
      <div className="dd-categories">
        <b>Restaurants</b>
        <span>Grocery</span>
        <span>Convenience</span>
        <span>Alcohol</span>
        <span>Flowers</span>
        <span>Pet supplies</span>
        <span>Retail</span>
      </div>
      <main className="dd-main">
        <div className="dd-promo">
          <div>
            <small>LUNCH, SORTED.</small>
            <h3>A little something<br />for everyone.</h3>
            <p>Fresh bowls. Local favorites. Delivered.</p>
          </div>
          <img src="/assets/grain-bowls.webp" alt="A selection of fresh grain bowls" />
        </div>
        <div className="dd-filters">
          <span><Fiou6 /> Filters</span>
          <span>DashPass</span>
          <span>Pickup</span>
          <span>Under 30 min</span>
          <span>Vegetarian <FifK4 /></span>
          <span>Rating 4.5+</span>
        </div>
        <div className="dd-section-title">
          <h3>Lunch near you</h3>
          <span>See all <FidyV /></span>
        </div>
        <div className="dd-restaurants">
          {results.map((r) => {
            const i = DD_RESTAURANTS.indexOf(r)
            const isSaved = saved.includes(r.name)
            return (
              <article key={r.name} className={'dd-restaurant ' + (selected === i ? 'chosen' : '')}>
                <button type="button" className="dd-restaurant-select" aria-pressed={selected === i} onClick={() => onSelect(i)}>
                  <img src={`/assets/${r.image}.webp`} alt={r.kind} />
                  <strong>{r.name}</strong>
                  <span>{r.rating} ★ <small>(200+) · {r.time}</small></span>
                  <small>{r.kind}</small>
                  <span className="dd-delivery">{r.price}</span>
                </button>
                <button
                  className={'dd-favorite ' + (isSaved ? 'saved' : '')}
                  type="button"
                  aria-label={`Save ${r.name}`}
                  aria-pressed={isSaved}
                  onClick={() => setSaved((s) => (s.includes(r.name) ? s.filter((n) => n !== r.name) : [...s, r.name]))}
                >
                  <Fiicx />
                </button>
              </article>
            )
          })}
        </div>
        {results.length === 0 && <p>No restaurants found. Try “bowls” or “vegetarian”.</p>}
        <div className="dd-selection">
          <FiYrT /> {DD_RESTAURANTS[selected].name} selected <span>Review your lunch options before ordering</span>
        </div>
      </main>
    </div>
  )
}

const IC_PRODUCTS = [
  { name: 'Hass Avocado', detail: '1 each', price: 1.5, image: 'avocado.webp' },
  { name: 'Organic Bananas', detail: 'Sold individually · 1 bunch', price: 2.5, image: 'bananas.webp' },
  { name: 'Oatly Original Oatmilk', detail: '32 fl oz', price: 3.25, image: 'oat-milk.webp' },
]

function InstacartPage() {
  const [qty, setQty] = useState([2, 1, 1])
  const [query, setQuery] = useState('')
  const subtotal = IC_PRODUCTS.reduce((sum, p, i) => sum + p.price * qty[i], 0)
  const count = qty.reduce((a, b) => a + b, 0)
  const step = (index, delta) => setQty((q) => q.map((v, i) => (i === index ? Math.max(0, Math.min(9, v + delta)) : v)))
  const q = query.toLowerCase()
  return (
    <div className="destination-page ic-page">
      <header className="ic-header">
        <FiND1 />
        <span className="ic-wordmark"><SisE_ />instacart</span>
        <label className="destination-search">
          <FiCKj />
          <input aria-label="Search groceries" placeholder="Search products and stores" value={query} onChange={(e) => setQuery(e.target.value)} />
        </label>
        <span><FiHzC /> Home</span>
        <span className="ic-cart"><FiiHs /> {count}</span>
      </header>
      <div className="ic-layout">
        <aside className="ic-sidebar">
          <span className="ic-store-logo">fresh<br />market</span>
          <h4>Fresh Market</h4>
          <small>Everyday store prices</small>
          <div className="ic-sidebar-active">Shop</div>
          <span>Buy it again</span>
          <span>Deals</span>
          <hr />
          <b>Departments</b>
          <span>Produce</span>
          <span>Dairy &amp; Eggs</span>
          <span>Meat &amp; Seafood</span>
          <span>Beverages</span>
          <span>Snacks</span>
          <span>Frozen</span>
          <span>Bakery</span>
        </aside>
        <main className="ic-main">
          <div className="ic-delivery">
            <span><FiOhp /> Delivery in as fast as 1 hour</span>
            <span>100% satisfaction guarantee</span>
          </div>
          <div className="ic-banner">
            <small>FRESH PICKS FOR YOUR WEEK</small>
            <h3>Good things<br />start here.</h3>
            <span>Everyday essentials, delivered.</span>
            <img src="/assets/avocado.webp" alt="" />
            <img src="/assets/bananas.webp" alt="" />
          </div>
          <div className="ic-section-title">
            <h3>Your weekly essentials</h3>
            <span>View all <FidyV /></span>
          </div>
          <div className="ic-products">
            {IC_PRODUCTS.map((p, i) =>
              p.name.toLowerCase().includes(q) && (
                <article key={p.name} className="ic-product">
                  <img src={`/assets/${p.image}`} alt={p.name} />
                  <div className="ic-quantity">
                    <button type="button" aria-label={`Remove one ${p.name}`} disabled={qty[i] === 0} onClick={() => step(i, -1)}>−</button>
                    <span aria-live="polite">{qty[i]}</span>
                    <button type="button" aria-label={`Add one ${p.name}`} disabled={qty[i] === 9} onClick={() => step(i, 1)}>+</button>
                  </div>
                  <strong>${p.price.toFixed(2)}</strong>
                  <span>{p.name}</span>
                  <small>{p.detail}</small>
                  <small className="ic-stock">Many in stock</small>
                </article>
              ),
            )}
          </div>
          {!IC_PRODUCTS.some((p) => p.name.toLowerCase().includes(q)) && <p>No products found. Try “oat” or “bananas”.</p>}
          <div className="ic-subtotal">
            <span><FiiHs /> {count} items in your cart</span>
            <strong aria-live="polite">Subtotal ${subtotal.toFixed(2)}</strong>
          </div>
        </main>
      </div>
    </div>
  )
}

const AB_PROFILE = { name: 'Sophie Hayes', email: 'sophie@example.com', portfolio: 'https://example.com/sophie', location: 'London, United Kingdom' }
const AB_FIELDS = [['name', 'Name', 'text'], ['email', 'Email', 'email'], ['portfolio', 'Portfolio', 'url'], ['location', 'Location', 'text']]

function AshbyPage() {
  const [form, setForm] = useState(AB_PROFILE)
  const [filled, setFilled] = useState(true)
  const [overview, setOverview] = useState(false)
  return (
    <div className="destination-page ab-page">
      <header className="ab-header">
        <FikRp />
        <img src="/assets/ashby-wordmark.svg" alt="Ashby" />
      </header>
      <h3>Product Designer</h3>
      <div className="ab-layout">
        <aside>
          {[['Location', 'London, United Kingdom'], ['Employment Type', 'Full time'], ['Location Type', 'Hybrid'], ['Department', 'Design']].map(([k, v]) => (
            <div key={k}>
              <small>{k}</small>
              <span>{v}</span>
            </div>
          ))}
        </aside>
        <main>
          <div className="ab-tabs" role="tablist" aria-label="Job details">
            <button type="button" role="tab" aria-selected={overview} onClick={() => setOverview(true)}>Overview</button>
            <button type="button" role="tab" aria-selected={!overview} onClick={() => setOverview(false)}>Application</button>
          </div>
          {overview ? (
            <div className="ab-overview">
              <h4>Design what comes next.</h4>
              <p>Help a small, thoughtful team build software that makes everyday work easier.</p>
              <h4>About the role</h4>
              <p>Work across product strategy, interaction design, and the details that make a product feel right.</p>
              <button type="button" onClick={() => setOverview(false)}>Apply for this role <FidyV /></button>
            </div>
          ) : (
            <form onSubmit={(e) => e.preventDefault()}>
              <div className="ab-autofill">
                <div>
                  <strong><FijH2 /> Autofill from profile</strong>
                  <small>Use your saved details to complete your application.</small>
                </div>
                <button type="button" onClick={() => { setForm(AB_PROFILE); setFilled(true) }}>Fill from profile</button>
              </div>
              {AB_FIELDS.map(([key, label, type]) => (
                <label key={key} className="ab-field">
                  {label}
                  <span>*</span>
                  <input
                    type={type}
                    value={form[key]}
                    autoComplete="off"
                    onChange={(e) => { const v = e.target.value; setForm((f) => ({ ...f, [key]: v })); setFilled(false) }}
                  />
                </label>
              ))}
              <div className="ab-ready">
                <FiYrT />
                {filled ? 'Filled with Merlin · Ready for your review' : 'Application draft · Your changes are saved in this demo'}
              </div>
            </form>
          )}
        </main>
      </div>
    </div>
  )
}

const PREVIEW_URLS = ['qatarairways.com', 'doordash.com', 'instacart.com', 'jobs.ashbyhq.com']

function WindowLights() {
  return (
    <div className="window-lights" aria-hidden="true">
      <i />
      <i />
      <i />
    </div>
  )
}

// eM: fixed 800px-wide browser frame scaled to the card width; height 0.77 * width.
export function BrowserPreview({ exampleIndex }) {
  const [selected, setSelected] = useState(0)
  const [width, setWidth] = useState(400)
  const ref = useRef(null)
  useEffect(() => {
    if (!ref.current) return
    const ro = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width))
    ro.observe(ref.current)
    return () => ro.disconnect()
  }, [])
  return (
    <div ref={ref} className="bs-preview-size" style={{ height: 0.77 * width }}>
      <div className="bs-preview browser-section" style={{ width: 800, transform: `scale(${width / 800})` }}>
        <div className="browser-demo browser-experience">
          <div className="browser-frame">
            <div className="bs-mini-toolbar">
              <WindowLights />
              <span><FiF5_ />{PREVIEW_URLS[exampleIndex]}</span>
              <Fi_Ri />
            </div>
            <div className={`browser-site browser-page-${exampleIndex}`}>
              {exampleIndex === 0 ? (
                <QatarPage selected={selected} onSelect={setSelected} />
              ) : exampleIndex === 1 ? (
                <DoorDashPage selected={selected} onSelect={setSelected} />
              ) : exampleIndex === 2 ? (
                <InstacartPage />
              ) : (
                <AshbyPage />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
