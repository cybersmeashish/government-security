# 01 — Government mission and authority register

Ashish Srivastava · 19 November 2026 · **Validated synthetic register**

## Decision

Separate the authority to keep a local public-service workflow moving from the authority to issue a final determination. A network outage changes operational conditions; it does not grant additional record access or decision rights.

The machine-readable register contains three synthetic missions: citizen permit review, public-registry review and emergency review continuity. Every mission names a service owner, security owner, local failure decision owner, dependencies, permitted actions, stopped actions and restoration acceptance.

| Mission | Locally permitted | Must stop | Local decision owner |
| --- | --- | --- | --- |
| Citizen permit review | Read an explicitly scoped record; append a review marker | Final determination without fresh central authority | Regional operations lead |
| Public-registry review | Read the assigned registry record | Cross-agency access and bulk disclosure | Regional operations lead |
| Emergency continuity | Context-bound read approved by separate local security and operations roles | Self-approval, approval reuse and stale finalization | Regional operations lead |

## Validation and limits

`tools.validate_registers` checks declared owners, distinct mission IDs, nonconflicting action lists and flow owner/classification/purpose/approval/failure behavior. The published negative fixture has an unresolved owner and missing classification and is rejected.

The register is a declaration. Runtime policy is implemented separately in `govlab.policy`; compare its observed cases before describing any declared outcome as enforced. All owners and missions are fictional role assignments.

## Inspect the artifacts

[Three-mission register](../examples/government-register.json) · [Validator](../tools/validate_registers.py) · [Negative fixture](../examples/negative/unowned-flow.json)

## Primary references

- [NIST CSWP 29 — Cybersecurity Framework 2.0](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf) — 2024-02-26

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
