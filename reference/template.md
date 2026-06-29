# BD Profile Template (canonical skeleton)

The authoritative section list and the field shape of each section, transcribed
from **Kai's BD Profile Template**. This is the L3 schema every research flow
follows. The section ORDER here is the order the compiler emits; it is also
encoded in `lib/profile.py:SECTION_ORDER` (the code is the source of truth for
ordering - keep this file in sync with it).

Each flow writes its sections as fenced blocks:

```
===== SECTION: <exact name from the list below> =====
<body: short paragraphs and "- " bullets, matching the shape noted here>
```

Rules that hold for every section (see `voice.md`):
- Plain Markdown only: paragraphs and `- ` bullets. No `#` headers inside a
  section body (the compiler supplies the heading), no tables, no bold/braces.
- Never fabricate a number, name, date, or award. Unknown -> `[verify: where to
  look]`. Reasoned guess -> `[inferred]`.
- Lead with the fact a partner needs; keep it skimmable.

---

## 1. About
3-5 sentence narrative: control (public/private nonprofit), type, location,
enrollment, founding, defining identity, and the **funding-relevant** framing
(e.g. "specialized arts institution, thin federal HERD footprint" for RISD).
End with selectivity/ranking color if notable.

## 2. Pitch Origination
How the lead came in (inbound form, referral, warm intro). From intake - the
human supplies this. Quote the inbound email/contact verbatim if provided, and
name the point of contact and who referred them.

## 3. Pricing and Scope
"Pricing Suggestions and Scope of Services for Engagement." Partner judgment,
captured at intake or left for the partner to fill. If empty, the compiler keeps
a visible `[to be completed by partner]` placeholder - never invent pricing.

## 4. Endowment and Financials
Bullets, latest fiscal year, with FY tag and source:
- Endowment: $ (FY, NACUBO if available)
- Revenue / Expenses / Net Revenue / Net Assets: $ (FY)
- Source line: ProPublica Nonprofit Explorer, IRS Form 990

## 5. Carnegie Classification
One line: `Control | Basic Classification | Access/Earnings profile`, plus
Major Academic Programs Mix (top fields by %), Highest Degree Awarded, Size and
Setting, and Historical Classification. From IPEDS / Carnegie lookup.

## 6. Lobbying Disclosures
Federal lobbying registrations (LDA). State "No lobbying disclosures since
<year>" when none recent; otherwise name the firm, years, income range, and
issues. Source: Senate LDA / OpenSecrets.

## 7. Mutual Peers
Lead with the standard explainer sentence (peers self-selected in IPEDS;
mutual = chose each other; Chronicle's tool visualizes this). Then a bullet
list of mutual peers; mark each (Client / Non-Client) when known.

## 8. Memberships
Bullet list of consortia / accreditor associations (e.g. NECHE, AICAD). `N/A`
if none.

## 9. Selectivity
Admission rate and selectivity posture, or `N/A`. From Scorecard/IPEDS.

## 10. EPSCoR
Whether the institution's state is an EPSCoR-eligible jurisdiction (NSF). One
line; `N/A` if not.

## 11. Religious Affiliation
Denomination if any, else `N/A`.

## 12. Designation
MSI and special designations (HSI, HBCU, TCU, AANAPISI, etc.) and Title III/V
eligibility. The defining eligibility line for M&Q targeting.

## 13. Strategic Plan
Analysis of the strategic plan **relevant to M&Q services** (funding capacity,
research growth, sponsored programs, government relations). Link to plan. If the
plan is in development, say so and summarize the stated process/priorities.

## 14. Mission, Vision, and Values
Mission statement, Vision, and Values - quoted or closely paraphrased from the
institution. Bullets for Values.

## 15. Key Leaders
One entry per leader (President, Provost, VP Advancement, sponsored-programs
lead, and the point of contact). Each:
- Name, credential, title (mark the *Point of Contact*)
- Prior Experience: reverse-chronological roles (org - title, years)
- Education: degree, field, institution, year
- Biography: 2-4 sentences, funding/leadership relevant
- LinkedIn line

## 16. Student Body
Bullets from IPEDS/Scorecard: total + UG enrollment, % aid (financial/federal/
Pell/state/loan), retention rate, graduation rate, % full-time, student-faculty
ratio, demographics (gender, race/ethnicity), and Eligibility flags (e.g. Title
III Eligible).

## 17. Foundation Funding
- Total over a year range: $ (N awards), link to funding history
- Overview: # unique funders, average grant size, largest funder
- Major Funders: bullets (funder | $ total | # grants | note)
- What the Funding Supports: bullets

## 18. Federal Funding
Narrative summary of federal funding by agency + purpose, then:
- Agency breakdown: bullets (Agency: $total, N awards, %)
- What the Funding Supports: bullets grouped by theme, naming flagship awards
- AI-Recommended Future Opportunity Ideas: bullets - concrete, eligible plays
  tying the institution's strengths to specific programs/agencies. Mark
  speculative reasoning `[inferred]`.

## 19. CDS
Congressionally Directed Spending / earmarks. Name the two Senators and the
House member(s), party, whether they participate in the earmarks process, and
any earmarks secured (or "Neither/none secured"). List any requested/funded
project with Requestor, Bill, Account, Amount.

## 20. HERD
NSF Higher Education R&D survey. Per year (latest 1-3): All HERD Rank + All HERD
Expenditures, Federal HERD Rank + Federal HERD Expenditures. State when not HERD
ranked / not eligible.

## 21. Sponsored Programs
The sponsored-programs / research office: name, one-line mission, and full staff
list (name, title). Note the M&Q point of contact if they sit here.

## 22. Centers and Institutes
Bullet list; one short descriptor each (research focus, NSF-funded flag where
relevant).

## 23. Academic Programs
Undergraduate and Graduate lists (degree - program). May be abbreviated to
notable/relevant programs for large institutions; say so if abbreviated.

## 24. Recent News
3-6 recent items: headline, date, and 1-2 sentence summary. Prefer
funding/leadership/research items relevant to M&Q.
