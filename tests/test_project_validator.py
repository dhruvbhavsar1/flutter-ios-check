"""Unit tests for Phase 1 project validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from analyzers.project_validator import ProjectValidationError, validate_flutter_project


class ProjectValidatorTests(unittest.TestCase):
    def test_missing_project_folder_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_path = Path(temporary_directory) / "missing-project"

            with self.assertRaisesRegex(
                ProjectValidationError, "Project folder not found"
            ):
                validate_flutter_project(missing_path)

    def test_existing_file_is_not_accepted_as_a_project_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "project"
            file_path.write_text("not a folder", encoding="utf-8")

            with self.assertRaisesRegex(
                ProjectValidationError, "Project folder not found"
            ):
                validate_flutter_project(file_path)

    def test_folder_without_pubspec_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)

            with self.assertRaisesRegex(
                ProjectValidationError, "Not a Flutter project"
            ):
                validate_flutter_project(project_path)

    def test_readable_pubspec_is_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            expected_contents = "name: example_app\n"
            (project_path / "pubspec.yaml").write_text(
                expected_contents, encoding="utf-8"
            )

            contents = validate_flutter_project(project_path)

            self.assertEqual(contents, expected_contents)

    def test_unreadable_pubspec_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            pubspec_path = project_path / "pubspec.yaml"
            pubspec_path.write_text("name: example_app\n", encoding="utf-8")

            with patch.object(
                Path, "read_text", side_effect=PermissionError("access denied")
            ):
                with self.assertRaisesRegex(
                    ProjectValidationError, "Unable to read pubspec.yaml"
                ):
                    validate_flutter_project(project_path)


if __name__ == "__main__":
    unittest.main()
