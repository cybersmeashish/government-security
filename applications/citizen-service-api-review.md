# 11 — Citizen-service application/API review

Ashish Srivastava · 19 November 2026 · **Live loopback API review**

## Review method

Run the actual loopback HTTP adapter with server-provisioned fixture sessions. Use a permitted read as the baseline, then change object, agency, action and session inputs.

| Request | Expected response | Meaning |
| --- | --- | --- |
| Reviewer reads `permit-001` | 200 | Assigned agency/object allowed |
| Same reviewer reads `permit-002` | 403 | Valid identity cannot expand object scope |
| Same reviewer reads `registry-001` | 403 | Other agency denied |
| Request without bearer session | 401 | Provisioned session required |
| Reviewer acknowledges own record | 200 | Local review marker only |
| Viewer acknowledges own record | 403 | Action permission absent |
| Finalizer requests finalization offline | 403 | Central authority requirement not satisfied |
| Unknown action or malformed route | 404 | Unpublished endpoint does not dispatch an action |

The seven integration HTTP observations are retained in the run artifact. Additional endpoint, action and missing-session checks are in the regression suite.

## Security consequence

Authorization occurs at the server action/object boundary, rather than trusting a UI to hide operations. Successful acknowledgment leaves the record's `pending` state unchanged; it is not a permit, benefit or legal determination.

This is a local adapter, not a production API. TLS, real login/MFA, rate limits, persistent sessions, concurrent-state safety, ingress deployment and independent penetration testing remain deployment work.

## Inspect the artifacts

[Loopback HTTP service](../govlab/service.py) · [Server-side checks](../govlab/policy.py) · [HTTP tests](../tests/test_government.py)

## Primary references

- [NIST SP 800-207 — Zero Trust Architecture](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf) — 2020-08

[All 24 contributions](../docs/contributions-01-24.md) · [Recorded verification and practical limits](../docs/verification.md)
