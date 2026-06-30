#!/usr/bin/env python3
"""Phase 3: compile the approved review draft into a Word .docx BD Profile.

Mechanical. No model call - pure parse of 02-assemble/output/profile-draft.md
into a styled Word document. Output is dated, so re-compiling preserves prior
versions.

House style: rather than rebuild the firm's chrome from scratch (which can never
match the custom M&Q banner, breadcrumb tag, logo header, footer and named
styles), this compiler opens the real M&Q template `03-compile/assets/base.docx`
as its base and writes the body into it. That guarantees byte-faithful branding:
  - the blue title banner ("Business Development Profile" + institution name,
    white on blue) and the "BD Profile" breadcrumb tag live in the template
    header; we only swap the institution-name placeholder and the footer date.
  - Heading 1/2 (bold blue), the Title/Subtitle banner styles, Calibri Light
    body, bullets (List Paragraph + the template's bullet numbering) all come
    from the template's own styles.xml, so nothing is approximated.

The body content rules (section order, leader subheads, headshots, the approval
gate) are unchanged from before. Headshots embed only when partner-approved in
.headshots.json; each is square-cropped and floated right with text wrapping,
matching the samples.

Usage:
  python 03-compile/build_docx.py
  python 03-compile/build_docx.py --in 02-assemble/output/profile-draft.md \
      --institution "Rhode Island School of Design" --date 2026-06-29

Writes 03-compile/output/BD_Profile_<institution>_<date>.docx
"""
import argparse
import datetime
import io
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "03-compile" / "assets"
BASE_DOC = ASSETS / "base.docx"
APPROVALS_FILE = ROOT / "02-assemble" / "output" / ".headshots.json"
sys.path.insert(0, str(ROOT))
from lib import profile  # noqa: E402

try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
except ImportError:
    print("ERROR: python-docx is not installed. Run: pip install -r requirements.txt",
          file=sys.stderr)
    sys.exit(1)

GRAY = RGBColor(0x80, 0x80, 0x80)
HEADSHOT_IN = 2.08
PLACEHOLDER_NAME = "University of College"   # institution slot in the template
BULLET_NUM_GENERAL = 20                       # template bullet list (facts)
BULLET_NUM_LEADER = 42                         # template bullet list (experience)
SUBHEAD_RE = re.compile(r"^#{3}\s+(.+?)\s*$")
PHOTO_RE = re.compile(r"^Photo:\s*(.+?)\s*$", re.IGNORECASE)

_DISPLAY_BACK = {v: k for k, v in profile.DISPLAY.items()}


def _is_url(s):
    return s.lower().startswith(("http://", "https://"))


def canonical(heading):
    if heading in _DISPLAY_BACK:
        return _DISPLAY_BACK[heading]
    if heading in profile.ORIGINATION_HEADINGS:
        return profile.ORIGINATION_KEY
    return heading


def slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "Institution"


