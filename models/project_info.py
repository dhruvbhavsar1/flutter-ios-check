"""Structured project information collected during a scan."""

from __future__ import annotations

from dataclasses import dataclass, field


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
