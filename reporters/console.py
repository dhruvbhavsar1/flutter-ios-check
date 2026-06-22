"""Concise and detailed console report formatting."""

from __future__ import annotations

from collections.abc import Iterable

from models.analysis_report import AnalysisReport, ReadinessStatus
from models.finding import Finding, Severity
from models.plugin_info import PluginInfo, PluginStatus

HEAVY_RULE = "\u2501" * 30
LIGHT_RULE = "\u2500" * 29


def print_scan_report(report: AnalysisReport, *, verbose: bool = False) -> None:
    """Print the default concise scan report or detailed diagnostics."""
    print("\U0001f34e Flutter iOS Readiness Report")
    print(HEAVY_RULE)
    print(f"Project: {report.project.project_name or 'Not specified'}")
    print(f"Version: {report.project.version or 'Not specified'}")
    print()
    print(f"Status: {report.status.value}")
    print(f"Readiness Score: {report.score}/100")
    print()
    _print_checks(report)
    print()
    _print_plugin_summary(report)
    print()
    _print_critical_issues(report.findings)
    print()
    _print_recommendations(report.findings)
    print(f"Result: {_result_text(report.status)}")
    if verbose:
        print()
        _print_verbose_details(report)
    else:
        print("Tip: Run 'python main.py plugins <project_path>' for details.")


def print_plugin_report(
    report: AnalysisReport,
    *,
    known_only: bool = False,
    unknown_only: bool = False,
) -> None:
    """Print plugin compatibility details, optionally filtered."""
    print("Plugin Compatibility Report")
    print(HEAVY_RULE)
    print(f"Project: {report.project.project_name or 'Not specified'}")
    print()

    groups = (
        (PluginStatus.COMPATIBLE, "Known Compatible", "\u2705"),
        (PluginStatus.WARNING, "Known Warning", "\u26a0"),
        (PluginStatus.CRITICAL, "Known Critical", "\U0001f6a8"),
        (PluginStatus.UNKNOWN, "Unknown", "\u2022"),
    )
    displayed = False
    for status, heading, icon in groups:
        if known_only and status is PluginStatus.UNKNOWN:
            continue
        if unknown_only and status is not PluginStatus.UNKNOWN:
            continue
        plugins = [plugin for plugin in report.plugins if plugin.status is status]
        if not plugins:
            continue
        displayed = True
        print(f"{heading} ({len(plugins)})")
        print(LIGHT_RULE)
        for plugin in plugins:
            print(f"{icon} {plugin.name}")
        print()

    if not displayed:
        print("No plugins match this filter.")


def _print_checks(report: AnalysisReport) -> None:
    print("Checks")
    print(LIGHT_RULE)
    checks = (
        (report.project.ios_folder_exists, "iOS Folder"),
        (report.project.plist_exists, "Info.plist"),
        (report.project.podfile_exists, "Podfile"),
    )
    for passed, label in checks:
        print(f"{'\u2705' if passed else '\u274c'} {label}")


def _print_plugin_summary(report: AnalysisReport) -> None:
    print("Plugin Support")
    print(LIGHT_RULE)
    print(f"Known Compatible: {report.plugin_count(PluginStatus.COMPATIBLE)}")
    warning_count = report.plugin_count(PluginStatus.WARNING)
    critical_count = report.plugin_count(PluginStatus.CRITICAL)
    if warning_count:
        print(f"Known Warning: {warning_count}")
    if critical_count:
        print(f"Known Critical: {critical_count}")
    print(f"Unknown: {report.plugin_count(PluginStatus.UNKNOWN)}")


def _print_critical_issues(findings: Iterable[Finding]) -> None:
    print("Critical Issues")
    print(LIGHT_RULE)
    issues = [
        finding
        for finding in findings
        if finding.severity in {Severity.ERROR, Severity.CRITICAL}
    ]
    if not issues:
        print("\u2705 None")
        return
    for finding in issues:
        icon = "\U0001f6a8" if finding.severity is Severity.CRITICAL else "\u274c"
        print(f"{icon} {finding.title}")


def _print_recommendations(findings: Iterable[Finding]) -> None:
    print("Recommended Actions")
    print(LIGHT_RULE)
    actions = _unique_recommendations(findings)
    if not actions:
        print("1. No critical action required")
        return
    for index, action in enumerate(actions[:3], start=1):
        print(f"{index}. {action}")
    if len(actions) < 3:
        print(f"{len(actions) + 1}. Re-scan project")


def _print_verbose_details(report: AnalysisReport) -> None:
    print("Detailed Plugin Analysis")
    print(LIGHT_RULE)
    if not report.plugins:
        print("No dependencies detected.")
    for plugin in report.plugins:
        print(
            f"{_plugin_icon(plugin)} {plugin.name} | "
            f"{plugin.category} | {plugin.status.value.title()}"
        )
        if plugin.note:
            print(f"  {plugin.note}")

    diagnostic_findings = [
        finding
        for finding in report.findings
        if finding.severity in {Severity.WARNING, Severity.ERROR, Severity.CRITICAL}
    ]
    if diagnostic_findings:
        print()
        print("Diagnostics")
        print(LIGHT_RULE)
        for finding in diagnostic_findings:
            print(f"{_finding_icon(finding)} {finding.title}: {finding.message}")


def _unique_recommendations(findings: Iterable[Finding]) -> list[str]:
    return list(
        dict.fromkeys(
            finding.recommendation
            for finding in findings
            if finding.recommendation
            and finding.severity in {Severity.WARNING, Severity.ERROR, Severity.CRITICAL}
        )
    )


def _result_text(status: ReadinessStatus) -> str:
    if status is ReadinessStatus.READY:
        return "READY FOR iOS BUILD"
    if status is ReadinessStatus.NEEDS_ATTENTION:
        return "NEEDS ATTENTION BEFORE iOS BUILD"
    return "NOT READY FOR iOS BUILD"


def _plugin_icon(plugin: PluginInfo) -> str:
    return {
        PluginStatus.COMPATIBLE: "\u2705",
        PluginStatus.WARNING: "\u26a0",
        PluginStatus.CRITICAL: "\U0001f6a8",
        PluginStatus.UNKNOWN: "\u2022",
    }[plugin.status]


def _finding_icon(finding: Finding) -> str:
    return {
        Severity.PASS: "\u2705",
        Severity.INFO: "\u2139",
        Severity.WARNING: "\u26a0",
        Severity.ERROR: "\u274c",
        Severity.CRITICAL: "\U0001f6a8",
    }[finding.severity]
