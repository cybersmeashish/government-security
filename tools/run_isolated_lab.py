"""Run only a task-owned, constrained government reference container and inspect it."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import uuid
from tools.source_manifest import source_manifest

ROOT = Path(__file__).resolve().parents[1]


def command(runtime, *arguments):
    result = subprocess.run([runtime, *arguments], capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(f"{runtime} {arguments[0]} failed: {result.stderr.strip()}")
    return result.stdout


def run(runtime, image):
    identity = None
    try:
        identity = command(runtime, "create", "--name", "ashish-government-" + uuid.uuid4().hex[:12],
            "--network", "none", "--read-only", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges", "--pids-limit", "64",
            "--memory", "256m", "--cpus", "1",
            "--tmpfs", "/lab-state:rw,nodev,nosuid,noexec,size=32m,uid=65532,gid=65532", image).strip()
        configuration = json.loads(command(runtime, "inspect", identity))[0]
        experiment = json.loads(command(runtime, "start", "-a", identity))
        completed = json.loads(command(runtime, "inspect", identity))[0]
        host = configuration["HostConfig"]
        restrictions = {
            "network_mode": host["NetworkMode"], "read_only_root": host["ReadonlyRootfs"],
            "user": configuration["Config"]["User"], "capabilities_dropped": host.get("CapDrop", []),
            "no_new_privileges": any(s.split("=")[0] == "no-new-privileges" for s in host.get("SecurityOpt", [])),
            "memory_bytes": host["Memory"], "nano_cpus": host["NanoCpus"], "pids_limit": host["PidsLimit"],
            "tmpfs": host.get("Tmpfs", {}), "image_id": configuration["Image"],
            "exit_code": completed["State"]["ExitCode"],
        }
        manifest = source_manifest(ROOT)
        source_match = experiment["source_manifest"] == manifest
        passed = (experiment["passed"] and experiment["network_isolation"]["passed"]
            and source_match and restrictions["network_mode"] == "none"
            and restrictions["read_only_root"] and restrictions["user"] == "65532:65532"
            and "ALL" in restrictions["capabilities_dropped"] and restrictions["no_new_privileges"]
            and restrictions["memory_bytes"] == 268435456 and restrictions["nano_cpus"] == 1000000000
            and restrictions["pids_limit"] == 64 and restrictions["exit_code"] == 0)
        return {"schema_version": 1, "observed_at": datetime.now(timezone.utc).isoformat(),
                "scope": "Synthetic government reference, not a deployed or accredited public service.",
                "restrictions": restrictions, "source_matches_image": source_match,
                "source_manifest": manifest, "experiment": experiment, "passed": passed}
    finally:
        if identity:
            subprocess.run([runtime, "rm", "-f", identity], capture_output=True, timeout=30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=("docker", "podman"), default="docker")
    parser.add_argument("--image", default="ashish-government:contributions-01-24")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/local/government-report.json")
    args = parser.parse_args()
    report = run(args.runtime, args.image)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "source_matches_image": report["source_matches_image"],
                      "cases": len(report["experiment"]["cases"])}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
