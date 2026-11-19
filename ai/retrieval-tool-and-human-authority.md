# 20 — AI retrieval and tool-authority cases

Ashish Srivastava · 19 November 2026 · **Tested deterministic AI router**

## Authorization chain

The deterministic assistant first restricts the tool to the admitted configuration's allowed subset, then checks the trusted identity's `ai.use` permission, and finally uses the same record/action authority as the citizen-service API.

Scoped summary is allowed and exposes service/status plus an explicit human decision owner. Other-record/other-agency retrieval, shell execution, finalization and missing AI authority are denied. A reviewer can acknowledge only when both router configuration and personal action authority permit it; a viewer cannot gain that action by using AI.

## Integration boundary

The experiment's signed router configuration permits only `summarize`; its attempted `acknowledge` is denied even for an otherwise authorized reviewer. Other unit cases exercise a router that also permits acknowledgment.

This is not a learned model or a prompt-injection defense result. For a real model, propagate authorized document/chunk scopes through retrieval, keep tool arguments and effects independently authorized, evaluate prompt and data attacks, and retain permitted evidence. Model output must not become an authority token.

## Inspect the artifacts

[Deterministic assistant](../govlab/policy.py) · [Retrieval/tool cases](../tests/test_government.py) · [Signed router configuration](model-data-admission.md)

## Primary references

- [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) — 2023-01
- [NIST SP 800-207 — Zero Trust Architecture](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf) — 2020-08

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
