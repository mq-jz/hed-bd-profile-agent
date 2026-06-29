# Research Flow: Federal Funding

You are one of the five parallel research sub-agents in Stage B. Work only within
this folder. Do not read sibling research/* folders. Do not stop for approval;
finish and report done.

This flow covers federal money and the congressional angle. It owns:
**Lobbying Disclosures, Federal Funding (+ optional future-opportunity ideas),
Congressionally Directed Funding.**

## Inputs
| File | Load |
|------|------|
| `00-intake/output/intake.md` | Identity (name, state) + notes |
| `reference/template.md` | Field shape for the three sections |
| `reference/patterns.md` | Federal-funding format + CDS boilerplate |
| `reference/voice.md` | Full |
| `reference/sources.md` | "federal-funding flow" rows only |
| `research/federal-funding/raw/usaspending.json` | After the fetch below |
| `research/federal-funding/raw/congress.json` | After the fetch below |

## Process

1. Fetch (or rely on `run_research_fetches.sh`):
   ```
   python scripts/fetch_usaspending.py --name "<institution>" --min 0 --years 10 --out research/federal-funding/raw
   python scripts/fetch_congress.py --state "<ST>" --out research/federal-funding/raw
   ```
   Read both. On `_error`, web-browse USA Spending / Congress.gov, tag `[verify]`.

2. **Federal Funding**: summarize awards by agency and purpose. Group spending
   into themes; name flagship awards with their program name and amount. Confirm
   the larger awards against NSF Award Search / agency pages - USA Spending names
   can be messy. Then write **AI-Recommended Future Opportunity Ideas**: 2-4
   concrete, *eligible* plays tying the institution's strengths to specific
   programs/agencies (see the RISD exemplar). Mark the reasoning `[inferred]`;
   never present a speculative opportunity as a fact.

3. **Congressionally Directed Funding**: from congress.json, name the two
   Senators and the House member(s), party, and committee posture (Appropriations
   matters most). Use the boilerplate in `patterns.md`: state whether each
   participates in the earmarks process and whether any earmarks were secured for
   THIS institution (check House CPF / Senate CDS disclosures). List any
   requested/funded project with Bill (CJS/LHHSE/THUD), Account, Amount, FY.

4. **Lobbying Disclosures**: federal LDA registrations (Senate LDA / OpenSecrets).
   "No lobbying disclosures since <year>" if none recent; otherwise the firm,
   years, income range, and issues.

## Output: `research/federal-funding/output/federal-funding.md`

```
===== SECTION: Lobbying Disclosures =====
<statement, or firm/years/income/issues>

===== SECTION: Federal Funding =====
<"Total Federal Funding: $X since YEAR" + by-agency bullets; then per-award list
 (full) or Funding-Totals-by-Agency rollup (short); optional AI-Recommended
 Future Opportunity Ideas bullets [inferred]>

===== SECTION: Congressionally Directed Funding =====
<Senators + House member, party, earmark participation, any secured/requested>
```

Must NOT include: `#` headers, tables, bold/braces; fabricated award amounts,
program names, member names, or earmarks (tag `[verify]`); future ideas
presented as fact (tag `[inferred]`); any section other than the three above.
Report "federal-funding: done" with a one-line summary.
