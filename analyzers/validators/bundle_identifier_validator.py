"""Validation for the iOS bundle identifier."""

from __future__ import annotations

import re

from models.finding import Finding, Severity

_BUNDLE_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9-]*(?:\.[A-Za-z][A-Za-z0-9-]*){2,}$"
)


def validate_bundle_identifier(bundle_identifier: str | None) -> Finding:
    """Perform a basic reverse-domain bundle identifier check."""
    if bundle_identifier is None or not bundle_identifier.strip():
        return Finding(
            Severity.ERROR,
            "Bundle Identifier",
            "No bundle identifier was found in Info.plist.",
            "Set CFBundleIdentifier to a reverse-domain value such as com.example.app.",
        )

    if not _BUNDLE_IDENTIFIER_PATTERN.fullmatch(bundle_identifier.strip()):
        return Finding(
            Severity.ERROR,
            "Bundle Identifier",
            (
                f"Bundle identifier '{bundle_identifier}' does not look like a "
                "reverse-domain identifier."
            ),
            "Use a basic reverse-domain format such as com.example.app.",
        )

    return Finding(
        Severity.PASS,
        "Bundle Identifier",
        f"Bundle identifier '{bundle_identifier}' uses a basic reverse-domain format.",
    )
