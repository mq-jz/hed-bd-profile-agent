# Task Routing

Build a BD Profile using the two-stage parallel flow. Determine the current
phase by which files exist.

Numbering note: there is no `01-` folder. Phase 1 is the parallel `research/*`
flows - because they fan out, they share one slot instead of a numbered folder,
so the on-disk sequence reads 00, 02, 03.

| Phase | Location | Produces | Gate |
|-------|----------|----------|------|
| A Intake | `00-intake` | `intake.md` (identity + pitch + pricing) | user approves, then FROZEN |
| 1 Research | `research/institutional-profile`, `research/financials`, `research/federal-funding`, `research/leadership`, `research/strategy-news` | one `output/<flow>.md` each (SECTION blocks) | none (runs in parallel) |
| 2 Assemble | `02-assemble` | `output/profile-draft.md` | partner reviews/edits the draft |
| 3 Compile | `03-compile` | `output/BD_Profile_<institution>_<date>.docx` | done |

## Routing logic

1. If `00-intake/output/intake.md` does not exist -> Stage A. Open
   `00-intake/CONTEXT.md`. After writing, get sign-off, then treat as frozen.
2. Else if any `research/*/output/` has no `.md` -> Phase 1. Warm fetches with
   `./run_research_fetches.sh`, then launch the missing flows in parallel. Each
   reads its own `CONTEXT.md`.
3. Else if `02-assemble/output/profile-draft.md` does not exist -> Phase 2. Run
   `python 02-assemble/draft.py`, then hand the draft to the partner for review.
4. Else (draft exists and partner has approved it) -> Phase 3. Run
   `python 03-compile/build_docx.py`.

## Reproducibility

Stage B (Phase 1 -> 2 -> 3) is designed to be re-run against the frozen intake.
- "rerun research/<flow>" refreshes one flow's output.
- "reassemble" re-runs `02-assemble/draft.py`; it OVERWRITES `profile-draft.md`,
  so warn the user it discards manual edits to the draft.
- Each compile is dated in its filename, so re-running compile preserves prior
  documents rather than clobbering them.

Do NOT rewrite `00-intake/output/intake.md` during Stage B. If identity, pitch
origination, or pricing changes, that is a new intake decision the user makes
explicitly.

## Environment

API keys live in `.env` (see `.env.example`). Fetch scripts read them. If a key
is missing, the relevant fetch writes an `_error` stub and the research flow
proceeds with `[verify]`. HERD, foundation funding, Carnegie peer set, and
lobbying have no free API - those are web-browsed and tagged `[verify]`.
