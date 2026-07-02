"""Validation for iOS URL schemes."""

from __future__ import annotations

from collections import Counter

from models.finding import Finding, Severity


def validate_url_schemes(url_schemes: list[str]) -> Finding:
    """Validate duplicate and empty URL scheme values."""
    empty_count = sum(1 for scheme in url_schemes if not scheme.strip())
    if empty_count:
        return Finding(
            Severity.WARNING,
            "URL Schemes",
            f"{empty_count} empty URL scheme value was found.",
            "Remove empty values from CFBundleURLSchemes.",
        )

    duplicates = sorted(
        scheme for scheme, count in Counter(url_schemes).items() if count > 1
    )
    if duplicates:
        return Finding(
            Severity.WARNING,
            "URL Schemes",
            f"Duplicate URL schemes were found: {', '.join(duplicates)}.",
            "Remove duplicate values from CFBundleURLSchemes.",
        )

    return Finding(
        Severity.PASS,
        "URL Schemes",
        f"{len(url_schemes)} URL scheme value(s) checked.",
    )
