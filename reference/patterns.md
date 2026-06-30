# Production Patterns (mined from `documents/`)

Conventions distilled from M&Q's real BD profiles so a new profile matches house
style. Source set: full profiles (Menlo, Mercy, Oakton, Trocaire, Louisiana
Delta), short profiles (Brenau, Connecticut, Graceland, Westmont), plus the
companion funding-history spreadsheets and two BD memos. These are .docx/.xlsx in
`documents/` - convert with `textutil -convert txt` / openpyxl to read them.

## Naming (use these exact section names)

Production differs from Kai's blank template:

| Use this (production) | Not this (old template) |
|---|---|
| Congressionally Directed Funding | CDS |
| Grants Office | Sponsored Programs |
| HERD Ranking and Research Expenditures (some title it just "HERD Ranking") | HERD |
| Mission Statement / Vision / Values (separate) | Mission, Vision, and Values |
| 2025 Carnegie Classification (the YEAR is in the heading) | Carnegie Classification |
| Pitch Origination / Prior Conversation / Former Client Information (per situation) | Pitch Origination |
| Academic Programs -> "Undergraduate Majors" / "Graduate" | — |

## Optional sections (omit when N/A - do NOT write "N/A")

Mutual Peers, Selectivity, EPSCoR, Religious Affiliation, Vision, Centers and
Institutes. Production profiles simply leave these out when they don't apply.
Core sections always appear. (Encoded as `kind` in `lib/profile.py:SECTION_ORDER`.)

## About = 3 mini-paragraphs

1. Identity (control, type, location, founding, enrollment, defining programs,
   funding-relevant framing).
2. One line summarizing federal funding (total since year, top agencies, use).
3. One line summarizing foundation funding (total since year, standout gift).
Short profiles compress all three into 2-3 sentences and often end with "Recent
awards are listed on the college's website."

## Funding sections key off two companion spreadsheets

Every profile links a **Foundation Funding History** and (often) a **Federal
Funding History** spreadsheet - these are the raw exports the prose summarizes:

- **Federal history** (USA Spending export; `scripts/fetch_usaspending.py`
  produces the same shape): Awardee, Start Date, Federal Funding Amount,
  Description, Awarding Agency hierarchy, Program Title.
- **Foundation history** (Candid Foundation Directory export - no free API):
  Grantmaker, State, Recipient, Primary Subject, Year Authorized, Grant Amount,
  Support Strategies, Description.

Profile text format:
- Foundation Funding opens with `Foundation Funding Total <YYYY-YYYY>: $<total>
  (<N> awards)`, then `Link to Foundation Funding History`, a narrative, then
  `Funder — $amount` bullets (top ~10).
- Federal Funding opens with a summary line in either production form -
  `Total Federal Funding: $X since <year>` (Menlo) OR `Federal Funding Total
  <YYYY-YYYY>: $X (<N> awards)` (Brenau; mirrors the Foundation line) - then
  by-agency bullets and a `Link to Federal Funding History`. FULL profiles then
  list awards (Agency, Office: Program / year / amount / description / PI); SHORT
  profiles give a `Funding Totals by Awarding Agency` rollup (Agency / # grants /
  total). A very thin record may be titled `Recent Award` instead.

## Congressionally Directed Funding boilerplate

Standard skeleton (fill names/party/state; state earmark participation and
whether any secured):

> Sen. <A> (<P>-<ST>) and Sen. <B> (<P>-<ST>) represent <Institution>. Both
> participate in the earmarks process. Neither have secured earmarks on behalf
> of <Institution>.
> Rep. <C> (<P>-<ST>-<##>) represents <Institution>. He/She participates in the
> earmarks process but has not secured any earmarks for <Institution>.

When there IS earmark activity, replace the "Neither have secured" line with the
request/award detail (FY, Bill - CJS / LHHSE / THUD, Account, Amount, awarded or
requested). See Connecticut College for a worked multi-request example.

## Grants Office "or absence"

If the institution has no grants/sponsored-programs office, say so and name who
handles grants ("Menlo's grants are managed by Advancement, led by CAO Kendra
Woo"; "Conn's grants and contracts are overseen by the Accounting Office").

## Key Leaders details

A "*all scheduled to attend pitch" note when relevant. Beyond LinkedIn, profiles
add notable interviews / TEDx / podcast links per leader. Prior Experience is
reverse-chronological, grouped by org with nested title+years.

## Short BD Profile

A lighter deliverable (`--short`): the funding-and-facts spine only. Drops
Pricing, Strategic Plan, Mission/Vision/Values, Student Body, Centers. Keeps
About (compressed), Endowment/Financials, Carnegie, Lobbying, Memberships,
Foundation Funding, Federal Funding, Congressionally Directed Funding, HERD,
Grants Office, Recent News. Encoded as `SHORT_SECTIONS`.

What the 4 real short profiles (Brenau, Connecticut, Graceland, Westmont) show,
and how the code matches it:
- The origination block IS kept - three of four open with a `Prior Conversation`
  section. So Short keeps the origination slot (it just uses whatever heading the
  intake supplied), it does NOT drop it.
- Academic Programs is omitted in three of four (only Connecticut keeps it), and
  Key Leaders is omitted in one of four (Connecticut). So both are
  include-only-when-produced in Short - no `[verify]` placeholder. Encoded as
  `SHORT_OPTIONAL`.
- Optional sections (Selectivity, Religious Affiliation, Designation, ...) still
  appear only when they apply.

## Former-client / re-engagement variant

When the institution is a FORMER M&Q client (`--former-client`; modeled on
Trocaire), the profile is a full BD Profile with a different spine, encoded as
`FORMER_CLIENT_SECTIONS`:
- the origination block is titled `Former Client Information`;
- Pricing and the Strategic Plan / Mission / Vision / Values / Centers cluster
  are dropped;
- HERD moves up, ahead of Key Leaders;
- a `Successful M&Q Projects` section (the prior M&Q work, from intake) is added
  after the funding sections;
- the federal section may be a thin `Recent Award` rather than a full workup.

## BD Memo - a SEPARATE deliverable (not built here)

`documents/BD Memo *.docx` (Council on Foundations, Grantmakers for Education)
are funder/conference research memos - a different deliverable from an
institution BD Profile. Out of scope for this workspace; noted so they are not
mistaken for a profile section or template.
