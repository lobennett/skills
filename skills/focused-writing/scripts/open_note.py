"""Create or open a dated personal note in an Obsidian vault."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlencode


def find_vault() -> Path:
    """Choose an explicit vault, the single open vault, or the sole vault."""
    explicit = os.environ.get("OBSIDIAN_VAULT")
    if explicit:
        return Path(explicit).expanduser()
    home = Path.home()
    if sys.platform == "darwin":
        config = home / "Library/Application Support/obsidian/obsidian.json"
    elif sys.platform == "win32":
        config = Path(os.environ.get("APPDATA", home))
        config = config / "obsidian/obsidian.json"
    else:
        config = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
        config = config / "obsidian/obsidian.json"
    if config.is_file():
        data = json.loads(config.read_text())
        vaults = list(data.get("vaults", {}).values())
        opened = [item for item in vaults if item.get("open")]
        candidates = opened or vaults
        matches = {
            Path(item["path"]).resolve()
            for item in candidates
        }
        if len(matches) == 1:
            return matches.pop()
        if len(matches) > 1:
            raise ValueError("Multiple Obsidian vaults; specify --vault")
    raise ValueError("No Obsidian vault found; specify --vault")


def prepare_note(vault: Path, day: str) -> tuple[Path, bool]:
    """Create a missing daily note or preserve an existing note verbatim."""
    parsed = datetime.strptime(day, "%m.%d.%y")
    if parsed.strftime("%m.%d.%y") != day:
        raise ValueError("Use a date formatted as MM.DD.YY")
    vault = vault.expanduser().resolve()
    if not (vault / ".obsidian").is_dir():
        raise ValueError(f"Not an Obsidian vault: {vault}; specify --vault")
    folder = vault / "personal"
    folder.mkdir(exist_ok=True)
    if not folder.resolve().is_relative_to(vault):
        raise ValueError("The personal folder must stay inside the vault")
    note = folder / f"{day}.md"
    if note.is_symlink():
        raise ValueError("Daily note is a symlink; inspect it before opening")
    try:
        with note.open("x", encoding="utf-8") as stream:
            stream.write(f"# {day}\n\n")
        created = True
    except FileExistsError:
        if not note.is_file():
            raise ValueError(f"Daily note is not a file: {note}") from None
        created = False
    return note, created


def open_note(note: Path) -> None:
    """Open the exact note through the registered Obsidian URI handler."""
    uri = "obsidian://open?" + urlencode({"path": str(note)})
    if sys.platform == "win32":
        os.startfile(uri)
    else:
        command = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.run([command, uri], check=True)


def main() -> None:
    """Create the daily note and launch Obsidian unless previewing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path)
    parser.add_argument("--date", default=datetime.now().astimezone().strftime(
        "%m.%d.%y"
    ))
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    try:
        note, created = prepare_note(args.vault or find_vault(), args.date)
        action = "Created" if created else "Existing"
        print(f"{action}: {note}")
        if not args.no_open:
            open_note(note)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Could not finish opening the note: {error}\n")


if __name__ == "__main__":
    main()
