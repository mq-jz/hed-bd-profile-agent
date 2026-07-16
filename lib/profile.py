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
#   kind = "partner"  human-supplied via intake (Pitch Origination, Pricing,
#                     Successful M&Q Projects). Emitted ONLY when intake supplied
#                     it - production omits Pricing and the origination block when
#                     they do not apply, so a missing one is skipped, not
#                     placeheld.
#
# SHORT_SECTIONS / FORMER_CLIENT_SECTIONS (below) are the variant skeletons.
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
    ("Strategic Goals",                "strategy-news",         "optional"),
    ("Key Leaders",                    "leadership",            "core"),
    ("Student Body",                   "institutional-profile", "core"),
    ("Foundation Funding",             "financials",            "core"),
    ("Federal Funding",                "federal-funding",       "core"),
    ("Successful M&Q Projects",        "00-intake",             "partner"),
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

# Heading level in the compiled .docx, mined from the production profiles
# (documents/BD Profile Menlo College.docx etc.) and Kai's template. The house
# style is NOT a flat list: a handful of sections are top-level group headers
# (Word "Heading 1") and the rest are subsections nested under "About" or, for
# the leader blocks, under "Key Leaders" (Word "Heading 2"). Menlo, for example,
# renders About / Key Leaders / Student Body / the funding sections / Recent News
# as Heading 1, and Endowment / Carnegie / Mission / Vision / Values and each
# individual leader as Heading 2. The compiler reads this map so its output
# matches; anything not listed defaults to Heading 2.
H1_SECTIONS = {
    "About", "Key Leaders", "Student Body", "Foundation Funding",
    "Federal Funding", "Successful M&Q Projects",
    "Congressionally Directed Funding",
    "HERD Ranking and Research Expenditures", "Grants Office",
    "Centers and Institutes", "Academic Programs", "Recent News",
}


def heading_level(name):
    """Word heading level (1 or 2) for a canonical section name."""
    return 1 if name in H1_SECTIONS else 2

# Some sections are matched/stored under a canonical key but RENDERED with a
# different heading in production. The assembler writes the display heading into
# profile-draft.md; the compiler emits it verbatim. (Origination is handled
# separately, below, because its heading is chosen by the intake situation.)
DISPLAY = {
    # Production titles this with the Carnegie classification-cycle year in the
    # heading ("2025 Carnegie Classification"), not a bare name. Bump the year
    # when a new Carnegie cycle ships and the documents/ samples follow it.
    "Carnegie Classification": "2025 Carnegie Classification",
}

# The partner-supplied origination slot is one canonical section
# (ORIGINATION_KEY) but is TITLED per the situation in the real profiles:
#   new lead            -> "Pitch Origination"
#   we have talked before -> "Prior Conversation"   (common in Short profiles)
#   former client        -> "Former Client Information"
# The intake file uses whichever heading fits; the assembler detects it and
# carries it through as the draft heading. All map to ORIGINATION_KEY for order.
ORIGINATION_KEY = "Pitch Origination"
ORIGINATION_HEADINGS = [
    "Pitch Origination", "Prior Conversation", "Former Client Information",
]

# A Short BD Profile (documents/Short BD Profile *.docx) keeps the
# funding-and-facts spine and drops the narrative-heavy sections (Pricing,
# Strategic Plan, Mission/Vision/Values, Student Body, Centers). The 4 real short
# profiles vary on exactly the SHORT_OPTIONAL sections below: Connecticut drops
# Key Leaders; three of four drop Academic Programs; three of four DO keep a
# "Prior Conversation" origination block. So Short keeps the origination slot,
# and treats Key Leaders / Academic Programs as include-only-when-produced.
SHORT_SECTIONS = [
    "About", "Pitch Origination", "Endowment and Financials",
    "Carnegie Classification", "Lobbying Disclosures", "Mutual Peers",
    "Memberships", "Selectivity", "EPSCoR", "Religious Affiliation",
    "Designation", "Key Leaders", "Foundation Funding", "Federal Funding",
    "Congressionally Directed Funding",
    "HERD Ranking and Research Expenditures", "Grants Office",
    "Academic Programs", "Recent News",
]
# Core-in-full sections that, in Short mode, appear ONLY when a flow produced
# them (no [verify] placeholder), matching the variation across the real shorts.
SHORT_OPTIONAL = {"Key Leaders", "Academic Programs"}

