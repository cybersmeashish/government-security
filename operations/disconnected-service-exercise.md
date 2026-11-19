# 13 — Disconnected public-service exercise

Ashish Srivastava · 19 November 2026 · **Executed reference exercise**

## Executed reference exercise

Start with trusted local sessions, `connected=False`, central evidence age 1,200 modeled seconds and synthetic records. The actual isolated container has external networking disabled, while local loopback API requests remain possible.

| Situation | Local action | Observed evidence |
| --- | --- | --- |
| Central connectivity absent | Scoped read and reviewer marker continue | `offline_scoped_read`, `http_own_record`, `http_review_marker` |
| Final determination requested | Stop, retain local review work | `offline_finalization_stopped`, `http_offline_finalization_denied` |
| Valid token requests another record/agency | Deny without expanding authority | Cross-record and cross-agency cases |
| Local compromise declared | Revoke local principal | `local_revocation_enforced` |
| Emergency review requested | Require bound security/operations handles | Emergency context, expiry and replay cases |

## Local decision and reconnection

The synthetic regional operations lead may maintain scoped review continuity; the service owner retains final decision authority. The 300-second finalization freshness threshold is a design assumption, not a statutory number. Reconnection must reconcile authority, locally queued review markers and current evidence before enabling finalization.

The experiment does not test a provider control plane, physical transfer equipment, global revocation delivery or a real agency workflow. Network isolation and local policy are separate observations.

## Inspect the artifacts

[Regional office case](../case-studies/disconnected-regional-office.md) · [Isolation verifier](../tools/run_isolated_lab.py) · [Authority semantics](../identity/privileged-and-service-authority.md)

## Primary references

- [NIST SP 800-207 — Zero Trust Architecture](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf) — 2020-08

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
