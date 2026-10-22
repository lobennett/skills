"""Create a small uv package using the user's preferred project structure."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tomllib


ASSETS = Path(__file__).resolve().parents[1] / "assets"


def initialize(
    destination: Path,
    name: str,
    description: str,
    python: str = "3.12",
    notebook: str | None = None,
    sync: bool = True,
) -> Path:
    """Create and optionally install a package in a new or empty directory.

    Args:
        destination: Directory for the new project.
        name: Lowercase, hyphenated project name.
        description: Short explanation of the package's purpose.
        python: Python major.minor version.
        notebook: Optional marimo or jupyter dependency group.
        sync: Whether to resolve dependencies and create the environment.

    Returns:
        Absolute project directory.

    Raises:
        ValueError: A name, version, or destination is unsuitable.
        subprocess.CalledProcessError: uv initialization or installation fails.
    """
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", name):
        raise ValueError("Use a lowercase package name separated by hyphens")
    if not re.fullmatch(r"3\.(?:1[1-9]|[2-9][0-9])", python):
        raise ValueError("Specify Python major.minor, at least 3.11")
    if notebook not in (None, "marimo", "jupyter"):
        raise ValueError("Notebook must be marimo or jupyter")
    if not description.strip() or "\n" in description:
        raise ValueError("Provide a one-line project description")
    destination = destination.expanduser().absolute()
    if destination.is_symlink():
        raise ValueError("Choose a real directory, not a symlink")
    if destination.exists() and (
        not destination.is_dir() or any(destination.iterdir())
    ):
        raise ValueError("Destination must be new or empty")
    subprocess.run(
        ["uv", "init", "--bare", "--lib", "--build-backend", "uv",
         "--python", python, "--vcs", "none", "--no-workspace",
         "--author-from", "none", "--name", name, str(destination)],
        check=True,
    )
    project_file = destination / "pyproject.toml"
    build = tomllib.loads(project_file.read_text())["build-system"]
    module = name.replace("-", "_")
    next_minor = int(python.split(".")[1]) + 1
    notebook_group = ""
    if notebook:
        requirements = ["marimo", "ipykernel"] if notebook == "marimo" else [
            "jupyterlab", "ipykernel"
        ]
        notebook_group = f"notebooks = {json.dumps(requirements)}\n"
    project_file.write_text(f"""[project]
name = "{name}"
version = "0.1.0"
description = {json.dumps(description)}
readme = "README.md"
requires-python = ">={python},<3.{next_minor}"
dependencies = []

[dependency-groups]
dev = ["pytest>=8,<10", "coverage>=7,<8", "pylint>=4,<5"]
{notebook_group}
[build-system]
requires = {json.dumps(build["requires"])}
build-backend = {json.dumps(build["build-backend"])}

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["{module}"]

[tool.coverage.report]
show_missing = true
""")
    package = destination / "src" / module
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(f'"""{name} package."""\n')
    (destination / "tests").mkdir()
    (destination / ".python-version").write_text(python + "\n")
    (destination / ".gitignore").write_text(
        ".venv/\n__pycache__/\n.pytest_cache/\n.coverage*\nhtmlcov/\n"
        "dist/\nresults/\n.DS_Store\n"
    )
    (destination / "README.md").write_text(
        f"# {name}\n\n{description}\n\n"
        "```bash\nuv sync\nuv run pytest\n"
        "uv run pylint --rcfile=tools/google-pylintrc src\nuv build\n```\n\n"
        f"Put reusable code in `src/{module}/` and tests in `tests/`.\n"
        "Add the first behavior test before expecting pytest to pass.\n"
        "Use `uv add --exact <dependency>` to add runtime requirements.\n"
        + ("Use `uv sync --group notebooks` for notebook tools.\n"
           if notebook else "")
    )
    shutil.copyfile(ASSETS / "AGENTS.md", destination / "AGENTS.md")
    (destination / "CLAUDE.md").write_text("@AGENTS.md\n")
    tools = destination / "tools"
    tools.mkdir()
    for filename in ("google-pylintrc", "LICENSE-google"):
        shutil.copyfile(ASSETS / filename, tools / filename)
    if sync:
        subprocess.run(["uv", "lock"], cwd=destination, check=True)
        command = ["uv", "sync", "--locked"]
        if notebook:
            command.extend(["--group", "notebooks"])
        subprocess.run(command, cwd=destination, check=True)
    return destination


def main() -> None:
    """Parse project settings and initialize the destination."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--description", required=True)
    parser.add_argument("--python", default="3.12")
    parser.add_argument("--notebook", choices=["marimo", "jupyter"])
    parser.add_argument("--no-sync", action="store_true")
    args = parser.parse_args()
    try:
        result = initialize(
            args.directory, args.name or args.directory.absolute().name,
            args.description, args.python, args.notebook, not args.no_sync,
        )
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Initialization stopped: {error}\n")
    print(result)
    if args.no_sync:
        print("Dependencies are not installed. Run uv lock and uv sync here.")


if __name__ == "__main__":
    main()
