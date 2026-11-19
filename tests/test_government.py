import copy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error
import urllib.request

from govlab.evidence import Exporter, detect, freshness, placement
from govlab.policy import Assistant, Denied, fixture
from govlab.service import LocalService
from govlab.model import ModelStore
from govlab.reference import check_reference, load_reference
from tools.validate_registers import validate

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path("/reference") if Path("/reference").exists() else ROOT / "vendor/reference"


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.a, self.t = fixture()

    def test_scoped_read_during_disconnection(self):
        self.assertFalse(self.a.connected)
        self.assertEqual(self.a.read(self.t["reviewer"], "permit-001", 100)["service"], "permit-review")

    def test_cross_record_denied(self):
        with self.assertRaises(Denied): self.a.read(self.t["reviewer"], "permit-002", 100)

    def test_cross_agency_denied(self):
        with self.assertRaises(Denied): self.a.read(self.t["reviewer"], "registry-001", 100)

    def test_registry_owner_can_read_registry(self):
        self.assertEqual(self.a.read(self.t["registry"], "registry-001", 100)["agency"], "registry")

    def test_expiry_boundary_denied(self):
        with self.assertRaises(Denied): self.a.read(self.t["expired"], "permit-001", 100)

    def test_revoked_session_denied(self):
        self.a.revoked.add("reviewer")
        with self.assertRaises(Denied): self.a.read(self.t["reviewer"], "permit-001", 100)

    def test_unknown_session_denied(self):
        with self.assertRaises(Denied): self.a.read("unissued", "permit-001", 100)

    def test_valid_other_site_identity_denied(self):
        with self.assertRaises(Denied): self.a.read(self.t["remote"], "permit-001", 100)

    def test_nonfinite_clock_denied(self):
        for now in (float("nan"), float("inf"), -1, True):
            with self.subTest(now=now):
                with self.assertRaises(Denied): self.a.read(self.t["reviewer"], "permit-001", now)

    def test_viewer_and_machine_acknowledgment_denied(self):
        for name in ("viewer", "machine"):
            with self.subTest(name=name):
                with self.assertRaises(Denied): self.a.acknowledge(self.t[name], "permit-001", 100)

    def test_reviewer_marker_does_not_finalize(self):
        before = copy.deepcopy(self.a.records)
        self.assertEqual(self.a.acknowledge(self.t["reviewer"], "permit-001", 100)["effect"], "local-review-marker")
        self.assertEqual(self.a.records, before)

    def test_finalization_stops_offline(self):
        with self.assertRaises(Denied): self.a.finalize(self.t["finalizer"], "permit-001", 100)

    def test_finalization_requires_fresh_central_authority(self):
        self.a.connected, self.a.central_age = True, 300
        self.assertEqual(self.a.finalize(self.t["finalizer"], "permit-001", 100)["effect"], "synthetic-finalization-only")
        for age in (301, float("nan"), -1):
            self.a.central_age = age
            with self.assertRaises(Denied): self.a.finalize(self.t["finalizer"], "permit-001", 100)

    def grants(self, record="permit-001"):
        return [self.a.approve_emergency(self.t[n], self.t["requester"], record, 100)
                for n in ("security", "operations")]

    def test_two_duty_context_bound_emergency_read(self):
        self.assertEqual(self.a.emergency_read(self.t["requester"], "permit-001", self.grants(), 101)["agency"], "civic")

    def test_emergency_replay_denied(self):
        grants = self.grants()
        self.a.emergency_read(self.t["requester"], "permit-001", grants, 101)
        with self.assertRaises(Denied): self.a.emergency_read(self.t["requester"], "permit-001", grants, 102)

    def test_emergency_other_record_denied(self):
        with self.assertRaises(Denied):
            self.a.emergency_read(self.t["requester"], "permit-002", self.grants(), 101)

    def test_emergency_other_requester_denied(self):
        self.a.principals["requester2"] = replace(self.a.principals["requester"], subject="requester2")
        token = self.a.issue("requester2")
        with self.assertRaises(Denied): self.a.emergency_read(token, "permit-001", self.grants(), 101)

    def test_duplicate_duty_and_raw_role_token_denied(self):
        grant = self.a.approve_emergency(self.t["security"], self.t["requester"], "permit-001", 100)
        for handles in ([grant, grant], [self.t["security"], self.t["operations"]]):
            with self.assertRaises(Denied): self.a.emergency_read(self.t["requester"], "permit-001", handles, 101)

    def test_emergency_approval_expiry_denied(self):
        with self.assertRaises(Denied): self.a.emergency_read(self.t["requester"], "permit-001", self.grants(), 400)

    def test_revoked_emergency_approver_denied(self):
        grants = self.grants()
        self.a.revoked.add("operations")
        with self.assertRaises(Denied): self.a.emergency_read(self.t["requester"], "permit-001", grants, 101)


