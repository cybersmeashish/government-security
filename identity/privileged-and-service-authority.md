# 10 — Privileged and machine-identity authority

Ashish Srivastava · 19 November 2026 · **Tested local authority fixture**

## Trusted authority model

The server provisions random fixture tokens mapped to trusted local principals. Principals have agency, site, identity kind, record scope, permissions and expiry. A client cannot assign these fields through the HTTP API.

Read authority requires a valid local identity, matching agency/site, explicit object scope and `read` permission. Review markers additionally require `acknowledge`; service identities and viewers lack that permission. Unknown, expired, locally revoked and other-site identities are rejected.

Emergency access is a separate workflow. Two local operators with security and operations duties approve a specific requester and record. Approval handles expire after at most 300 modeled seconds, are bound to context and are consumed once. Duplicate duties, retargeting, expiry, revoked approvers and replay are denied.

## Limits and consequence

The fixture has no production authentication endpoint: test sessions are provisioned by trusted code. It does not demonstrate password authentication, MFA, production transport, durable revocation or protected clock behavior. A global revocation learned only through a disconnected central service is not resolved by this local cache.

Do not grant final public-service determination merely because local authentication succeeds. The modeled finalization action additionally requires connected central authority with age at most 300 seconds.

## Inspect the artifacts

[Local authority and emergency workflow](../govlab/policy.py) · [Authority regression cases](../tests/test_government.py)

## Primary references

- [NIST SP 800-207 — Zero Trust Architecture](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf) — 2020-08
- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
