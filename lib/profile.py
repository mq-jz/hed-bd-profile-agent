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

# Canonical BD Profile section order and naming, taken from the production
# profiles in documents/ (Menlo, Mercy, Oakton, Connecticut, etc.) - which use
# slightly different names than Kai's blank template (e.g. "Congressionally
# Directed Funding" not "CDS", "Grants Office" not "Sponsored Programs"). The
# assembler and compiler both emit sections in THIS order regardless of which
# flow produced them. Each tuple is (section_name, owning_flow, kind):
#
#   kind = "core"     always present in a full profile; if no flow produced it,
#                     the assembler emits a visible [verify] placeholder.
#   kind = "optional" included only when a flow actually produced it (e.g.
#                     Selectivity, EPSCoR, Religious Affiliation, Mutual Peers).
#                     Production profiles OMIT these when N/A - so does the
#                     assembler, no placeholder.
#   kind = "partner"  human-supplied via intake (Pitch Origination, Pricing).
#
# SHORT_SECTIONS (below) is the subset used by a "Short BD Profile".
SECTION_ORDER = [
    ("About",                          "institutional-profile", "core"),
    ("Pitch Origination",              "00-intake",             "partner"),
    ("Pricing Suggestions and Scope of Services for Engagement", "00-intake", "partner"),
    ("Endowment and Financials",       "financials",            "core"),
    ("Carnegie Classification",        "institutional-profile", "core"),
    ("Lobbying Disclosures",           "federal-funding",       "core"),
    ("Mutual Peers",                   "institutional-profile", "optional"),
    ("Memberships",                    "institutional-profile", "core"),
    ("Selectivity",                    "institutional-profile", "optional"),
    ("EPSCoR",                         "institutional-profile", "optional"),
    ("Religious Affiliation",          "institutional-profile", "optional"),
    ("Designation",                    "institutional-profile", "core"),
    ("Strategic Plan",                 "strategy-news",         "core"),
    ("Mission Statement",              "strategy-news",         "core"),
    ("Vision",                         "strategy-news",         "optional"),
    ("Values",                         "strategy-news",         "core"),
    ("Key Leaders",                    "leadership",            "core"),
    ("Student Body",                   "institutional-profile", "core"),
    ("Foundation Funding",             "financials",            "core"),
    ("Federal Funding",                "federal-funding",       "core"),
    ("Congressionally Directed Funding", "federal-funding",     "core"),
    ("HERD Ranking and Research Expenditures", "financials",    "core"),
    ("Grants Office",                  "leadership",            "core"),
    ("Centers and Institutes",         "strategy-news",         "optional"),
    ("Academic Programs",              "strategy-news",         "core"),
    ("Recent News",                    "strategy-news",         "core"),
]

SECTION_NAMES = [name for name, _, _ in SECTION_ORDER]
KIND = {name: kind for name, _, kind in SECTION_ORDER}
OWNER = {name: owner for name, owner, _ in SECTION_ORDER}

# A Short BD Profile (see documents/Short BD Profile *.docx) drops the
# narrative-heavy sections (Pitch, Pricing, Strategic Plan, Mission/Vision/
# Values, Student Body) and keeps the funding-and-facts spine. Optional sections
# still appear only when produced.
SHORT_SECTIONS = [
    "About", "Endowment and Financials", "Carnegie Classification",
    "Lobbying Disclosures", "Mutual Peers", "Memberships", "Selectivity",
    "EPSCoR", "Religious Affiliation", "Designation", "Key Leaders",
    "Foundation Funding", "Federal Funding", "Congressionally Directed Funding",
    "HERD Ranking and Research Expenditures", "Grants Office",
    "Academic Programs", "Recent News",
]

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


def ordered_sections(merged, short=False):
    """Yield (name, body, is_placeholder) in canonical order, then extras.

    - A "core" section with no content yields a visible [verify] placeholder so
      the gap shows in the draft and the document.
    - An "optional" section with no content is SKIPPED (production profiles omit
      Selectivity/EPSCoR/Religious Affiliation/etc. when N/A).
    - A "partner" section (Pitch, Pricing) is treated like core - it should come
      from intake; a missing one is a visible gap.
    - short=True restricts output to SHORT_SECTIONS.
    Sections a flow emitted that are not in SECTION_ORDER are yielded last,
    flagged, so they are never silently dropped.
    """
    names = SHORT_SECTIONS if short else SECTION_NAMES
    for name in names:
        body = merged.get(name, "").strip()
        if body:
            yield name, body, False
        elif KIND.get(name) == "optional":
            continue
        else:
            yield name, f"[verify: not produced - owned by {OWNER.get(name)}]", True
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
