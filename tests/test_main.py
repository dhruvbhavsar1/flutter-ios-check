"""Tests for concise scan and detailed plugin CLI output."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from main import main


class MainTests(unittest.TestCase):
    def run_cli(self, arguments: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(arguments)
        return exit_code, output.getvalue()

    def create_project(self, root: Path, *, complete_ios: bool = True) -> None:
        (root / "pubspec.yaml").write_text(
            "name: example_app\n"
            "version: 1.0.0+1\n"
            "environment:\n"
            '  sdk: ">=3.0.0 <4.0.0"\n'
            "dependencies:\n"
            "  firebase_core: ^3.0.0\n"
            "  camera: ^0.11.0\n"
            "  custom_package: ^1.0.0\n",
            encoding="utf-8",
        )
        if complete_ios:
            (root / "ios" / "Runner").mkdir(parents=True)
            (root / "ios" / "Podfile").touch()
            (root / "ios" / "Runner" / "Info.plist").touch()

    def test_default_scan_is_concise_and_does_not_list_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            self.create_project(project_path)

            exit_code, output = self.run_cli(["scan", str(project_path)])

            self.assertEqual(exit_code, 0)
            for expected in (
                "\U0001f34e Flutter iOS Readiness Report",
                "Project: example_app",
                "Version: 1.0.0+1",
                "Status: READY",
                "Readiness Score: 93/100",
                "\u2705 iOS Folder",
                "\u2705 Info.plist",
                "\u2705 Podfile",
                "Known Compatible: 1",
                "Known Warning: 1",
                "Unknown: 1",
                "Result: READY FOR iOS BUILD",
            ):
                self.assertIn(expected, output)
            self.assertNotIn("firebase_core\n", output)
            self.assertNotIn("Plugin Detected", output)
            self.assertLessEqual(len(output.splitlines()), 30)

    def test_legacy_path_argument_still_runs_scan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            self.create_project(project_path)

            exit_code, output = self.run_cli([str(project_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn("Flutter iOS Readiness Report", output)

    def test_missing_files_show_critical_issues_and_recommendations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            self.create_project(project_path, complete_ios=False)

            exit_code, output = self.run_cli(["scan", str(project_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn("Status: NOT READY", output)
            self.assertIn("\U0001f6a8 Missing iOS Folder", output)
            self.assertIn("\u274c Missing Info.plist", output)
            self.assertIn("\u274c Missing Podfile", output)
            self.assertIn("flutter create .", output)
            self.assertIn("Result: NOT READY FOR iOS BUILD", output)

    def test_plugins_command_groups_plugins_without_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            self.create_project(project_path)

            exit_code, output = self.run_cli(["plugins", str(project_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn("Known Compatible (1)", output)
            self.assertIn("\u2705 firebase_core", output)
            self.assertIn("Known Warning (1)", output)
            self.assertIn("\u26a0 camera", output)
            self.assertIn("Unknown (1)", output)
            self.assertIn("\u2022 custom_package", output)
            self.assertEqual(output.count("firebase_core"), 1)

    def test_plugin_filters_show_only_requested_classification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            self.create_project(project_path)

            _, known_output = self.run_cli(
                ["plugins", str(project_path), "--known"]
            )
            _, unknown_output = self.run_cli(
                ["plugins", str(project_path), "--unknown"]
            )

            self.assertIn("firebase_core", known_output)
            self.assertIn("camera", known_output)
            self.assertNotIn("custom_package", known_output)
            self.assertIn("custom_package", unknown_output)
            self.assertNotIn("firebase_core", unknown_output)

    def test_verbose_scan_displays_plugin_metadata_and_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            self.create_project(project_path)

            exit_code, output = self.run_cli(
                ["scan", str(project_path), "--verbose"]
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("Detailed Plugin Analysis", output)
            self.assertIn("firebase_core | Firebase | Compatible", output)
            self.assertIn("camera | Permission | Warning", output)
            self.assertIn("Diagnostics", output)

    def test_validation_errors_preserve_nonzero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_path = Path(temporary_directory) / "missing"

            exit_code, output = self.run_cli(["scan", str(missing_path)])

            self.assertEqual(exit_code, 1)
            self.assertEqual(output, "\u274c Project folder not found\n")


if __name__ == "__main__":
    unittest.main()
