# 19 — Public-sector AI use-case register

Ashish Srivastava · 19 November 2026 · **Synthetic AI use-case register**

## AI use-case register

| Use case | Data | Permitted effect | Accountable human | Current evidence |
| --- | --- | --- | --- | --- |
| Record summary | One explicitly scoped synthetic record | Return service/status without citizen/address fields | Public-service owner | Deterministic retrieval and filtering cases |
| Review marker | One explicitly scoped record | Append a local review marker when the operator has action permission | Review operator | Allowed reviewer and denied viewer cases |
| Public guidance | Approved public sources | Future guidance with sources, human review and accessibility criteria | AI/service owner | Proposed; no learned-model implementation |

## Governance connection

Use Govern/Map/Measure/Manage questions to record ownership, context, actual evaluation and residual treatment. The reference's measured risks are retrieval scope, tool authority, output fields and signed router-data admission. It does not measure model quality, fairness, hallucination, multilingual accessibility or prompt-injection robustness.

Do not allow the AI router to create a public-service determination, execute shell commands or expand record access. The responsible human decision-maker and allowed side effect must remain explicit.

## Inspect the artifacts

[Use-case register](../examples/ai-use-cases.json) · [AI case](../case-studies/public-sector-ai-assistant.md) · [Evaluation record](../templates/ai-evaluation-record.md)

## Primary references

- [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) — 2023-01

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
