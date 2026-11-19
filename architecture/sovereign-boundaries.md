# 07 — Sovereignty boundary register

Ashish Srivastava · 19 November 2026 · **Seven declared boundaries**

## Decision

Treat sovereignty as seven separate boundaries: data, administrators, keys, suppliers, support, placement and recovery. A site label or disconnected network does not establish all seven.

The JSON register assigns an owner and evidence type to each boundary. Data and administrator scope have executed negative cases. Key/recovery behavior uses ephemeral software custody and maintained cryptographic primitives. Supplier inputs are pinned and verified before import. Support restriction is a design assumption. Placement remains a declared/observed claim requiring independent assurance.

| Boundary | Reference position | Operational acceptance gate |
| --- | --- | --- |
| Data | Agency/object checks | Approved classification and storage/export enforcement |
| Administrators | Scoped, expiring, locally revocable sessions | Production login, privilege controls and durable revocation |
| Keys | Ephemeral software vault | Protected trust roots, custodians and recoverable wrapping material |
| Suppliers | Exact shared source and hash-locked packages | Lifecycle, support and durable update acceptance |
| Support | No support authority in fixture | Evidence of actual support interfaces and delegated access |
| Placement | Site strings | Independent workload, backup, evidence and recovery location evidence |
| Recovery | Clean-target, approved fixture restore | Realistic service objectives and stable-storage exercises |

Record a boundary exception as a specific decision with an owner and review date. Do not describe a design assumption as observed enforcement.

## Inspect the artifacts

[Seven-dimension register](../examples/sovereignty-boundaries.json) · [Exception record](../templates/sovereignty-exception.md)

## Primary references

- [NIST CSWP 29 — Cybersecurity Framework 2.0](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf) — 2024-02-26
- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
