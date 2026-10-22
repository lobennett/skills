# Project defaults

Follow the full [Google Python guide][python], [shell guide][shell], and
[Markdown guide][markdown]. The generated `AGENTS.md` points to the same sources.

* Python: four-space indentation, 80-character lines with guide exceptions,
  clear names, grouped imports, useful type annotations, Google-style docstrings,
  specific exceptions, context managers, and guarded executable entry points.
* Shell: Bash, two-space indentation, quoted expansions, arrays, `[[ ... ]]`,
  local function variables, and checked command statuses. Prefer Python for
  complex scripts or scripts longer than about 100 lines.
* Documentation: one H1, descriptive headings and links, language-tagged code
  fences, blank lines around blocks, and prose wrapped at 80 characters. Keep
  the README under 300 words and describe the commands someone needs to use.

Package defaults are `src/`, `uv_build`, Python 3.12, `uv.lock`,
pytest/coverage/Pylint development dependencies, and an optional notebook group.
Use dependencies needed by the project. Prefer exact runtime requirements;
the lock records all resolved versions.

Keep package functions reusable, CLIs thin, and configuration in explicit
arguments or a TOML file when configuration is needed. Add folders only when
they contain useful material. See [uv project creation][uv] for alternatives.

[python]: https://google.github.io/styleguide/pyguide.html
[shell]: https://google.github.io/styleguide/shellguide.html
[markdown]: https://google.github.io/styleguide/docguide/style.html
[uv]: https://docs.astral.sh/uv/concepts/projects/init/
