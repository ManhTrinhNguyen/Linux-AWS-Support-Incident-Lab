"""Real HTTP integration tests; no Docker or third-party dependencies required."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("server", Path(__file__).parents[1] / "app/server.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        app.DATA = Path(cls.temp.name)
        app.CONTROL = app.DATA
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def request(self, path, method="GET"):
        req = urllib.request.Request(self.base + path, method=method)
        try:
            response = urllib.request.urlopen(req, timeout=8)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.code, json.load(response)

    def test_health_and_unknown_route(self):
        status, body = self.request("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertTrue(body["request_id"])
        self.assertEqual(self.request("/missing")[0], 404)

    def test_write_and_unknown_post(self):
        self.assertEqual(self.request("/notes", "POST")[0], 201)
        self.assertIn("support lab", (app.DATA / "notes.txt").read_text())
        self.assertEqual(self.request("/missing", "POST")[0], 404)

    def test_permission_failure(self):
        with patch.object(Path, "open", side_effect=PermissionError(13, "Permission denied")):
            status, body = self.request("/notes", "POST")
        self.assertEqual((status, body["error"]), (500, "write_failed"))

    def test_full_storage(self):
        with patch.object(Path, "open", side_effect=OSError(28, "No space left on device")):
            status, body = self.request("/notes", "POST")
        self.assertEqual((status, body["error"]), (500, "storage_full"))

    def test_slow_request_leaves_health_available(self):
        (app.CONTROL / "slow").touch()
        try:
            with patch.object(app.time, "sleep") as pause:
                self.assertEqual(self.request("/")[0], 200)
                pause.assert_called_once_with(5)
                self.assertEqual(self.request("/health")[0], 200)
        finally:
            (app.CONTROL / "slow").unlink()

if __name__ == "__main__":
    unittest.main()