class AITests(unittest.TestCase):
    def setUp(self):
        self.a, self.t = fixture()
        self.ai = Assistant(self.a)

    def test_summary_filters_citizen_fields(self):
        result = self.ai.execute(self.t["viewer"], "permit-001", "summarize", 100)
        self.assertNotIn("citizen", result)
        self.assertNotIn("address", result)
        self.assertEqual(result["decision_owner"], "human public-service owner")

    def test_cross_record_and_agency_retrieval_denied(self):
        for record in ("permit-002", "registry-001"):
            with self.assertRaises(Denied): self.ai.execute(self.t["viewer"], record, "summarize", 100)

    def test_arbitrary_and_final_decision_tools_denied(self):
        for tool in ("shell", "finalize", "export", "read-all"):
            with self.assertRaises(Denied): self.ai.execute(self.t["reviewer"], "permit-001", tool, 100)

    def test_machine_without_ai_scope_denied(self):
        with self.assertRaises(Denied): self.ai.execute(self.t["machine"], "permit-001", "summarize", 100)

    def test_reviewer_ack_allowed_viewer_denied(self):
        self.assertEqual(self.ai.execute(self.t["reviewer"], "permit-001", "acknowledge", 100)["effect"], "local-review-marker")
        with self.assertRaises(Denied): self.ai.execute(self.t["viewer"], "permit-001", "acknowledge", 100)

    def test_admitted_tool_subset_still_restricts_router(self):
        restricted = Assistant(self.a, ("summarize",))
        with self.assertRaises(Denied): restricted.execute(self.t["reviewer"], "permit-001", "acknowledge", 100)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.a, self.t = fixture()
        self.a.principals["reviewer"] = replace(self.a.principals["reviewer"],
            permissions=self.a.principals["reviewer"].permissions | {"evidence.export"})
        self.exporter = Exporter()
        self.events = [{"type": "denied", "time": 100, "site": "north",
                        "classification": "operational-synthetic", "citizen": "Synthetic Person A",
                        "record": "permit-001", "free_text": "synthetic detail"}]

    def export(self, **changes):
        params = {"events": self.events, "recipient": "agency-csoc", "purpose": "incident-review",
                  "batch_id": "batch-1", "now": 100}
        params.update(changes)
        return self.exporter.export(self.a, self.t["reviewer"], **params)

    def test_freshness_states_and_exact_boundary(self):
        self.assertEqual(freshness(None, 100), "missing")
        self.assertEqual(freshness({"verified": False, "observed_at": 100}, 100), "unverified")
        self.assertEqual(freshness({"verified": True, "observed_at": 100}, 160), "current")
        self.assertEqual(freshness({"verified": True, "observed_at": 100}, 161), "delayed")

    def test_future_and_nonfinite_evidence_unverified(self):
        for report in ({"verified": True, "observed_at": 101},
                       {"verified": True, "observed_at": float("nan")}):
            self.assertEqual(freshness(report, 100), "unverified")

    def test_placement_matches_are_not_assurance(self):
        self.assertEqual(placement({"backup": "north"}, None)["state"], "unverified")
        self.assertEqual(placement({"backup": "north"}, {"backup": "south"})["state"], "conflict")
        self.assertEqual(placement({"backup": "north"}, {"backup": "north"})["state"], "matching-claims")

    def test_export_filters_fields_and_records_custody(self):
        result = self.export()
        self.assertEqual(set(result["events"][0]), {"type", "time", "site"})
        self.assertEqual(result["custody"]["recipient"], "agency-csoc")
        self.assertEqual(len(result["custody"]["sha256"]), 64)

    def test_export_wrong_recipient_and_purpose_denied(self):
        for changes in ({"recipient": "public"}, {"purpose": "model-training"}):
            with self.assertRaises(Denied): self.export(**changes)

    def test_export_replay_denied(self):
        self.export()
        with self.assertRaises(Denied): self.export()

    def test_export_other_site_and_classification_denied(self):
        for field, value in (("site", "south"), ("classification", "restricted-synthetic")):
            events = copy.deepcopy(self.events); events[0][field] = value
            with self.assertRaises(Denied): self.export(events=events)

    def test_export_missing_authority_denied(self):
        with self.assertRaises(Denied):
            self.exporter.export(self.a, self.t["viewer"], self.events, "agency-csoc", "incident-review", "b", 100)

    def test_export_invalid_time_and_backlog_limit_denied(self):
        events = copy.deepcopy(self.events); events[0]["time"] = float("nan")
        with self.assertRaises(Denied): self.export(events=events)
        with self.assertRaises(Denied): self.export(events=self.events * 101)

    def test_denial_and_emergency_rules(self):
        self.assertEqual(detect([{"type": "denied", "time": 100}] * 3, 100), ["repeated-denial"])
        self.assertEqual(detect([{"type": "emergency-read", "time": 100}], 100), ["emergency-review"])

    def test_old_future_and_unknown_events_have_no_rule_alert(self):
        events = [{"type": "denied", "time": 1}] * 3 + [{"type": "emergency-read", "time": 101}]
        self.assertEqual(detect(events, 100), [])
        self.assertEqual(detect([{"type": "unknown-import-pattern", "time": 100}], 100), [])


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.a, self.t = fixture()

    def request(self, service, path, name=None, method="GET"):
        headers = {} if name is None else {"Authorization": "Bearer " + self.t[name]}
        request = urllib.request.Request(service.url + path, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)

    def test_live_api_scoped_read_and_cross_record_denial(self):
        with LocalService(self.a) as service:
            self.assertEqual(service.server.server_address[0], "127.0.0.1")
            self.assertEqual(self.request(service, "/records/permit-001", "reviewer")[0], 200)
            self.assertEqual(self.request(service, "/records/permit-002", "reviewer")[0], 403)

    def test_live_api_cross_agency_and_missing_session(self):
        with LocalService(self.a) as service:
            self.assertEqual(self.request(service, "/records/registry-001", "reviewer")[0], 403)
            self.assertEqual(self.request(service, "/records/permit-001")[0], 401)

    def test_live_api_action_scope_and_offline_finalization(self):
        with LocalService(self.a) as service:
            self.assertEqual(self.request(service, "/records/permit-001/acknowledge", "reviewer", "POST")[0], 200)
            self.assertEqual(self.request(service, "/records/permit-001/acknowledge", "viewer", "POST")[0], 403)
            self.assertEqual(self.request(service, "/records/permit-001/finalize", "finalizer", "POST")[0], 403)

    def test_live_api_unknown_endpoints(self):
        with LocalService(self.a) as service:
            self.assertEqual(self.request(service, "/records/permit-001/delete", "reviewer", "POST")[0], 404)
            self.assertEqual(self.request(service, "/records/permit-001/finalize", "reviewer")[0], 404)


