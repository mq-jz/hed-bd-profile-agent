#!/usr/bin/env python3
"""Phase 2: assemble the section blocks from all five research flows (plus the
two human-supplied intake sections) into ONE reviewable draft.

Mechanical fan-in. No model call, no content generation - it only collects,
orders, and reports. The draft is the review gate: a partner reads and edits
`02-assemble/output/profile-draft.md`, then Phase 3 compiles it to .docx.

Usage:
  python 02-assemble/draft.py
  python 02-assemble/draft.py --institution "Rhode Island School of Design"

Reads:
  research/*/output/*.md            (the five flows' SECTION blocks)
  00-intake/output/intake.md        (Pitch Origination + Pricing and Scope)
Writes:
  02-assemble/output/profile-draft.md
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import profile  # noqa: E402

RESEARCH_FLOWS = [
    "institutional-profile", "financials", "federal-funding",
    "leadership", "strategy-news",
]


def read_flow_outputs():
    texts = []
    missing = []
    for flow in RESEARCH_FLOWS:
        out = ROOT / "research" / flow / "output"
        mds = sorted(p for p in out.glob("*.md"))
        if not mds:
            missing.append(flow)
            continue
        for p in mds:
            texts.append(p.read_text())
    return texts, missing


def intake_sections():
    """Lift Pitch Origination and Pricing and Scope out of intake.md as fenced
    SECTION blocks so they flow through the same collector as research output."""
    path = ROOT / "00-intake" / "output" / "intake.md"
    if not path.exists():
        return "", False
    text = path.read_text()
    # intake.md heading -> canonical profile section name
    wanted = {
        "Pitch Origination": "Pitch Origination",
        "Pricing and Scope": "Pricing Suggestions and Scope of Services for Engagement",
    }
    blocks = []
    for heading, section in wanted.items():
        # grab the body under "## <heading>" up to the next "## " or EOF
        m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s+|\Z)",
                      text, re.MULTILINE | re.DOTALL)
        body = (m.group(1).strip() if m else "").strip()
        if not body:
            body = "[to be completed by partner]" if "Pricing" in section \
                else "[verify: pitch origination not captured in intake]"
        blocks.append(f"===== SECTION: {section} =====\n{body}\n")
    return "\n".join(blocks), True


def institution_name(arg):
    if arg:
        return arg
    path = ROOT / "00-intake" / "output" / "intake.md"
    if path.exists():
        m = re.search(r"^-\s*Institution:\s*(.+?)\s*$",
                      path.read_text(), re.MULTILINE)
        if m:
            return m.group(1).strip()
    return "Unknown Institution"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--institution", help="override institution name for the title")
    ap.add_argument("--short", action="store_true",
                    help="assemble a Short BD Profile (funding-and-facts spine only)")
    args = ap.parse_args()

    flow_texts, missing = read_flow_outputs()
    intake_text, have_intake = intake_sections()
    if intake_text:
        flow_texts.append(intake_text)

    if not flow_texts:
        print("ERROR: no research output and no intake found. Run Stage A and "
              "the research flows first.", file=sys.stderr)
        sys.exit(1)

    merged = profile.collect(flow_texts)
    name = institution_name(args.institution)

    kind = "Short BD Profile" if args.short else "BD Profile"
    lines = [f"# {kind} (draft): {name}", "",
             "<!-- Review gate. Edit freely, then run 03-compile/build_docx.py.",
             "     [verify] / [inferred] tags below need a human pass. -->", ""]
    placeholders = []
    all_body = []
    for sect, body, is_placeholder in profile.ordered_sections(merged, short=args.short):
        lines.append(f"## {sect}")
        lines.append("")
        lines.append(body)
        lines.append("")
        all_body.append(body)
        if is_placeholder:
            placeholders.append(sect)

    out = ROOT / "02-assemble" / "output" / "profile-draft.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip() + "\n")

    # Report (no content generated - just a checklist for the reviewer)
    tags = profile.scan_tags("\n".join(all_body))
    print(f"Wrote {out}")
    print(f"  institution : {name}")
    if missing:
        print(f"  flows missing output : {', '.join(missing)}")
    if not have_intake:
        print("  intake.md not found : Pitch Origination / Pricing are placeholders")
    if placeholders:
        print(f"  EMPTY sections (placeholder) : {', '.join(placeholders)}")
    print(f"  [verify]/[inferred] tags to resolve : {len(tags)}")
    print("Review/edit the draft, then: python 03-compile/build_docx.py")


if __name__ == "__main__":
    main()
