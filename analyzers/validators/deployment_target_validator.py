"""Validation for the iOS deployment target."""

from __future__ import annotations

from models.finding import Finding, Severity

_RECOMMENDED_IOS_TARGET = (13, 0)


def validate_deployment_target(deployment_target: str | None) -> Finding:
    """Validate that the extracted deployment target is modern enough."""
    if deployment_target is None or not deployment_target.strip():
        return Finding(
            Severity.WARNING,
            "Deployment Target",
            "No iOS deployment target was found in the Podfile.",
            "Set the Podfile platform to iOS 13.0 or later.",
        )

    parsed_target = _parse_version(deployment_target)
    if parsed_target is None:
        return Finding(
            Severity.WARNING,
            "Deployment Target",
            f"Deployment target '{deployment_target}' could not be interpreted.",
            "Use a numeric iOS deployment target such as 13.0.",
        )

    if parsed_target < _RECOMMENDED_IOS_TARGET:
        return Finding(
            Severity.WARNING,
            "Deployment Target",
            (
                f"Deployment target {deployment_target} is below iOS 13.0. "
                "iOS 13.0 or later is recommended for modern Flutter applications."
            ),
            "Increase the deployment target to iOS 13.0 or later.",
        )

    return Finding(
        Severity.PASS,
        "Deployment Target",
        f"Deployment target {deployment_target} is iOS 13.0 or later.",
    )


def _parse_version(value: str) -> tuple[int, int] | None:
    parts = value.strip().split(".")
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
    except (IndexError, ValueError):
        return None
    return major, minor
