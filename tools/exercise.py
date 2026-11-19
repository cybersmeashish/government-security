"""Execute bounded government cases and retain observations, including unsafe gaps."""
import argparse
import copy
from dataclasses import replace
from datetime import datetime, timezone
import errno
import http.client
import json
import os
from pathlib import Path
import platform
import socket
import tempfile
import time

from govlab.evidence import Exporter, detect, freshness, placement
from govlab.model import ModelStore
from govlab.policy import Assistant, Denied, fixture, valid_time
from govlab.reference import load_reference
from govlab.service import LocalService
from tools.source_manifest import source_manifest
from tools.validate_registers import validate

ROOT = Path(__file__).resolve().parents[1]


def isolation_probe():
    directory, routes = Path("/sys/class/net"), Path("/proc/net/route")
    interfaces = sorted(p.name for p in directory.iterdir()) if directory.exists() else []
    defaults = []
    if routes.exists():
        for line in routes.read_text().splitlines()[1:]:
            fields = line.split()
            if len(fields) >= 4 and fields[1] == "00000000" and int(fields[3], 16) & 1:
                defaults.append(fields[0])
    error_number, outcome = None, "unexpected-connection"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(1)
        try:
            connection.connect(("192.0.2.1", 443))
        except OSError as error:
            error_number = error.errno
            outcome = "network-unreachable" if error.errno == errno.ENETUNREACH else type(error).__name__
    return {"passed": platform.system() == "Linux" and interfaces == ["lo"] and routes.exists()
            and not defaults and error_number == errno.ENETUNREACH,
            "interfaces": interfaces, "default_ipv4_routes": defaults,
            "external_probe": {"target": "192.0.2.1:443 (documentation-only address)",
                               "outcome": outcome, "errno": error_number},
            "scope": "network namespace observation; not physical air-gap assurance"}


