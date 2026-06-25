"""Concise and detailed console report formatting."""

from __future__ import annotations

from typing import Any

from models.analysis_report import AnalysisReport
from models.plugin_info import PluginStatus

HEAVY_RULE = "\u2501" * 36
LIGHT_RULE = "\u2500" * 36


def print_scan_report(report: AnalysisReport, *, verbose: bool = False) -> None:
    """Print the Phase 4 extraction report."""
    project = report.project
    print("\U0001f34e Flutter iOS Readiness Analyzer")
    print(HEAVY_RULE)
    print()
    print("Project")
    print(LIGHT_RULE)
    print(f"Name           : {_display(project.project_name)}")
    print(f"Version        : {_display(project.version)}")
    print(f"SDK Constraint : {_display(project.sdk_constraint)}")
    print()
    print("iOS Configuration")
    print(LIGHT_RULE)
    print(f"Deployment Target : {_display(project.ios_deployment_target)}")
    print(f"Display Name      : {_display(project.display_name)}")
    print(f"Bundle Identifier : {_display(project.bundle_identifier)}")
    print()
    print("Project Files")
    print(LIGHT_RULE)
    print(f"{_file_icon(project.ios_folder_exists)} iOS Folder")
    print(f"{_file_icon(project.plist_exists)} Info.plist")
    print(f"{_file_icon(project.podfile_exists)} Podfile")
    print()
    print("Configuration Summary")
    print(LIGHT_RULE)
    print(f"Permissions : {len(project.permissions)}")
    print(f"URL Schemes : {len(project.url_schemes)}")
    print(f"ATS         : {'Present' if project.ats_settings is not None else 'Not present'}")
    print()
    if verbose:
        _print_verbose_configuration(report)
    else:
        print("Analysis Complete")
        print()
        print("Tip: Run 'flutter-ios-check scan --verbose' for full details.")


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


def _print_verbose_configuration(report: AnalysisReport) -> None:
    project = report.project
    print("Permissions")
    print(LIGHT_RULE)
    if project.permissions:
        for permission in project.permissions:
            print(f"\u2713 {permission}")
    else:
        print("None")

    print()
    print("URL Schemes")
    print(LIGHT_RULE)
    if project.url_schemes:
        for scheme in project.url_schemes:
            print(scheme)
    else:
        print("None")

    print()
    print("ATS Configuration")
    print(LIGHT_RULE)
    if project.ats_settings:
        for key, value in sorted(project.ats_settings.items()):
            print(f"{key}: {_format_ats_value(value)}")
    else:
        print("Not present")

    print()
    print("Analysis Complete")


def _display(value: object) -> str:
    if value is None or value == "":
        return "Not specified"
    return str(value)


def _file_icon(exists: bool) -> str:
    return "\u2705" if exists else "\u274c"


def _format_ats_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
