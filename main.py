"""Command-line entry point for the Flutter iOS Readiness Analyzer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from analyzers.project_scanner import ProjectScanError, scan_project
from analyzers.project_validator import ProjectValidationError
from models.project_info import ProjectInfo


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Check whether a folder is ready for Flutter iOS analysis."
    )
    parser.add_argument(
        "flutter_project_path",
        type=Path,
        help="Path to the Flutter project folder.",
    )
    return parser


def configure_output_encoding() -> None:
    """Use UTF-8 in Windows shells that cannot display status symbols."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """Validate and scan a Flutter project."""
    configure_output_encoding()
    args = build_parser().parse_args(argv)

    try:
        project_info = scan_project(args.flutter_project_path)
    except (ProjectValidationError, ProjectScanError) as error:
        print(f"\u2717 {error}")
        return 1

    print_report(project_info)
    return 0


def print_report(project_info: ProjectInfo) -> None:
    """Display validation results and collected project information."""
    print("## Flutter iOS Readiness Analyzer")
    print()
    print("\u2713 Folder Found")
    print()
    print("\u2713 Flutter Project Detected")
    print()
    print("\u2713 pubspec.yaml Loaded")
    print()
    print("Project Information")
    print()
    print(f"Name: {project_info.project_name or 'Not specified'}")
    print()
    print(f"Version: {project_info.version or 'Not specified'}")
    print()
    print(f"SDK Constraint: {project_info.sdk_constraint or 'Not specified'}")
    print()
    print("Dependencies:")
    if project_info.dependencies:
        for dependency in project_info.dependencies:
            print(dependency)
    else:
        print("None")
    print()
    print(_status_line(project_info.ios_folder_exists, "iOS Folder"))
    print()
    print(_status_line(project_info.podfile_exists, "Podfile"))
    print()
    print(_status_line(project_info.plist_exists, "Info.plist"))


def _status_line(exists: bool, label: str) -> str:
    status = "Found" if exists else "Missing"
    symbol = "\u2713" if exists else "\u2717"
    return f"{symbol} {label} {status}"


if __name__ == "__main__":
    raise SystemExit(main())
