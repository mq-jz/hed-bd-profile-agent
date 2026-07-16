#!/usr/bin/env python3
"""Headless "build a BD Profile" orchestrator - the callable core behind any
front door (Teams / Outlook / Copilot Studio).

One entrypoint: an institution name goes in, a dated .docx comes out. It chains
the existing mechanical stages

    resolve identity -> warm fetches -> [research] -> assemble -> compile

and treats the five research flows as a PLUGGABLE step (--research-cmd), because
those are Claude sub-agents that run in the hosting runtime, not a Python script.
When research output already exists (or a research command is supplied) the
document is full; when it does not, the profile is still produced from the
fetched data with visible [verify] gaps rather than failing.

This module is deliberately UI-agnostic: the CLI and api/service.py both call
build_profile(); a Teams bot, an Outlook flow, or a Copilot Studio custom
connector call the same thing over HTTP.

CLI:
  python scripts/build_profile.py --institution "Union College" --state NY \
      --ein 141338580 [--variant full|short|former_client] [--no-media] \
      [--origination "<inbound email/Teams text>"] \
      [--skip-fetches] [--research-cmd "<cmd that writes research/*/output/*.md>"]

Programmatic:
  from build_profile import build_profile
  result = build_profile("Union College", state="NY", ein="141338580")

Emits a JSON result:
  {institution, matched, variant, docx, sections, verify_count, warnings, steps}
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import profile  # noqa: E402

RESEARCH_FLOWS = ["institutional-profile", "financials", "federal-funding",
                  "leadership", "strategy-news"]
INTAKE = ROOT / "00-intake" / "output" / "intake.md"
DRAFT = ROOT / "02-assemble" / "output" / "profile-draft.md"
COMPILE_OUT = ROOT / "03-compile" / "output"


def _env():
    """Subprocess env with a Scorecard key defaulted (DEMO_KEY is rate-limited)."""
    e = dict(os.environ)
    e.setdefault("DATA_GOV_API_KEY", "DEMO_KEY")
    return e


def _run(argv, timeout=900):
    """Run a subprocess from ROOT, capturing combined output."""
    p = subprocess.run(argv, cwd=str(ROOT), env=_env(), text=True,
                       capture_output=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# ------------------------------------------------------------ identity
def resolve_identity(name, state=None, ein=None, tmp=None):
    """Best-effort canonical identity via College Scorecard (+ ProPublica EIN).

    Returns {name, state, scorecard_id, ein, control, carnegie, city, candidates}.
    Caller-supplied state/ein always win; candidates are returned so a front door
    can disambiguate when the name is ambiguous (e.g. several "Union College"s).
    """
    tmp = Path(tmp or (ROOT / "scratch-identity"))
    tmp.mkdir(parents=True, exist_ok=True)
    out = {"name": name, "state": (state or "").upper() or None, "ein": ein,
           "scorecard_id": None, "control": None, "carnegie": None,
           "city": None, "candidates": [], "warnings": []}

    rc, _ = _run(["python", "scripts/fetch_scorecard.py", "--name", name,
                  "--out", str(tmp)])
    sc_path = tmp / "scorecard.json"
    if rc == 0 and sc_path.exists():
        try:
            data = json.loads(sc_path.read_text())
            schools = data.get("schools", []) or []
            out["candidates"] = [
                {"scorecard_id": s.get("id"), "name": s.get("name"),
                 "state": s.get("state"), "city": s.get("city")}
                for s in schools
            ]
            pick = None
            if state:
                pick = next((s for s in schools
                             if (s.get("state") or "").upper() == state.upper()), None)
            if not pick:
                pick = next((s for s in schools
                             if (s.get("name") or "").strip().lower() == name.strip().lower()), None)
            if not pick and schools:
                pick = schools[0]
                if len(schools) > 1:
                    out["warnings"].append(
                        f"scorecard: {len(schools)} matches for '{name}'; "
                        f"picked {pick.get('name')} ({pick.get('state')}). "
                        f"Pass --state/--ein to disambiguate.")
            if pick:
                out["scorecard_id"] = pick.get("id")
                out["state"] = out["state"] or (pick.get("state") or None)
                out["control"] = pick.get("control")
                out["carnegie"] = pick.get("carnegie_basic")
                out["city"] = pick.get("city")
        except (json.JSONDecodeError, OSError) as e:
            out["warnings"].append(f"scorecard parse failed: {e}")
    else:
        out["warnings"].append("scorecard fetch failed; identity is thin")

    if not out["ein"]:
        rc, _ = _run(["python", "scripts/fetch_propublica.py", "--name", name,
                      "--out", str(tmp)])
        pp_path = tmp / "propublica.json"
        if rc == 0 and pp_path.exists():
            try:
                data = json.loads(pp_path.read_text())
                cands = data.get("candidates", []) or []
                chosen = None
                if out["state"]:
                    chosen = next((c for c in cands
                                   if (c.get("state") or "").upper() == out["state"]
                                   and "COLLEGE" in (c.get("name", "").upper())), None)
                ein = (chosen or {}).get("ein") or data.get("selected_ein")
                if ein:
                    out["ein"] = re.sub(r"\D", "", str(ein))
                    out["warnings"].append(
                        "ein resolved automatically; confirm it is the right entity "
                        "(pass --ein to pin it)")
            except (json.JSONDecodeError, OSError) as e:
                out["warnings"].append(f"propublica parse failed: {e}")
    return out


# ------------------------------------------------------------- intake
_CARNEGIE = {21: "Baccalaureate Colleges: Arts & Sciences Focus"}


def ensure_intake(identity, origination=None, overwrite=False):
    """Write the frozen identity block (and optional Pitch Origination) unless a
    matching human intake already exists. A new/different institution, an explicit
    --origination, or --overwrite-intake triggers a fresh write; otherwise an
    existing intake for the same institution is preserved (keeps its origination)."""
    name = identity["name"]
    same = False
    if INTAKE.exists() and INTAKE.stat().st_size:
        m = re.search(r"^-\s*Institution:\s*(.+?)\s*$", INTAKE.read_text(), re.MULTILINE)
        same = bool(m and m.group(1).strip().lower() == name.strip().lower())
    if same and not origination and not overwrite:
        return "kept existing intake"

    carn = identity.get("carnegie")
    carn_txt = _CARNEGIE.get(carn, "[verify: Carnegie basic classification]") if isinstance(carn, int) else "[verify]"
    lines = [f"# Intake: {name}", "", "## Identity",
             f"- Institution: {name}",
             f"- State: {identity.get('state') or '[verify]'}",
             f"- EIN: {identity.get('ein') or '[verify]'}",
             f"- Scorecard ID: {identity.get('scorecard_id') or '[verify]'}",
             f"- Control: {identity.get('control') or '[verify]'}",
             f"- Carnegie: {carn_txt}",
             f"- City: {identity.get('city') or '[verify]'}", ""]
    if origination:
        lines += ["## Pitch Origination", origination.strip(), ""]
    INTAKE.parent.mkdir(parents=True, exist_ok=True)
    INTAKE.write_text("\n".join(lines))
    return "wrote fresh intake"


# ------------------------------------------------------------- steps
def _research_status():
    have = [f for f in RESEARCH_FLOWS
            if any(Path(ROOT / "research" / f / "output").glob("*.md"))]
    return have, [f for f in RESEARCH_FLOWS if f not in have]


def build_profile(institution, state=None, ein=None, variant="full",
                  media=True, origination=None, warm_fetches=True,
                  research_cmd=None, overwrite_intake=False, date=None,
                  progress=None):
    """Run the full pipeline for one institution and return a result dict.

    variant: "full" | "short" | "former_client".  research_cmd: optional shell
    command that produces research/*/output/*.md (the Claude research step);
    if omitted, existing outputs are used and missing sections become [verify].
    progress(name, status, detail) is called at each stage if provided.
    """
    def step(name, status, detail=""):
        if progress:
            progress(name, status, detail)

    t0 = time.time()
    result = {"institution": institution, "variant": variant, "docx": None,
              "sections": 0, "verify_count": 0, "warnings": [], "steps": []}

    def record(name, ok, detail=""):
        result["steps"].append({"step": name, "ok": ok, "detail": detail})

    # 1. identity
    step("identity", "running")
    ident = resolve_identity(institution, state, ein)
    result["matched"] = {k: ident[k] for k in
                         ("name", "state", "scorecard_id", "ein", "control", "city")}
    result["candidates"] = ident.get("candidates", [])
    result["warnings"] += ident.get("warnings", [])
    record("identity", True, f"{ident.get('state')} · Scorecard {ident.get('scorecard_id')}")
    step("identity", "done")

    # 2. intake
    note = ensure_intake(ident, origination, overwrite_intake)
    record("intake", True, note)

    # 3. warm fetches (mechanical)
    if warm_fetches and ident.get("state"):
        step("fetches", "running")
        argv = ["bash", str(ROOT / "run_research_fetches.sh"),
                institution, ident["state"]]
        if ident.get("ein"):
            argv.append(ident["ein"])
        rc, log = _run(argv, timeout=300)
        record("fetches", rc == 0, "warmed raw/" if rc == 0 else "fetch errors (stubs written)")
        step("fetches", "done")
    else:
        record("fetches", True, "skipped")

    # 4. research (pluggable agent step)
    if research_cmd:
        step("research", "running")
        rc, log = _run(["bash", "-lc", research_cmd], timeout=3600)
        record("research", rc == 0, "ran research-cmd" if rc == 0 else "research-cmd failed")
        step("research", "done")
    have, missing = _research_status()
    if not research_cmd:
        record("research", bool(have),
               f"used existing outputs: {', '.join(have) or 'none'}"
               + (f"; missing {', '.join(missing)} -> [verify]" if missing else ""))
    if missing:
        result["warnings"].append(
            f"research flows without output ({', '.join(missing)}) become [verify] "
            "placeholders; supply --research-cmd to run the Claude research agents")

    # 5. assemble (mechanical)
    step("assemble", "running")
    argv = ["python", str(ROOT / "02-assemble" / "draft.py"),
            "--institution", institution]
    if variant == "short":
        argv.append("--short")
    elif variant == "former_client":
        argv.append("--former-client")
    rc, log = _run(argv)
    if rc != 0:
        record("assemble", False, log.strip()[-300:])
        step("assemble", "error")
        result["error"] = "assemble failed"
        return result
    record("assemble", True, "profile-draft.md")
    step("assemble", "done")

    # 6. compile (mechanical)
    step("compile", "running")
    argv = ["python", str(ROOT / "03-compile" / "build_docx.py"),
            "--institution", institution]
    if not media:
        argv.append("--no-media")
    if date:
        argv += ["--date", date]
    rc, log = _run(argv, timeout=300)
    if rc != 0:
        record("compile", False, log.strip()[-300:])
        step("compile", "error")
        result["error"] = "compile failed"
        return result
    m = re.search(r"Wrote\s+(.+\.docx)", log)
    docx = m.group(1).strip() if m else None
    if not docx or not Path(docx).exists():
        docs = sorted(COMPILE_OUT.glob("*.docx"), key=lambda p: p.stat().st_mtime)
        docx = str(docs[-1]) if docs else None
    result["docx"] = docx
    record("compile", bool(docx), Path(docx).name if docx else "no docx found")
    step("compile", "done")

    # summary stats from the draft
    if DRAFT.exists():
        text = DRAFT.read_text()
        result["sections"] = len(profile.split_draft(text))
        result["verify_count"] = len(profile.scan_tags(text))
    result["elapsed_sec"] = round(time.time() - t0, 1)
    return result


def main():
    ap = argparse.ArgumentParser(description="Build a BD Profile .docx headlessly.")
    ap.add_argument("--institution", required=True)
    ap.add_argument("--state")
    ap.add_argument("--ein")
    ap.add_argument("--variant", choices=["full", "short", "former_client"], default="full")
    ap.add_argument("--no-media", action="store_true", help="skip leader headshots")
    ap.add_argument("--origination", help="inbound email/Teams text -> Pitch Origination")
    ap.add_argument("--skip-fetches", action="store_true")
    ap.add_argument("--research-cmd", help="command that writes research/*/output/*.md")
    ap.add_argument("--overwrite-intake", action="store_true")
    ap.add_argument("--date", help="date stamp YYYY-MM-DD (defaults to today)")
    args = ap.parse_args()

    res = build_profile(
        args.institution, state=args.state, ein=args.ein, variant=args.variant,
        media=not args.no_media, origination=args.origination,
        warm_fetches=not args.skip_fetches, research_cmd=args.research_cmd,
        overwrite_intake=args.overwrite_intake, date=args.date,
        progress=lambda n, s, d="": print(f"  [{s:7}] {n} {d}".rstrip(), file=sys.stderr),
    )
    print(json.dumps(res, indent=2))
    sys.exit(0 if res.get("docx") and not res.get("error") else 1)


if __name__ == "__main__":
    main()
