"""Scan a validated Flutter project and collect structured project information."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from analyzers.ios_config_parser import IOSConfigParseError, parse_ios_configuration
from analyzers.project_validator import validate_flutter_project
from models.project_info import ProjectInfo


class ProjectScanError(Exception):
    """Raised when project metadata cannot be parsed."""


def scan_project(project_path: Path) -> ProjectInfo:
    """Validate and scan a Flutter project."""
    # Reusing Phase 1 validation preserves its checks and reads the file once.
    pubspec_contents = validate_flutter_project(project_path)
    pubspec = _parse_pubspec(pubspec_contents)
    ios_path = project_path / "ios"

    project_info = ProjectInfo(
        project_name=_string_value(pubspec.get("name")),
        version=_string_value(pubspec.get("version")),
        sdk_constraint=_extract_sdk_constraint(pubspec),
        dependencies=_extract_dependencies(pubspec),
        ios_folder_exists=ios_path.is_dir(),
        podfile_exists=(ios_path / "Podfile").is_file(),
        plist_exists=(ios_path / "Runner" / "Info.plist").is_file(),
    )
    try:
        return parse_ios_configuration(project_path, project_info)
    except IOSConfigParseError as error:
        raise ProjectScanError(str(error)) from error


def _parse_pubspec(contents: str) -> dict[str, Any]:
    """Parse pubspec YAML and ensure its top level is a mapping."""
    try:
        parsed = yaml.safe_load(contents)
    except yaml.YAMLError as error:
        raise ProjectScanError(f"Unable to parse pubspec.yaml: {error}") from error

    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise ProjectScanError("Unable to parse pubspec.yaml: expected a YAML mapping")
    return parsed


def _extract_sdk_constraint(pubspec: dict[str, Any]) -> str:
    environment = pubspec.get("environment")
    if not isinstance(environment, dict):
        return ""
    return _string_value(environment.get("sdk"))


def _extract_dependencies(pubspec: dict[str, Any]) -> list[str]:
    dependencies = pubspec.get("dependencies")
    if not isinstance(dependencies, dict):
        return []
    return sorted(str(name) for name in dependencies)


def _string_value(value: object) -> str:
    """Convert a scalar pubspec value to a displayable string."""
    return "" if value is None else str(value)
