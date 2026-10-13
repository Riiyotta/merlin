// /privacy (CLONE_SPEC_PAGES_B.md §4). Body text is PLACEHOLDER, not Merlin's policy; see src/components/legal/privacyData.js.
import LegalPage from '../components/legal/LegalPage.jsx'
import { privacyPage } from '../components/legal/privacyData.js'

export default function PrivacyPage() {
  return (
    <LegalPage
      page={privacyPage}
      current="/privacy"
      metaTitle="Privacy and control — Merlin"
      metaDescription="How Merlin handles your information, what stays on your Mac, and how to manage access and your data."
    />
  )
}
