# Working on these skills

The repository contains eleven skills. Keep imported skill names and attribution.
Record changes to imported behavior in `THIRD_PARTY_NOTICES.md`.

Write short, specific descriptions that identify when a skill applies. Keep
supporting material inside its skill folder so individual installation works.
Use relative resource paths and portable tool instructions for Claude and Codex.

Custom skills should stay under 500 words in their main instructions. Prefer
instructions; add scripts when repeatable filesystem or authentication behavior
needs reliable execution. Test scripts in temporary directories. Never include
passwords, tokens, personal notes, or generated projects in this repository.

Use Google Python, shell, and Markdown style. Run
`python3 -m unittest discover -s tests` after changing executable helpers.
Preserve existing installations and user documents. Keep one authoritative copy
of each skill, exposed through directory symlinks by `install.py`.
