# 16 — Evidence-export authority

Ashish Srivastava · 19 November 2026 · **Tested disclosure policy**

## Disclosure contract

Only a trusted principal with `evidence.export` may send operational-synthetic events to `agency-csoc` for `incident-review`. Events must come from the same site, have an approved type and valid timestamp, and fit the bounded 100-event batch. Exported fields are restricted to `type`, `time` and `site`.

The local custody record contains batch ID, recipient, purpose, exporter and SHA-256 of the filtered bytes. Reusing a batch ID is denied. Restricted-classification data, unknown recipients, wrong purpose, other-site events, unverified timestamps and missing exporter authority are denied.

## Timestamp uncertainty

The experiment intentionally produces an event with an invalid clock input. That event is quarantined from normal export and its attempted export is explicitly denied. The result records the quarantined-event count rather than pretending the exported batch is complete.

The digest is an integrity reference, not a signature or recipient receipt. Replay state and custody records are ephemeral. Durable audit custody, approved agency disclosure authority, real privacy review and authenticated transfer are still required.

## Inspect the artifacts

[Disclosure checker](../govlab/evidence.py) · [Owner and flow contract](../examples/government-register.json) · [Disclosure record](../templates/evidence-disclosure-record.md)

## Primary references

- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
