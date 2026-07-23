"""Structured project information collected during a scan."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ProjectInfo:
    """Information extracted from a Flutter project."""

    project_name: str
    version: str
    sdk_constraint: str
    dependencies: list[str] = field(default_factory=list)
    ios_folder_exists: bool = False
    podfile_exists: bool = False
    plist_exists: bool = False
    ios_deployment_target: str | None = None
    bundle_identifier: str | None = None
    display_name: str | None = None
    permissions: list[str] = field(default_factory=list)
    url_schemes: list[str] = field(default_factory=list)
    ats_settings: dict[str, Any] | None = None
    background_modes: list[str] = field(default_factory=list)
    google_service_info_exists: bool = False
    firebase_initialization_detected: bool = False
    push_notifications_capability_detected: bool = False