def exercise(reference_root, require_isolation=False):
    lock, shared = load_reference(reference_root)
    c, admission, recovery, updates = [shared[k] for k in ("crypto", "admission", "recovery", "updates")]
    cases = []
    def record(identity, passed, observation, category="expected-control"):
        cases.append({"id": identity, "passed": bool(passed), "observation": observation, "category": category})
    def deny(identity, operation, category="expected-control"):
        try:
            operation()
        except (Denied, c.Rejected) as error:
            record(identity, True, {"result": "denied", "reason": str(error)}, category)
        else:
            record(identity, False, {"result": "unexpected-allow"}, category)

    register = json.loads((ROOT / "examples/government-register.json").read_text())
    issues = validate(register)
    record("three_mission_register", not issues, {"mission_count": len(register["missions"]), "issues": issues})
    invalid = json.loads((ROOT / "examples/negative/unowned-flow.json").read_text())
    bad = validate(invalid)
    record("unowned_unclassified_flow_rejected", len(bad) >= 2, {"issues": bad})
    record("pinned_shared_source", len(lock["source_manifest"]) == 52,
           {"commit": lock["commit"], "verified_source_files": len(lock["source_manifest"])})

    a, tokens = fixture()
    own = a.read(tokens["reviewer"], "permit-001", 100)
    record("offline_scoped_read", own["agency"] == "civic" and not a.connected,
           {"service": own["service"], "central_age": a.central_age, "connected": a.connected})
    deny("cross_record_denied", lambda: a.read(tokens["reviewer"], "permit-002", 100))
    deny("cross_agency_denied", lambda: a.read(tokens["reviewer"], "registry-001", 100))
    deny("other_site_identity_denied", lambda: a.read(tokens["remote"], "permit-001", 100))
    deny("expired_identity_denied", lambda: a.read(tokens["expired"], "permit-001", 100))
    deny("nonfinite_clock_denied", lambda: a.read(tokens["reviewer"], "permit-001", float("nan")))
    marker = a.acknowledge(tokens["reviewer"], "permit-001", 100)
    record("local_review_marker", marker["effect"] == "local-review-marker"
           and a.records["permit-001"]["status"] == "pending", marker)
    deny("viewer_action_denied", lambda: a.acknowledge(tokens["viewer"], "permit-001", 100))
    deny("service_identity_action_denied", lambda: a.acknowledge(tokens["machine"], "permit-001", 100))
    deny("offline_finalization_stopped", lambda: a.finalize(tokens["finalizer"], "permit-001", 100))
    a.connected, a.central_age = True, 301
    deny("stale_connected_finalization_stopped", lambda: a.finalize(tokens["finalizer"], "permit-001", 100))
    a.central_age = 300
    decision = a.finalize(tokens["finalizer"], "permit-001", 100)
    record("fresh_connected_finalization_fixture", decision["effect"] == "synthetic-finalization-only", decision)
    a.revoked.add("reviewer")
    deny("local_revocation_enforced", lambda: a.read(tokens["reviewer"], "permit-001", 100))
    a.revoked.remove("reviewer")
    a.connected, a.central_age = False, 1200

    def grants(record_id="permit-001"):
        return [a.approve_emergency(tokens[name], tokens["requester"], record_id, 100)
                for name in ("security", "operations")]
    approved = grants()
    emergency = a.emergency_read(tokens["requester"], "permit-001", approved, 101)
    record("two_duty_emergency_read", emergency["agency"] == "civic",
           {"scope": "context-bound, single-use local approval handles; ephemeral state"})
    deny("emergency_approval_replay_denied", lambda: a.emergency_read(tokens["requester"], "permit-001", approved, 102))
    another = grants()
    deny("emergency_other_record_denied", lambda: a.emergency_read(tokens["requester"], "permit-002", another, 101))
    deny("emergency_duplicate_duty_denied", lambda: a.emergency_read(tokens["requester"], "permit-001", [another[0]] * 2, 101))
    deny("emergency_expired_approval_denied", lambda: a.emergency_read(tokens["requester"], "permit-001", another, 400))

    with LocalService(a) as service:
        def request(method, endpoint, token=None):
            client = http.client.HTTPConnection("127.0.0.1", service.server.server_port, timeout=3)
            try:
                headers = {"Authorization": "Bearer " + token} if token else {}
                client.request(method, endpoint, headers=headers)
                result = client.getresponse()
                return result.status, json.loads(result.read())
            finally:
                client.close()
        for identity, method, endpoint, name, expected in (
            ("http_own_record", "GET", "/records/permit-001", "reviewer", 200),
            ("http_cross_record_denied", "GET", "/records/permit-002", "reviewer", 403),
            ("http_cross_agency_denied", "GET", "/records/registry-001", "reviewer", 403),
            ("http_missing_session_denied", "GET", "/records/permit-001", None, 401),
            ("http_review_marker", "POST", "/records/permit-001/acknowledge", "reviewer", 200),
            ("http_viewer_action_denied", "POST", "/records/permit-001/acknowledge", "viewer", 403),
            ("http_offline_finalization_denied", "POST", "/records/permit-001/finalize", "finalizer", 403),
        ):
            status, _ = request(method, endpoint, tokens[name] if name else None)
            record(identity, status == expected, {"http_status": status, "expected": expected})

    known = detect([{"type": "denied", "time": 100}] * 3, 100)
    record("repeated_denial_alert", known == ["repeated-denial"], {"alerts": known})
    unknown = detect([{"type": "unknown-import-pattern", "time": 100}], 100)
    record("unknown_event_detection_gap", not unknown, {"alerts": unknown, "gap": "no rule covers this event"},
           "observed-gap")
    states = {name: freshness(value, 100) for name, value in (
        ("current", {"verified": True, "observed_at": 100}),
        ("delayed", {"verified": True, "observed_at": 20}),
        ("missing", None), ("unverified", {"verified": False, "observed_at": 100}))}
    record("four_visibility_states", all(k == v for k, v in states.items()), states)
    report = {"verified": True, "observed_at": 100}
    conclusion = [freshness(report, now) == "current" for now in (160, 161)]
    record("central_conclusion_expires", conclusion == [True, False],
           {"current_at_160": conclusion[0], "current_at_161": conclusion[1], "threshold_seconds": 60})
    record("future_evidence_unverified", freshness({"verified": True, "observed_at": 101}, 100) == "unverified",
           {"state": freshness({"verified": True, "observed_at": 101}, 100)})
    a.principals["reviewer"] = replace(a.principals["reviewer"],
        permissions=a.principals["reviewer"].permissions | {"evidence.export"})
    exporter = Exporter()
    valid_events = [event for event in a.events if valid_time(event.get("time"))]
    invalid_events = [event for event in a.events if not valid_time(event.get("time"))]
    deny("unverified_time_export_denied", lambda: exporter.export(
        a, tokens["reviewer"], invalid_events, "agency-csoc", "incident-review", "invalid-time", 100))
    exported = exporter.export(a, tokens["reviewer"], valid_events, "agency-csoc", "incident-review", "batch-1", 100)
    record("filtered_custody_export", all(set(event) <= {"type", "time", "site"} for event in exported["events"]),
           {"event_count": len(exported["events"]), "quarantined_unverified_time_events": len(invalid_events),
            "custody": exported["custody"]})
    deny("export_recipient_denied", lambda: exporter.export(a, tokens["reviewer"], [], "public", "incident-review", "b2", 100))
    deny("export_purpose_denied", lambda: exporter.export(a, tokens["reviewer"], [], "agency-csoc", "model-training", "b2", 100))
    deny("export_replay_denied", lambda: exporter.export(a, tokens["reviewer"], [], "agency-csoc", "incident-review", "batch-1", 100))
    restricted = [{"type": "allowed", "site": "north", "time": 100, "classification": "restricted-synthetic"}]
    deny("restricted_export_denied", lambda: exporter.export(a, tokens["reviewer"], restricted, "agency-csoc", "incident-review", "b2", 100))

    claims = json.loads((ROOT / "examples/placement-claims.json").read_text())
    for identity, observed, expected in (
        ("placement_no_observation", None, "unverified"),
        ("placement_conflict", claims["conflict"], "conflict"),
        ("placement_matching_claims_gap", claims["observed_fixture_claims"], "matching-claims"),
    ):
        result = placement(claims["declared"], observed)
        record(identity, result["state"] == expected, result,
               "observed-gap" if expected in {"unverified", "matching-claims"} else "expected-control")

    release, security, operations, approval_policy = c.demo_signers()
    def evidence(body, purpose):
        return [c.approve(signer, purpose, body) for signer in (security, operations)]
    def gate():
        return admission.Admission({release.key_id: release.public}, approval_policy, site="north")
    package = admission.bundle(b"synthetic government application v1", release, "gov-app-1", 1, site="north")
    signatures = evidence(c.canonical(package["manifest"]), "admit-release")
    admission_gate = gate()
    accepted = admission_gate.inspect(package, signatures)
    record("signed_government_update_admitted", accepted.site == "north", {"version": accepted.version, "sha256": accepted.sha256})
    altered = copy.deepcopy(package); altered["payload"] = c.b64(b"altered update")
    deny("altered_update_denied", lambda: gate().inspect(altered, signatures))
    wrong = admission.bundle(b"other destination", release, "other", 1, site="south")
    deny("signed_wrong_site_update_denied", lambda: gate().inspect(wrong, evidence(c.canonical(wrong["manifest"]), "admit-release")))
    deny("missing_update_approvals_denied", lambda: gate().inspect(package, []))
    deny("update_replay_denied", lambda: admission_gate.inspect(package, signatures))
    restarted = gate().inspect(package, signatures)
    record("ephemeral_update_restart_gap", restarted.version == 1,
           {"accepted_old_version_after_new_gate": restarted.version, "gap": "protected durable replay state absent"},
           "observed-gap")

    scratch = "/lab-state" if Path("/lab-state").exists() else None
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        store = updates.UpdateStore(Path(directory) / "updates", approval_policy)
        store.deploy(accepted)
        second = admission.bundle(b"synthetic government application v2", release, "gov-app-2", 2, site="north")
        accepted2 = admission_gate.inspect(second, evidence(c.canonical(second["manifest"]), "admit-release"))
        deny("interrupted_update_denied", lambda: store.deploy(accepted2, "before_activate"))
        record("interrupted_update_keeps_active", store.active()["version"] == 1, {"active_version": store.active()["version"]})
        store.deploy(accepted2)
        rollback_body = c.canonical({"from": 2, "to": 1, "sha256": store.history[1]["sha256"]})
        store.rollback(1, evidence(rollback_body, "rollback-release"))
        record("approved_government_rollback", store.active()["version"] == 1, {"active_version": store.active()["version"]})

        wrapping = os.urandom(32)
        vault = c.Vault("civic/north", approval_policy)
        encrypted = vault.encrypt(b"synthetic retained government value")
        backup_keys = vault.backup(wrapping)
        live_records = [{"id": identity, **value} for identity, value in a.records.items()]
        config = {"agency": "civic", "site": "north", "jurisdiction": "US-federal-civilian-reference"}
        backup = recovery.snapshot(config, live_records, backup_keys, wrapping)
        live_records.append({"id": "permit-after-snapshot", "agency": "civic", "site": "north"})
        durations, restored = [], None
        for index in range(5):
            start = time.perf_counter()
            restored = recovery.restore(backup, wrapping, evidence(c.canonical(backup), "restore-site"),
                                        approval_policy, Path(directory) / ("restore-" + str(index)))
            durations.append(time.perf_counter() - start)
        missing = sorted({r["id"] for r in live_records} - {r["id"] for r in restored["records"]})
        recovered_vault = c.Vault.recover(restored["vault_backup"], wrapping,
            evidence(c.canonical(restored["vault_backup"]), "recover-key"), approval_policy, "civic/north")
        restoration = {"samples_seconds": durations, "restored_records": len(restored["records"]),
                       "live_records": len(live_records), "missing_record_ids": missing,
                       "scope": "tiny software-key/config/record fixture; not whole-service RTO/RPO"}
        record("clean_restore_config_records_keys", restored["config"] == config
               and recovered_vault.decrypt(encrypted) == b"synthetic retained government value", restoration)
        record("actual_post_snapshot_change_absent", missing == ["permit-after-snapshot"], {"missing_record_ids": missing})
        deny("wrong_restoration_key_denied", lambda: recovery.restore(
            backup, os.urandom(32), evidence(c.canonical(backup), "restore-site"), approval_policy,
            Path(directory) / "wrong-key"))
        deny("dirty_restoration_target_denied", lambda: recovery.restore(
            backup, wrapping, evidence(c.canonical(backup), "restore-site"), approval_policy,
            Path(directory) / "restore-0"))

    model_data = c.canonical({"schema": "government-router-data-v1", "site": "north",
                              "tools": ["summarize"], "description": "synthetic admitted router policy"})
    candidate = admission.bundle(model_data, release, "gov-router-2", 2, site="north", kind="model-data")
    model_store = ModelStore(gate())
    active = model_store.admit(candidate, evidence(c.canonical(candidate["manifest"]), "admit-release"))
    record("signed_router_data_admitted", active["version"] == 2 and active["site"] == "north", active)
    ai = Assistant(a, active["tools"])
    summary = ai.execute(tokens["viewer"], "permit-001", "summarize", 100)
    record("ai_summary_filtered", "citizen" not in summary and "address" not in summary, summary)
    deny("ai_cross_agency_denied", lambda: ai.execute(tokens["viewer"], "registry-001", "summarize", 100))
    deny("ai_shell_denied", lambda: ai.execute(tokens["reviewer"], "permit-001", "shell", 100))
    deny("ai_non_admitted_tool_denied", lambda: ai.execute(tokens["reviewer"], "permit-001", "acknowledge", 100))
    deny("router_data_replay_denied", lambda: model_store.admit(candidate, evidence(c.canonical(candidate["manifest"]), "admit-release")))
    older = admission.bundle(model_data, release, "gov-router-1", 1, site="north", kind="model-data")
    deny("router_data_downgrade_denied", lambda: model_store.admit(older, evidence(c.canonical(older["manifest"]), "admit-release")))

    isolation = isolation_probe() if require_isolation else {"passed": None, "scope": "not requested on host"}
    if require_isolation:
        record("explicit_network_isolation", isolation["passed"], isolation, "actual-network-observation")
    return {"schema_version": 1, "observed_at": datetime.now(timezone.utc).isoformat(),
            "synthetic": True, "environment": {"python": platform.python_version(),
                "system": platform.system(), "machine": platform.machine()},
            "source_manifest": source_manifest(ROOT),
            "reference": {"commit": lock["commit"], "verified_source_files": len(lock["source_manifest"])},
            "network_isolation": isolation, "cases": cases, "restoration": restoration,
            "passed": all(case["passed"] for case in cases),
            "limits": ["Synthetic public-service decisions, ephemeral fixture sessions and local approval state.",
                       "No production login/MFA/TLS, protected durable anti-rollback, HSM or provider placement assurance.",
                       "AI is a deterministic router; no learned model, real citizen data or prompt robustness evaluation.",
                       "Passed expected-gap cases identify unsafe limitations; no compliance or accreditation claim.",
                       "Restoration measures a tiny fixture on the selected temporary filesystem, not whole-site recovery."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, default=ROOT / "vendor/reference")
    parser.add_argument("--require-isolation", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = exercise(args.reference_root, args.require_isolation)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
