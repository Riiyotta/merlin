// /terms (CLONE_SPEC_PAGES_B.md §5). Body text is PLACEHOLDER, not Merlin's terms; see src/components/legal/termsData.js.
import LegalPage from '../components/legal/LegalPage.jsx'
import { termsPage } from '../components/legal/termsData.js'

export default function TermsPage() {
  return (
    <LegalPage
      page={termsPage}
      current="/terms"
      metaTitle="Terms of Service — Merlin"
      metaDescription="Terms governing access to and use of Merlin."
    />
  )
}
