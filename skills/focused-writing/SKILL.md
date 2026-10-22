---
name: focused-writing
description: Start focused writing by creating or opening today's personal note in an Obsidian vault. Use for focused writing or a request to open the daily writing note.
---

# Focused writing

Open today's note in Obsidian, using local time and the path
`personal/MM.DD.YY.md` within the selected vault. Resolve the bundled script from
this skill directory and run:

```bash
python3 scripts/open_note.py
```

The script selects the single open vault registered with Obsidian, or the sole
registered vault if none is open. When selection is ambiguous, ask which vault
to use. `--vault /path/to/vault` or the `OBSIDIAN_VAULT` environment variable
sets an explicit location. Keep machine-specific preferences in the user's
environment, outside this repository.

`--date 10.21.26` opens a specific day. A new note contains only its date
heading. An existing note opens unchanged; repeated invocation never appends
duplicate headings.

Use the operating system's Obsidian URI handler to open the note. Report its
path and whether it was created or already existed. If Obsidian cannot open,
keep the note and report the opening failure accurately.

Keep the writing surface simple. If the user supplies an idea or writing task,
help with that request; do not add a template, schedule, prompts, or rewritten
prose to the note unless requested. Creating this skill is separate from
starting a writing session.
