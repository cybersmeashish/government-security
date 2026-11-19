# Reproduce the government reference

Python 3.12 and Docker are the measured path. Connected preparation fetches a fixed shared research commit and hash-locked dependencies; isolated execution has no external networking.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --no-cache-dir --require-hashes -r requirements.lock
git clone https://github.com/cybersmeashish/sovereign-disconnected-cloud-security.git .upstream
git -C .upstream checkout --detach 747cf5428daa12a7b89126011a9f64accf4154af
python -m tools.prepare_reference --checkout .upstream
python -m unittest discover -s tests -v
python -m tools.validate_registers examples/government-register.json
python -m tools.exercise --output evidence/local/host-experiment.json
docker pull python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
python -m tools.prepare_reference --checkout .upstream --wheels
docker build --network=none --pull=false -t ashish-government:contributions-01-24 .
python -m tools.run_isolated_lab --output evidence/local/government-report.json
```

`prepare_reference` verifies all 52 pinned shared source inputs before copying them. The image installs only local hash-locked wheels. The execution wrapper creates and removes only its uniquely named container and asserts network none, loopback-only interfaces, no default IPv4 route, explicit `ENETUNREACH`, non-root identity, read-only root, dropped capabilities, no-new-privileges and CPU/memory/process limits.

The government source manifest covers code, tests, example JSON, upstream lock, dependency lock and image recipe. It excludes Markdown, primary-source collection metadata, workflows and observed evidence. Rebuild after a hashed input changes; the wrapper rejects stale source/image pairing.

[Workflow](../.github/workflows/verify.yml) · [Measured verification](verification.md) · [Shared pin](../references/upstream-lock.json)
