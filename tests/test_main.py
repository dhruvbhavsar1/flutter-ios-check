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

    def test_success_output_contains_project_information(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "name: example_app\n"
                "version: 1.0.0+1\n"
                "environment:\n"
                '  sdk: ">=3.0.0 <4.0.0"\n'
                "dependencies:\n"
                "  camera: ^0.11.0\n"
                "  image_picker: ^1.0.0\n",
                encoding="utf-8",
            )
            (project_path / "ios" / "Runner").mkdir(parents=True)
            (project_path / "ios" / "Podfile").touch()
            (project_path / "ios" / "Runner" / "Info.plist").touch()

            exit_code, output = self.run_cli(project_path)

            self.assertEqual(exit_code, 0)
            for expected_text in (
                "✓ Folder Found",
                "✓ Flutter Project Detected",
                "✓ pubspec.yaml Loaded",
                "Project Information",
                "Name: example_app",
                "Version: 1.0.0+1",
                "SDK Constraint: >=3.0.0 <4.0.0",
                "camera",
                "image_picker",
                "✓ iOS Folder Found",
                "✓ Podfile Found",
                "✓ Info.plist Found",
            ):
                self.assertIn(expected_text, output)

    def test_missing_ios_files_are_reported_without_failing_scan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "name: example_app\n", encoding="utf-8"
            )

            exit_code, output = self.run_cli(project_path)

            self.assertEqual(exit_code, 0)
            self.assertIn("✗ iOS Folder Missing", output)
            self.assertIn("✗ Podfile Missing", output)
            self.assertIn("✗ Info.plist Missing", output)

    def test_missing_folder_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_path = Path(temporary_directory) / "missing"

            exit_code, output = self.run_cli(missing_path)

            self.assertEqual(exit_code, 1)
            self.assertEqual(output, "✗ Project folder not found\n")

    def test_non_flutter_folder_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            exit_code, output = self.run_cli(Path(temporary_directory))

            self.assertEqual(exit_code, 1)
            self.assertEqual(output, "✗ Not a Flutter project\n")

    def test_invalid_pubspec_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "dependencies: [invalid", encoding="utf-8"
            )

            exit_code, output = self.run_cli(project_path)

            self.assertEqual(exit_code, 1)
            self.assertTrue(output.startswith("✗ Unable to parse pubspec.yaml:"))


if __name__ == "__main__":
    unittest.main()
