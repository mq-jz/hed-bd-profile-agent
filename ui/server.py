#!/usr/bin/env python3
"""Kanban UI server for the BD Profile pipeline (zero third-party deps).

A small stdlib HTTP server that reads the workspace filesystem to place each
pipeline step on a kanban board (To Do / In Progress / Review / Done) and runs
the MECHANICAL steps (warm fetches, assemble, compile) as real subprocesses when
you click their button. The AGENT steps (intake and the five research flows) are
driven by Claude sub-agents, not scripts, so the board shows their status and the
command to run them, but cannot launch them itself.

Run:
    python ui/server.py            # serves http://127.0.0.1:8765
    python ui/server.py --port 9000

State is derived live from the same output files the CLI stages write, so the
board never drifts from the pipeline - there is no separate database.
"""
import argparse
import json
import os
import re
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = Path(__file__).resolve().parent
LOG_DIR = UI_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
REVIEW_MARKER = ROOT / "02-assemble" / "output" / ".review-approved"
HEADSHOTS_FILE = ROOT / "02-assemble" / "output" / ".headshots.json"
DRAFT_FILE = ROOT / "02-assemble" / "output" / "profile-draft.md"
_SUBHEAD_RE = re.compile(r"^#{3}\s+(.+?)\s*$")
_PHOTO_RE = re.compile(r"^Photo:\s*(.+?)\s*$", re.IGNORECASE)

RESEARCH_FLOWS = [
    ("institutional-profile", "Institutional Profile"),
    ("financials", "Financials"),
    ("federal-funding", "Federal Funding"),
    ("leadership", "Leadership"),
    ("strategy-news", "Strategy & News"),
]

# Pipeline steps in board order. kind: "agent" (Claude sub-agent, status-only),
# "script" (runnable subprocess), "manual" (a human gate toggled in the UI).
STEPS = [
    {"id": "intake", "title": "Intake", "kind": "agent", "owner": "00-intake",
     "deps": [],
     "hint": "Ask Claude: \"run 00-intake for <institution>\"."},
    {"id": "fetches", "title": "Warm raw fetches", "kind": "script",
     "owner": "scripts", "deps": ["intake"],
     "hint": "Runs run_research_fetches.sh (Scorecard, ProPublica, USASpending, Congress)."},
    *[
        {"id": fid, "title": f"Research: {label}", "kind": "agent",
         "owner": f"research/{fid}", "deps": ["fetches"],
         "hint": f"Ask Claude: \"run research/{fid}\"."}
        for fid, label in RESEARCH_FLOWS
    ],
    {"id": "assemble", "title": "Assemble draft", "kind": "script",
     "owner": "02-assemble", "deps": [fid for fid, _ in RESEARCH_FLOWS],
     "hint": "Runs draft.py -> profile-draft.md (overwrites manual edits)."},
    {"id": "review", "title": "Partner review", "kind": "manual",
     "owner": "02-assemble", "deps": ["assemble"],
     "hint": "Edit profile-draft.md, then mark approved to unlock compile."},
    {"id": "headshots", "title": "Headshot approval", "kind": "headshots",
     "owner": "02-assemble", "deps": ["assemble"],
     "hint": "Approve or reject each sourced leader headshot before it is embedded."},
    {"id": "compile", "title": "Compile .docx", "kind": "script",
     "owner": "03-compile", "deps": ["review", "headshots"],
     "hint": "Runs build_docx.py -> dated BD_Profile_*.docx."},
]
STEP_BY_ID = {s["id"]: s for s in STEPS}

# Running/finished jobs, keyed by step id. Guarded by JOBS_LOCK.
JOBS = {}
JOBS_LOCK = threading.Lock()


# ---------------------------------------------------------------- state reads
def _nonempty_glob(folder, pattern):
    p = ROOT / folder
    return [f for f in p.glob(pattern) if f.is_file() and f.stat().st_size > 0]


def parse_intake():
    """Pull Institution / State / EIN out of the frozen intake identity block."""
    path = ROOT / "00-intake" / "output" / "intake.md"
    out = {"institution": "", "state": "", "ein": "", "exists": False}
    if not path.exists() or path.stat().st_size == 0:
        return out
    text = path.read_text()
    out["exists"] = True
    if m := re.search(r"^\s*-\s*Institution:\s*(.+?)\s*$", text, re.MULTILINE):
        out["institution"] = m.group(1).strip()
    if m := re.search(r"^\s*-\s*State:\s*([A-Za-z]{2})\b", text, re.MULTILINE):
        out["state"] = m.group(1).upper()
    if m := re.search(r"^\s*-\s*EIN:\s*([0-9\-]{5,})", text, re.MULTILINE):
        out["ein"] = re.sub(r"\D", "", m.group(1))
    return out


def _is_url(s):
    return s.lower().startswith(("http://", "https://"))


