"""Tests for the command-line interface."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from main import main


class MainTests(unittest.TestCase):
    def run_cli(self, project_path: Path) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main([str(project_path)])
        return exit_code, output.getvalue()

    def test_success_output_contains_project_information_and_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "name: example_app\n"
                "version: 1.0.0+1\n"
                "environment:\n"
                '  sdk: ">=3.0.0 <4.0.0"\n'
                "dependencies:\n"
                "  camera: ^0.11.0\n"
                "  custom_package: ^1.0.0\n",
                encoding="utf-8",
            )
            (project_path / "ios" / "Runner").mkdir(parents=True)
            (project_path / "ios" / "Podfile").touch()
            (project_path / "ios" / "Runner" / "Info.plist").touch()

            exit_code, output = self.run_cli(project_path)

            self.assertEqual(exit_code, 0)
            for expected_text in (
                "\u2713 Folder Found",
                "\u2713 Flutter Project Detected",
                "\u2713 pubspec.yaml Loaded",
                "Project Information",
                "Name: example_app",
                "Version: 1.0.0+1",
                "SDK Constraint: >=3.0.0 <4.0.0",
                "Detected Plugins:",
                "Analysis Findings",
                "\u2713 iOS Folder Found",
                "\u2713 Podfile Found",
                "\u2713 Info.plist Found",
                "\u2139 Plugin Detected",
                "\u2139 Known iOS Plugin",
                "camera\nCategory: permission",
                "\u2139 Unknown Plugin",
                "custom_package\nNo rule currently exists.",
                "Analysis Complete",
            ):
                self.assertIn(expected_text, output)

    def test_missing_ios_files_generate_error_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "name: example_app\n", encoding="utf-8"
            )

            exit_code, output = self.run_cli(project_path)

            self.assertEqual(exit_code, 0)
            self.assertIn("\u274c iOS Folder Missing", output)
            self.assertIn("\u274c Missing Podfile", output)
            self.assertIn("\u274c Missing Info.plist", output)

    def test_missing_folder_output_preserves_phase_1_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_path = Path(temporary_directory) / "missing"

            exit_code, output = self.run_cli(missing_path)

            self.assertEqual(exit_code, 1)
            self.assertEqual(output, "\u2717 Project folder not found\n")

    def test_non_flutter_folder_output_preserves_phase_1_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            exit_code, output = self.run_cli(Path(temporary_directory))

            self.assertEqual(exit_code, 1)
            self.assertEqual(output, "\u2717 Not a Flutter project\n")

    def test_invalid_pubspec_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "dependencies: [invalid", encoding="utf-8"
            )

            exit_code, output = self.run_cli(project_path)

            self.assertEqual(exit_code, 1)
            self.assertTrue(output.startswith("\u2717 Unable to parse pubspec.yaml:"))


if __name__ == "__main__":
    unittest.main()
