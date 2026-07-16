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
Two to three short paragraphs. Lead with what makes the institution NOTABLE, not
a catalog restatement of facts covered in later sections.
1. Identity, opening with the distinctive hook (what it is best known for -
   e.g. performing arts and dance, a design-research posture) plus control
   (public / private nonprofit), type, location, founding, enrollment, and the
   **funding-relevant** framing ("thin federal HERD footprint", "teaching-focused,
   not a research university").
2. A one-line federal funding summary. Write it as the literal marker
   `Federal funding: [assemble: federal headline]`.
3. A one-line foundation funding summary. Write it as the literal marker
   `Foundation funding: [assemble: foundation headline]`.

Paragraphs 2 and 3 are cross-flow data, and the flows run in parallel and never
read each other. So institutional-profile does NOT research or write those two
sentences - it leaves the markers above. The OWNING flow writes the sentence as an
`About headline: <one line>` line inside its own section (Federal Funding is
written by federal-funding; Foundation Funding by financials), and
`02-assemble/draft.py` moves it into About and strips it from the source section,
so the fact appears exactly once. See `lib/profile.py:link_about_headlines`.

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
Keep it tight: the latest fiscal year, each figure FY-tagged. At most a one-line
multi-year trend if it is decision-relevant. Do NOT reproduce endowment
composition / Note-9 reconciliation tables or restate prior years line by line.
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
One or two sentences of explainer (peers self-selected in IPEDS; mutual = chose
each other; Chronicle's tool visualizes this) - not a methodology essay - then a
bullet list. For each peer, cross-reference Salesforce and mark **client /
former-client status and the M&Q account owner** when the peer is in the CRM
(e.g. "Client - owner: J. Smith" / "Former client" / "Non-client"); tag
`[verify: check Salesforce]` if the connector is unavailable. Omit the section if
no mutual-peer data.

## Memberships  (core)
A bare bullet list of consortia / accreditor associations (e.g. AICCU, AACSB,
NECHE). Do NOT append provenance narration ("confirmed via the member
directory", "listed on the NAICU detail page") - name the association and stop.

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
- Prior Experience: reverse-chronological, grouped by organization. The employer
  is one bullet; each role + years is a sub-bullet **indented two spaces beneath
  its employer** (the compiler renders the indent as a nested list level):
  ```
  - Prior Experience
    - University of Oxford, Rhodes Trust
      - Chief Executive (Warden), 2018-2024
    - Agnes Scott College
      - President, 2006-2017
  ```
- Education: degree, field, institution, year (same nested shape when useful)
- Biography: 2-4 sentences, funding/leadership relevant. Where it matters, read
  whether this leader is or is not the substantive owner of a grants / research
  conversation.
- A "Connect with <name> on LinkedIn" line - include the **actual profile URL**
  when you can resolve it (e.g. "Connect with <name> on LinkedIn:
  https://www.linkedin.com/in/..."); fall back to the bare phrase only when no
  profile is found. Add notable interviews / talks if found.

## Student Body  (core)
Bullets from IPEDS/Scorecard. Pull the **full financial-aid percentage set** the
sources actually publish - do not leave available numbers blank. Check IPEDS
College Navigator's Financial Aid section (and the same institution's page) for
the percentages Scorecard omits:
- Total + UG enrollment
- Percent receiving aid: any financial aid / federal grants / Pell / state or
  local grants / student loans (each labeled with its source-year)
- Retention; graduation; % full-time; student-faculty ratio
- Eligibility flags (e.g. Title III Eligible (SIP, HSI))
- Student Demographics (parent bullet), with each figure as a sub-bullet
  **indented two spaces** beneath it - gender first, then race/ethnicity:
  ```
  - Student Demographics
    - Women: 50.8%
    - Men: 49.2%
    - White: 62.7%
    - Hispanic/Latino: 12.3%
  ```

## Foundation Funding  (core)
- An `About headline: <one line>` line - the one-sentence foundation summary
  (total since <year> and the standout gift) that the assembler moves into About
  paragraph 3 and strips from here.
- "Foundation Funding Total <YYYY-YYYY>: $<total> (<N> awards)"
- "Link to Foundation Funding History" (the companion Candid-export spreadsheet)
- A narrative paragraph: what it supports, the standout funder/gift
- Top funders as bullets: "Funder Name — $amount"

## Federal Funding  (core)

**EXCLUDE pandemic / formula relief entirely.** HEERF, CARES, CRRSAA, and ARP
money is not competitively won - every institution got it by formula, so it says
nothing about this institution's grant capability and it inflates the total.
Leave it out of the section completely: not in the headline total, not as an
agency bullet, not in the award list, not in About. Do not write a sentence
explaining that you excluded it. This section reports COMPETITIVE federal awards.
(Congressionally directed spending is also not competitive, but it IS
decision-relevant, so it lives in Congressionally Directed Funding. Do not
re-list earmarks here; cross-reference that section at most once.)

- An `About headline: <one line>` line - the one-sentence federal summary that the
  assembler moves into About paragraph 2 and strips from here. Competitive figure
  only (e.g. "About headline: $476,131 in competitive awards since 2016, nearly
  all of it a single NSF biology grant, with small IMLS and NIST awards behind
  it.").
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
Bullets, one per member (see patterns.md for the boilerplate) - not prose
paragraphs. For each: name (party-state[-district]), whether they participate in
the earmark process, whether they sit on **Appropriations** and what that means
for leverage (name the source: POLITICO Pro or the committee's official roster),
and whether any earmark has been secured for this institution. List any
requested/funded project with Bill, Account, Amount, and FY. Do NOT add a
pre-2011 historical-earmark note or restate awards already in Federal Funding.

## HERD Ranking and Research Expenditures  (core)
Answer the yes/no first and keep it short.
- **Not HERD ranked:** a single line ("Not HERD ranked.") - no per-FY bullets,
  no explanatory paragraph, no BD-lens essay, no chart. A teaching-focused college
  belongs here.
- **HERD ranked:** the All and Federal HERD rank for the latest year, plus
  expenditure dollars **pulled from the institution's Salesforce record** (the
  logged research-expenditure figures) by year; tag `[verify: check Salesforce]`
  if the connector is unavailable. When expenditures grow year over year, emit a
  chart directive so the compiler renders a line graph (see patterns.md):
  `Chart: HERD expenditures | 2021=$X; 2022=$Y; 2023=$Z`
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
3-6 recent items, formatted for skimming and matching the house format in the
production profiles in `documents/`. Each item is a bullet: a headline-forward
lead and date, then a tight 1-2 sentence summary, and **always a link to the
article being summarized**. Prefer funding / research / leadership / advancement
news. Do not pad with routine items.
