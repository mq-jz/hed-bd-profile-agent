# BD Profile build service - API contract

The channel-agnostic backend behind the BD Profile Agent. A Teams bot, an
Outlook / Power Automate flow, or a Copilot Studio custom connector all call the
same three endpoints. Builds are **asynchronous** (a real run takes ~10-15 min):
submit -> poll -> fetch.

Run locally: `python api/service.py` (defaults to `http://127.0.0.1:8781`).
Also usable as a one-shot CLI: `python scripts/build_profile.py --institution "..."`.

## 1. Start a build
`POST /build`  (Content-Type: application/json)

```json
{
  "institution": "Union College",          // required
  "state": "NY",                            // optional; disambiguates the name
  "ein": "141338580",                       // optional; pins the exact 990 entity
  "variant": "full",                        // full | short | former_client
  "origination": "Hi Kai, can you pull a BD profile on Union College... - Jess",
  "media": true,                            // embed leader headshots
  "research_cmd": null                      // optional: command that runs the Claude research flows
}
```
`origination` is the inbound email / Teams message text; it becomes the profile's
Pitch Origination section. Omit `research_cmd` to use existing research output
(missing sections render as `[verify]`); supply it to run the research agents.

**202 Accepted**
```json
{
  "job_id": "9f2a1c4b7d10",
  "status": "queued",
  "institution": "Union College",
  "status_url": "http://<host>/build/9f2a1c4b7d10"
}
```
`400` if `institution` is missing or `variant` is invalid.

## 2. Poll status
`GET /build/{job_id}`

```json
{
  "job_id": "9f2a1c4b7d10",
  "status": "running",                       // queued | running | done | error
  "institution": "Union College",
  "matched": {"name":"Union College","state":"NY","scorecard_id":196866,"ein":"141338580","city":"Schenectady"},
  "candidates": [ {"scorecard_id":196866,"name":"Union College","state":"NY","city":"Schenectady"} ],
  "steps": [ {"step":"research","status":"running","detail":""} ],
  "warnings": [ "research flows without output (...) become [verify] ..." ],
  "verify_count": 6,
  "sections": 22,
  "docx_url": "http://<host>/build/9f2a1c4b7d10/docx",   // present when status == done
  "docx_filename": "BD_Profile_Union_College_2026-07-08.docx",
  "error": null
}
```
`candidates` lets the front door disambiguate (e.g. several "Union College"s):
re-`POST` with the chosen `state`/`ein`. `404` for an unknown `job_id`.

## 3. Download the document
`GET /build/{job_id}/docx` -> streams the `.docx`
(`Content-Disposition: attachment`). `409` if the job is not `done` yet.

`GET /health` -> `{"ok": true}`.

## Notes for the front door (handled in your M365 tenant)
- **Async:** submit on the message, poll `status_url` (or have the flow wait),
  then post the `.docx` back - Teams file/Adaptive Card, or an Outlook reply.
- **Origination:** pass the triggering message text as `origination` so the
  profile records how the request came in.
- **Review gate:** deliver as a draft / to the BD channel for partner review
  before anything goes external.
- **One build at a time:** the service serializes builds (shared workspace);
  per-request isolation (a worktree per job) is the follow-up for concurrency.
- **Research step:** the five research flows are Claude agents; in production the
  service invokes them via `research_cmd` (a headless agent run). The mechanical
  stages (identity, fetches, assemble, compile) run in-process.
