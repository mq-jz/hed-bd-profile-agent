# Phase 3: Compile to .docx (mechanical)

Only after the partner approves `02-assemble/output/profile-draft.md`, compile it
into the Word deliverable.

```
python 03-compile/build_docx.py
```

Pure parse of the approved draft into a styled .docx in canonical template
order - no model call, so it cannot hallucinate or time out. Reads the draft's
`## Section` headings via `lib/profile.py:split_draft` (the same lib the
assembler writes with, so they cannot drift), renders paragraphs and Markdown
`- ` bullets into Word heading/bullet styles.

Writes `03-compile/output/BD_Profile_<institution>_<date>.docx`. The filename is
dated, so re-compiling preserves prior versions rather than clobbering them.

If `[verify]` / `[inferred]` tags remain in the draft, the script still compiles
but warns with a count - those tags will appear verbatim in the Word document.
Resolve them in the draft and recompile for a clean deliverable.

Requires `python-docx` (`pip install -r requirements.txt`).
