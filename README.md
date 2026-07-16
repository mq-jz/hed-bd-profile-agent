# BD Profile Agent - Parallel ICM Workspace

An ICM workspace that produces a McAllister & Quinn **BD Profile** for a single
higher-education institution: a partner-grade research dossier (identity,
financials, federal funding, leadership, strategy, news) compiled into a Word
.docx matching the firm's template.

It uses a two-stage fan-out / fan-in flow: a one-time intake captures identity
and the human-supplied context; a reproducible discovery stage runs five
parallel research flows that each own a cluster of template sections; a
mechanical assemble collapses them into one editable draft; the partner reviews/
edits that single document; and only then does compile produce the dated Word
file.

## Flow

```
STAGE A (one-time)
00-intake     one agent; identity + pitch origination + pricing; approve -> FROZEN
   |
STAGE B (reproducible)            <- Phase 1; there is no 01- folder
research/*    FIVE parallel agent flows (independent, no cross-dependency)
   institutional-profile   financials   federal-funding   leadership   strategy-news
   each writes ===== SECTION: <name> ===== blocks for the sections it owns
   |
02-assemble   python 02-assemble/draft.py  ->  ONE profile-draft.md (template order)
   |
[ partner reviews / edits 02-assemble/output/profile-draft.md ]   <- review gate
   |
03-compile    python 03-compile/build_docx.py  ->  dated .docx
```

The five research flows are Phase 1 of Stage B; because they fan out they share
one slot rather than a numbered `01-` folder (numbering goes 00, 02, 03).

Design choices that make this robust:
- Intake resolves identity once, so the five flows read only intake.md and never
  depend on each other.
- Sections are written by the flows; assembling and ordering is pure Python in
  draft.py. The assembler generates no content, so it cannot hallucinate.
- Compile is pure python-docx parsing of the approved draft into Word. No model
  call, so it cannot time out. Output is dated, so re-runs preserve history.
- The canonical section order lives once in `lib/profile.py:SECTION_ORDER`,
  shared by the assembler and the compiler so they cannot drift.

## Section ownership

| Flow | Sections |
|------|----------|
| institutional-profile | About, Carnegie Classification, Mutual Peers*, Memberships, Selectivity*, EPSCoR*, Religious Affiliation*, Designation, Student Body |
| financials | Endowment and Financials, Foundation Funding, HERD Ranking and Research Expenditures |
| federal-funding | Lobbying Disclosures, Federal Funding (+ optional future ideas), Congressionally Directed Funding |
| leadership | Key Leaders, Grants Office |
| strategy-news | Strategic Plan, Mission Statement, Vision*, Values, Strategic Goals*, Centers and Institutes*, Academic Programs, Recent News |
| 00-intake (human) | Pitch Origination, Pricing Suggestions and Scope of Services for Engagement, Successful M&Q Projects* |

`*` = optional section: emitted only when it applies (production profiles omit
Selectivity/EPSCoR/Religious Affiliation/Mutual Peers/Vision/Centers when N/A).
Section names and order follow the production profiles in `documents/`, distilled
in `reference/patterns.md`. Two variant skeletons exist: a **Short BD Profile**
(`--short`, the funding-and-facts spine) and a **former-client** profile
(`--former-client`, modeled on Trocaire - drops Pricing + Strategic/Mission/
Vision/Values, moves HERD up, adds Successful M&Q Projects). See patterns.md.

## Layout

```
CLAUDE.md             identity + two-stage flow rules (L0 map)
CONTEXT.md            phase routing (L1)
reference/            template.md (skeleton), patterns.md (production conventions),
                      voice.md, sources.md, exemplar-risd.md
documents/            real BD profiles, memos, funding-history spreadsheets (examples)
scripts/              API fetch scripts (mechanical): scorecard, propublica,
                      usaspending, congress
lib/http.py           shared HTTP helper (error stubs, no crash)
lib/profile.py        shared SECTION_ORDER + block/draft parse (assemble + compile)
run_research_fetches.sh   warm all raw/ folders in parallel
00-intake/            Stage A contract + output/intake.md
research/<flow>/      Phase 1 contracts (one per parallel flow) + raw/ + output/
02-assemble/          Phase 2 assembler -> profile-draft.md
03-compile/           Phase 3 docx compiler -> dated .docx
ui/                   kanban pipeline board + live presentation dashboard
                      (stdlib server + two self-contained HTML pages)
```

## Live presentation demo (Teams conversation)

`python ui/server.py` (no extra deps) serves a full-screen, guided **demo** at
http://127.0.0.1:8765/live. It is a scripted, deterministic replay of a full
pipeline run (baked with Union College's real fetched data), so it never
depends on the network or a live run on stage. The server is demo-only: it
serves `live.html`, its vendored libs, and streams the newest compiled
deliverable at `/api/deliverable` for the closing file cards.

The story starts and ends in a Microsoft Teams chat between **Kai** (the M&Q
analyst) and the **BD Profile Agent** bot: Kai relays Jess's inbound ask, the
agent resolves canonical identity into an approvable intake card, then asks a
short round of clarifying questions (meeting date, who's on their side, angle
and emphasis, pricing left to the partner) before freezing intake. A run card
then opens the **multi-agent dashboard** - the five research flows fanning out
in parallel and streaming their sections/leaders/news, a live agent-activity
terminal, animated metrics, and the fan-in to assemble -> review -> compile.
Returning to Teams, the bot delivers the dated `.docx` (and the capture-deck
`.pptx`, served at `/api/deliverable?kind=pptx`) as downloadable file cards.

Advance each pulsing action with **Enter** (or click); on the dashboard use
**Space/arrows** to step phases, **R** restart, **Esc** back to Teams, **F**
fullscreen. The page (`ui/live.html`) loads React, Tailwind, Motion
(motion.dev), and anime.js from `ui/vendor/` (committed locally, no build step
and no runtime CDN), so it renders even on a locked-down venue network.

## Quick start

1. `pip install -r requirements.txt` (python-docx for the compile).
2. `cp .env.example .env` and fill keys (data.gov for College Scorecard,
   Congress.gov). USA Spending and ProPublica need no key.
3. Stage A: run the intake flow, approve the result.
4. Stage B: `./run_research_fetches.sh "<institution>" "<ST>" [EIN]`, launch the
   five research flows, then `python 02-assemble/draft.py`, review the draft,
   then `python 03-compile/build_docx.py`.

For a lighter deliverable, assemble in short mode: `python 02-assemble/draft.py
--short`; for a former client, `--former-client` (then compile as usual).

See `docs/ICM_OVERVIEW.md` for how this maps to the ICM layer model, and
`reference/patterns.md` for the house-style conventions mined from `documents/`.
