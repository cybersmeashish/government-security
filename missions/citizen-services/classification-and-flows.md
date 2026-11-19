# 05 — Citizen-data classification and flow register

Ashish Srivastava · 19 November 2026 · **Synthetic data and flow records**

## Decision

Classify citizen-record content separately from operational evidence. An incident-review recipient does not automatically have authority to receive a citizen record or to reuse evidence for AI training.

The data dictionary identifies synthetic record IDs, agency/site labels, service state, fictional names/addresses and operational event fields. `restricted-synthetic` and `operational-synthetic` are local fixture labels, not official federal classification markings or FIPS impact categories.

Four flows have explicit owners: operator-to-record access, quarantined imports, incident evidence export and central finalization. Each declares destination, purpose, approval and failure behavior. Export is limited to allowed operational fields; a restricted-classification event is rejected rather than silently relabeled.

## Retention decision

The proposed retention entry is “owner decision required,” rather than an invented statutory number. Agency records schedules, legal holds, privacy obligations, deletion controls and audit retention must be assessed in their actual context. The lab keeps events in memory and therefore does not demonstrate durable retention.

## Evidence

The register validator rejects an unowned/unclassified flow. API and AI cases reject cross-object/cross-agency access. The export cases retain only `type`, `time` and `site`, reject wrong purpose/recipient/classification, and explicitly quarantine events with unverified timestamps.

## Inspect the artifacts

[Data dictionary](data-dictionary.csv) · [Four-flow register](../../examples/government-register.json) · [Disclosure tests](../../operations/evidence-export-authority.md)

## Primary references

- [FIPS 199 — security categorization](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.199.pdf) — 2004-02
- [NIST CSWP 29 — Cybersecurity Framework 2.0](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf) — 2024-02-26

[All 24 contributions](../../docs/contributions-01-24.md) · [Recorded verification and practical limits](../../docs/verification.md)
