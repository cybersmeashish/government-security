"""Local government authority, scoped records, and accountable AI tool routing."""
import copy
from dataclasses import dataclass
import math
import secrets


class Denied(ValueError):
    pass


def valid_time(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


@dataclass(frozen=True)
class Principal:
    subject: str
    agency: str
    site: str
    kind: str
    permissions: frozenset
    records: frozenset
    expires: float
    duty: str = ""


class Authority:
    """Trusted server-side identities; client tokens cannot assign their own scope."""
    def __init__(self, records, principals, site="north"):
        self.site = site
        self.records = copy.deepcopy(records)
        self.principals = dict(principals)
        self.revoked, self.tokens = set(), {}
        self.emergency_grants = {}
        self.events, self.acknowledgments = [], []
        self.connected, self.central_age = False, 1200

    def issue(self, subject):
        if subject not in self.principals:
            raise Denied("unknown principal")
        token = secrets.token_urlsafe(32)
        self.tokens[token] = subject
        return token

    def principal(self, token, now):
        subject = self.tokens.get(token)
        principal = self.principals.get(subject)
        if (principal is None or subject in self.revoked or not valid_time(now)
                or not valid_time(principal.expires) or now >= principal.expires
                or principal.site != self.site):
            raise Denied("identity, local revocation, expiry or site denied")
        return principal

    def permit(self, token, record_id, action, now):
        try:
            principal = self.principal(token, now)
            record = self.records.get(record_id)
            if (record is None or record["agency"] != principal.agency
                    or record["site"] != self.site or record_id not in principal.records
                    or action not in principal.permissions):
                raise Denied("agency, object or action denied")
            if action == "finalize" and (
                not self.connected or not valid_time(self.central_age) or self.central_age > 300
            ):
                raise Denied("final public-service determination requires fresh central authority")
        except Denied:
            self.events.append({"type": "denied", "site": self.site, "time": now, "record": record_id,
                                "classification": "operational-synthetic"})
            raise
        self.events.append({"type": "allowed", "site": self.site, "time": now, "record": record_id,
                            "classification": "operational-synthetic"})
        return principal, record

    def read(self, token, record_id, now):
        _, record = self.permit(token, record_id, "read", now)
        return copy.deepcopy(record)

    def acknowledge(self, token, record_id, now):
        principal, _ = self.permit(token, record_id, "acknowledge", now)
        entry = {"record": record_id, "operator": principal.subject,
                 "time": now, "effect": "local-review-marker"}
        self.acknowledgments.append(entry)
        return copy.deepcopy(entry)

    def finalize(self, token, record_id, now):
        self.permit(token, record_id, "finalize", now)
        return {"record": record_id, "effect": "synthetic-finalization-only"}

    def approve_emergency(self, approver, requester, record_id, now):
        principal = self.principal(approver, now)
        requested = self.principal(requester, now)
        record = self.records.get(record_id)
        if (principal.kind != "operator" or "emergency.approve" not in principal.permissions
                or principal.duty not in {"security", "operations"}
                or requested.kind != "operator" or "emergency.request" not in requested.permissions
                or principal.subject == requested.subject or principal.agency != requested.agency
                or record is None or record["agency"] != requested.agency or record["site"] != self.site):
            raise Denied("emergency approval denied")
        handle = secrets.token_urlsafe(32)
        self.emergency_grants[handle] = {
            "approver": approver, "requester": requested.subject, "record": record_id,
            "expires": min(now + 300, principal.expires, requested.expires), "used": False,
        }
        return handle

    def emergency_read(self, requester, record_id, approvals, now):
        principal = self.principal(requester, now)
        record = self.records.get(record_id)
        if (principal.kind != "operator" or "emergency.request" not in principal.permissions
                or record is None or record["agency"] != principal.agency
                or record["site"] != self.site or len(approvals) != 2):
            raise Denied("emergency scope denied")
        grants = [self.emergency_grants.get(handle) for handle in approvals]
        if any(g is None or g["used"] or g["requester"] != principal.subject
               or g["record"] != record_id or now >= g["expires"] for g in grants):
            raise Denied("approval context, expiry or replay denied")
        approvers = [self.principal(grant["approver"], now) for grant in grants]
        if (len({p.subject for p in approvers}) != 2
                or any(p.subject == principal.subject or p.agency != principal.agency
                       or p.kind != "operator" or "emergency.approve" not in p.permissions
                       for p in approvers)
                or {p.duty for p in approvers} != {"security", "operations"}):
            raise Denied("independent local security and operations approvers required")
        for grant in grants:
            grant["used"] = True
        self.events.append({"type": "emergency-read", "site": self.site, "time": now,
                            "record": record_id, "approvers": [p.subject for p in approvers],
                            "classification": "operational-synthetic"})
        return copy.deepcopy(record)


class Assistant:
    """A deterministic tool router, without a learned model or executable prompt."""
    def __init__(self, authority, permitted_tools=("summarize", "acknowledge")):
        self.authority = authority
        self.permitted_tools = frozenset(permitted_tools) & {"summarize", "acknowledge"}

    def execute(self, token, record_id, tool, now):
        if tool not in self.permitted_tools:
            raise Denied("tool not permitted")
        principal = self.authority.principal(token, now)
        if "ai.use" not in principal.permissions:
            raise Denied("AI use denied")
        if tool == "acknowledge":
            return self.authority.acknowledge(token, record_id, now)
        record = self.authority.read(token, record_id, now)
        return {"service": record["service"], "status": record["status"],
                "decision_owner": "human public-service owner",
                "model": "deterministic-fixture"}


def fixture():
    records = {
        "permit-001": {"agency": "civic", "site": "north", "service": "permit-review",
                       "status": "pending", "classification": "restricted-synthetic",
                       "citizen": "Synthetic Person A", "address": "Fictional Address A"},
        "permit-002": {"agency": "civic", "site": "north", "service": "permit-review",
                       "status": "pending", "classification": "restricted-synthetic",
                       "citizen": "Synthetic Person B", "address": "Fictional Address B"},
        "registry-001": {"agency": "registry", "site": "north", "service": "registry-review",
                         "status": "pending", "classification": "restricted-synthetic",
                         "citizen": "Synthetic Person C", "address": "Fictional Address C"},
    }
    def principal(name, agency="civic", site="north", kind="operator",
                  permissions=("read",), scope=("permit-001",), expires=1000, duty=""):
        return Principal(name, agency, site, kind, frozenset(permissions),
                         frozenset(scope), expires, duty)
    people = {
        "reviewer": principal("reviewer", permissions=("read", "acknowledge", "ai.use")),
        "viewer": principal("viewer", permissions=("read", "ai.use")),
        "finalizer": principal("finalizer", permissions=("read", "finalize")),
        "registry": principal("registry", agency="registry", scope=("registry-001",)),
        "remote": principal("remote", site="south"),
        "expired": principal("expired", expires=100),
        "machine": principal("machine", kind="service"),
        "requester": principal("requester", permissions=("emergency.request",), scope=()),
        "security": principal("security", permissions=("emergency.approve",), duty="security"),
        "operations": principal("operations", permissions=("emergency.approve",), duty="operations"),
    }
    authority = Authority(records, people)
    return authority, {name: authority.issue(name) for name in people}
