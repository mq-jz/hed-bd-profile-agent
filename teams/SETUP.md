# Talk to Claude in Microsoft Teams

The quickest way to chat with Claude inside Teams: a **Copilot Studio agent** that
calls the **Anthropic Messages API** through a custom connector, published to Teams.
This is the foundation — later, the same agent can also call the BD Profile build
endpoint (`api/CONTRACT.md`) as a second action.

## What you need (your M365 tenant)
- An **Anthropic API key** (`sk-ant-...`) — billed per token. Get one at console.anthropic.com.
- **Copilot Studio** license + permission to publish an agent to Teams.
- ~30 minutes.

## Steps

### 1. Create the custom connector
Power Platform → **Custom connectors → New → Import an OpenAPI file** →
upload `teams/anthropic-messages-connector.json`.
- **Security:** API key, header `x-api-key`.
- Create a **connection** and paste your Anthropic key. (The key lives in the
  connection, never in the agent definition.)
- **Test** the `SendMessage` action with a sample body (below) to confirm 200.

Sample test body:
```json
{
  "model": "claude-opus-4-8",
  "max_tokens": 2048,
  "system": "You are a helpful assistant.",
  "messages": [{ "role": "user", "content": "Say hello in one sentence." }]
}
```
Read the reply from `content[0].text`.

### 2. Build the Copilot Studio agent
Copilot Studio → **New agent** (e.g. "Claude"). In a topic (or generative
orchestration):
- Keep a conversation-history variable — an array of `{role, content}` objects.
- On each user turn: append `{role:"user", content:<user text>}`, call
  **SendMessage** with the full `messages` array, then append the reply
  `{role:"assistant", content:<content[0].text>}` and post it back.

The Messages API is **stateless** — you must send the whole history every turn.
That accumulation is the only real logic; everything else is the connector.

### 3. Publish to Teams
Copilot Studio → **Channels → Microsoft Teams → publish**. One click also covers
M365 Copilot chat. Submit for admin approval if your tenant requires it.

## Choices
- **Model:** default `claude-opus-4-8` (most capable). For high-volume/cheaper
  chat use `claude-sonnet-5`. Set it in the request body.
- **Persona:** edit the `system` prompt in the action to give the assistant its
  voice / house rules.
- **Snappier vs. smarter:** the base setup omits extended thinking for fast
  replies. For harder questions, add `"thinking": {"type": "adaptive"}` to the
  request body (adds latency).

## Notes
- The custom connector call is synchronous and fast (normal chat replies), so no
  async/polling is needed here — unlike the BD profile build, which is long-running
  (see `api/CONTRACT.md`).
- Keep the API key in the connection/secret store; never paste it into the agent
  or a message.
- This is the same connector pattern used for the BD Profile build endpoint — once
  this works, adding the BD build as a second action is straightforward.
