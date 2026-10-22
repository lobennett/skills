# Sources and adaptations

## Matt Pocock skills

Eight skills are imported from [mattpocock/skills](https://github.com/mattpocock/skills)
at commit `5beb35b040e3de97e54fa9e386d7e42d15c295c2` (2026-10-19), under MIT.
The original license is included inside each imported skill.

Original paths: `skills/productivity/{writing-for-agents,teach,wait-what,handoff}`
and `skills/engineering/{codebase-design,prototype,improve-codebase-architecture,grill-with-docs}`.

Local adaptations:

* Tool-specific skill calls become relative file references.
* `grilling` and `domain-modeling` are bundled as internal references in
  `grill-with-docs`, with their format files. The architecture review carries
  these references and the design vocabulary to support individual installation.
* Optional subagents have an inline fallback when delegation is unavailable.
* Teaching uses a dedicated learning folder when invoked inside a software repo.
* Prototypes preserve the project's branch policy and scientific checks.
* Handoffs prefer the project's existing handoff location when one is specified.
* The invocation reference distinguishes Claude and Codex configuration.

## Google style

The uv initializer includes Google's `pylintrc`. Its copyright and Apache 2.0
license are retained beside the configuration and copied into generated
projects. Its canonical source is
<https://google.github.io/styleguide/pylintrc>.

The original custom skills are `uv-project`, `sherlock-connect`, and
`focused-writing`. The uv initializer uses `src/`, `uv_build`, Python 3.12,
dependency groups, pytest and coverage. The writing helper discovers the active
Obsidian vault or accepts a vault path supplied by the user.
