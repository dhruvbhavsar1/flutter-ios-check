"""Rule engine for producing findings from scanned project information."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.finding import Finding, Severity
from models.project_info import ProjectInfo

DEFAULT_PLUGIN_RULES_PATH = (
    Path(__file__).resolve().parent.parent / "rules" / "plugins.json"
)


class RuleEngineError(Exception):
    """Raised when analysis rules cannot be loaded or are invalid."""


def analyze_project(
    project_info: ProjectInfo,
    plugin_rules_path: Path = DEFAULT_PLUGIN_RULES_PATH,
) -> list[Finding]:
    """Apply all Phase 3 rules to a scanned Flutter project."""
    plugin_rules = load_plugin_rules(plugin_rules_path)

    findings = [
        _file_finding(
            exists=project_info.ios_folder_exists,
            found_title="iOS Folder Found",
            missing_title="iOS Folder Missing",
            found_message="The Flutter project contains an iOS directory.",
            missing_message="This project cannot be built for iOS.",
        ),
        _file_finding(
            exists=project_info.podfile_exists,
            found_title="Podfile Found",
            missing_title="Missing Podfile",
            found_message="Podfile was found inside the iOS directory.",
            missing_message="Podfile was not found inside the iOS directory.",
        ),
        _file_finding(
            exists=project_info.plist_exists,
            found_title="Info.plist Found",
            missing_title="Missing Info.plist",
            found_message="Info.plist was found inside ios/Runner.",
            missing_message="Info.plist was not found inside ios/Runner.",
        ),
    ]

    for plugin_name in project_info.dependencies:
        findings.append(
            Finding(
                severity=Severity.INFO,
                title="Plugin Detected",
                message=plugin_name,
            )
        )
        findings.append(_plugin_classification_finding(plugin_name, plugin_rules))
    return findings


def load_plugin_rules(rules_path: Path = DEFAULT_PLUGIN_RULES_PATH) -> dict[str, str]:
    """Load and validate the plugin category database."""
    try:
        contents = rules_path.read_text(encoding="utf-8")
        raw_rules: Any = json.loads(contents)
    except OSError as error:
        raise RuleEngineError(f"Unable to read plugin rules: {error}") from error
    except json.JSONDecodeError as error:
        raise RuleEngineError(f"Unable to parse plugin rules: {error}") from error

    if not isinstance(raw_rules, dict):
        raise RuleEngineError("Invalid plugin rules: expected a JSON object")

    rules: dict[str, str] = {}
    for plugin_name, metadata in raw_rules.items():
        if not isinstance(plugin_name, str) or not isinstance(metadata, dict):
            raise RuleEngineError("Invalid plugin rules: malformed plugin entry")

        category = metadata.get("category")
        if not isinstance(category, str) or not category.strip():
            raise RuleEngineError(
                f"Invalid plugin rules: missing category for {plugin_name}"
            )
        rules[plugin_name] = category

    return rules


def _file_finding(
    *,
    exists: bool,
    found_title: str,
    missing_title: str,
    found_message: str,
    missing_message: str,
) -> Finding:
    if exists:
        return Finding(Severity.PASS, found_title, found_message)
    return Finding(Severity.ERROR, missing_title, missing_message)


def _plugin_classification_finding(
    plugin_name: str, plugin_rules: dict[str, str]
) -> Finding:
    category = plugin_rules.get(plugin_name)
    if category is not None:
        return Finding(
            severity=Severity.INFO,
            title="Known iOS Plugin",
            message=f"{plugin_name}\nCategory: {category}",
        )

    return Finding(
        severity=Severity.INFO,
        title="Unknown Plugin",
        message=f"{plugin_name}\nNo rule currently exists.",
    )
