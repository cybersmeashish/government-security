# 22 — Government cryptography transition inventory

Ashish Srivastava · 19 November 2026 · **Purpose-separated transition inventory**

## Purpose-separated inventory

The CSV separates communication key establishment, update signatures, identity signatures, evidence custody, backup encryption, recovery wrapping and future model artifact signatures. It records owner, current reference state, migration question, compatibility evidence and unresolved gap.

The government fixture uses Ed25519 signatures and AES-256-GCM software backup encryption through maintained `cryptography`. It does not use PQ cryptography in its own runtime. NIST FIPS 203 specifies ML-KEM key establishment; FIPS 204 specifies ML-DSA signatures. A key-establishment mechanism is not a replacement for an artifact-signature mechanism.

## Linked compatibility evidence

The shared research repository separately recorded six host OpenSSL ML-KEM/ML-DSA/Ed25519 compatibility and negative checks. The inventory links that original report and its limitations. Those six checks are not counted as new government tests and do not demonstrate government TLS, identity or backup migration.

Prioritize long-lived confidentiality and trust dependencies according to the actual mission, information lifetime, interfaces and available maintained implementations. Test interoperability, artifact size, keys/certificates, offline update processes and recovery compatibility. No self-designed cryptographic primitive, government migration mandate date or validated product claim is introduced here.

## Inspect the artifacts

[Purpose-separated inventory](government-crypto-transition-inventory.csv) · [Shared implementation provenance](../references/upstream-lock.json)

## Primary references

- [FIPS 203 — ML-KEM](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf) — 2024-08-13
- [FIPS 204 — ML-DSA](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf) — 2024-08-13

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
