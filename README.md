# Skills

Reusable skills for Claude Code and Codex. Edit the files here; installation
links each skill folder so changes remain in one place.

## Install

Requires Python 3.11 or later. From this repository:

```bash
python3 install.py claude
python3 install.py codex
python3 install.py both
```

Claude uses `~/.claude/skills`; Codex uses `~/.agents/skills`. Existing unrelated
skills are preserved. To install only selected skills:

```bash
python3 install.py both --skills uv-project focused-writing
```

Start a fresh agent session if the skills do not appear. Invoke `/uv-project`
in Claude Code or `$uv-project` in Codex, followed by your request.

## Included skills

| Skill | Use |
| --- | --- |
| writing-for-agents | Write useful agent instructions |
| codebase-design | Design small, understandable interfaces |
| teach | Learn through visual lessons and practice |
| prototype | Explore a design with a runnable demonstration |
| improve-codebase-architecture | Review architectural friction visually |
| grill-with-docs | Question a design and record decisions |
| wait-what | Re-explain something clearly |
| handoff | Prepare another session to continue |
| uv-project | Initialize a uv package with Google style guidance |
| sherlock-connect | Authenticate through macOS dialogs and share SSH |
| focused-writing | Create or open today's note in an Obsidian vault |

Examples: “Initialize a uv project in ./analysis”; “Connect to Sherlock as
SUNET_ID”; “Start focused writing.” Sherlock still requires Stanford MFA.

## Maintain

```bash
python3 -m unittest discover -s tests
```

Keep additions narrow. Imported skills retain their supporting resources and
invocation settings. See [attribution](THIRD_PARTY_NOTICES.md) for sources and
local adaptations. This installer targets local Claude Code and Codex sessions.

Skill locations follow the [Codex](https://developers.openai.com/codex/skills/)
and [Claude Code](https://code.claude.com/docs/en/skills) documentation.
