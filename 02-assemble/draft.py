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


def _body_under(text, heading):
    """Return the body under '## <heading>' up to the next '## ' or EOF."""
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s+|\Z)",
                  text, re.MULTILINE | re.DOTALL)
    return (m.group(1).strip() if m else "").strip()


def intake_sections():
    """Lift the human-supplied sections out of intake.md as fenced SECTION blocks
    so they flow through the same collector as research output.

    A block is emitted ONLY when intake actually supplied content - production
    omits the origination block and Pricing when they do not apply, so we never
    inject a placeholder body for them. Returns (blocks_text, have_intake,
    origination_display, found) where origination_display is the production
    heading the intake used for the origination slot (or None) and found flags
    which partner sections were present.
    """
    path = ROOT / "00-intake" / "output" / "intake.md"
    found = {"origination": False, "pricing": False, "mq_projects": False}
    if not path.exists():
        return "", False, None, found
    text = path.read_text()
    blocks = []
    origination_display = None

    # Origination slot: accept any of the production headings; keep the one used.
    for heading in profile.ORIGINATION_HEADINGS:
        body = _body_under(text, heading)
        if body:
            blocks.append(f"===== SECTION: {profile.ORIGINATION_KEY} =====\n{body}\n")
            origination_display = heading
            found["origination"] = True
            break

    # Pricing: only when the partner supplied real intent (not the placeholder).
    pricing = _body_under(text, "Pricing and Scope")
    if pricing and "to be completed by partner" not in pricing.lower():
        blocks.append(
            "===== SECTION: Pricing Suggestions and Scope of Services for "
            f"Engagement =====\n{pricing}\n")
        found["pricing"] = True

    # Successful M&Q Projects: former-client engagements list prior M&Q work.
    mq = _body_under(text, "Successful M&Q Projects")
    if mq:
        blocks.append(f"===== SECTION: Successful M&Q Projects =====\n{mq}\n")
        found["mq_projects"] = True

    return "\n".join(blocks), True, origination_display, found


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
    ap.add_argument("--former-client", action="store_true",
                    help="assemble the former-client / re-engagement variant "
                         "(drops Pricing + Strategic/Mission/Vision/Values, moves "
                         "HERD up, adds Successful M&Q Projects; see Trocaire)")
    args = ap.parse_args()

    if args.short and args.former_client:
        print("ERROR: choose one of --short / --former-client, not both.",
              file=sys.stderr)
        sys.exit(1)
    mode = "short" if args.short else "former_client" if args.former_client else "full"

    flow_texts, missing = read_flow_outputs()
    intake_text, have_intake, origination_display, found = intake_sections()
    if intake_text:
        flow_texts.append(intake_text)

    if not flow_texts:
        print("ERROR: no research output and no intake found. Run Stage A and "
              "the research flows first.", file=sys.stderr)
        sys.exit(1)

    merged = profile.collect(flow_texts)
    # Move the owning flows' "About headline:" sentences into About's
    # "[assemble: ...]" markers (mechanical copy; see lib/profile.py).
    unfilled_headlines = profile.link_about_headlines(merged)
    name = institution_name(args.institution)

    # Section name -> production heading text for the draft (compiler emits it
    # verbatim). Origination's heading depends on what intake used.
    display = dict(profile.DISPLAY)
    if origination_display:
        display[profile.ORIGINATION_KEY] = origination_display

    kind = "Short BD Profile" if args.short else "BD Profile"
    lines = [f"# {kind} (draft): {name}", "",
             "<!-- Review gate. Edit freely, then run 03-compile/build_docx.py.",
             "     [verify] / [inferred] tags below need a human pass. -->", ""]
    placeholders = []
    all_body = []
    for sect, body, is_placeholder in profile.ordered_sections(merged, mode=mode):
        lines.append(f"## {display.get(sect, sect)}")
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
    print(f"  variant : {mode}")
    if missing:
        print(f"  flows missing output : {', '.join(missing)}")
    if not have_intake:
        print("  intake.md not found : no origination / Pricing captured")
    else:
        if not found["origination"]:
            print("  NOTE: no origination block in intake "
                  "(Pitch Origination / Prior Conversation / Former Client "
                  "Information) - section omitted, as production does when N/A")
        if not found["pricing"]:
            print("  NOTE: no Pricing intent in intake - Pricing section omitted "
                  "(add it at intake when the partner has it)")
    if placeholders:
        print(f"  EMPTY sections (placeholder) : {', '.join(placeholders)}")
    if unfilled_headlines:
        print(f"  NOTE: About headline not supplied by the owning flow : "
              f"{', '.join(unfilled_headlines)} - add an 'About headline:' line "
              f"to the owning section and reassemble")
    print(f"  [verify]/[inferred] tags to resolve : {len(tags)}")
    print("Review/edit the draft, then: python 03-compile/build_docx.py")


if __name__ == "__main__":
    main()
