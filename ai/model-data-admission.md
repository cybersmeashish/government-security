# 21 — AI model/data update admission

Ashish Srivastava · 19 November 2026 · **Tested signed router-data admission**

## Model/data admission contract

The implemented artifact is **router configuration data**, not model weights. The payload has an exact schema, `north` site, description and distinct allowed tools from `summarize`/`acknowledge`. Its signed package kind must be `model-data`.

`ModelStore` validates the bounded JSON schema and then delegates authenticity, digest, site/build context/provenance, version and separate approvals to the pinned shared admission gate. The accepted tool subset is passed into the assistant.

Positive and negative cases cover valid signed configuration, application bundle misuse, other-site data, shell-tool permission, altered payload, missing approvals, replay and downgrade. The integration artifact retains accepted version/digest and later denied replay/downgrade.

## Future real-model work

Inventory weight/tokenizer/runtime/license/accelerator/index dependencies and their exact update paths. Add compatibility and real-model behavior evaluations before deployment. Preserve protected durable admission state and separate model authenticity from retrieval/tool authorization. Those controls are not established by this deterministic configuration fixture.

## Inspect the artifacts

[Configuration admission](../govlab/model.py) · [Verified shared verifier](../govlab/reference.py) · [Admission negative cases](../tests/test_government.py)

## Primary references

- [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) — 2023-01
- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
