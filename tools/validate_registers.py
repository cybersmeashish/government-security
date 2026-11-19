"""Check government mission/flow declarations; no claim of deployed enforcement."""
import argparse
import json
from pathlib import Path


def validate(register):
    issues = []
    if not isinstance(register, dict) or register.get("schema_version") != 1:
        return ["unsupported register schema"]
    owners = register.get("owners")
    if not isinstance(owners, dict) or not owners:
        return ["accountable owners are required"]
    missions = register.get("missions")
    if not isinstance(missions, list) or len(missions) != 3:
        return ["three synthetic missions are required"]
    identities = set()
    for mission in missions:
        if not isinstance(mission, dict):
            issues.append("mission must be an object"); continue
        identity = mission.get("id")
        if not isinstance(identity, str) or not identity:
            issues.append("mission IDs must be distinct")
            identity = "<invalid>"
        elif identity in identities:
            issues.append("mission IDs must be distinct")
        identities.add(identity)
        for field in ("service_owner", "security_owner", "failure_decision_owner"):
            if not isinstance(mission.get(field), str) or mission[field] not in owners:
                issues.append(f"{identity}: unresolved {field}")
        for field in ("agency", "site", "citizen_impact", "dependencies", "permitted_actions",
                      "stopped_actions", "recovery_acceptance"):
            if not mission.get(field):
                issues.append(f"{identity}: missing {field}")
        permitted, stopped = mission.get("permitted_actions"), mission.get("stopped_actions")
        if (not isinstance(permitted, list) or not isinstance(stopped, list)
                or any(not isinstance(action, str) for action in [*(permitted or []) , *(stopped or [])])):
            issues.append(f"{identity}: action lists must contain strings")
        elif set(permitted) & set(stopped):
            issues.append(f"{identity}: conflicting action authority")
    flows = register.get("flows")
    if not isinstance(flows, list) or not flows:
        issues.append("at least one flow is required")
        flows = []
    for flow in flows:
        if not isinstance(flow, dict):
            issues.append("flow must be an object")
            continue
        for field in ("id", "source", "destination", "classification", "purpose",
                      "approval", "failure_behavior"):
            if not flow.get(field):
                issues.append(f"flow: missing {field}")
        if not isinstance(flow.get("owner"), str) or flow["owner"] not in owners:
            issues.append("flow: unresolved owner")
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("register", type=Path)
    args = parser.parse_args()
    issues = validate(json.loads(args.register.read_text()))
    print(json.dumps({"valid": not issues, "issues": issues}, indent=2))
    raise SystemExit(bool(issues))


if __name__ == "__main__":
    main()
