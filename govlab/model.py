"""Admission of signed deterministic-router data; no model weights are evaluated."""
import base64
import json
from .policy import Denied


class ModelStore:
    def __init__(self, gate):
        self.gate = gate
        self.active = None

    def admit(self, candidate, approvals):
        try:
            if candidate["manifest"]["kind"] != "model-data":
                raise Denied("application bundle cannot become router data")
            raw = base64.b64decode(candidate["payload"], validate=True)
            if len(raw) > 65536:
                raise Denied("router data too large")
            data = json.loads(raw)
            if (not isinstance(data, dict)
                    or set(data) != {"schema", "site", "tools", "description"}
                    or data["schema"] != "government-router-data-v1"
                    or data["site"] != self.gate.site
                    or not isinstance(data["description"], str)
                    or not isinstance(data["tools"], list) or not data["tools"]
                    or any(type(tool) is not str for tool in data["tools"])
                    or len(set(data["tools"])) != len(data["tools"])
                    or not set(data["tools"]) <= {"summarize", "acknowledge"}):
                raise Denied("router data scope, schema or tool permissions denied")
            accepted = self.gate.inspect(candidate, approvals)
        except (KeyError, TypeError, ValueError) as error:
            raise Denied(str(error)) from error
        self.active = {"version": accepted.version, "sha256": accepted.sha256,
                       "site": accepted.site, "tools": tuple(data["tools"])}
        return dict(self.active)
