# 15 — Local monitoring and central freshness

Ashish Srivastava · 19 November 2026 · **Tested detection/freshness models**

## Local detection and central knowledge

The local illustrative detector has two rules: at least three denials in the recent 60 modeled seconds emit `repeated-denial`; an emergency read in that window emits `emergency-review`. Old, future and nonfinite-time events are excluded from those rules. This is not comprehensive threat detection.

The central model distinguishes `current`, `delayed`, `missing` and `unverified` reports. A verified observation at time 100 remains current at 160 and becomes delayed at 161. An observation from the future is unverified.

## Recorded gap

An `unknown-import-pattern` event emits no alert. The experiment records this missing rule explicitly. A healthy pipeline and current report do not establish detection coverage.

The `verified` flag is a trusted fixture input; this module does not verify a report signature. Production use needs authenticated site evidence, clock/ordering uncertainty, durable retention, backlog/loss indicators, rule evaluation datasets and protected reporting transport.

## Inspect the artifacts

[Detection and freshness model](../govlab/evidence.py) · [Threshold/negative cases](../tests/test_government.py) · [Permitted central disclosure](evidence-export-authority.md)

## Primary references

- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
