#!/usr/bin/env python3
"""BD Profile build service - the callable backend for any front door.

A tiny stdlib HTTP service (zero third-party deps) that exposes the
"institution in -> dated .docx out" contract asynchronously, because a real run
takes minutes. A Teams bot, an Outlook / Power Automate flow, or a Copilot
Studio custom connector all use the SAME three calls:

  POST /build            {institution, state?, ein?, variant?, origination?, media?}
                         -> 202 {job_id, status:"queued", status_url, ...}
  GET  /build/<job_id>   -> {status, steps, matched, docx_url?, verify_count, ...}
  GET  /build/<job_id>/docx  -> streams the .docx (attachment) when done

Plus GET /health. Builds run one at a time (they mutate the shared workspace);
extra requests queue. See api/CONTRACT.md for the field-level contract.

Run:
  python api/service.py                 # http://127.0.0.1:8781
  python api/service.py --port 9001 --host 0.0.0.0
"""
import argparse
import json
import os
import re
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
import build_profile as bp  # noqa: E402

JOBS = {}
JOBS_LOCK = threading.Lock()
BUILD_LOCK = threading.Lock()   # serialize builds (shared workspace)
VALID_VARIANTS = {"full", "short", "former_client"}
# Optional shared secret. When BD_API_KEY is set, every call except /health must
# send it as `Authorization: Bearer <key>` (or an `x-api-key` header). Set it
# before exposing the service publicly (tunnel / Azure) so it isn't open.
API_KEY = os.environ.get("BD_API_KEY", "").strip()


def _new_job(body):
    jid = uuid.uuid4().hex[:12]
    job = {
        "job_id": jid, "status": "queued", "institution": body.get("institution"),
        "variant": body.get("variant", "full"), "steps": [], "matched": None,
        "candidates": [], "warnings": [], "verify_count": None, "sections": None,
        "docx": None, "error": None,
    }
    with JOBS_LOCK:
        JOBS[jid] = job
    return job


def _worker(jid, body):
    job = JOBS[jid]

    def progress(name, status, detail=""):
        with JOBS_LOCK:
            steps = [s for s in job["steps"] if s["step"] != name]
            steps.append({"step": name, "status": status, "detail": detail})
            job["steps"] = steps

    with BUILD_LOCK:                       # one build at a time
        with JOBS_LOCK:
            job["status"] = "running"
        try:
            res = bp.build_profile(
                body["institution"], state=body.get("state"), ein=body.get("ein"),
                variant=body.get("variant", "full"), media=bool(body.get("media", True)),
                origination=body.get("origination"),
                warm_fetches=bool(body.get("warm_fetches", True)),
                research_cmd=body.get("research_cmd"), progress=progress,
            )
            with JOBS_LOCK:
                job.update({
                    "matched": res.get("matched"), "candidates": res.get("candidates", []),
                    "warnings": res.get("warnings", []), "sections": res.get("sections"),
                    "verify_count": res.get("verify_count"), "docx": res.get("docx"),
                    "elapsed_sec": res.get("elapsed_sec"),
                })
                if res.get("error"):
                    job["status"], job["error"] = "error", res["error"]
                elif res.get("docx"):
                    job["status"] = "done"
                else:
                    job["status"], job["error"] = "error", "no document produced"
        except Exception as e:                       # never leave a job stuck
            with JOBS_LOCK:
                job["status"], job["error"] = "error", f"{type(e).__name__}: {e}"


def _public(job, base):
    out = {k: job[k] for k in
           ("job_id", "status", "institution", "variant", "steps", "matched",
            "candidates", "warnings", "verify_count", "sections", "error")}
    out["elapsed_sec"] = job.get("elapsed_sec")
    if job["status"] == "done" and job.get("docx"):
        out["docx_url"] = f"{base}/build/{job['job_id']}/docx"
        out["docx_filename"] = Path(job["docx"]).name
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):  # quiet
        pass

    def _json(self, code, payload):
        data = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _base(self):
        host = self.headers.get("Host") or f"127.0.0.1:{self.server.server_address[1]}"
        proto = self.headers.get("X-Forwarded-Proto") or "http"
        return f"{proto}://{host}"

    def _authorized(self):
        if not API_KEY:
            return True
        auth = (self.headers.get("Authorization") or "").strip()
        if auth.lower().startswith("bearer "):
            auth = auth[7:].strip()
        return auth == API_KEY or (self.headers.get("x-api-key") or "").strip() == API_KEY

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self._json(200, {"ok": True, "service": "bd-profile-build"})
        if not self._authorized():
            return self._json(401, {"error": "unauthorized"})
        m = re.fullmatch(r"/build/([a-f0-9]{12})", path)
        if m:
            with JOBS_LOCK:
                job = JOBS.get(m.group(1))
            if not job:
                return self._json(404, {"error": "unknown job_id"})
            return self._json(200, _public(job, self._base()))
        m = re.fullmatch(r"/build/([a-f0-9]{12})/docx", path)
        if m:
            with JOBS_LOCK:
                job = JOBS.get(m.group(1))
            if not job:
                return self._json(404, {"error": "unknown job_id"})
            if job["status"] != "done" or not job.get("docx") or not Path(job["docx"]).exists():
                return self._json(409, {"error": f"not ready (status={job['status']})"})
            data = Path(job["docx"]).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type",
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            self.send_header("Content-Disposition",
                             f'attachment; filename="{Path(job["docx"]).name}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return self._json(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/build":
            return self._json(404, {"error": "not found"})
        if not self._authorized():
            return self._json(401, {"error": "unauthorized"})
        length = int(self.headers.get("Content-Length", 0) or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._json(400, {"error": "invalid JSON body"})
        if not (body.get("institution") or "").strip():
            return self._json(400, {"error": "institution is required"})
        if body.get("variant", "full") not in VALID_VARIANTS:
            return self._json(400, {"error": f"variant must be one of {sorted(VALID_VARIANTS)}"})
        job = _new_job(body)
        threading.Thread(target=_worker, args=(job["job_id"], body), daemon=True).start()
        payload = _public(job, self._base())
        payload["status_url"] = f"{self._base()}/build/{job['job_id']}"
        return self._json(202, payload)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8781)))
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"BD Profile build service -> http://{args.host}:{args.port}  (POST /build)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
