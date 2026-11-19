# 18 — Clean public-service restoration

Ashish Srivastava · 19 November 2026 · **Measured fixture restoration**

## Measured restoration method

Use the pinned shared AES-GCM snapshot to encrypt a synthetic configuration, three government records and an encrypted software-vault backup. Keep wrapping material separate in memory. Security and operations independently sign the restore request.

After the backup is created, append an actual fourth record, `permit-after-snapshot`, to the live fixture. Restore into five distinct empty directories and derive missing record IDs by comparing the restored and live sets. Recover the software vault and decrypt its retained test value.

The run artifact contains all five elapsed samples, restored/live record counts and the actual missing ID. Wrong wrapping material and a previously used nonempty target are rejected.

## Interpretation and dependencies

This establishes the tiny fixture's observed configuration/data/software-key restoration behavior. It does not establish whole-service recovery, physical key custody, stable-media durability or a government RTO/RPO.

Dependencies remain pinned Python packages, separate wrapping material, approval public keys, trusted restore code and clean writable storage. Local identity sessions, token/approval/replay state and organizational communications are not restored by this snapshot. A realistic recovery exercise must include those dependencies and approved service objectives.

## Inspect the artifacts

[Raw restoration samples](../../evidence/2026-11-19/restoration-observations.json) · [Backup/change/restore experiment](../../tools/exercise.py) · [Recovery acceptance record](../../templates/recovery-acceptance.md)

## Primary references

- [NIST SP 800-53 Rev. 5 official OSCAL catalog](https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) — 5.2.0

[All 24 contributions](../../docs/contributions-01-24.md) · [Recorded verification and practical limits](../../docs/verification.md)
