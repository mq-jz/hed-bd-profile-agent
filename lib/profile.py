"""Shared helpers for the BD Profile workspace.

Both the draft assembler (02-assemble/draft.py) and the docx compiler
(03-compile/build_docx.py) consume the same plain-text SECTION block format the
research flows emit. Keeping the canonical section order and the parse logic
here means the two mechanical stages never drift apart.

Format recap (see CLAUDE.md and reference/template.md). Each research flow writes
one or more fenced sections; the body under a fence is free-form Markdown
(paragraphs and "- " bullets) matching the template:

    ===== SECTION: About =====
    University of College is a public liberal arts college in City, State...

    ===== SECTION: Carnegie Classification =====
    Public | Special Focus | ...

A "section" is the text under a `===== SECTION: <name> =====` line, up to the
next fence. The assembler collects sections from every flow and emits them in
SECTION_ORDER (the canonical template skeleton); the compiler maps each to a
Word heading. Sections no flow produced are emitted as a [verify] placeholder so
a gap is visible, never silently dropped.
"""
import re

# Canonical BD Profile section order, transcribed from Kai's BD Profile
# Template. The assembler and compiler both emit sections in THIS order
# regardless of which research flow produced them. Each tuple is
# (section_name, owning_flow) - owning_flow is documentation only (it tells you
# which research/<flow> is responsible) and drives the [verify] placeholder text.
SECTION_ORDER = [
    ("About",                       "institutional-profile"),
    ("Pitch Origination",           "00-intake"),
    ("Pricing and Scope",           "00-intake"),
    ("Endowment and Financials",    "financials"),
    ("Carnegie Classification",     "institutional-profile"),
    ("Lobbying Disclosures",        "federal-funding"),
    ("Mutual Peers",                "institutional-profile"),
    ("Memberships",                 "institutional-profile"),
    ("Selectivity",                 "institutional-profile"),
    ("EPSCoR",                      "institutional-profile"),
    ("Religious Affiliation",       "institutional-profile"),
    ("Designation",                 "institutional-profile"),
    ("Strategic Plan",              "strategy-news"),
    ("Mission, Vision, and Values", "strategy-news"),
    ("Key Leaders",                 "leadership"),
    ("Student Body",                "institutional-profile"),
    ("Foundation Funding",          "financials"),
    ("Federal Funding",             "federal-funding"),
    ("CDS",                         "federal-funding"),
    ("HERD",                        "financials"),
    ("Sponsored Programs",          "leadership"),
    ("Centers and Institutes",      "strategy-news"),
    ("Academic Programs",           "strategy-news"),
    ("Recent News",                 "strategy-news"),
]

SECTION_NAMES = [name for name, _ in SECTION_ORDER]

FENCE_RE = re.compile(r"^=====\s*SECTION:\s*(.+?)\s*=====\s*$", re.IGNORECASE)
TAG_RE = re.compile(r"\[(?:verify|inferred)\b[^\]]*\]", re.IGNORECASE)
# A markdown bullet line: leading whitespace, a "-" or "*", then the text.
BULLET_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")


def split_sections(text):
    """Return an ordered list of (section_name, body_text) from one flow file.

    Lines before the first fence are ignored, so flows may keep a header note
    above their first `===== SECTION: ... =====` line.
    """
    sections = []
    current = None
    buf = []
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if m:
            if current is not None:
                sections.append((current, "\n".join(buf).strip("\n")))
            current = m.group(1).strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections.append((current, "\n".join(buf).strip("\n")))
    return sections


def collect(flow_texts):
    """Merge sections from many flow files into {section_name: body}.

    `flow_texts` is an iterable of raw file contents. Section-name matching is
    case-insensitive and tolerant of minor spacing; the canonical name from
    SECTION_ORDER is used as the key. Unknown section names are kept under their
    given name (surfaced later as 'extra' so nothing is silently lost). If two
    flows emit the same section, the bodies are concatenated with a blank line.
    """
    canon = {n.lower(): n for n in SECTION_NAMES}
    merged = {}
    for text in flow_texts:
        for name, body in split_sections(text):
            key = canon.get(name.strip().lower(), name.strip())
            if not body.strip():
                continue
            if key in merged:
                merged[key] = merged[key] + "\n\n" + body.strip()
            else:
                merged[key] = body.strip()
    return merged


def ordered_sections(merged):
    """Yield (name, body, is_placeholder) in canonical order, then extras.

    Canonical sections with no content yield a [verify] placeholder body so the
    gap is visible in the draft and the final document. Sections a flow emitted
    that are not in SECTION_ORDER are yielded last, flagged, so they are never
    dropped.
    """
    for name, owner in SECTION_ORDER:
        body = merged.get(name, "").strip()
        if body:
            yield name, body, False
        else:
            yield name, f"[verify: not produced - owned by {owner}]", True
    for name in merged:
        if name not in SECTION_NAMES:
            yield name, merged[name].strip() + "\n\n[verify: section not in template skeleton]", False


HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")


def split_draft(text):
    """Split a review draft (## Heading bodies) into [(name, body), ...].

    The assembler writes profile-draft.md with `## <section>` headings; the
    compiler reads it back with this. Symmetric to split_sections() so the two
    mechanical stages share one parser and cannot drift. A leading `# Title` and
    any preamble before the first `## ` heading are ignored.
    """
    sections = []
    current = None
    buf = []
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            if current is not None:
                sections.append((current, "\n".join(buf).strip("\n")))
            current = m.group(1).strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections.append((current, "\n".join(buf).strip("\n")))
    return sections


def scan_tags(text):
    """Return all [verify ...] / [inferred ...] tag strings in order."""
    return TAG_RE.findall(text)


def iter_lines(body):
    """Yield ('bullet', indent_level, text) or ('para', 0, text) per line.

    Blank lines are skipped. Bullet indent_level is 0 for a top-level bullet and
    increments per two leading spaces (or per tab) so the compiler can render
    nested bullets. Used by build_docx.py to choose a Word paragraph style.
    """
    for raw in body.splitlines():
        if not raw.strip():
            continue
        m = BULLET_RE.match(raw)
        if m:
            indent = m.group(1).replace("\t", "  ")
            level = len(indent) // 2
            yield "bullet", level, m.group(2).strip()
        else:
            yield "para", 0, raw.strip()
