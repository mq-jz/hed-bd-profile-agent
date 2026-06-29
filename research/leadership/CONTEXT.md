# Research Flow: Leadership

You are one of the five parallel research sub-agents in Stage B. Work only within
this folder. Do not read sibling research/* folders. Do not stop for approval;
finish and report done.

This flow covers the people. It owns: **Key Leaders, Grants Office.**

## Inputs
| File | Load |
|------|------|
| `00-intake/output/intake.md` | Identity + named contacts/leaders + notes |
| `reference/template.md` | Key Leaders + Grants Office field shape |
| `reference/patterns.md` | Key-leader detail + Grants-Office "or absence" |
| `reference/voice.md` | Full |
| `reference/sources.md` | "leadership flow" rows only |

This flow has no seeded fetch - it is web research. Start from the institution's
leadership pages, the office of the president/provost, the sponsored-programs /
research office directory, and LinkedIn.

## Process

1. **Key Leaders**: profile the leaders that matter for a BD pitch -
   President, Provost, VP/Chief of Institutional Advancement, the
   sponsored-programs / research lead, and the **point of contact named in
   intake** (mark them *Point of Contact*). For each: name + credential + title,
   reverse-chronological Prior Experience (org - title, years), Education
   (degree, field, institution, year), a 2-4 sentence biography emphasizing
   funding/leadership relevance, and a LinkedIn line. Match the exemplar's depth.

2. **Grants Office**: the grants / sponsored-programs / research office - its
   name, a one-line mission, and the full staff list (name, title). Note if the
   M&Q point of contact sits here. If there is NO such office, say so and name
   who handles grants (e.g. Advancement, the Accounting Office) - see patterns.md.

Confirm titles and tenure dates from the institution site; tag uncertain dates
`[verify]`. Do not invent prior roles, degrees, or years - a wrong bio in front
of a client is worse than a `[verify]` gap.

## Output: `research/leadership/output/leadership.md`

```
===== SECTION: Key Leaders =====
<one entry per leader, bullets for Prior Experience + Education, a short bio,
 a LinkedIn line; mark the Point of Contact>

===== SECTION: Grants Office =====
<office name + one-line mission + staff list, or who handles grants if none>
```

Must NOT include: `#` headers, tables, bold/braces; fabricated roles, degrees,
dates, or names (tag `[verify]`); any section other than the two above. Report
"leadership: done" with a one-line summary.
