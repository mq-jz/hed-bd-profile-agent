#!/usr/bin/env python3
"""Demo server for the BD Profile "Live" walkthrough (zero third-party deps).

A tiny stdlib HTTP server whose only job is to serve `ui/live.html` - the
scripted Teams-to-dashboard-to-Teams replay - together with its locally vendored
JS libs, and to stream the newest compiled deliverable when the demo's closing
file cards are clicked.

Run:
    python ui/server.py            # serves http://127.0.0.1:8765/live
    python ui/server.py --port 9000

This is demo-only. The Kanban board and its build API were removed - the
pipeline is driven from the CLI stages and Claude sub-agents, not a UI.
"""
import argparse
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = Path(__file__).resolve().parent


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):           # quiet default access logging
        pass

    def _send(self, code, payload, ctype="application/json"):
        import json
        if ctype == "application/json":
            data = json.dumps(payload).encode()
        else:
            data = payload if isinstance(payload, bytes) else payload.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_deliverable(self, kind="docx", match=None):
        """Stream the newest compiled deliverable (.docx / .pptx), or the
        review-gate first draft (kind=draft), for the demo's file cards.

        `match` pins the demo to one institution's artifacts: without it the
        newest file wins, and a later run for a different college silently
        changes what the demo's file cards download."""
        if kind == "draft":
            fp = ROOT / "02-assemble" / "output" / "profile-draft.md"
            if match:
                token = match.lower()
                if not (fp.exists() and token.replace("-", " ").replace("_", " ")
                        in fp.read_text()[:200].lower()):
                    archived = sorted(ROOT.glob(f"archive/*{token}*/profile-draft.md"))
                    if archived:
                        fp = archived[-1]
            if not fp.exists():
                return self._send(404, {"error": "no assembled draft yet"})
            data = fp.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition",
                             f'attachment; filename="{fp.name}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        ctypes = {
            "docx": "application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument"
                    ".presentationml.presentation",
        }
        if kind not in ctypes:
            return self._send(400, {"error": "kind must be docx|pptx|draft"})
        out_dir = ROOT / "03-compile" / "output"
        by_time = lambda paths: sorted(paths, key=lambda p: p.stat().st_mtime)
        if match:
            # Prefix beats substring: match=BD_Profile_Union_College must not pick
            # up Short_BD_Profile_Union_College_... just because it is newer.
            docs = (by_time(out_dir.glob(f"{match}*.{kind}"))
                    or by_time(out_dir.glob(f"*{match}*.{kind}"))
                    or by_time(out_dir.glob(f"*.{kind}")))  # never 404 mid-demo
        else:
            docs = by_time(out_dir.glob(f"*.{kind}"))
        if not docs:
            return self._send(404, {"error": f"no compiled .{kind} yet"})
        fp = docs[-1]
        data = fp.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctypes[kind])
        self.send_header("Content-Disposition", f'attachment; filename="{fp.name}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    VENDOR_CTYPES = {
        ".js": "application/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".woff2": "font/woff2",
        ".svg": "image/svg+xml; charset=utf-8",
    }

    def _serve_vendor(self, path):
        """Serve the locally vendored assets for the demo (no CDN): JS libs, the
        Hanken Grotesk woff2, and the M&Q logo svg."""
        vendor_dir = (UI_DIR / "vendor").resolve()
        fp = (vendor_dir / path[len("/vendor/"):]).resolve()
        if not str(fp).startswith(str(vendor_dir) + os.sep) or not fp.is_file():
            return self._send(404, {"error": "not found"})
        ctype = self.VENDOR_CTYPES.get(fp.suffix.lower(),
                                       "application/octet-stream")
        return self._send(200, fp.read_bytes(), ctype)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/live", "/live.html"):
            html = (UI_DIR / "live.html").read_text()
            return self._send(200, html, "text/html; charset=utf-8")
        if path.startswith("/vendor/"):
            return self._serve_vendor(path)
        if path == "/api/deliverable":
            qs = parse_qs(urlparse(self.path).query)
            return self._serve_deliverable(kind=(qs.get("kind") or ["docx"])[0],
                                           match=(qs.get("match") or [None])[0])
        return self._send(404, {"error": "not found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8765)))
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"BD Profile demo -> http://{args.host}:{args.port}/live  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
