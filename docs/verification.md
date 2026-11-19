# Government reference — observed verification

Recorded 19 November 2026. The work is a synthetic reference portfolio with individually labelled contribution stages.

| Check | Actual result |
| --- | --- |
| Host regression suite | 54 unique tests; OK; 2.161 seconds |
| Same suite in isolated Linux container | 54 tests; OK; 2.106 seconds |
| Isolated government scenarios | 63 passed expectations, including 4 expected-gap observations |
| Government runtime inputs | 22 selected source hashes matched image |
| Shared research inputs | 52 source hashes verified before import from pinned commit `747cf5428daa` |
| Network | Only loopback, no default IPv4 route, explicit external probe `ENETUNREACH` |
| Runtime | Non-root, read-only root, network none, capabilities dropped, no-new-privileges; 1 CPU, 256 MiB, 64 processes |
| Live API | Allowed own-record read/marker; denied cross-object, cross-agency, missing-session and unauthorized/offline actions |
| Clean restoration | Five timed empty-target restores; 3 of 4 live records restored; actual later record absent |
| Evidence export | Invalid-time event quarantined; wrong recipient/purpose/classification/replay denied |

[Unmodified artifact](../evidence/2026-11-19/government-isolation-report.json) · [Unit results](../evidence/2026-11-19/unit-results.json) · [Raw restoration](../evidence/2026-11-19/restoration-observations.json) · [Reproduction](reproduction.md)

**Passed means actual observations matched stated expectations.** Expected-gap cases identify absent durable replay protection, incomplete detection and unsupported placement claims. They are not assertions that those controls are production safe.

## Input and count scope

The 54 regression tests are repeated across execution environments, not added together. The 63 scenarios are government-specific observations and are not added to earlier shared-repository scenario counts. The shared six PQ compatibility experiments are linked historical host evidence; this government workflow does not run or count them.

Government source matching covers code, tests, example JSON, pinned upstream lock, dependency lock and recipe. Markdown, primary-source collection metadata, workflow and evidence files are excluded. Whole-repository publication is checked separately.

## Practical limits

Trusted sessions are server-provisioned fixtures, not production login. Policy, approval handles, revocation and replay state are in memory. Software keys/wrapping material are ephemeral. The AI assistant is deterministic, without a learned model. Placement compares strings, not independent site/provider observations. Restoration uses small tmpfs data and omits identity/approval/replay state.

No provider deployment, production TLS/MFA, HSM, protected clock/durable authority, physical air-gap assurance, real citizen data, agency adoption, compliance certification, national accreditation or peer review is claimed.
