---
name: uv-project
description: Initialize a Python package with uv, a src layout, tests, and Google Python, shell, and documentation conventions. Use when creating a uv project or adopting these defaults in an existing project.
---

# Initialize a uv project

Inspect the destination and applicable agent instructions. Infer the package name
and purpose from the request. Default to Python 3.12 unless the project needs
another version. Reuse existing configuration when adapting a project; the helper
only accepts a new or empty directory.

Run the bundled initializer, resolving its path relative to this skill:

```bash
uv run --no-project --python 3.12 scripts/init_project.py /path/to/project \
  --name package-name --description "What this package does"
```

It creates a `src/` package, a `uv_build` configuration, a bounded Python minor
version, Google Pylint configuration, pytest/coverage settings, and concise
`README.md`, `AGENTS.md`, and `CLAUDE.md`. It then locks and syncs dependencies.
Use `--notebook marimo` or `--notebook jupyter` when requested. A notebook is an
optional dependency group, not a mandatory part of every package.

Add only dependencies needed for the task, using `uv add --exact`. Runtime
requirements belong in `project.dependencies`; development tools and notebook
tools have separate groups. Keep `uv.lock` in version control and `.venv/`,
build outputs, caches, and generated results out. Use `uv run` for Python tools.

Read the linked [style guidance](references/style.md) when writing code or docs.
Use useful annotations and Google-style docstrings, small CLI entry points,
configuration separate from computation, and tests of actual behavior. Keep
research computations in the package so notebooks can call them.

Validate the generated project with `uv run pylint --rcfile=tools/google-pylintrc
src`, `uv build`, and the applicable tests. An empty `tests/` directory contains
no tests yet; do not report it as a passing suite. Check authored shell scripts
with `bash -n` and ShellCheck when installed. End with the path, commands, and
validation results.
