"""Command-line entry point for the Flutter iOS Readiness Analyzer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from analyzers.project_validator import ProjectValidationError, validate_flutter_project


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
    """Use UTF-8 when stdout supports runtime encoding configuration.

    Some Windows shells still default to an encoding that cannot represent the
    required checkmark and cross symbols.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Phase 1 project validation checks."""
    configure_output_encoding()
    args = build_parser().parse_args(argv)

    try:
        validate_flutter_project(args.flutter_project_path)
    except ProjectValidationError as error:
        print(f"✗ {error}")
        return 1

    print("## Flutter iOS Readiness Analyzer")
    print()
    print("✓ Folder Found")
    print()
    print("✓ Flutter Project Detected")
    print()
    print("✓ pubspec.yaml Loaded")
    print()
    print("Ready For Analysis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
