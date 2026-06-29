# Stage A: Intake (one-time, then frozen)

Capture, in one pass, everything the five research flows need so they never
depend on each other or re-resolve identity. Write `00-intake/output/intake.md`,
get user sign-off, then treat it as FROZEN - Stage B reads it, never rewrites
it.

You are the intake agent. Do NOT start research here. Resolve identity, capture
the human-supplied context, and stop for approval.

## Inputs
| Source | Use |
|--------|-----|
| The user | Institution name, the pitch origination (inbound email / referral / form), any known contacts, and pricing/scope intent |
| `scripts/fetch_scorecard.py` | Canonical identity match (id, control, Carnegie, state, MSI) |
| `scripts/fetch_propublica.py` | EIN + 990 record to pin financials later |

## Process

1. Get the institution name from the user. Run the identity fetches:
   ```
   python scripts/fetch_scorecard.py --name "<institution>" --out 00-intake/output/raw
   python scripts/fetch_propublica.py --name "<institution>" --out 00-intake/output/raw
   ```
   Read both. Confirm the right match with the user if there is ambiguity
   (multiple campuses, similar names). Record the chosen Scorecard `id`, the
   ProPublica `EIN`, control, state, and Carnegie code.

2. Confirm whether the institution is R1/R2. M&Q's HED practice targets
   non-R1/R2; if it IS R1/R2, flag it for the partner but proceed if they want
   the profile anyway.

3. Capture **Pitch Origination** from the user verbatim - the inbound email,
   the referral chain, who the point of contact is. This is human-supplied and
   cannot be researched.

4. Capture **Pricing and Scope** intent if the partner has any. If not, record
   `[to be completed by partner]` - never invent pricing.

## Output: `00-intake/output/intake.md`

```
# Intake: <Institution>

## Identity (frozen)
- Institution: <official name>
- Scorecard id: <id>
- EIN: <ein or [verify]>
- Control: <public | private nonprofit>
- State: <2-letter>   City: <city>
- Carnegie basic code: <code>  ->  R-status: <not R1/R2 | R1 | R2 | [verify]>
- Designations: <HSI/HBCU/... or none>

## Pitch Origination
<verbatim inbound / referral / how the lead came in; name the point of contact>

## Pricing and Scope
<partner intent, or [to be completed by partner]>

## Notes for research
<anything the flows should know: known leaders, a specific grant the contact
mentioned (e.g. RISD's NSF/EPIIC gap analysis), campuses to disambiguate, etc.>
```

The Identity block feeds `run_research_fetches.sh` (name, state, EIN). Get
sign-off, then freeze. The Pitch Origination and Pricing blocks pass straight
into the final profile (the assembler reads them from here).
