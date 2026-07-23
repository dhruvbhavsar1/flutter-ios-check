"""Plugin compatibility information."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PluginStatus(StrEnum):
    """Compatibility classifications supported by the plugin database."""

    COMPATIBLE = "compatible"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class PluginInfo:
    """Classification of one Flutter dependency."""

    name: str
    category: str
    status: PluginStatus
    note: str = ""


@dataclass(frozen=True, slots=True)
class PluginRule:
    """Validated metadata loaded from the plugin rule database."""

    category: str
    status: PluginStatus
    note: str = ""
    required_permissions: tuple[str, ...] = ()
