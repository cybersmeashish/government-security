# Citizen-service portal — record and action authority

**Synthetic case · executed loopback API and local policy fixture**

A civic reviewer may read `permit-001` and append a local review marker. A separate registry principal may read `registry-001`. A valid civic session does not permit reading `permit-002` or another agency's record. The marker does not change the pending service state or create a final determination.

[Mission register](../missions/mission-authority-register.md) · [Data/flows](../missions/citizen-services/classification-and-flows.md) · [Threat model](../missions/citizen-services/threat-model.md)

[Actual API review](../applications/citizen-service-api-review.md) · [Authority implementation](../govlab/policy.py) · [Recorded results](../docs/verification.md) · [Decision brief](../briefs/government-local-authority-decision.md)

**Decision:** fund production authority and protected state before exposing this design as a public service. Real login, TLS/MFA, persistent policy, database/network enforcement, independent penetration testing and applicable agency obligations remain unresolved.
