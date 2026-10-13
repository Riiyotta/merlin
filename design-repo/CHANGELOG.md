# Changelog

## repositoryVersion 1.0.0 / allowlistVersion 1.0.0 / pageSpecVersion 1.0.0 (initial build)

Built bottom-up from the local clone (React 18 + Vite) of https://www.merlin.computer using the pre-existing CLONE_SPEC*.md files as strong first drafts, spot-checked and corrected against the real source (see README "Where the pre-existing specs were wrong").

- tokens: 352 (foundation 249, semantic 57, component 20, layout 26); the site ships no histogram, so `extraction/derive_histograms.py` derives one from the compiled CSS.
- 13 primitives, 21 components, 32 section contracts, 7 templates, 8 routes (+2 routing behaviors), 19 graph rules, 14 asset roles, 26 motion patterns.
- closed `assetRole` enum built from a grep of real asset usage, wired through schema + allowlist + example, each role pinned to its exact generationPolicy.
- `verify_all.py` (allowlist parity both ways, allowlistVersion, recomputed manifest counts, citation range + quoted-content checks, histogram recompute, route/template/graph/schema parity, page-order precision, README counts marker, no absolute paths); `prove_drift.py` proves each check catches injected drift.
- `schema/tests/adversarial_test.py`: mutations rejected + controls passing (every real route, the example, both directions of each graph exception).
- `/privacy` + `/terms` grouped into one `legal` template only after a real structural comparison.
