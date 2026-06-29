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

3. **Foundation Funding**: private-foundation grant history. Candid/Foundation
   Directory is the primary source (subscription - if you cannot access it, tag
   `[verify]` and give what public 990s and news show). Report total over a year
   range, # funders, average grant, largest funder, major funders, and what the
   funding supports.

4. **HERD**: NSF Higher Education R&D survey rank + expenditures (All and
   Federal) for the latest 1-3 years. Use the NCSES data tool. State plainly
   when the institution was not HERD-ranked / not eligible in a year. No
   fabricated ranks - tag `[verify]`.

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
<total + link line, Overview bullets, Major Funders bullets, What It Supports>

===== SECTION: HERD =====
<per-year All/Federal rank + expenditures, or not-ranked statement>
```

Must NOT include: `#` headers, tables, bold/braces; fabricated dollar figures,
ranks, or funders (tag `[verify]`); any section other than the three above.
Report "financials: done" with a one-line summary.
