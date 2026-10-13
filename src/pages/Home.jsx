import '../styles/home.css'
import Hero from '../components/Hero.jsx'
import Companies from '../components/Companies.jsx'
import Routines from '../components/Routines.jsx'
import Browser from '../components/Browser.jsx'
import Meetings from '../components/Meetings.jsx'
import Companion from '../components/Companion.jsx'
import Privacy from '../components/Privacy.jsx'
import Faq from '../components/Faq.jsx'
import Footer from '../components/Footer.jsx'
import FloatingNav from '../components/FloatingNav.jsx'

export default function Home() {
  return (
    <main className="merlin-story site-layout" id="top">
      <a className="skip-link" href="#routines">Skip to product examples</a>
      <Hero />
      <Companies />
      <Routines />
      <Browser />
      <Meetings />
      <Companion />
      <Privacy />
      <Faq />
      <Footer />
      <FloatingNav />
    </main>
  )
}
