"""Tests for the Phase 1 command-line interface."""

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

    def test_success_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "name: example_app\n", encoding="utf-8"
            )

            exit_code, output = self.run_cli(project_path)

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                output,
                "## Flutter iOS Readiness Analyzer\n"
                "\n"
                "✓ Folder Found\n"
                "\n"
                "✓ Flutter Project Detected\n"
                "\n"
                "✓ pubspec.yaml Loaded\n"
                "\n"
                "Ready For Analysis\n",
            )

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


if __name__ == "__main__":
    unittest.main()
