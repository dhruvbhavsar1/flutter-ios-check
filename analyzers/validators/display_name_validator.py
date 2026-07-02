"""Validation for the iOS display name."""

from __future__ import annotations

from models.finding import Finding, Severity


def validate_display_name(display_name: str | None) -> Finding:
    """Validate that a display name is present."""
    if display_name is None or not display_name.strip():
        return Finding(
            Severity.WARNING,
            "Display Name",
            "No iOS display name was found in Info.plist.",
            "Set CFBundleDisplayName or CFBundleName in Info.plist.",
        )

    return Finding(
        Severity.PASS,
        "Display Name",
        f"Display name '{display_name}' is present.",
    )