def title_from_draft(text, override):
    if override:
        return override
    m = re.search(r"^#\s+.*?BD Profile.*?:\s*(.+?)\s*$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else "Institution"


# ------------------------------------------------------ template chrome
def _set_para_text(p, text):
    """Collapse a paragraph's runs to a single run carrying `text` (keeps the
    first run's properties so the banner/breadcrumb styling survives)."""
    runs = p.findall(qn("w:r"))
    if not runs:
        return
    t = runs[0].find(qn("w:t"))
    if t is None:
        t = OxmlElement("w:t")
        runs[0].append(t)
    t.text = text
    t.set(qn("xml:space"), "preserve")
    for r in runs[1:]:
        p.remove(r)


def customize_chrome(doc, institution, stamp, breadcrumb):
    """Swap the institution-name placeholder in the header banner/breadcrumb,
    set the breadcrumb tag (BD Profile / Short BD Profile), and stamp the footer
    date. All edits are on the template's own header/footer parts."""
    def norm(s):
        return " ".join(s.split())
    for part in doc.part.package.iter_parts():
        pn = str(part.partname)
        if "header" in pn:
            el = part.element
            for p in el.iter(qn("w:p")):
                txt = norm("".join(t.text or "" for t in p.iter(qn("w:t"))))
                if txt == PLACEHOLDER_NAME:
                    _set_para_text(p, institution)
                elif txt == "BD Profile" and breadcrumb != "BD Profile":
                    _set_para_text(p, breadcrumb)
        elif "footer" in pn:
            for t in part.element.iter(qn("w:t")):
                if t.text and re.match(r"\d{4}-\d{2}-\d{2}", t.text.strip()):
                    t.text = stamp
    # Document-title metadata (Word's title property) also ships the placeholder.
    try:
        doc.core_properties.title = f"{breadcrumb}: {institution}"
        doc.core_properties.subject = institution
    except Exception:
        pass


def reset_body(doc):
    """Empty the template's placeholder body but keep the section that links to
    the header banner and footer; return that sectPr to append back at the end."""
    body = doc.element.body
    rich = None
    for sp in body.iter(qn("w:sectPr")):
        if sp.find(qn("w:headerReference")) is not None:
            rich = deepcopy(sp)
            break
    for child in list(body):
        body.remove(child)
    return body, rich


# ------------------------------------------------------------- body bits
def _small(paragraph, text, color=GRAY):
    run = paragraph.add_run(text)
    run.font.size = Pt(9)
    run.font.color.rgb = color
    return run


def _bullet(doc, text, level, num_id):
    p = doc.add_paragraph(text, style="List Paragraph")
    pPr = p._p.get_or_add_pPr()
    numPr = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl"); ilvl.set(qn("w:val"), str(min(level, 2)))
    nid = OxmlElement("w:numId"); nid.set(qn("w:val"), str(num_id))
    numPr.append(ilvl); numPr.append(nid)
    pPr.append(numPr)
    return p


def _square_crop(data):
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    s = min(w, h)
    left = (w - s) // 2
    top = max(0, (h - s) // 4)
    im = im.crop((left, top, left + s, top + s))
    out = io.BytesIO()
    im.save(out, format="JPEG", quality=85)
    out.seek(0)
    return out


def _floatify(run):
    drawing = run._r.find(qn("w:drawing"))
    inline = drawing.find(qn("wp:inline")) if drawing is not None else None
    if inline is None:
        return
    extent = inline.find(qn("wp:extent"))
    docPr = inline.find(qn("wp:docPr"))
    cNv = inline.find(qn("wp:cNvGraphicFramePr"))
    graphic = inline.find(qn("a:graphic"))
    if extent is None or graphic is None:
        return
    anchor = OxmlElement("wp:anchor")
    for k, v in {"distT": "0", "distB": "91440", "distL": "114300",
                 "distR": "114300", "simplePos": "0",
                 "relativeHeight": "251658240", "behindDoc": "0", "locked": "0",
                 "layoutInCell": "1", "allowOverlap": "1"}.items():
        anchor.set(k, v)
    sp = OxmlElement("wp:simplePos"); sp.set("x", "0"); sp.set("y", "0")
    anchor.append(sp)
    ph = OxmlElement("wp:positionH"); ph.set("relativeFrom", "column")
    al = OxmlElement("wp:align"); al.text = "right"; ph.append(al)
    anchor.append(ph)
    pv = OxmlElement("wp:positionV"); pv.set("relativeFrom", "paragraph")
    off = OxmlElement("wp:posOffset"); off.text = "0"; pv.append(off)
    anchor.append(pv)
    anchor.append(extent)
    ee = OxmlElement("wp:effectExtent")
    for a in ("l", "t", "r", "b"):
        ee.set(a, "0")
    anchor.append(ee)
    wrap = OxmlElement("wp:wrapSquare"); wrap.set("wrapText", "bothSides")
    anchor.append(wrap)
    if docPr is not None:
        anchor.append(docPr)
    if cNv is not None:
        anchor.append(cNv)
    anchor.append(graphic)
    drawing.remove(inline)
    drawing.append(anchor)


def _embed_headshot(doc, url):
    try:
        req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        try:
            stream = _square_crop(data)
        except Exception:
            stream = io.BytesIO(data)
        run = doc.add_paragraph().add_run()
        run.add_picture(stream, width=Inches(HEADSHOT_IN), height=Inches(HEADSHOT_IN))
        _floatify(run)
        return True
    except (error.URLError, OSError, ValueError) as e:
        _small(doc.add_paragraph(), f"[headshot unavailable: {url} ({e.__class__.__name__})]")
        return False


def _photo_decision(url, approvals):
    if approvals is None:
        return "embed"
    status = approvals.get(url)
    if status == "approved":
        return "embed"
    if status == "rejected":
        return "rejected"
    return "pending"


def add_body(doc, body, allow_media=False, approvals=None, num_id=BULLET_NUM_GENERAL):
    for raw in body.splitlines():
        s = raw.strip()
        if not s:
            continue
        m = SUBHEAD_RE.match(s)
        if m:
            doc.add_heading(m.group(1).strip(), level=2)
            continue
        m = PHOTO_RE.match(s)
        if m:
            val = m.group(1)
            if allow_media:
                if _is_url(val):
                    decision = _photo_decision(val, approvals)
                    if decision == "embed":
                        _embed_headshot(doc, val)
                    elif decision == "rejected":
                        _small(doc.add_paragraph(), "[headshot rejected in review]")
                    else:
                        _small(doc.add_paragraph(), "[headshot pending approval]")
                else:
                    _small(doc.add_paragraph(), f"[headshot to add: {val}]")
            continue
        m = profile.BULLET_RE.match(raw)
        if m:
            indent = m.group(1).replace("\t", "  ")
            _bullet(doc, m.group(2).strip(), len(indent) // 2, num_id)
            continue
        p = doc.add_paragraph(s)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def _scrub_metadata(path, placeholder, replacement):
    """Rewrite docProps/{app,core}.xml in the saved package to drop any leftover
    template-name placeholder (invisible metadata, but tidy to remove)."""
    import zipfile
    targets = ("docProps/app.xml", "docProps/core.xml")
    tmp = path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(path) as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in targets and placeholder.encode() in data:
                data = data.decode("utf-8").replace(placeholder, replacement).encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(path)


def load_approvals():
    if not APPROVALS_FILE.exists():
        return None
    try:
        data = json.loads(APPROVALS_FILE.read_text())
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile",
                    default=str(ROOT / "02-assemble" / "output" / "profile-draft.md"))
    ap.add_argument("--institution", help="override institution name")
    ap.add_argument("--date", help="override date stamp (YYYY-MM-DD)")
    ap.add_argument("--no-media", action="store_true",
                    help="skip downloading/embedding leader headshots")
    args = ap.parse_args()

    src = Path(args.infile)
    if not src.exists():
        print(f"ERROR: draft not found: {src}\nRun: python 02-assemble/draft.py",
              file=sys.stderr)
        sys.exit(1)
    if not BASE_DOC.exists():
        print(f"ERROR: template base missing: {BASE_DOC}", file=sys.stderr)
        sys.exit(1)

    text = src.read_text()
    name = title_from_draft(text, args.institution)
    stamp = args.date or datetime.date.today().isoformat()
    is_short = bool(re.search(r"^#\s+Short BD Profile", text, re.MULTILINE))
    kind = "Short BD Profile" if is_short else "BD Profile"

    sections = profile.split_draft(text)
    if not sections:
        print("ERROR: no '## Section' headings found in the draft.", file=sys.stderr)
        sys.exit(1)

    approvals = None if args.no_media else load_approvals()
    doc = Document(str(BASE_DOC))
    customize_chrome(doc, name, stamp, kind)
    body, rich = reset_body(doc)

    embedded = 0
    for sect, body_text in sections:
        level = profile.heading_level(canonical(sect))
        doc.add_heading(sect, level=level)
        is_leaders = canonical(sect) == "Key Leaders"
        allow_media = is_leaders and not args.no_media
        if allow_media:
            for ln in body_text.splitlines():
                m = PHOTO_RE.match(ln.strip())
                if m and _is_url(m.group(1)) and _photo_decision(m.group(1), approvals) == "embed":
                    embedded += 1
        add_body(doc, body_text, allow_media=allow_media, approvals=approvals,
                 num_id=BULLET_NUM_LEADER if is_leaders else BULLET_NUM_GENERAL)

    if rich is not None:
        body.append(rich)

    out_dir = ROOT / "03-compile" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{slug(kind)}_{slug(name)}_{stamp}.docx"
    doc.save(str(out))
    # docProps/app.xml (TitlesOfParts) keeps the template name as invisible
    # metadata; scrub it so the placeholder appears nowhere in the package.
    _scrub_metadata(out, PLACEHOLDER_NAME, name)

    tags = profile.scan_tags(text)
    print(f"Wrote {out}")
    print(f"  sections : {len(sections)}  (banner: {kind} - {name})")
    if not args.no_media:
        gate = "active" if approvals is not None else "inactive (no .headshots.json)"
        print(f"  headshots: {embedded} embedded; approval gate {gate}")
    if tags:
        print(f"  WARNING: {len(tags)} unresolved [verify]/[inferred] tags remain "
              f"in the document. Resolve in the draft and recompile if needed.")


if __name__ == "__main__":
    main()
