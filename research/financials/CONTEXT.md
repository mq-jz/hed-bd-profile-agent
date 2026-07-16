# Research Flow: Financials

You are one of the five parallel research sub-agents in Stage B. Work only within
this folder. Do not read sibling research/* folders. Do not stop for approval;
finish and report done.

This flow covers the money the institution already has and raises. It owns:
**Endowment and Financials, Foundation Funding, HERD.**

## Inputs
| File | Load |
|------|------|
| `00-intake/output/intake.md` | Identity (name, EIN) |
| `reference/template.md` | Field shape for the three sections |
| `reference/patterns.md` | Funding-section formats + companion spreadsheets |
| `reference/voice.md` | Full |
| `reference/sources.md` | "financials flow" rows only |
| `research/financials/raw/propublica.json` | After the fetch below |

## Process

1. Fetch 990 financials (use the EIN from intake if known - more reliable than
   name):
   ```
   python scripts/fetch_propublica.py --ein "<ein>" --out research/financials/raw
   # or, if no EIN: --name "<institution>"
   ```
   Read it. The `recent_filings` give revenue, expenses, total assets proxy by
   tax year. If `_error` or the wrong org matched, rerun with an EIN from
   `candidates[]`, or web-browse the 990 and tag `[verify]`.

2. **Endowment and Financials**: endowment market value comes from NACUBO (not
   the 990) - web-browse the latest NACUBO-TIAA study; tag `[verify]` if not
   found. Revenue / Expenses / Net Revenue / Net Assets from the latest 990.
   Tag every figure with its fiscal year. Source line: ProPublica + IRS 990.
   Keep it tight - latest FY plus at most a one-line trend; do NOT reproduce
   endowment composition / Note-9 reconciliation tables or restate prior years.

3. **Foundation Funding**: open the section with an `About headline: <one line>`
   line - the one-sentence foundation summary (total since <year> and the standout
   gift) that the assembler moves into the About section and strips from here, so
   write it as a standalone sentence. Example:
   `About headline: about $3.17 million since 2023 across three publicly announced grants, anchored by the Kahlert Foundation's $2.5 million for the new nursing program.`
   Then: private-foundation grant history. Candid/Foundation
   Directory is the primary source (subscription - if you cannot access it, tag
   `[verify]` and give what public 990s and news show). Report total over a year
   range, # funders, average grant, largest funder, major funders, and what the
   funding supports.

4. **HERD Ranking and Research Expenditures**: answer yes/no first, briefly.
   If NOT ranked (NCSES data tool), write a single line "Not HERD ranked." - no
   per-FY bullets, no explanatory paragraph, no BD-lens essay. If ranked: give the
   All and Federal rank for the latest year, and pull the logged
   research-expenditure dollars by year from the institution's **Salesforce**
   record (MQSF connector), or tag `[verify: check Salesforce]`. When those
   expenditures grow year over year, add a chart directive on its own line so the
   compiler renders a line graph:
   `Chart: HERD expenditures | 2021=$X; 2022=$Y; 2023=$Z`
   No fabricated ranks or figures - tag `[verify]`.

## Output: `research/financials/output/financials.md`

```
===== SECTION: Endowment and Financials =====
- Endowment: $<value> <FY> (NACUBO) [verify if not found]
- Revenue: $<value> <FY>
- Expenses: $<value> <FY>
- Net Revenue: $<value> <FY>
- Net Assets: $<value> <FY>
- Source: ProPublica Nonprofit Explorer, IRS Form 990

===== SECTION: Foundation Funding =====
<"About headline: <one line>" (assembler moves it into About); then
 "Foundation Funding Total YYYY-YYYY: $X (N awards)", link line, narrative,
 top funders as "Funder — $amount" bullets>

===== SECTION: HERD Ranking and Research Expenditures =====
<"Not HERD ranked." (one line), OR: latest All/Federal rank + Salesforce
 expenditure $ by year + a "Chart: HERD expenditures | YEAR=$..." line if growing>
```

Must NOT include: `#` headers, tables, bold/braces; fabricated dollar figures,
ranks, or funders (tag `[verify]`); any section other than the three above.
Report "financials: done" with a one-line summary.
