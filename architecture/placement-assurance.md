# 09 — Placement assurance case

Ashish Srivastava · 19 November 2026 · **Tested claim-state model**

## Decision

Separate a workload/backup/evidence/recovery placement declaration from independently supported location assurance.

The fixture compares four declared labels with absent, conflicting or matching observed labels. Missing observation is `unverified`; disagreement is `conflict`; agreement is `matching-claims`. Matching strings do not establish actual provider, physical or recovery placement.

## Evidence required beyond this model

The operations owner should collect deployment inventory, provider capability/dependency documentation, actual backup and recovery configuration, support/admin paths, and independent observations appropriate to the platform. Record observation method, time, trust source and gaps. The method must cover recovery copies and evidence stores as well as active workloads.

`placement_matching_claims_gap` is an expected-gap scenario. It passes because the model correctly reports a limitation, not because residency was proved.

## Inspect the artifacts

[Three placement inputs](../examples/placement-claims.json) · [Claim-state model](../govlab/evidence.py) · [Assurance record](../templates/placement-assurance-record.md)

## Primary references

- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
