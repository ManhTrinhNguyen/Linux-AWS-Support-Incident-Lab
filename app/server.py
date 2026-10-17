import errno
import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DATA = Path(os.environ.get("DATA_DIR", "/data"))
CONTROL = Path(os.environ.get("CONTROL_DIR", "/control"))

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, request_id):
        payload = json.dumps({**body, "request_id": request_id}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Request-ID", request_id)
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass  # A timed-out proxy may already have closed its connection.
        print(json.dumps({"request_id": request_id, "path": self.path,
                          "status": status}), flush=True)

    def do_GET(self):
        rid = str(uuid.uuid4())
        if self.path == "/health":
            self.reply(200, {"status": "ok"}, rid)
        elif self.path == "/":
            if (CONTROL / "slow").exists():
                time.sleep(5)
            self.reply(200, {"service": "support-incident-lab"}, rid)
        else:
            self.reply(404, {"error": "not_found"}, rid)

    def do_POST(self):
        rid = str(uuid.uuid4())
        if self.path != "/notes":
            self.reply(404, {"error": "not_found"}, rid)
            return
        # No customer data needed: this endpoint only writes a fixed lab marker.
        try:
            with (DATA / "notes.txt").open("a") as out:
                out.write("support lab verification\n")
            self.reply(201, {"status": "saved"}, rid)
        except OSError as exc:
            print(json.dumps({"request_id": rid, "errno": exc.errno,
                              "detail": str(exc)}), flush=True)
            code = "storage_full" if exc.errno == errno.ENOSPC else "write_failed"
            self.reply(500, {"error": code}, rid)

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8000"))), Handler).serve_forever()
