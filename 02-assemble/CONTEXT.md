# Phase 2: Assemble the draft (mechanical)

Collect the five research flows' SECTION blocks plus the two human-supplied
intake sections (Pitch Origination, Pricing and Scope) into ONE reviewable
draft, in canonical template order.

This is a mechanical fan-in. It generates no content - it only collects, orders,
and reports gaps. Run it once all five `research/*/output/*.md` exist (or run it
early to see which are still missing).

```
python 02-assemble/draft.py                  # full profile
python 02-assemble/draft.py --short          # Short BD Profile (funding spine)
python 02-assemble/draft.py --former-client  # former-client / re-engagement variant
```

Reads `research/*/output/*.md` and `00-intake/output/intake.md`; writes
`02-assemble/output/profile-draft.md`. Section ordering, the variant skeletons,
and the [verify] placeholder for any empty core section come from
`lib/profile.py` (`SECTION_ORDER`, `SHORT_SECTIONS`, `FORMER_CLIENT_SECTIONS`).
The assembler also writes the production heading text into the draft (e.g.
`2025 Carnegie Classification`, and whichever origination heading the intake
used), so the compiled .docx matches the real profiles.

Partner sections are include-only-when-supplied: if intake has no origination
block or no Pricing intent, those sections are OMITTED (production does the same)
and the script prints a NOTE - it does not leave a placeholder heading.

The script prints a checklist: the variant, flows with no output, omitted partner
sections, empty (placeholder) core sections, and the count of
`[verify]`/`[inferred]` tags to resolve.

## Review gate

`profile-draft.md` is the human review gate. The partner:
- resolves `[verify]` / `[inferred]` tags,
- adds Pricing/Scope if wanted (it is omitted when intake had none - add the
  heading back, or capture it at intake and re-assemble),
- edits any narrative,
then proceeds to Phase 3.

Re-running `draft.py` OVERWRITES `profile-draft.md` and discards manual edits -
warn the user before re-assembling. To refresh one section, re-run that research
flow then re-assemble, or edit the draft directly.
