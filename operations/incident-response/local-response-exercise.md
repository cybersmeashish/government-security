# 17 — Government incident-response exercise

Ashish Srivastava · 19 November 2026 · **Reference response walkthrough**

## Reference walkthrough

These are programmatically exercised local response decisions and a proposed agency exercise script. No real incident or agency tabletop participation is claimed.

| Inject | Local decision owner | Executed bounded action | Evidence | Reconnection / escalation question |
| --- | --- | --- | --- | --- |
| Reviewer account declared compromised | Local security lead | Add principal to local revocation state; subsequent read denied | `local_revocation_enforced` | How are global sessions and durable revocation reconciled? |
| Imported update appears altered | Security + operations | Reject signed bundle with changed payload; retain active release | `altered_update_denied` | Who owns supplier investigation and trusted replacement? |
| Central connectivity/authority lost | Regional operations lead | Continue scoped review; stop final determination | Offline read and finalization cases | Who may enable finalization after authority refresh? |
| Emergency access requested | Local security + operations | Approve one requester/record with distinct duties and single-use handles | Emergency read/context/replay cases | Where are approvals and evidence protected across restart? |

## Agency exercise extension

Assign an incident commander, communications fallback and disclosure owner. Record inject time, decision, authority relied upon, observation, unresolved dependency and escalation deadline. Repeat with unavailable approvers, uncertain time, depleted storage and a realistic restoration target.

The existing reference execution does not measure agency response time or prove communications capability. The playbook's proposed extensions remain unexecuted organizational work.

## Inspect the artifacts

[Exercise record](../../templates/incident-exercise-record.md) · [Local continuity](../disconnected-service-exercise.md) · [Executed decisions](../../tools/exercise.py)

## Primary references

- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../../docs/contributions-01-24.md) · [Recorded verification and practical limits](../../docs/verification.md)
