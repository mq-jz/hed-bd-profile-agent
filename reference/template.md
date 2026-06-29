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

## Pricing Suggestions and Scope of Services for Engagement  (partner)
Partner judgment, captured at intake or left for the partner. If empty the
compiler keeps a visible `[to be completed by partner]` line - never invent
pricing.

## Endowment and Financials  (core)
Bullets, latest fiscal year, each FY-tagged:
- Endowment: $ (FY; NACUBO if available)
- Revenue / Expenses / Net Revenue / Net Assets: $ (FY)
- Source: ProPublica NonProfit Explorer, Institution's IRS Form 990

## Carnegie Classification  (core)
Lead with the year ("2025 Carnegie Classification"), then:
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

## Key Leaders  (core)
Note "*all scheduled to attend pitch" or similar when the partner flags it. One
entry per leader - President, Provost/Academic lead, VP/Chief Advancement, the
grants/research lead, and the intake point of contact (mark them). Each:
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
- A bulleted summary: "Total Federal Funding: $X since <year>", then by-agency
  bullets ("U.S. Department of Education ($2.77M): HSI capacity, student
  success...").
- Then EITHER a per-award list (full profile: Agency, Office: Program / year /
  amount / description / PI) OR a "Funding Totals by Awarding Agency" rollup
  (short profile: Agency / # grants / total).
- Optionally **AI-Recommended Future Opportunity Ideas**: concrete, *eligible*
  plays tying strengths to specific programs/agencies, each tagged `[inferred]`.
  Value-add, not in every profile.

## Congressionally Directed Funding  (core)
Standard structure (see patterns.md for the boilerplate): name both Senators
(party) and whether they participate in earmarks and have secured any for this
institution; then the House member(s). List any requested/funded project with
Bill, Account, Amount, and FY.

## HERD Ranking and Research Expenditures  (core)
NSF HERD survey, per year (latest 1-3): All HERD Rank + Expenditures, Federal
HERD Rank + Expenditures. "Not HERD ranked." / "Not eligible in <year>." when so.

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
