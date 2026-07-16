# Demo chat transcript — BD Profile Agent (Teams)

This is the script as implemented in `ui/live.html`. Edit the dialogue, then
tell Claude "apply the demo script" to sync changes back. Notes in [brackets]
are staging directions, not spoken text. Timestamps are cosmetic.

Cast: **Kai** (M&Q analyst) · **Agent** (BD Profile Agent bot) · Jess G. (VP,
appears only as the quoted inbound ask).

Flow: intake in chat → watch the run (3 steps, unattended, ends at the compiled
document) → finished .docx lands back in chat. No pricing step, no review gate.

---

## Act 1 — Intake (in Teams chat)

[System line, gray, under the date divider]
> BD Profile Agent was added to the chat. The agent walks intake with you, runs
> five research agents in parallel, and returns the deliverables here.

**Kai** (2:10 PM) [auto-types; presenter presses Send]
> New profile request from Jess for Union College.

[Attached to Kai's message: "Grant strategy support for Union.eml" — the
 inbound email from Scott Rava. Visual chip, right-aligned; the agent files its
 content verbatim on the identity card below.]

**Agent** (2:10 PM)
> On it. Starting Stage A intake for Union College — resolving canonical
> identity against College Scorecard, the IRS exempt-org file, and the Carnegie
> Classification…

**Agent** (2:11 PM)
> Here is what I resolved. Approve it and the intake is frozen — Stage B reads
> it but never rewrites it.

[Identity card. Title: "STAGE A · Intake — canonical identity". Rows:]
> - Institution: Union College
> - Location: Schenectady, NY
> - Control: Private, nonprofit
> - EIN: 14-1338580
> - College Scorecard: #196866
> - Carnegie: Baccalaureate: Arts & Sciences Focus
>
> **Pitch Origination** — inbound email, filed verbatim:
> > From: Scott Rava, VP for College Relations, Union College
> > To: Jess G. (McAllister & Quinn) · Subject: Grant strategy support for Union
> > *"Jess — good to connect last week. With President Kiss beginning her first
> > full year, we are taking a fresh look at how Union pursues federal and
> > foundation funding, and we would like to hear how McAllister & Quinn works
> > with colleges like ours. Could your team walk us through your approach on a
> > call the week of July 21? — Scott"*
>

[Card button: "✓ Looks right — approve" · after click: "✓ Approved by Kai —
 identity locked"]

**Agent** (2:12 PM)
> Identity locked. A few quick questions so the profile lands right — first, is
> there a meeting or call on the calendar with Union yet?

**Kai** (2:12 PM) [auto-typed]
> Jess has an intro call with their leadership on July 21. She wants this in
> hand a few days before.

**Agent** (2:12 PM)
> Noted — intro call July 21. Who do you expect on their side, or want the
> profile to focus on?

**Kai** (2:12 PM) [auto-typed]
> Scott Rava in College Relations set it up. President Kiss may join — she is
> new, so cover the transition.

**Agent** (2:13 PM)
> Good context — new president, college-relations entry. Anything else to
> clarify before I freeze the intake: angle, emphasis, things to avoid?

**Kai** (2:13 PM) [auto-typed]
> Emphasize the federal funding picture and any earmark opening. Full profile
> otherwise.

**Agent** (2:14 PM)
> Intake frozen ✓. Captured: intro call July 21 ·
> contact: Scott Rava, College Relations; President Kiss may join · emphasis:
> federal funding picture, leadership transition, earmark opening. Kicking off
> Stage B — five independent research agents run in parallel, unattended, all
> the way to the finished Word document (~15 min). None of them can rewrite the
> intake or read each other.

[Run card. Title: "STAGE B · BD Profile run — Union College". Body:]
> 1 · Warm fetches — Scorecard · ProPublica 990 · USASpending · Congress.gov
> 2 · **Five research agents in parallel** — institutional profile, financials,
>     federal funding, leadership, strategy & news
> 3 · Assemble the draft and **compile the dated Word document** — no
>     touchpoints in between

[Run card footer: "▶ Watch the run live" · "~15 min unattended, end to end ·
 replayed here in 3 steps"]

## Act 2 — [Dashboard replay: Intake & fetches → Parallel research → Assemble &
compile. Timer runs to 15:00 "profile delivered"; Kai's status pill stays
"back on client work · questions asked: 0" the whole run. Ends with
"Done — back to Teams ›".]

## Act 3 — Delivery (back in Teams)

**Agent** (2:26 PM)
> Profile complete — 15:00 of unattended runtime. The five research agents
> returned their sections, the draft assembled in template order, and the
> branded Word document is compiled. One flag before the call: Union's finance
> seat is in transition — CFO Scott Jones left for Knox College in February,
> and John Cozzolino is serving as Interim VP for Finance. Anything I could not
> confirm is flagged [verify] in the document.

[File card: "BD_Profile_Union_College_2026-07-16_UPDATED.docx" · "BD Profile ·
 compiled, dated, ready to send" · downloads the improved-formatting Union .docx]

**Kai** (2:27 PM) [auto-typed]
> Perfect — thanks. Sending it over to Jess now.

**Agent** (2:27 PM)
> 👍 Anything still tagged [verify] in the draft is a flagged gap, not a guess.
> When you want a refresh, just say "rerun research" and
> Stage B re-runs against the frozen intake.

---

## Where each line lives in `ui/live.html`

| Transcript element | Source |
|---|---|
| Kai's auto-typed messages | `COMPOSER_SCRIPT` (beats 0, 3, 4, 5, 90) + `PITCH`/`THANKS` |
| Agent messages, Act 1 | beat chain `beat===1,2,3,4,5,6` |
| Identity card rows / origination note | `IDENT_ROWS` + `IdentityCard` (`JESS_ASK`) |
| Run card | `RunCard` |
| Act 3 message + docx card | the `delivered` effect |
| Wrap-up | beat `91` |
| Dashboard captions | `NARRATION`, `TERM`, `STEP_LABELS` |
