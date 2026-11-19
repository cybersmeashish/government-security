"""Freshness, placement claims and a bounded disclosure policy."""
import hashlib
import json

from .policy import Denied, valid_time


def freshness(report, now):
    if report is None:
        return "missing"
    if (not report.get("verified") or not valid_time(now)
            or not valid_time(report.get("observed_at")) or report["observed_at"] > now):
        return "unverified"
    return "current" if now - report["observed_at"] <= 60 else "delayed"


def placement(declared, observed):
    if not observed:
        return {"state": "unverified", "reason": "no observed claims"}
    if declared != observed:
        return {"state": "conflict", "reason": "observed claims differ"}
    return {"state": "matching-claims", "reason": "independent location assurance still required"}


def detect(events, now):
    """Two illustrative rules over a bounded recent window, not comprehensive detection."""
    valid = [event for event in events if valid_time(event.get("time")) and valid_time(now)
             and 0 <= now - event["time"] <= 60]
    alerts = []
    if sum(event.get("type") == "denied" for event in valid) >= 3:
        alerts.append("repeated-denial")
    if any(event.get("type") == "emergency-read" for event in valid):
        alerts.append("emergency-review")
    return alerts


class Exporter:
    FIELDS = {"type", "time", "site"}
    def __init__(self):
        self.recipients = {"agency-csoc": {"purpose": "incident-review", "site": "north"}}
        self.seen = set()

    def export(self, authority, token, events, recipient, purpose, batch_id, now):
        principal = authority.principal(token, now)
        policy = self.recipients.get(recipient)
        if ("evidence.export" not in principal.permissions or policy is None
                or policy["purpose"] != purpose or policy["site"] != principal.site
                or not isinstance(batch_id, str) or not batch_id or batch_id in self.seen):
            raise Denied("recipient, purpose, authority or replay denied")
        if (not isinstance(events, list) or len(events) > 100
                or any(not isinstance(event, dict) or event.get("site") != principal.site
                       or event.get("classification") != "operational-synthetic"
                       or not valid_time(event.get("time"))
                       or event.get("type") not in {"allowed", "denied", "emergency-read"}
                       for event in events)):
            raise Denied("evidence size, schema, site or classification denied")
        filtered = [{key: value for key, value in event.items() if key in self.FIELDS}
                    for event in events]
        try:
            raw = json.dumps(filtered, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        except (ValueError, TypeError) as error:
            raise Denied("invalid evidence encoding") from error
        self.seen.add(batch_id)
        return {"events": filtered, "custody": {
            "batch_id": batch_id, "recipient": recipient, "purpose": purpose,
            "exporter": principal.subject, "sha256": hashlib.sha256(raw).hexdigest(),
            "scope": "local custody record; not a signed recipient receipt",
        }}