def parse_headshot_candidates():
    """From the assembled draft's Key Leaders block, pair each '### Name' subhead
    with its following 'Photo: <value>' line. Returns [{leader, photo, is_url}]."""
    if not DRAFT_FILE.exists():
        return []
    out = []
    leader = None
    for raw in DRAFT_FILE.read_text().splitlines():
        s = raw.strip()
        m = _SUBHEAD_RE.match(s)
        if m:
            leader = m.group(1).strip()
            continue
        m = _PHOTO_RE.match(s)
        if m and leader:
            val = m.group(1)
            out.append({"leader": leader, "photo": val, "is_url": _is_url(val)})
            leader = None
    return out


def load_approvals():
    if not HEADSHOTS_FILE.exists():
        return {}
    try:
        data = json.loads(HEADSHOTS_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def headshot_state():
    """Candidate list joined with their approval status, plus a decided count
    over the real-URL candidates (the only ones that need a decision)."""
    approvals = load_approvals()
    cands = parse_headshot_candidates()
    rows, url_total, decided = [], 0, 0
    for c in cands:
        status = "n/a"
        if c["is_url"]:
            url_total += 1
            status = approvals.get(c["photo"], "pending")
            if status in ("approved", "rejected"):
                decided += 1
        rows.append({**c, "status": status})
    return {"candidates": rows, "url_total": url_total, "decided": decided}


def set_headshot(url, decision):
    if decision not in ("approved", "rejected", "pending"):
        return 400, {"error": "decision must be approved|rejected|pending"}
    approvals = load_approvals()
    if decision == "pending":
        approvals.pop(url, None)
    else:
        approvals[url] = decision
    HEADSHOTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEADSHOTS_FILE.write_text(json.dumps(approvals, indent=2))
    return 200, {"url": url, "status": decision}


def _done(step_id):
    if step_id == "intake":
        return parse_intake()["exists"]
    if step_id == "headshots":
        if not _done("assemble"):
            return False
        hs = headshot_state()
        return hs["decided"] >= hs["url_total"]   # all real URLs decided (0/0 ok)
    if step_id == "fetches":
        return any(_nonempty_glob(f"research/{fid}/raw", "*.json")
                   for fid, _ in RESEARCH_FLOWS)
    if step_id in {fid for fid, _ in RESEARCH_FLOWS}:
        return bool(_nonempty_glob(f"research/{step_id}/output", "*.md"))
    if step_id == "assemble":
        return bool(_nonempty_glob("02-assemble/output", "profile-draft.md"))
    if step_id == "review":
        return REVIEW_MARKER.exists()
    if step_id == "compile":
        return bool(_nonempty_glob("03-compile/output", "*.docx"))
    return False


def _job_running(step_id):
    with JOBS_LOCK:
        job = JOBS.get(step_id)
        if not job:
            return False
        if job["proc"].poll() is None:
            return True
        # finished: stamp returncode once
        if job.get("returncode") is None:
            job["returncode"] = job["proc"].returncode
            job["ended"] = time.time()
        return False


def _detail(step_id):
    """A short human line about the step's artifact / last run."""
    bits = []
    with JOBS_LOCK:
        job = JOBS.get(step_id)
    if job and job.get("returncode") is not None:
        rc = job["returncode"]
        bits.append("last run ok" if rc == 0 else f"last run failed (exit {rc})")
    if step_id == "intake":
        info = parse_intake()
        if info["exists"]:
            bits.append(info["institution"] or "intake.md present")
    elif step_id == "fetches":
        n = sum(len(_nonempty_glob(f"research/{fid}/raw", "*.json"))
                for fid, _ in RESEARCH_FLOWS)
        if n:
            bits.append(f"{n} raw file(s)")
    elif step_id in {fid for fid, _ in RESEARCH_FLOWS}:
        mds = _nonempty_glob(f"research/{step_id}/output", "*.md")
        if mds:
            bits.append(mds[0].name)
    elif step_id == "assemble":
        f = _nonempty_glob("02-assemble/output", "profile-draft.md")
        if f:
            bits.append(f"{f[0].stat().st_size} bytes")
    elif step_id == "headshots":
        if _done("assemble"):
            hs = headshot_state()
            if hs["url_total"]:
                bits.append(f"{hs['decided']}/{hs['url_total']} photos decided")
            else:
                bits.append("no sourced photos")
    elif step_id == "compile":
        docs = sorted(_nonempty_glob("03-compile/output", "*.docx"),
                      key=lambda p: p.stat().st_mtime)
        if docs:
            bits.append(docs[-1].name)
    return " · ".join(bits)


def _status(step):
    sid = step["id"]
    if _job_running(sid):
        return "running"
    if _done(sid):
        return "done"
    deps_met = all(_done(d) for d in step["deps"])
    return "todo" if deps_met else "blocked"


def _column(step, status):
    if status == "done":
        return "Done"
    if status == "running":
        return "In Progress"
    if step["id"] in ("review", "headshots"):   # actionable-or-waiting human gates
        return "Review"
    return "To Do"


def board_state():
    steps = []
    for s in STEPS:
        status = _status(s)
        runnable = (
            s["kind"] == "script" and status == "todo"
        ) or s["kind"] in ("manual", "headshots")   # gates are always actionable
        steps.append({
            "id": s["id"], "title": s["title"], "kind": s["kind"],
            "owner": s["owner"], "hint": s["hint"], "status": status,
            "column": _column(s, status), "detail": _detail(s["id"]),
            "runnable": runnable,
        })
    return {
        "identity": parse_intake(),
        "columns": ["To Do", "In Progress", "Review", "Done"],
        "steps": steps,
        "now": time.strftime("%H:%M:%S"),
    }


# --------------------------------------------------------------- job launching
def _launch(step_id, argv):
    """Start argv as a subprocess from ROOT, streaming output to a log file."""
    with JOBS_LOCK:
        existing = JOBS.get(step_id)
        if existing and existing["proc"].poll() is None:
            return False, "already running"
        log_path = LOG_DIR / f"{step_id}.log"
        logf = open(log_path, "w")
        logf.write(f"$ {' '.join(argv)}\n\n")
        logf.flush()
        proc = subprocess.Popen(
            argv, cwd=str(ROOT), stdout=logf, stderr=subprocess.STDOUT,
            text=True,
        )
        JOBS[step_id] = {"proc": proc, "log": log_path, "logf": logf,
                         "started": time.time(), "returncode": None,
                         "argv": argv}
    return True, "started"


def run_step(step_id, body):
    step = STEP_BY_ID.get(step_id)
    if not step:
        return 404, {"error": "unknown step"}
    if step["kind"] != "script":
        return 400, {"error": f"{step_id} is an agent step; run it via Claude"}
    if not all(_done(d) for d in step["deps"]):
        return 409, {"error": "dependencies not done yet"}

    if step_id == "fetches":
        info = parse_intake()
        name = (body.get("name") or info["institution"]).strip()
        state = (body.get("state") or info["state"]).strip()
        ein = (body.get("ein") or info["ein"]).strip()
        if not name or not state:
            return 400, {"error": "institution name and 2-letter state required"}
        argv = ["bash", str(ROOT / "run_research_fetches.sh"), name, state]
        if ein:
            argv.append(ein)
    elif step_id == "assemble":
        argv = ["python", str(ROOT / "02-assemble" / "draft.py")]
        variant = (body.get("variant") or "").strip()
        if variant == "short":
            argv.append("--short")
        elif variant == "former_client":
            argv.append("--former-client")
        if body.get("name"):
            argv += ["--institution", body["name"]]
    elif step_id == "compile":
        argv = ["python", str(ROOT / "03-compile" / "build_docx.py")]
    else:
        return 400, {"error": "step not runnable"}

    ok, msg = _launch(step_id, argv)
    code = 202 if ok else 409
    return code, {"status": msg, "argv": argv}


def set_review(approved):
    REVIEW_MARKER.parent.mkdir(parents=True, exist_ok=True)
    if approved:
        if not _done("assemble"):
            return 409, {"error": "assemble a draft before approving review"}
        REVIEW_MARKER.write_text(f"approved {time.ctime()}\n")
    elif REVIEW_MARKER.exists():
        REVIEW_MARKER.unlink()
    return 200, {"approved": approved}


def tail_log(step_id, n=200):
    path = LOG_DIR / f"{step_id}.log"
    if not path.exists():
        return ""
    lines = path.read_text(errors="replace").splitlines()
    return "\n".join(lines[-n:])


# --------------------------------------------------------------------- server
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):           # quiet default access logging
        pass

    def _send(self, code, payload, ctype="application/json"):
        if ctype == "application/json":
            data = json.dumps(payload).encode()
        else:
            data = payload if isinstance(payload, bytes) else payload.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            html = (UI_DIR / "index.html").read_text()
            return self._send(200, html, "text/html; charset=utf-8")
        if path == "/api/state":
            return self._send(200, board_state())
        if path == "/api/headshots":
            return self._send(200, headshot_state())
        if path.startswith("/api/log/"):
            sid = path.rsplit("/", 1)[-1]
            return self._send(200, {"log": tail_log(sid)})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._body()
        if path.startswith("/api/run/"):
            sid = path.rsplit("/", 1)[-1]
            code, payload = run_step(sid, body)
            return self._send(code, payload)
        if path == "/api/review":
            code, payload = set_review(bool(body.get("approved")))
            return self._send(code, payload)
        if path == "/api/headshots":
            code, payload = set_headshot(body.get("url", ""), body.get("decision", ""))
            return self._send(code, payload)
        return self._send(404, {"error": "not found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8765)))
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"BD Profile kanban -> http://{args.host}:{args.port}  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
