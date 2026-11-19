"""Loopback-only HTTP adapter for trusted fixture sessions, not production login."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
from urllib.parse import unquote

from .policy import Denied


class LocalService:
    def __init__(self, authority, now=100):
        self.authority, self.now = authority, now
        outer = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def reply(self, status, value):
                body = json.dumps(value, allow_nan=False).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                self.dispatch("read")

            def do_POST(self):
                self.dispatch("acknowledge" if self.path.endswith("/acknowledge") else "finalize")

            def dispatch(self, action):
                path = self.path.split("/")
                if (len(path) not in (3, 4) or path[1] != "records" or not path[2]
                        or (len(path) == 4 and path[3] not in {"acknowledge", "finalize"})
                        or (self.command == "GET" and len(path) != 3)
                        or (self.command == "POST" and len(path) != 4)):
                    self.reply(404, {"error": "unknown endpoint"})
                    return
                authorization = self.headers.get("Authorization", "")
                if not authorization.startswith("Bearer "):
                    self.reply(401, {"error": "fixture session required"})
                    return
                try:
                    result = getattr(outer.authority, action)(
                        authorization[7:], unquote(path[2]), outer.now)
                except Denied:
                    self.reply(403, {"error": "denied"})
                    return
                self.reply(200, result)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server.server_port}"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
