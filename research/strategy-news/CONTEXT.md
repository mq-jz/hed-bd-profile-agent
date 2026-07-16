# Research Flow: Strategy & News

You are one of the five parallel research sub-agents in Stage B. Work only within
this folder. Do not read sibling research/* folders. Do not stop for approval;
finish and report done.

This flow covers direction and programs. It owns: **Strategic Plan, Mission
Statement, Vision, Values, Centers and Institutes, Academic Programs, Recent
News.** (Mission / Vision / Values are SEPARATE sections; Vision and Centers are
optional - omit when the institution has none.)

## Inputs
| File | Load |
|------|------|
| `00-intake/output/intake.md` | Identity + notes |
| `reference/template.md` | Field shape for the sections |
| `reference/patterns.md` | Naming + optional-section conventions |
| `reference/voice.md` | Full |
| `reference/sources.md` | "strategy-news flow" rows only |

This flow is web research from the institution's own site (strategic plan,
mission/values, centers index, academic catalog, newsroom).

## Process

1. **Strategic Plan**: analyze it **through the M&Q lens** - what it says about
   funding capacity, research growth, sponsored programs, government relations,
   advancement. Link the plan. If the plan is in development, say so and
   summarize the stated process and priorities.

2. **Mission Statement / Vision / Values** (separate sections): quote or closely
   paraphrase. Values as bullets. Omit Vision if the institution publishes none.

3. **Centers and Institutes**: bullet list with a one-line descriptor each; flag
   NSF-funded / research centers that matter for funding.

4. **Academic Programs**: Undergraduate and Graduate lists (degree - program).
   For a large institution, abbreviate to notable/relevant programs and say you
   abbreviated.

5. **Recent News**: 3-6 recent items formatted for skimming and matching the
   house format in the `documents/` profiles (see `patterns.md`). Each item is a
   bullet: a headline-forward lead + date, a tight 1-2 sentence summary, and
   ALWAYS the link to the article summarized. Prefer funding / research /
   leadership / advancement news relevant to M&Q; no routine filler.

## Output: `research/strategy-news/output/strategy-news.md`

```
===== SECTION: Strategic Plan =====
<M&Q-relevant analysis + link, or "X has not published a strategic plan">

===== SECTION: Mission Statement =====
<mission statement>

===== SECTION: Vision =====
<vision statement - omit this whole block if none>

===== SECTION: Values =====
<values bullets>

===== SECTION: Centers and Institutes =====
<bullets, one descriptor each - omit this block if none>

===== SECTION: Academic Programs =====
<Undergraduate Majors bullets; Graduate bullets>

===== SECTION: Recent News =====
<3-6 skimmable bullets: headline lead + date, tight summary, and a link to the
 article summarized>
```

Must NOT include: `#` headers, tables, bold/braces; fabricated program names,
centers, or news items with invented dates (tag `[verify]`); any section other
than those above. Report "strategy-news: done" with a one-line summary.
