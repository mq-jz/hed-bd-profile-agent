# Phase 2: Assemble the draft (mechanical)

Collect the five research flows' SECTION blocks plus the two human-supplied
intake sections (Pitch Origination, Pricing and Scope) into ONE reviewable
draft, in canonical template order.

This is a mechanical fan-in. It generates no content - it only collects, orders,
and reports gaps. Run it once all five `research/*/output/*.md` exist (or run it
early to see which are still missing).

```
python 02-assemble/draft.py
```

Reads `research/*/output/*.md` and `00-intake/output/intake.md`; writes
`02-assemble/output/profile-draft.md`. Section ordering and the [verify]
placeholder for any empty section come from `lib/profile.py:SECTION_ORDER`.

The script prints a checklist: flows with no output, empty (placeholder)
sections, and the count of `[verify]`/`[inferred]` tags to resolve.

## Review gate

`profile-draft.md` is the human review gate. The partner:
- resolves `[verify]` / `[inferred]` tags,
- fills `Pricing and Scope` if it was left `[to be completed by partner]`,
- edits any narrative,
then proceeds to Phase 3.

Re-running `draft.py` OVERWRITES `profile-draft.md` and discards manual edits -
warn the user before re-assembling. To refresh one section, re-run that research
flow then re-assemble, or edit the draft directly.
