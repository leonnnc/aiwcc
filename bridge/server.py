#!/usr/bin/env python3
"""AIWCC local read-only bridge. Binds only to loopback; never executes user tasks."""
from __future__ import annotations
import json, os, platform, shutil, subprocess, time
from collections import deque
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home()
HOST, PORT = "127.0.0.1", int(os.environ.get("AIWCC_PORT", "8765"))
STARTED = time.time()
EVENTS = deque(maxlen=80)
LAST_FINGERPRINT = None

def event(level, title, detail):
    EVENTS.appendleft({"time": datetime.now(timezone.utc).isoformat(), "level": level, "title": title, "detail": detail})

def run_readonly(args, timeout=2):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return p.stdout.strip() if p.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""

def opencode_info():
    binary = shutil.which("opencode")
    if not binary:
        candidate = HOME / ".opencode/bin/opencode"
        binary = str(candidate) if candidate.is_file() and os.access(candidate, os.X_OK) else None
    version = run_readonly([binary, "--version"]) if binary else ""
    cfg_path = HOME / ".config/opencode/opencode.json"
    model, mcp_count = None, 0
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        model = cfg.get("model")
        mcp = cfg.get("mcp", {})
        mcp_count = len(mcp) if isinstance(mcp, dict) else 0
    except (OSError, json.JSONDecodeError):
        pass
    running = False
    proc = Path("/proc")
    try:
        for entry in proc.iterdir():
            if entry.name.isdigit():
                try:
                    cmd = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore")
                    if "opencode" in cmd and "aiwcc" not in cmd:
                        running = True
                        break
                except OSError:
                    continue
    except OSError:
        pass
    return {"installed": bool(binary), "version": version or None, "running": running,
            "configured_model": model, "configured_mcp_servers": mcp_count}

def snapshot():
    info = opencode_info()
    data = {"bridge": {"connected": True, "version": "0.1.0", "uptime_seconds": int(time.time()-STARTED)},
            "host": {"hostname": platform.node(), "system": platform.system(), "release": platform.release(),
                     "machine": platform.machine()},
            "opencode": info, "timestamp": datetime.now(timezone.utc).isoformat()}
    return data

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        print("[AIWCC] " + (fmt % args))

    def translate_path(self, path):
        requested = urlparse(path).path
        if requested in ("/", "/index.html"):
            return str(ROOT / "index.html")
        return str(ROOT / "__aiwcc_not_found__")

    def end_headers(self):
        origin = self.headers.get("Origin", "")
        if origin.startswith("http://127.0.0.1:") or origin.startswith("http://localhost:"):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def do_GET(self):
        request_host = self.headers.get("Host", "").split(":")[0].strip("[]").lower()
        if request_host not in ("127.0.0.1", "localhost"):
            self.send_error(403, "Localhost requests only")
            return
        path = urlparse(self.path).path
        if path == "/api/health":
            return self.send_json({"ok": True, "service": "aiwcc-bridge", "version": "0.1.0"})
        if path == "/api/status":
            global LAST_FINGERPRINT
            data = snapshot()
            fingerprint = json.dumps(data["opencode"], sort_keys=True)
            if LAST_FINGERPRINT is None:
                event("info", "Bridge connected", "AIWCC local bridge started in read-only mode.")
            elif fingerprint != LAST_FINGERPRINT:
                event("info", "Runtime status changed", "OpenCode or its configuration changed.")
            LAST_FINGERPRINT = fingerprint
            data["events"] = list(EVENTS)
            return self.send_json(data)
        if path == "/api/events":
            return self.send_json({"events": list(EVENTS)})
        return super().do_GET()

    def send_json(self, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def main():
    event("info", "Bridge initialized", "Read-only local monitoring enabled.")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"AIWCC Bridge listening at http://{HOST}:{PORT}")
    print("Read-only monitoring only. No shell command or workflow execution endpoint is exposed.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AIWCC Bridge...")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
