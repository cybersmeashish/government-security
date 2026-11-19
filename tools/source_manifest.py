import hashlib
from pathlib import Path


def source_manifest(root):
    root = Path(root)
    paths = set()
    for pattern in ("govlab/**/*.py", "tools/**/*.py", "tests/**/*.py", "examples/**/*.json",
                    "references/upstream-lock.json", "requirements.lock", "Dockerfile"):
        paths.update(p for p in root.glob(pattern) if p.is_file())
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}
