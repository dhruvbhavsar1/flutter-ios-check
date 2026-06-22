"""Rule engine for project checks, plugin classification, and readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.analysis_report import AnalysisReport, ReadinessStatus
from models.finding import Finding, Severity
from models.plugin_info import PluginInfo, PluginRule, PluginStatus
from models.project_info import ProjectInfo

DEFAULT_PLUGIN_RULES_PATH = (
    Path(__file__).resolve().parent.parent / "rules" / "plugins.json"
)


class RuleEngineError(Exception):
    """Raised when analysis rules cannot be loaded or are invalid."""


def build_analysis_report(
    project_info: ProjectInfo,
    plugin_rules_path: Path = DEFAULT_PLUGIN_RULES_PATH,
) -> AnalysisReport:
    """Apply all rules and return a complete readiness report."""
    plugins = classify_plugins(project_info.dependencies, plugin_rules_path)
    findings = analyze_project(project_info, plugins)
    score = calculate_readiness_score(project_info, plugins)
    return AnalysisReport(
        project=project_info,
        findings=findings,
        plugins=plugins,
        score=score,
        status=readiness_status(score),
    )


def analyze_project(
    project_info: ProjectInfo,
    plugins: list[PluginInfo] | None = None,
) -> list[Finding]:
    """Generate concise structural and plugin-risk findings."""
    if plugins is None:
        plugins = classify_plugins(project_info.dependencies)

    findings = [
        _file_finding(
            exists=project_info.ios_folder_exists,
            found_title="iOS Folder",
            missing_title="Missing iOS Folder",
            found_message="iOS project directory is available.",
            missing_message="The project cannot be built for iOS.",
            recommendation="Run 'flutter create .' from the Flutter project root.",
            missing_severity=Severity.CRITICAL,
        ),
        _file_finding(
            exists=project_info.plist_exists,
            found_title="Info.plist",
            missing_title="Missing Info.plist",
            found_message="iOS application configuration is available.",
            missing_message="ios/Runner/Info.plist was not found.",
            recommendation="Restore the iOS runner files with 'flutter create .'.",
            missing_severity=Severity.ERROR,
        ),
        _file_finding(
            exists=project_info.podfile_exists,
            found_title="Podfile",
            missing_title="Missing Podfile",
            found_message="CocoaPods configuration is available.",
            missing_message="ios/Podfile was not found.",
            recommendation=(
                "Run 'flutter create .', then run 'pod install' inside ios/."
            ),
            missing_severity=Severity.ERROR,
        ),
    ]

    for plugin in plugins:
        if plugin.status is PluginStatus.WARNING:
            findings.append(
                Finding(
                    Severity.WARNING,
                    f"Plugin warning: {plugin.name}",
                    plugin.note or "Review this plugin before building for iOS.",
                    f"Review the iOS setup instructions for {plugin.name}.",
                )
            )
        elif plugin.status is PluginStatus.CRITICAL:
            findings.append(
                Finding(
                    Severity.CRITICAL,
                    f"Critical plugin: {plugin.name}",
                    plugin.note or "This plugin may block an iOS build.",
                    f"Resolve or replace {plugin.name} before building for iOS.",
                )
            )

    return findings


def classify_plugins(
    dependency_names: list[str],
    plugin_rules_path: Path = DEFAULT_PLUGIN_RULES_PATH,
) -> list[PluginInfo]:
    """Classify dependencies using the plugin compatibility database."""
    rules = load_plugin_rules(plugin_rules_path)
    plugins: list[PluginInfo] = []

    for name in dependency_names:
        rule = rules.get(name)
        if rule is None:
            plugins.append(
                PluginInfo(
                    name=name,
                    category="Unknown",
                    status=PluginStatus.UNKNOWN,
                    note="No compatibility rule currently exists.",
                )
            )
        else:
            plugins.append(
                PluginInfo(
                    name=name,
                    category=rule.category,
                    status=rule.status,
                    note=rule.note,
                )
            )
    return plugins


def calculate_readiness_score(
    project_info: ProjectInfo, plugins: list[PluginInfo]
) -> int:
    """Calculate a bounded structural-readiness score from 0 to 100."""
    score = 100
    if not project_info.ios_folder_exists:
        score -= 40
    if not project_info.plist_exists:
        score -= 25
    if not project_info.podfile_exists:
        score -= 25

    warning_count = sum(p.status is PluginStatus.WARNING for p in plugins)
    critical_count = sum(p.status is PluginStatus.CRITICAL for p in plugins)
    unknown_count = sum(p.status is PluginStatus.UNKNOWN for p in plugins)
    score -= min(warning_count * 5, 15)
    score -= min(critical_count * 15, 30)
    score -= min(unknown_count * 2, 10)
    return max(0, min(score, 100))


def readiness_status(score: int) -> ReadinessStatus:
    """Map a score to its user-facing readiness status."""
    if score >= 90:
        return ReadinessStatus.READY
    if score >= 70:
        return ReadinessStatus.NEEDS_ATTENTION
    return ReadinessStatus.NOT_READY


def load_plugin_rules(
    rules_path: Path = DEFAULT_PLUGIN_RULES_PATH,
) -> dict[str, PluginRule]:
    """Load and validate the plugin compatibility database."""
    try:
        raw_rules: Any = json.loads(rules_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise RuleEngineError(f"Unable to read plugin rules: {error}") from error
    except json.JSONDecodeError as error:
        raise RuleEngineError(f"Unable to parse plugin rules: {error}") from error

    if not isinstance(raw_rules, dict):
        raise RuleEngineError("Invalid plugin rules: expected a JSON object")

    rules: dict[str, PluginRule] = {}
    for plugin_name, metadata in raw_rules.items():
        if not isinstance(plugin_name, str) or not isinstance(metadata, dict):
            raise RuleEngineError("Invalid plugin rules: malformed plugin entry")

        category = metadata.get("category")
        status_value = metadata.get("status")
        note = metadata.get("note", "")
        if not isinstance(category, str) or not category.strip():
            raise RuleEngineError(
                f"Invalid plugin rules: missing category for {plugin_name}"
            )
        try:
            status = PluginStatus(status_value)
        except (TypeError, ValueError) as error:
            raise RuleEngineError(
                f"Invalid plugin rules: invalid status for {plugin_name}"
            ) from error
        if not isinstance(note, str):
            raise RuleEngineError(
                f"Invalid plugin rules: invalid note for {plugin_name}"
            )
        rules[plugin_name] = PluginRule(category, status, note)

    return rules


def _file_finding(
    *,
    exists: bool,
    found_title: str,
    missing_title: str,
    found_message: str,
    missing_message: str,
    recommendation: str,
    missing_severity: Severity,
) -> Finding:
    if exists:
        return Finding(Severity.PASS, found_title, found_message)
    return Finding(
        missing_severity,
        missing_title,
        missing_message,
        recommendation,
    )
