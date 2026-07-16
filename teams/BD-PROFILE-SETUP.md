# Build a BD Profile from Microsoft Teams (Path A: Copilot Studio custom connector)

Front the async build service (`api/CONTRACT.md`) from Teams with a **low-code
Copilot Studio agent** plus one **Power Automate flow**. No Microsoft 365 Agents
SDK, no hosted bot code, no Azure Bot registration. The only backend is
`api/service.py`; the connector is `api/connector-swagger.json`.

This is the sibling of `teams/SETUP.md` (chat with Claude). That one is a fast,
synchronous connector; this one is long-running (a real build takes ~10-15 min),
so the async work lives in a Power Automate flow.

## Architecture

```
Teams / M365 Copilot chat
  -> Copilot Studio agent           captures institution (+ state), passes the message as origination
     -> Power Automate flow         StartBuild -> Do-until poll -> DownloadProfile
        -> api/service.py           POST /build  |  GET /build/{id}  |  GET /build/{id}/docx
  <- posts the .docx back to the chat / BD channel, flagged "draft for partner review"
```

Why the flow does the async part: Copilot Studio topics loop poorly, and a chat
turn cannot block for 15 minutes. Power Automate has a real `Do until` loop and
can run in the background and post back when done.

## What you need (your M365 tenant)
- `api/service.py` reachable from your tenant over **HTTPS** (see Step 0).
- **`BD_API_KEY`** set on the service and shared with the connector connection.
- **Copilot Studio** license + permission to publish an agent to Teams.
- **Power Automate** (ships with Copilot Studio) for the async loop.
- ~45 minutes.

## Step 0 - Expose the service over HTTPS
The service listens on `127.0.0.1:8781` by default. Copilot Studio and Power
Automate call it from the cloud, so it needs a public HTTPS URL and an API key.

- **Set the key first:** `export BD_API_KEY="<a long random string>"`. Without
  it the service is open (fine locally, never when exposed).
- **Dev / demo:** run `python api/service.py --host 0.0.0.0 --port 8781` and put
  a tunnel in front (VS Code dev tunnels, ngrok). Note the `https://...` URL.
- **Production:** host on Azure (Container App / App Service / VM) behind HTTPS,
  same command. Builds run **one at a time** (shared workspace) - size for that.

Confirm it is up: `GET https://<host>/health` -> `{"ok": true}`.

## Step 1 - Import the custom connector
Power Platform -> **Custom connectors -> New -> Import an OpenAPI file** ->
upload `api/connector-swagger.json`.
- **General:** set **Host** to your service host (replaces `REPLACE-WITH-YOUR-HOST`);
  scheme **HTTPS**.
- **Security:** API key, header **`x-api-key`**.
- Create a **connection** and paste your `BD_API_KEY`. (The key lives in the
  connection, never in the agent or a message.)
- **Test** the `StartBuild` action (include `origination` - see the gotcha below):
  ```json
  {
    "institution": "Union College",
    "state": "NY",
    "origination": "Partner asked for a quick BD profile on Union College ahead of a call."
  }
  ```
  Expect **202** with a `job_id` and `status_url`. Then call `GetBuildStatus`
  with that `job_id` and watch `status` move `queued -> running -> done`, ending
  with a `docx_url` and `docx_filename`.

> **Gotcha (verified):** a build needs **at least one of** an `origination` message
> **or** existing research output - otherwise the assemble step fails with
> `no research output and no intake found` and the job ends `error`. With neither,
> there is literally nothing to write. This never bites the real Teams flow (the
> triggering message is always the `origination`), but a bare
> `{"institution": "..."}` test will fail. Always pass `origination`.

## Step 2 - Build the Power Automate flow (the async orchestrator)
Create a flow with trigger **"When an agent calls the flow"** (Copilot Studio).
Inputs: `institution` (text, required), `state` (text, optional),
`origination` (text, optional), `variant` (text, optional, default `full`).

1. **StartBuild** (connector) with those inputs. Save `job_id` from the response.
2. **Initialize variable** `status` (string) = `queued`.
3. **Do until** `status` is `done` OR `status` is `error`
   (set a cap so it can't spin forever - e.g. count 40, which is ~20 min):
   - **Delay** 30 seconds.
   - **GetBuildStatus** with `job_id`.
   - **Set variable** `status` = `body('GetBuildStatus')?['status']`.
4. **Condition** `status` == `done`:
   - **Yes:** **DownloadProfile** with `job_id`. Return to the agent:
     `docx_filename`, the file content, `verify_count`, and `matched.name`.
   - **No:** return the `error` string so the agent can apologize gracefully.

Disambiguation (optional but nice): after the first `GetBuildStatus` where
`matched` is null but `candidates` has more than one entry, return the
candidate list to the agent and let the user pick a state/EIN, then re-run
`StartBuild` with it.

## Step 3 - Build the Copilot Studio agent
Copilot Studio -> **New agent** (e.g. "BD Profile").
- **Instructions / persona:** a senior M&Q BD analyst. It collects the
  institution name (ask for the state if the name is ambiguous) and passes the
  user's triggering message text as `origination`.
- **Topic "Build a profile":**
  - Ask for the institution (and state if needed).
  - Call the **Power Automate flow** from Step 2.
  - Tell the user it takes ~10-15 minutes (see Step 4 for how to not block).
  - On completion, post the `.docx` back as a file, state the `verify_count`,
    and remind: **"Draft - partner review before anything goes external."**

## Step 4 - Async delivery (a build takes ~10-15 min)
A chat turn cannot wait 15 minutes. Pick one:
- **Fire-and-forget + proactive reply (recommended).** The flow runs in the
  background; when done it posts the `.docx` to the user or the BD channel
  (**Post message in a chat or channel**, or an Adaptive Card). The agent's
  immediate reply is: *"Building Union College - I'll drop the profile here when
  it's ready (~10-15 min)."*
- **Same-turn wait (demo only).** Keep the topic waiting on the flow. Acceptable
  for `short` runs or when research output already exists (no research step), but
  it risks channel timeouts on a full run.

## Step 5 - Review gate & delivery hygiene
- Deliver to the **BD channel** or as a **draft**, flagged for **partner review
  before external use**. Surface `verify_count` so the reviewer sees how many
  `[verify]` gaps remain.
- Never auto-send a profile externally from the agent.

## Step 6 - Publish to Teams
Copilot Studio -> **Channels -> Microsoft Teams -> publish**. The same click also
covers M365 Copilot chat. Submit for admin approval if your tenant requires it.

## What this path deliberately does NOT expose
- **`research_cmd` and `warm_fetches`** are omitted from the connector on
  purpose: a Teams user must never be able to pass a shell command. Configure the
  research runner **server-side** (an env var or a wrapper around
  `build_profile`), not through the connector. The front-door surface is only
  `institution`, `state`, `ein`, `variant`, `origination`, `media`.
- No Agents SDK, no bot code. If you later want a code-first custom engine agent
  (streaming, richer conversation, M365 Copilot embedding), that is Path B - it
  would still call this same service.

## Limits / follow-ups
- **One build at a time** (shared workspace). For concurrency, per-job worktree
  isolation is the follow-up noted in `api/CONTRACT.md`.
- **Native Power Automate async** (`x-ms-long-running-operation`) would let the
  connector poll for you instead of the manual `Do until` loop, but it requires
  `service.py` to return a `Location` header on the 202. Small, optional
  enhancement; the manual loop above works today.
- **Headshots.** The Kanban UI has an interactive headshot-approval gate; the
  headless build path does not. Send `media: false` to skip auto-embedded
  headshots, or add an approval step before delivery.
