"""Exercise installation, project creation, note preservation, and SSH setup."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_module("installer", "install.py")
notes = load_module(
    "notes", "skills/focused-writing/scripts/open_note.py"
)
sherlock = load_module(
    "sherlock", "skills/sherlock-connect/scripts/connect.py"
)
project = load_module("project", "skills/uv-project/scripts/init_project.py")


class InstallationTests(unittest.TestCase):
    def test_both_agents_and_idempotent_install(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            first = installer.install("both", [], home)
            second = installer.install("both", [], home)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 22)
            for link in first:
                self.assertTrue(link.is_symlink())
                self.assertTrue((link / "SKILL.md").is_file())
            self.assertEqual(len(list((ROOT / "skills").rglob("SKILL.md"))), 11)

    def test_conflict_prevents_partial_install(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            existing = home / ".claude/skills/teach"
            existing.mkdir(parents=True)
            original = existing / "SKILL.md"
            original.write_text("user's skill")
            with self.assertRaises(ValueError):
                installer.install("both", ["handoff", "teach"], home)
            self.assertEqual(original.read_text(), "user's skill")
            self.assertFalse((home / ".agents").exists())
            self.assertFalse((existing.parent / "handoff").exists())

    def test_unknown_skill_and_individual_install(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            with self.assertRaises(ValueError):
                installer.install("both", ["unknown"], home)
            links = installer.install(
                "codex", ["improve-codebase-architecture"], home
            )
            self.assertEqual(len(links), 1)
            reference = links[0] / "references/design/design.md"
            self.assertTrue(reference.is_file())


class NoteTests(unittest.TestCase):
    def test_open_vault_is_selected_without_a_fixed_name(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config = home / "Library/Application Support/obsidian/obsidian.json"
            config.parent.mkdir(parents=True)
            active = home / "Writing"
            config.write_text(json.dumps({"vaults": {
                "first": {"path": str(home / "Archive")},
                "second": {"path": str(active), "open": True},
            }}))
            with mock.patch.object(notes.Path, "home", return_value=home):
                with mock.patch.object(notes.sys, "platform", "darwin"):
                    with mock.patch.dict(os.environ, {}, clear=True):
                        self.assertEqual(notes.find_vault(), active.resolve())

    def test_multiple_open_vaults_require_a_choice(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            config = home / "Library/Application Support/obsidian/obsidian.json"
            config.parent.mkdir(parents=True)
            config.write_text(json.dumps({"vaults": {
                "first": {"path": str(home / "First"), "open": True},
                "second": {"path": str(home / "Second"), "open": True},
            }}))
            with mock.patch.object(notes.Path, "home", return_value=home):
                with mock.patch.object(notes.sys, "platform", "darwin"):
                    with mock.patch.dict(os.environ, {}, clear=True):
                        with self.assertRaises(ValueError):
                            notes.find_vault()

    def test_environment_overrides_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            with mock.patch.dict(os.environ, {"OBSIDIAN_VAULT": str(vault)}):
                self.assertEqual(notes.find_vault(), vault)

    def test_repeated_open_preserves_text(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            (vault / ".obsidian").mkdir()
            note, created = notes.prepare_note(vault, "10.21.26")
            self.assertTrue(created)
            self.assertEqual(note.name, "10.21.26.md")
            note.write_text("My unfinished writing\n")
            again, created = notes.prepare_note(vault, "10.21.26")
            self.assertFalse(created)
            self.assertEqual(again.read_text(), "My unfinished writing\n")

    def test_invalid_date_and_unknown_vault(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            with self.assertRaises(ValueError):
                notes.prepare_note(vault, "10.21.26")
            (vault / ".obsidian").mkdir()
            for day in ("../../outside", "02.30.26", "1.2.26"):
                with self.assertRaises(ValueError):
                    notes.prepare_note(vault, day)
            self.assertFalse((vault / "personal").exists())

    def test_uri_encodes_file_path(self):
        note = Path("/tmp/Example & notes/personal/10.21.26.md")
        with mock.patch.object(notes.sys, "platform", "darwin"):
            with mock.patch.object(notes.subprocess, "run") as run:
                notes.open_note(note)
        command = run.call_args.args[0]
        self.assertEqual(command[0], "open")
        self.assertEqual(
            parse_qs(urlparse(command[1]).query)["path"], [str(note)]
        )


class SherlockTests(unittest.TestCase):
    def test_reuses_master_without_authentication(self):
        with mock.patch.object(sherlock, "master_ready", return_value=True):
            with mock.patch.object(sherlock.subprocess, "run") as run:
                self.assertTrue(sherlock.connect(
                    "example", "login", Path("/tmp/socket")
                ))
                run.assert_not_called()

    def test_status_never_authenticates(self):
        with mock.patch.object(sherlock, "master_ready", return_value=False):
            with mock.patch.object(sherlock.subprocess, "run") as run:
                self.assertFalse(sherlock.connect(
                    "example", "login", Path("/tmp/socket"), status_only=True
                ))
                run.assert_not_called()

    def test_new_dtn_master_uses_askpass_and_no_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            socket = Path(directory) / "socket"
            askpass = ROOT / "skills/sherlock-connect/scripts/askpass.applescript"
            with mock.patch.object(
                sherlock, "master_ready", side_effect=[False, True]
            ):
                with mock.patch.object(sherlock.subprocess, "run") as run:
                    self.assertTrue(sherlock.connect(
                        "example", "dtn", socket, askpass
                    ))
            command = run.call_args.args[0]
            self.assertIn("-fMN", command)
            self.assertIn("StrictHostKeyChecking=ask", command)
            self.assertEqual(command[-1], "example@dtn.sherlock.stanford.edu")
            self.assertEqual(run.call_args.kwargs["stdin"], subprocess.DEVNULL)
            environment = run.call_args.kwargs["env"]
            self.assertEqual(environment["SSH_ASKPASS_REQUIRE"], "force")
            self.assertEqual(environment["SSH_ASKPASS"], str(askpass.resolve()))

    def test_failure_never_reports_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            askpass = ROOT / "skills/sherlock-connect/scripts/askpass.applescript"
            with mock.patch.object(sherlock, "master_ready", return_value=False):
                with mock.patch.object(
                    sherlock.subprocess, "run",
                    side_effect=subprocess.CalledProcessError(255, "ssh"),
                ):
                    with self.assertRaises(subprocess.CalledProcessError):
                        sherlock.connect(
                            "example", "login", Path(directory) / "socket",
                            askpass,
                        )


class ProjectTests(unittest.TestCase):
    def test_existing_content_is_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            original = target / "keep.txt"
            original.write_text("keep")
            with mock.patch.object(project.subprocess, "run") as run:
                with self.assertRaises(ValueError):
                    project.initialize(target, "demo", "Example")
                run.assert_not_called()
            self.assertEqual(original.read_text(), "keep")

    def test_real_uv_scaffold(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "demo"
            project.initialize(
                target, "demo-package", "Readable demonstration.", sync=False
            )
            document = tomllib.loads((target / "pyproject.toml").read_text())
            self.assertEqual(document["build-system"]["build-backend"], "uv_build")
            self.assertEqual(document["project"]["requires-python"], ">=3.12,<3.13")
            self.assertTrue((target / "src/demo_package/__init__.py").is_file())
            self.assertTrue((target / "tools/LICENSE-google").is_file())
            self.assertFalse((target / ".git").exists())
            self.assertFalse((target / "uv.lock").exists())


if __name__ == "__main__":
    unittest.main()
