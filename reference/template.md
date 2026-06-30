# BD Profile Template (canonical skeleton)

The authoritative section list and the field shape of each section, taken from
the **production profiles in `documents/`** (Menlo, Mercy, Oakton, Trocaire,
Louisiana Delta = full; Brenau, Connecticut, Graceland, Westmont = short) and
Kai's blank template. This is the L3 schema every research flow follows. The
section ORDER and the core/optional/partner kind live in
`lib/profile.py:SECTION_ORDER` (the code is the source of truth - keep this file
in sync with it). `reference/patterns.md` distills the cross-profile conventions;
`reference/exemplar-risd.md` is a full worked example.

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
- **core** sections always appear; **optional** sections (marked below) are
  emitted only when they apply - if N/A, DROP them, do not write "N/A" and do not
  emit a placeholder. **partner** sections come from intake.
- Lead with the fact a partner needs; keep it skimmable.

Use the EXACT section names below (production naming differs from Kai's blank
template: "Congressionally Directed Funding" not "CDS"; "Grants Office" not
"Sponsored Programs"; "HERD Ranking and Research Expenditures"; Mission/Vision/
Values are separate sections).

**Variant skeletons** (each is a section list in `lib/profile.py`):
- **Full** (`SECTION_NAMES`) - the order below.
- **Short** (`SHORT_SECTIONS`, `draft.py --short`) - the funding-and-facts
  spine; drops Pricing / Strategic Plan / Mission / Vision / Values / Student
  Body / Centers; KEEPS the origination block; Key Leaders and Academic Programs
  appear only when produced (the real short profiles vary on exactly these).
- **Former client** (`FORMER_CLIENT_SECTIONS`, `draft.py --former-client`) - a
  full profile that drops Pricing and the Strategic/Mission/Vision/Values/Centers
  cluster, moves HERD ahead of Key Leaders, titles the origination block "Former
  Client Information", and adds "Successful M&Q Projects". Modeled on Trocaire.

---

## About  (core)
Two to three short paragraphs:
1. Identity: control (public / private nonprofit), type, location, founding,
   enrollment, defining programs, and the **funding-relevant** framing
   (e.g. "thin federal HERD footprint" / "design-research, not an art school").
2. A one-line federal funding summary: total since <year>, top agencies, what it
   supports.
3. A one-line foundation funding summary: total since <year>, the standout gift.

(A Short profile compresses these into 2-3 sentences; see the short exemplars.)

## Pitch Origination  (partner - from intake)
How the lead came in (inbound form, referral, warm intro), the point of contact,
and who referred them. Quote the inbound email / partner note verbatim if given.
The HEADING varies with the situation (the assembler carries whichever the
intake used): `Pitch Origination` (new lead), `Prior Conversation` (we have
talked before - common in Short profiles), or `Former Client Information` (a
re-engagement). Omitted entirely when intake captured no origination.

## Pricing Suggestions and Scope of Services for Engagement  (partner)
Partner judgment, captured at intake. OMITTED when the partner supplied no
pricing intent (production profiles drop the section rather than show an empty
one - 3 of 5 full samples have no Pricing heading). Never invent pricing; add it
at intake when the partner has it.

## Endowment and Financials  (core)
Bullets, latest fiscal year, each FY-tagged:
- Endowment: $ (FY; NACUBO if available)
- Revenue / Expenses / Net Revenue / Net Assets: $ (FY)
- Source: ProPublica NonProfit Explorer, Institution's IRS Form 990

## Carnegie Classification  (core)
The HEADING carries the classification-cycle year - production titles this
section `2025 Carnegie Classification`, not a bare "Carnegie Classification"
(the assembler supplies the year via `profile.DISPLAY`). The body then opens
with the control on its own line:
- Control (Public / Private)
- Institutional Classification: <Carnegie basic, e.g. Special Focus: Business>
- Highest Degree Awarded:
- Student Access and Earnings Classification:
- Size and Campus Setting:
- Historical Classification:

## Lobbying Disclosures  (core)
"No lobbying disclosures." / "...since <year>." when none; otherwise firm, years,
income range, and issues. Source: Senate LDA / OpenSecrets.

