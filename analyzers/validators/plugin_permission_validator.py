"""Validate plugin iOS usage-description requirements."""

from __future__ import annotations

from collections.abc import Mapping

from models.finding import Finding, Severity
from models.plugin_info import PluginRule


def validate_plugin_permissions(
    dependency_names: list[str],
    permissions: list[str],
    plugin_rules: Mapping[str, PluginRule],
) -> list[Finding]:
    """Return warnings for mapped plugins missing Info.plist permission keys.

    Plugins without a permission mapping, including unknown plugins, are ignored.
    """
    configured_permissions = set(permissions)
    findings: list[Finding] = []
    for plugin_name in dependency_names:
        rule = plugin_rules.get(plugin_name)
        if rule is None:
            continue
        for permission in rule.required_permissions:
            if permission not in configured_permissions:
                findings.append(
                    Finding(
                        Severity.WARNING,
                        f"Plugin permission: {plugin_name}",
                        (
                            f'Plugin "{plugin_name}" requires {permission} '
                            "but it was not found in Info.plist."
                        ),
                        f"Add {permission} to ios/Runner/Info.plist.",
                    )
                )
    return findings