class RegisterTests(unittest.TestCase):
    def test_complete_register_passes(self):
        self.assertEqual(validate(json.loads((ROOT / "examples/government-register.json").read_text())), [])

    def test_unowned_unclassified_flow_fails(self):
        issues = validate(json.loads((ROOT / "examples/negative/unowned-flow.json").read_text()))
        self.assertIn("flow: missing classification", issues)
        self.assertIn("flow: unresolved owner", issues)

    def test_duplicate_mission_and_conflicting_authority_fail(self):
        register = json.loads((ROOT / "examples/government-register.json").read_text())
        register["missions"][1]["id"] = register["missions"][0]["id"]
        register["missions"][0]["stopped_actions"] += ["scoped-read"]
        issues = validate(register)
        self.assertIn("mission IDs must be distinct", issues)
        self.assertTrue(any("conflicting action authority" in issue for issue in issues))

    def test_unknown_failure_owner_fails(self):
        register = json.loads((ROOT / "examples/government-register.json").read_text())
        register["missions"][0]["failure_decision_owner"] = "unknown"
        self.assertTrue(any("failure_decision_owner" in issue for issue in validate(register)))

    def test_malformed_missions_and_flows_report_issues(self):
        register = json.loads((ROOT / "examples/government-register.json").read_text())
        register["missions"][0]["id"] = []
        register["missions"][0]["permitted_actions"] = [None]
        register["flows"] = [None]
        self.assertIn("flow must be an object", validate(register))


class ReferenceAndModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock, cls.modules = load_reference(REFERENCE)

    def setUp(self):
        crypto, admission = self.modules["crypto"], self.modules["admission"]
        self.c = crypto
        self.release, self.security, self.operations, self.policy = crypto.demo_signers()
        self.gate = admission.Admission({self.release.key_id: self.release.public}, self.policy, site="north")
        self.store = ModelStore(self.gate)

    def candidate(self, version=1, site="north", kind="model-data", tools=("summarize",)):
        data = self.c.canonical({"schema": "government-router-data-v1", "site": site,
                                  "tools": list(tools), "description": "synthetic router configuration"})
        return self.modules["admission"].bundle(data, self.release, "router-" + str(version),
                                                  version, site=site, kind=kind)

    def approvals(self, candidate):
        return [self.c.approve(s, "admit-release", self.c.canonical(candidate["manifest"]))
                for s in (self.security, self.operations)]

    def test_exact_reference_hashes_match(self):
        self.assertEqual(len(check_reference(REFERENCE)["source_manifest"]), 52)

    def test_missing_reference_fails_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError): check_reference(directory)

    def test_signed_router_data_is_admitted(self):
        candidate = self.candidate()
        self.assertEqual(self.store.admit(candidate, self.approvals(candidate))["tools"], ("summarize",))

    def test_application_cannot_be_admitted_as_model(self):
        candidate = self.candidate(kind="application")
        with self.assertRaises(Denied): self.store.admit(candidate, self.approvals(candidate))

    def test_other_site_router_denied(self):
        candidate = self.candidate(site="south")
        with self.assertRaises(Denied): self.store.admit(candidate, self.approvals(candidate))

    def test_signed_unsafe_tool_configuration_denied(self):
        candidate = self.candidate(tools=("shell",))
        with self.assertRaises(Denied): self.store.admit(candidate, self.approvals(candidate))

    def test_model_data_alteration_and_missing_approvals_denied(self):
        candidate = self.candidate()
        with self.assertRaises(Denied): self.store.admit(candidate, [])
        candidate["payload"] = self.c.b64(self.c.canonical({
            "schema": "government-router-data-v1", "site": "north", "tools": ["summarize"],
            "description": "altered after signing"}))
        with self.assertRaises(Denied): self.store.admit(candidate, self.approvals(candidate))

    def test_model_replay_and_downgrade_denied(self):
        second = self.candidate(version=2)
        self.store.admit(second, self.approvals(second))
        first = self.candidate(version=1)
        with self.assertRaises(Denied): self.store.admit(first, self.approvals(first))
        with self.assertRaises(Denied): self.store.admit(second, self.approvals(second))
