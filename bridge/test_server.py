import importlib.util
import json
import unittest
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
from http.server import ThreadingHTTPServer

MODULE = Path(__file__).with_name("server.py")
spec = importlib.util.spec_from_file_location("aiwcc_bridge", MODULE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class BridgeTests(unittest.TestCase):
    def test_snapshot_has_expected_read_only_sections(self):
        data = bridge.snapshot()
        self.assertTrue(data["bridge"]["connected"])
        self.assertIn("hostname", data["host"])
        self.assertIn("installed", data["opencode"])
        self.assertIn("configured_mcp_servers", data["opencode"])

    def test_telemetry_endpoint_accepts_allowlisted_events(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), bridge.Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            body = json.dumps({"type": "session.execution.started", "created": 123}).encode("utf-8")
            request = __import__("urllib.request", fromlist=["Request"]).Request(
                f"http://127.0.0.1:{server.server_port}/api/telemetry",
                data=body, headers={"Content-Type": "application/json"}, method="POST"
            )
            with urlopen(request, timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertTrue(payload["accepted"])
            self.assertEqual(bridge.EVENTS[0]["title"], "Agent execution started")
            ready = json.dumps({"type": "aiwcc.plugin.ready", "created": 124}).encode("utf-8")
            ready_request = __import__("urllib.request", fromlist=["Request"]).Request(
                f"http://127.0.0.1:{server.server_port}/api/telemetry",
                data=ready, headers={"Content-Type": "application/json"}, method="POST"
            )
            with urlopen(ready_request, timeout=2) as response:
                ready_payload = json.loads(response.read().decode("utf-8"))
            self.assertTrue(ready_payload["accepted"])
            self.assertEqual(bridge.EVENTS[0]["title"], "OpenCode telemetry connected")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_health_endpoint(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), bridge.Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/api/health", timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["service"], "aiwcc-bridge")
            with urlopen(f"http://127.0.0.1:{server.server_port}/api/status", timeout=3) as response:
                status = json.loads(response.read().decode("utf-8"))
            self.assertIn("host", status)
            self.assertIn("opencode", status)
            try:
                urlopen(f"http://127.0.0.1:{server.server_port}/bridge/server.py", timeout=2)
                self.fail("Bridge source must not be served")
            except Exception as error:
                self.assertTrue(getattr(error, "code", None) == 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

if __name__ == "__main__":
    unittest.main()
