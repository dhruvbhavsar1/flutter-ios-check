"""Validation for App Transport Security settings."""

from __future__ import annotations

from typing import Any

from models.finding import Finding, Severity


def validate_ats_configuration(ats_settings: dict[str, Any] | None) -> Finding:
    """Warn only when ATS explicitly allows arbitrary network loads."""
    if ats_settings and ats_settings.get("NSAllowsArbitraryLoads") is True:
        return Finding(
            Severity.WARNING,
            "ATS Configuration",
            "ATS allows arbitrary network loads. This may reduce application security.",
            "Avoid NSAllowsArbitraryLoads=true unless the app has a specific need.",
        )

    if ats_settings is None:
        return Finding(
            Severity.PASS,
            "ATS Configuration",
            "No ATS override was found.",
        )

    return Finding(
        Severity.PASS,
        "ATS Configuration",
        "ATS configuration does not allow arbitrary network loads.",
    )
