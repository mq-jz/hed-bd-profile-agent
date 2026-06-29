#!/usr/bin/env python3
"""Phase 3: compile the approved review draft into a Word .docx BD Profile.

Mechanical. No model call - pure parse of 02-assemble/output/profile-draft.md
into a styled Word document in the canonical template order. Because it cannot
generate content, it cannot hallucinate or time out. Output is dated, so
re-compiling preserves prior versions.

Usage:
  python 03-compile/build_docx.py
  python 03-compile/build_docx.py --in 02-assemble/output/profile-draft.md \
      --institution "Rhode Island School of Design" --date 2026-06-29

Writes 03-compile/output/BD_Profile_<institution>_<date>.docx
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import profile  # noqa: E402

try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    print("ERROR: python-docx is not installed. Run: pip install -r requirements.txt",
          file=sys.stderr)
    sys.exit(1)

BULLET_STYLES = {0: "List Bullet", 1: "List Bullet 2", 2: "List Bullet 3"}


def slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "Institution"


def title_from_draft(text, override):
    if override:
        return override
    m = re.search(r"^#\s+BD Profile.*?:\s*(.+?)\s*$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else "Institution"


def add_body(doc, body):
    for kind, level, content in profile.iter_lines(body):
        if kind == "bullet":
            doc.add_paragraph(content, style=BULLET_STYLES.get(level, "List Bullet 3"))
        else:
            doc.add_paragraph(content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile",
                    default=str(ROOT / "02-assemble" / "output" / "profile-draft.md"))
    ap.add_argument("--institution", help="override institution name")
    ap.add_argument("--date", help="override date stamp (YYYY-MM-DD)")
    args = ap.parse_args()

    src = Path(args.infile)
    if not src.exists():
        print(f"ERROR: draft not found: {src}\nRun: python 02-assemble/draft.py",
              file=sys.stderr)
        sys.exit(1)

    text = src.read_text()
    name = title_from_draft(text, args.institution)
    stamp = args.date or datetime.date.today().isoformat()

    doc = Document()
    doc.add_heading(f"BD Profile: {name}", level=0)

    sections = profile.split_draft(text)
    if not sections:
        print("ERROR: no '## Section' headings found in the draft.", file=sys.stderr)
        sys.exit(1)

    for sect, body in sections:
        doc.add_heading(sect, level=1)
        add_body(doc, body)

    out_dir = ROOT / "03-compile" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"BD_Profile_{slug(name)}_{stamp}.docx"
    doc.save(str(out))

    tags = profile.scan_tags(text)
    print(f"Wrote {out}")
    print(f"  sections : {len(sections)}")
    if tags:
        print(f"  WARNING: {len(tags)} unresolved [verify]/[inferred] tags remain "
              f"in the document. Resolve in the draft and recompile if needed.")


if __name__ == "__main__":
    main()
