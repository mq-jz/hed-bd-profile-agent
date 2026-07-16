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
| `reference/patterns.md` | About 3-para shape + optional-section rule |
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
   demographics, MSI designations. Percent fields are already x100. For
   **Student Body**, do not leave available aid numbers blank: pull the full
   financial-aid percentage set (any-aid / federal grants / Pell / state or local
   grants / loans) from IPEDS College Navigator's Financial Aid section where
   Scorecard omits it. Structure demographics as a `Student Demographics` parent
   bullet with each figure indented two spaces beneath it (see template.md).

3. Web-browse to confirm and fill: Carnegie size/setting + historical class +
   programs mix (Carnegie lookup), mutual peers (Chronicle tool), memberships
   (accreditor/consortia), EPSCoR (is the state EPSCoR-eligible), religious
   affiliation, and any null demographic/selectivity values (IPEDS). For
   **Mutual Peers**, cross-reference Salesforce (MQSF connector): for each peer,
   mark client / former-client status and the M&Q account owner, or
   `[verify: check Salesforce]` if the connector is unavailable. Keep the peer
   explainer to one or two sentences. For **Memberships**, list the associations
   only - no "confirmed via..." provenance narration.

4. Write **About** last - 3 mini-paragraphs (see `patterns.md` and the RISD
   exemplar). Lead para 1 with what the institution is NOTABLE for (the
   distinctive hook), not a restatement of facts covered below. Paras 2-3 are
   cross-flow funding data you cannot see, so do NOT research or write them - emit
   these two literal marker lines and let the assembler fill them from the owning
   flows:
   ```
   Federal funding: [assemble: federal headline]

   Foundation funding: [assemble: foundation headline]
   ```

Optional sections (Mutual Peers, Selectivity, EPSCoR, Religious Affiliation):
emit the block ONLY when it applies. If N/A, omit it entirely - do not write
"N/A" and do not emit an empty block (the assembler drops optional sections).

## Output: `research/institutional-profile/output/institutional-profile.md`

Emit one fenced block per section, bodies as short paragraphs and `- ` bullets
matching `reference/template.md`:

```
===== SECTION: About =====
<narrative>

===== SECTION: Carnegie Classification =====
<lead "<year> Carnegie Classification"; control; Institutional Classification;
 Highest Degree; Student Access and Earnings; Size and Setting; Historical>

===== SECTION: Memberships =====
<bullets>

===== SECTION: Designation =====
<MSI + Title III/V eligibility lines>

===== SECTION: Student Body =====
<bullets: enrollment; the full aid %s (any-aid/federal/Pell/state/loan); retention;
 graduation; ratio; eligibility; then a "Student Demographics" bullet with each
 figure indented two spaces beneath it>
```

Plus, ONLY when they apply (omit otherwise - do not write N/A):

```
===== SECTION: Mutual Peers =====
<one-to-two-sentence explainer, then a bullet per peer marking Salesforce client/
 former-client status and account owner, or [verify: check Salesforce]>

===== SECTION: Selectivity =====
<admission rate / selectivity posture>

===== SECTION: EPSCoR =====
<one line: state is EPSCoR-eligible>

===== SECTION: Religious Affiliation =====
<denomination>
```

Must NOT include: `#` headers inside a body, tables, bold/braces; fabricated
percentages or classifications (tag `[verify]`); any section not in the list
above. Report "institutional-profile: done" with a one-line summary.
