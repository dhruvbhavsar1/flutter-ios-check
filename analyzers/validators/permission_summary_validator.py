"""Permission summary reporting."""

from __future__ import annotations

from models.finding import Finding, Severity


def summarize_permissions(permissions: list[str]) -> Finding:
    """Report how many permission usage descriptions were extracted."""
    count = len(permissions)
    return Finding(
        Severity.INFO,
        "Permissions Found",
        f"{count} permission description(s) detected.",
    )
