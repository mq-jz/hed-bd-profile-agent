# ICM Overview - BD Profile Agent

How this workspace maps to the Interpreted Context Methodology (ICM): engineer
*what context loads at which step* so the agent works with signal, not noise.

## The layers here

- **L0 - The Map (`CLAUDE.md`).** Loaded every session. Says who you are (an M&Q
  BD analyst), the one deliverable (a BD Profile .docx), and the two-stage flow.
  Held under the ~800-word budget; it points outward rather than restating the
  stage contracts.
- **L1 - The Router (`CONTEXT.md`).** Routes a task to the right phase by which
  files exist on disk (intake.md? research output? draft?). No state is held in
  the model - the folder structure carries it.
- **L2 - Stage contracts (`00-intake/CONTEXT.md`, each `research/*/CONTEXT.md`,
  `02-assemble`, `03-compile`).** One step's inputs, process, and outputs. Each
  research flow's contract names exactly which files it may read and which
  SECTION blocks it must emit - a tight contract so the model fills no gaps by
  inference.
- **L3 - Reference (`reference/`).** Pulled in only when a flow needs it:
  `template.md` (the section skeleton + field shape), `voice.md` (register +
  anti-fabrication discipline), `sources.md` (per-flow sources), and
  `exemplar-risd.md` (a completed gold-standard profile).
- **L4 - Output.** `research/*/output/*.md` (section blocks) -> reviewed by the
  assembler's gap report -> `02-assemble/output/profile-draft.md` (the human
  review gate) -> `03-compile/output/*.docx`.

## Layer triage (C06): what is AI vs deterministic

The 60/30/10 split, applied:
- **Deterministic fetch (cheap, exact):** identity match, 990 financials,
  federal awards, congressional delegation - `scripts/fetch_*.py` write plain
  JSON or an `_error` stub. They never crash the pipeline (C07 graceful
  degradation).
- **AI (genuine judgment):** the narrative research - framing the About,
  analyzing the strategic plan through the M&Q lens, profiling leaders, and
  proposing eligible future federal opportunities.
- **Deterministic assemble/compile:** ordering sections (`draft.py`) and
  building the Word file (`build_docx.py`) are pure Python. They generate no
  content, so they cannot hallucinate or time out. The canonical order lives
  once in `lib/profile.py:SECTION_ORDER`, shared by both, so they cannot drift.

## Output drift control (C02)

Every flow contract carries an explicit **Must NOT include** list (no `#`
headers in bodies, no tables/bold/braces, no fabricated figures, ineligible
inferences tagged). `voice.md` makes anti-fabrication non-negotiable: unknown ->
`[verify]`, reasoned guess -> `[inferred]`, conflicting sources shown both ways.
The assembler surfaces every remaining tag and every empty section as a
checklist, and empty sections compile as a visible `[verify]` placeholder -
never silently dropped.

## Context hygiene (C03) / reproducibility (C04)

References point one way: down and outward. A research flow reads intake + its
own reference rows + its own raw fetch - never a sibling flow. State lives on
disk: the current phase is inferred from which files exist, so a fresh session
reconstructs where it is. Intake is frozen after approval; Stage B is re-runnable
against it, and each compile is dated so history is preserved.

## Acronym note

"ICM" here is canon's **Interpreted Context Methodology** and the L0-L4 layer
model above. This workspace is a sibling of `hed-opportunity-matrix` and follows
the same parallel fan-out/fan-in architecture.
