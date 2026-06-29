# Research Flow: Institutional Profile

You are one of the five parallel research sub-agents in Stage B. Work only within
this folder. Do not read sibling research/* folders. Do not stop for approval;
finish and report done.

This flow establishes who the institution is. It owns these profile sections:
**About, Carnegie Classification, Mutual Peers, Memberships, Selectivity,
EPSCoR, Religious Affiliation, Designation, Student Body.**

## Inputs
| File | Load |
|------|------|
| `00-intake/output/intake.md` | Full (identity, designations, notes) |
| `reference/template.md` | The field shape for each section above |
| `reference/voice.md` | Full |
| `reference/sources.md` | "institutional-profile flow" rows only |
| `research/institutional-profile/raw/scorecard.json` | After the fetch below |

## Process

1. Fetch (if not already warmed by `run_research_fetches.sh`):
   ```
   python scripts/fetch_scorecard.py --name "<institution>" --out research/institutional-profile/raw
   ```
   Read it. If `_error`, web-browse Scorecard/IPEDS and tag `[verify]`.

2. From scorecard.json fill the hard facts: control, Carnegie code, enrollment,
   selectivity (admission rate), retention/graduation, student-faculty ratio,
   demographics, MSI designations. Percent fields are already x100.

3. Web-browse to confirm and fill: Carnegie size/setting + historical class +
   programs mix (Carnegie lookup), mutual peers (Chronicle tool), memberships
   (accreditor/consortia), EPSCoR (is the state EPSCoR-eligible), religious
   affiliation, and any null demographic/selectivity values (IPEDS).

4. Write **About** last - a 3-5 sentence narrative that frames the institution
   through the funding lens (see the RISD exemplar's opening).

## Output: `research/institutional-profile/output/institutional-profile.md`

Emit one fenced block per section, bodies as short paragraphs and `- ` bullets
matching `reference/template.md`:

```
===== SECTION: About =====
<narrative>

===== SECTION: Carnegie Classification =====
<control | class | profile, then mix / highest degree / size+setting / historical>

===== SECTION: Mutual Peers =====
<explainer sentence, then bullet list; mark (Client/Non-Client) when known>

===== SECTION: Memberships =====
<bullets or N/A>

===== SECTION: Selectivity =====
<admission rate / posture or N/A>

===== SECTION: EPSCoR =====
<one line; state EPSCoR-eligible? or N/A>

===== SECTION: Religious Affiliation =====
<denomination or N/A>

===== SECTION: Designation =====
<MSI + Title III/V eligibility lines>

===== SECTION: Student Body =====
<bullets: enrollment, aid %s, retention, graduation, ratio, demographics, eligibility>
```

Must NOT include: `#` headers inside a body, tables, bold/braces; fabricated
percentages or classifications (tag `[verify]`); any section not in the list
above. Report "institutional-profile: done" with a one-line summary.