# A former-client / re-engagement profile (documents/BD Profile Trocaire
# College.docx) is a full BD Profile that drops Pricing and the Strategic Plan /
# Mission / Vision / Values / Centers cluster, moves HERD up ahead of Key
# Leaders, titles the origination block "Former Client Information", and adds
# "Successful M&Q Projects" after the funding sections (the federal section may
# be a thin "Recent Award").
FORMER_CLIENT_SECTIONS = [
    "About", "Pitch Origination", "Endowment and Financials",
    "Carnegie Classification", "Lobbying Disclosures", "Mutual Peers",
    "Memberships", "Selectivity", "EPSCoR", "Religious Affiliation",
    "Designation", "HERD Ranking and Research Expenditures", "Key Leaders",
    "Student Body", "Foundation Funding", "Federal Funding",
    "Successful M&Q Projects", "Congressionally Directed Funding",
    "Grants Office", "Academic Programs", "Recent News",
]

# Variant name -> ordered section-name list. "full" uses the canonical order.
VARIANTS = {
    "full": SECTION_NAMES,
    "short": SHORT_SECTIONS,
    "former_client": FORMER_CLIENT_SECTIONS,
}

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


# ------------------------------------------------------- About funding headlines
# About's paragraphs 2-3 are one-line summaries of Federal Funding and Foundation
# Funding. That is cross-flow data, but the five flows run in PARALLEL and never
# read each other, so institutional-profile cannot see those numbers and must not
# re-derive them (duplicated work, and the two copies can disagree).
#
# Instead the OWNING flow - which already has the data - writes the sentence as an
# "About headline: <one line>" line inside its own section, institutional-profile
# leaves an "[assemble: federal headline]" marker in About, and the assembler
# moves the sentence across. This stays mechanical (a copy, not a summary) and the
# line is STRIPPED from the source section, so the fact still appears exactly once.
ABOUT_HEADLINE_RE = re.compile(r"^About headline:\s*(.+?)\s*$",
                               re.MULTILINE | re.IGNORECASE)
MARKER_RE = re.compile(r"\[assemble:\s*(.+?)\s*\]", re.IGNORECASE)
# marker key -> the section that owns the sentence
ABOUT_MARKERS = {
    "federal headline": "Federal Funding",
    "foundation headline": "Foundation Funding",
}


def pop_about_headline(body):
    """Return (headline or None, body with the 'About headline:' line removed)."""
    m = ABOUT_HEADLINE_RE.search(body)
    if not m:
        return None, body
    cleaned = ABOUT_HEADLINE_RE.sub("", body, count=1)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return m.group(1).strip(), cleaned


def link_about_headlines(merged):
    """Move each owning section's 'About headline:' sentence into About's
    matching '[assemble: ...]' marker. Mutates `merged`; returns the list of
    marker keys that could not be filled (each left as a visible [verify]).
    """
    headlines = {}
    for marker, owner in ABOUT_MARKERS.items():
        if owner in merged:
            line, merged[owner] = pop_about_headline(merged[owner])
            if line:
                headlines[marker] = line
    if "About" not in merged:
        return []
    unfilled = []

    def _fill(m):
        key = m.group(1).strip().lower()
        if key in headlines:
            return headlines[key]
        unfilled.append(key)
        owner = ABOUT_MARKERS.get(key, "the owning flow")
        return (f"[verify: {key} not produced - add an 'About headline:' line "
                f"to {owner}]")

    merged["About"] = MARKER_RE.sub(_fill, merged["About"])
    return unfilled


def ordered_sections(merged, mode="full"):
    """Yield (name, body, is_placeholder) in the variant's order, then extras.

    - A "core" section with no content yields a visible [verify] placeholder so
      the gap shows in the draft and the document.
    - An "optional" section with no content is SKIPPED (production profiles omit
      Selectivity/EPSCoR/Religious Affiliation/Centers/etc. when N/A).
    - A "partner" section (Pitch Origination, Pricing, Successful M&Q Projects)
      is included only when intake supplied it - production omits Pricing and the
      origination block when they do not apply, so a missing one is SKIPPED, not
      placeheld. (draft.py reports the omission for the reviewer.)
    - In short mode the SHORT_OPTIONAL sections (Key Leaders, Academic Programs)
      are likewise include-only-when-produced, matching the real short profiles.
    - mode is "full" (default), "short", or "former_client"; it selects the
      VARIANTS section list.
    Sections a flow emitted that are not in SECTION_ORDER are yielded last,
    flagged, so they are never silently dropped.
    """
    names = VARIANTS.get(mode, SECTION_NAMES)
    for name in names:
        body = merged.get(name, "").strip()
        if body:
            yield name, body, False
            continue
        kind = KIND.get(name)
        skip = (
            kind == "optional"
            or kind == "partner"
            or (mode == "short" and name in SHORT_OPTIONAL)
        )
        if skip:
            continue
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
