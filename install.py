"""Link selected skills into the user's Claude Code or Codex directories."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DESTINATIONS = {"claude": ".claude/skills", "codex": ".agents/skills"}


def install(agent: str, names: list[str], home: Path) -> list[Path]:
    """Install skills without replacing unrelated directories or links.

    Args:
        agent: Claude, Codex, or both.
        names: Skill directory names; an empty list installs all skills.
        home: User home directory, injectable for isolated tests.

    Returns:
        Paths to the requested installations, including existing correct links.

    Raises:
        ValueError: An unknown skill or conflicting installation exists.
    """
    available = {
        path.parent.name: path.parent
        for path in (ROOT / "skills").glob("*/SKILL.md")
    }
    selected = sorted(set(names or available))
    unknown = set(selected) - available.keys()
    if unknown:
        unknown_names = ", ".join(sorted(unknown))
        raise ValueError(f"Unknown skills: {unknown_names}")
    agents = list(DESTINATIONS) if agent == "both" else [agent]
    links = [
        (home / DESTINATIONS[target] / name, available[name])
        for target in agents for name in selected
    ]
    for destination, source in links:
        if destination.is_symlink() and destination.resolve() == source:
            continue
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"Existing installation preserved: {destination}")
    for destination, source in links:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.is_symlink():
            destination.symlink_to(source, target_is_directory=True)
    return [destination for destination, _ in links]


def main() -> None:
    """Install all skills or a selected subset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agent", choices=["claude", "codex", "both"])
    parser.add_argument("--skills", nargs="+", default=[])
    args = parser.parse_args()
    try:
        for destination in install(args.agent, args.skills, Path.home()):
            print(destination)
    except ValueError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
