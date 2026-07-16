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

2. **Federal Funding**: this section reports COMPETITIVE federal awards.
   **EXCLUDE pandemic / formula relief entirely** (HEERF, CARES, CRRSAA, ARP -
   usually Department of Education formula money). The USA Spending export will be
   full of it and it is often the largest line; filter it out. It is not
   competitively won (every institution got it by formula), so it says nothing
   about this institution's grant capability and only inflates the total. Leave it
   out of the headline, the agency bullets, the award list, and About - and do NOT
   write a sentence explaining that you excluded it. Earmarks are likewise not
   competitive but ARE decision-relevant: they live in Congressionally Directed
   Funding, so do not re-list them here (cross-reference at most once).

   Open the section with an `About headline: <one line>` line - the one-sentence
   federal summary the assembler moves into the About section (it is stripped from
   here, so write it as a standalone sentence). Competitive figure only. Example:
   `About headline: $476,131 in competitive awards since 2016, nearly all of it a single NSF biology grant, with small IMLS and NIST awards behind it.`
   Then summarize the competitive awards by agency and purpose. Group spending
   into themes; name flagship awards with their program name and amount. Confirm
   the larger awards against NSF Award Search / agency pages - USA Spending names
   can be messy. Then write
   **AI-Recommended Future Opportunity Ideas**: 2-4 concrete, *eligible* plays
   tying the institution's strengths to specific programs/agencies (see the RISD
   exemplar). Mark the reasoning `[inferred]`; never present a speculative
   opportunity as a fact.

3. **Congressionally Directed Funding**: bullets, one per member (not prose) -
   see the boilerplate in `patterns.md`. From congress.json, name the two
   Senators and the House member(s), party, whether each participates in the
   earmark process, and whether any earmark was secured for THIS institution
   (check House CPF / Senate CDS disclosures). Keep the valued read of whether a
   member sits on **Appropriations** and what that means for leverage - name the
   source (POLITICO Pro or the committee's official roster). List any
   requested/funded project with Bill (CJS/LHHSE/THUD), Account, Amount, FY. Do
   NOT add a pre-2011 historical-earmark note or re-list awards already in Federal
   Funding.

4. **Lobbying Disclosures**: federal LDA registrations (Senate LDA / OpenSecrets).
   "No lobbying disclosures since <year>" if none recent; otherwise the firm,
   years, income range, and issues.

## Output: `research/federal-funding/output/federal-funding.md`

```
===== SECTION: Lobbying Disclosures =====
<statement, or firm/years/income/issues>

===== SECTION: Federal Funding =====
<"About headline: <one line>" (assembler moves it into About); then
 "Total Federal Funding: $X since YEAR" + by-agency bullets; then per-award list
 (full) or Funding-Totals-by-Agency rollup (short); optional AI-Recommended
 Future Opportunity Ideas bullets [inferred]>

===== SECTION: Congressionally Directed Funding =====
<one bullet per member: name (party-state[-district]), earmark participation,
 on/off Appropriations + source, any secured/requested project>
```

Must NOT include: `#` headers, tables, bold/braces; fabricated award amounts,
program names, member names, or earmarks (tag `[verify]`); future ideas
presented as fact (tag `[inferred]`); any section other than the three above.
Report "federal-funding: done" with a one-line summary.
