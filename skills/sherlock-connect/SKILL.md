---
name: sherlock-connect
description: Connect or reconnect to Stanford Sherlock using a shared SSH connection and macOS authentication dialogs. Use when Sherlock access expires or the user asks to connect without opening another terminal.
---

# Connect to Sherlock

Inspect existing project connection helpers or SSH aliases to find the SUNet ID
and shared socket. Reuse a working connection. If the username is unknown, ask
for the SUNet ID; passwords and Duo codes belong only in the authentication UI.

On macOS, resolve this helper relative to the skill and run:

```bash
python3 scripts/connect.py --user SUNET_ID
```

The helper opens native hidden-input dialogs through SSH's askpass mechanism.
The user enters their password and selects a Duo option there, then approves
the push on their device. Values pass directly to SSH; never ask for them in
chat, record them, or enable shell tracing. An unfamiliar host fingerprint must
be checked by the user before acceptance.

Use `--target dtn` for transfers. Use `--socket /existing/socket` to match an
existing transfer helper.
Login defaults to `~/.ssh/sherlock-USER.sock`; DTN defaults to
`~/.ssh/sherlock-dtn-USER.sock`. `--status` checks without prompting.

Keep the command tracked while authentication runs. Allow time for the native
dialog and Duo; report success only after the SSH master check passes. The
connection backgrounds after authentication and can be reused for eight hours
of idle time while this computer remains connected. Reconnection or site
reauthentication may still be necessary after sleep or network changes.

On Linux, supply an installed graphical askpass executable using `--askpass`.
In a headless environment, explain that interactive authentication is required
and use the user's existing connection workflow.

Print the shared socket and reuse command. This skill establishes access only;
job submission follows the user's separate request. Before subsequent work,
read Sherlock's `/etc/agents/AGENTS.md` when present. Use Slurm compute nodes for
computation and the DTN for bulk transfers. Existing Slurm jobs survive logout.

Reference: [Sherlock connection guidance](https://www.sherlock.stanford.edu/docs/getting-started/connecting/).
