# Project conventions

Use `uv run` for Python commands and tools. Add runtime requirements with
`uv add --exact`; keep development and notebook tools in their dependency groups.
Commit `uv.lock` and use `uv sync --locked` to reproduce the environment.

## Python

Follow the [Google Python style guide][python]: four-space indentation,
80-character lines with guide exceptions, grouped imports, useful type
annotations, Google-style docstrings, specific exceptions, and context managers.
Use guarded entry points for executables. Put reusable computation in `src/`,
keep command-line interfaces small, and test observable behavior in `tests/`.

## Shell

Follow the [Google Shell style guide][shell]: Bash, two-space indentation,
quoted expansions, arrays, local function variables, and checked exit statuses.
Use Python for complex logic or scripts exceeding about 100 lines.

## Documentation

Follow the [Google Markdown style guide][markdown]: one H1, descriptive links
and headings, fenced code with language tags, blank lines around blocks, and
prose wrapped at 80 characters. Keep the README under 300 words.

## Validation

Run relevant tests with `uv run pytest`, lint with
`uv run pylint --rcfile=tools/google-pylintrc src`, and verify packaging with
`uv build`. Check changed shell scripts with `bash -n` and ShellCheck when
available. Linters supplement review; they do not establish scientific validity.

[python]: https://google.github.io/styleguide/pyguide.html
[shell]: https://google.github.io/styleguide/shellguide.html
[markdown]: https://google.github.io/styleguide/docguide/style.html