## Mutual Peers  (optional)
Explainer sentence (peers self-selected in IPEDS; mutual = chose each other;
Chronicle's tool visualizes this), then a bullet list; mark (Client / Non-Client)
when known. Omit the section if no mutual-peer data.

## Memberships  (core)
Bullet list of consortia / accreditor associations (e.g. AICCU, AACSB, NECHE).

## Selectivity  (optional)
Admission rate / selectivity posture. Omit if not meaningful.

## EPSCoR  (optional)
Whether the state is an NSF EPSCoR-eligible jurisdiction. Omit if not.

## Religious Affiliation  (optional)
Denomination. Omit if none.

## Designation  (core)
MSI and special designations (HSI, HBCU, TCU, AANAPISI, PBI) and Title III/V
eligibility - the defining eligibility line for M&Q targeting.

## Strategic Plan  (core)
Analysis through the M&Q lens (funding capacity, research growth, sponsored
programs, government relations, advancement) + link. If none, say so ("X has not
published a strategic plan"). If in development, summarize the stated process.

## Mission Statement  (core)
Quoted or closely paraphrased.

## Vision  (optional)
The vision statement, if the institution publishes one separately.

## Values  (core)
Values as bullets.

## Strategic Goals  (optional)
The named goals/pillars of the strategic plan as bullets, when the institution
publishes them as a distinct list (e.g. Louisiana Delta). Omit if the goals are
already covered inside Strategic Plan.

## Key Leaders  (core)
Note "*all scheduled to attend pitch" or similar when the partner flags it. One
entry per leader - President, Provost/Academic lead, VP/Chief Advancement, the
grants/research lead, and the intake point of contact (mark them). A leader entry
may instead be a department heading (e.g. "Advancement") when the contact is a
team rather than a named person. Each:
- Name, credential, title
- Prior Experience: reverse-chronological roles (org, then title + years nested)
- Education: degree, field, institution, year
- Biography: 2-4 sentences, funding/leadership relevant
- A "Connect with <name> on LinkedIn" line; add notable interviews/talks if found

## Student Body  (core)
Bullets from IPEDS/Scorecard: total + UG enrollment; % aid (financial / federal /
Pell / state / loan); retention; graduation; % full-time; student-faculty ratio;
demographics (gender, then race/ethnicity); Eligibility flags (e.g. Title III
Eligible (SIP, HSI)).

## Foundation Funding  (core)
- "Foundation Funding Total <YYYY-YYYY>: $<total> (<N> awards)"
- "Link to Foundation Funding History" (the companion Candid-export spreadsheet)
- A narrative paragraph: what it supports, the standout funder/gift
- Top funders as bullets: "Funder Name — $amount"

## Federal Funding  (core)
- A summary line in one of the two production forms: `Total Federal Funding: $X
  since <year>` OR (mirroring the Foundation line) `Federal Funding Total
  <YYYY-YYYY>: $X (<N> awards)`. Then by-agency bullets ("U.S. Department of
  Education ($2.77M): HSI capacity, student success...") and a `Link to Federal
  Funding History`.
- Then EITHER a per-award list (full profile: Agency, Office: Program / year /
  amount / description / PI) OR a "Funding Totals by Awarding Agency" rollup
  (short profile: Agency / # grants / total).
- A thin institution may title a minimal version `Recent Award` (see the
  former-client variant) instead of a full Federal Funding workup.
- Optionally **AI-Recommended Future Opportunity Ideas**: concrete, *eligible*
  plays tying strengths to specific programs/agencies, each tagged `[inferred]`.
  Value-add, not in every profile.

## Successful M&Q Projects  (partner - former-client variant)
For a re-engagement with a former client, the M&Q work previously delivered
(project, year, outcome/amount secured) as bullets. Supplied via intake; appears
after the funding sections. Omitted for a new prospect.

## Congressionally Directed Funding  (core)
Standard structure (see patterns.md for the boilerplate): name both Senators
(party) and whether they participate in earmarks and have secured any for this
institution; then the House member(s). List any requested/funded project with
Bill, Account, Amount, and FY.

## HERD Ranking and Research Expenditures  (core)
NSF HERD survey, per year (latest 1-3): All HERD Rank + Expenditures, Federal
HERD Rank + Expenditures. "Not HERD ranked." / "Not eligible in <year>." when so.
(Some profiles title this simply "HERD Ranking"; the canonical heading is the
full name. In the former-client variant this section moves up, ahead of Key
Leaders.)

## Grants Office  (core)
The grants / sponsored-programs / research office: name, one-line mission, full
staff list (name, title). If there is none, say so and name who handles grants
(e.g. "managed by Advancement, led by <CAO>") - production profiles do this.

## Centers and Institutes  (optional)
Bullets, one descriptor each; flag NSF-funded / research centers. Omit if none.

## Academic Programs  (core)
"Undergraduate Majors" (or "Bachelor's Degree Majors") and "Graduate" lists
(degree - program). Abbreviate for large institutions and say so.

## Recent News  (core)
3-6 recent items: headline, date, 1-2 sentence summary. Prefer funding /
research / leadership / advancement news.
