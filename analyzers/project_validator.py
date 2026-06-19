"""Validation helpers for identifying a readable Flutter project."""

from __future__ import annotations

from pathlib import Path


class ProjectValidationError(Exception):
    """Raised when a project does not pass a Phase 1 validation check."""


def validate_flutter_project(project_path: Path) -> str:
    """Validate a project folder and return its pubspec.yaml contents.

    Args:
        project_path: Folder expected to contain a Flutter project.

    Returns:
        The text read from the project's pubspec.yaml file.

    Raises:
        ProjectValidationError: If the folder or pubspec.yaml is invalid.
    """
    if not project_path.exists() or not project_path.is_dir():
        raise ProjectValidationError("Project folder not found")

    pubspec_path = project_path / "pubspec.yaml"
    if not pubspec_path.is_file():
        raise ProjectValidationError("Not a Flutter project")

    try:
        return pubspec_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        # Keep filesystem details available for troubleshooting without a traceback.
        detail = error.strerror if isinstance(error, OSError) else str(error)
        message = "Unable to read pubspec.yaml"
        if detail:
            message = f"{message}: {detail}"
        raise ProjectValidationError(message) from error
