"""Prepare verified upstream source and, optionally, a platform wheelhouse."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from govlab.reference import check_reference

ROOT = Path(__file__).resolve().parents[1]


def prepare(checkout):
    checkout = Path(checkout).resolve()
    lock = check_reference(checkout)
    target = ROOT / "vendor/reference"
    target.mkdir(parents=True, exist_ok=True)
    for relative in lock["source_manifest"]:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(checkout / relative, destination)
    check_reference(target)
    if (target / "requirements.lock").read_bytes() != (ROOT / "requirements.lock").read_bytes():
        raise ValueError("dependency lock differs from the pinned upstream lock")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--wheels", action="store_true")
    parser.add_argument("--architecture", choices=("arm64", "amd64"))
    args = parser.parse_args()
    target = prepare(args.checkout)
    if args.wheels:
        command = [sys.executable, "-m", "tools.prepare_dependencies"]
        if args.architecture:
            command += ["--architecture", args.architecture]
        subprocess.run(command, cwd=target, check=True)
        shutil.copytree(target / "vendor/wheels", ROOT / "vendor/wheels", dirs_exist_ok=True)
    print(json.dumps({"reference_verified": True, "source_files": len(check_reference(target)["source_manifest"]),
                      "wheels_requested": args.wheels}, indent=2))


if __name__ == "__main__":
    main()
