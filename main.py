"""Command-line entry point for the Flutter iOS Readiness Analyzer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from analyzers.project_scanner import ProjectScanError, scan_project
from analyzers.project_validator import ProjectValidationError
from analyzers.rule_engine import RuleEngineError, build_analysis_report
from models.analysis_report import AnalysisReport
from reporters.console import print_plugin_report, print_scan_report


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser and supported subcommands."""
    parser = argparse.ArgumentParser(
        prog="flutter-ios-check",
        description="Analyze a Flutter project's iOS readiness.",
    )
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Run the readiness scan.")
    scan_parser.add_argument(
        "flutter_project_path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Flutter project root (defaults to the current directory).",
    )
    scan_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed plugin metadata and diagnostics.",
    )

    plugins_parser = subparsers.add_parser(
        "plugins", help="Show plugin compatibility details."
    )
    plugins_parser.add_argument(
        "flutter_project_path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Flutter project root (defaults to the current directory).",
    )
    filters = plugins_parser.add_mutually_exclusive_group()
    filters.add_argument("--known", action="store_true", help="Show known plugins only.")
    filters.add_argument(
        "--unknown", action="store_true", help="Show unknown plugins only."
    )
    return parser


def configure_output_encoding() -> None:
    """Use UTF-8 in Windows shells that cannot display report symbols."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, analyze the project, and display the selected report."""
    configure_output_encoding()
    normalized_argv = _normalize_argv(list(argv) if argv is not None else sys.argv[1:])
    args = build_parser().parse_args(normalized_argv)

    try:
        report = _analyze(args.flutter_project_path)
    except (ProjectValidationError, ProjectScanError, RuleEngineError) as error:
        print(f"\u274c {error}")
        return 1

    if args.command == "plugins":
        print_plugin_report(
            report,
            known_only=args.known,
            unknown_only=args.unknown,
        )
    else:
        print_scan_report(report, verbose=args.verbose)
    return 0


def _analyze(project_path: Path) -> AnalysisReport:
    project_info = scan_project(project_path)
    return build_analysis_report(project_info)


def _normalize_argv(argv: list[str]) -> list[str]:
    """Support legacy `main.py <path>` calls and default to scanning cwd."""
    if not argv:
        return ["scan"]
    if argv[0] in {"scan", "plugins"} or argv[0].startswith("-"):
        return argv
    return ["scan", *argv]


if __name__ == "__main__":
    raise SystemExit(main())
