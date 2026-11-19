# 14 — Government update-admission case

Ashish Srivastava · 19 November 2026 · **Executed signed-update cases**

## Executed admission chain

Application bytes enter quarantine. The pinned shared verifier checks the signed manifest, payload digest, exact site/architecture/build context/provenance subject, monotonic version and separate cryptographic security/operations approvals before returning an accepted artifact.

Government cases use site `north`: valid release accepted; altered bytes, a validly signed other-site release, missing approvals and replay rejected. Staging an interrupted v2 update leaves v1 active. A rollback from v2 to known v1 requires fresh signed rollback approvals.

## Observed unsafe gap

A newly constructed gate accepts the previously valid v1 bundle because its replay/version state is in memory. `ephemeral_update_restart_gap` records this actual outcome. Persisting a file is not enough if an attacker can replace its floor; a deployment needs a protected, recoverable authority/freshness design.

The package envelope and provenance are synthetic and bounded. They do not establish a SLSA level, DSSE compliance, real supplier assurance or production crash consistency. The source is imported only after 52 pinned shared input hashes match the selected commit.

## Inspect the artifacts

[Pinned shared-source verification](../govlab/reference.py) · [Immutable commit and source hashes](../references/upstream-lock.json) · [Government update/rollback cases](../tools/exercise.py)

## Primary references

- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
