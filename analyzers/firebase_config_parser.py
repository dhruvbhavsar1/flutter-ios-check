"""Static Firebase-related project configuration discovery."""

from __future__ import annotations

from pathlib import Path
import re


_FIREBASE_INITIALIZATION = re.compile(r"\bFirebase\s*\.\s*initializeApp\s*\(")


def firebase_initialization_exists(project_path: Path) -> bool:
    """Return whether Dart application code initializes Firebase.

    Only source files under ``lib`` are inspected; generated and dependency code is
    intentionally excluded.
    """
    source_path = project_path / "lib"
    if not source_path.is_dir():
        return False
    for dart_file in source_path.rglob("*.dart"):
        try:
            if _FIREBASE_INITIALIZATION.search(dart_file.read_text(encoding="utf-8")):
                return True
        except (OSError, UnicodeError):
            continue
    return False


def push_notifications_capability_exists(project_path: Path) -> bool:
    """Check known local Xcode configuration markers for push notifications."""
    candidates = (
        project_path / "ios" / "Runner" / "Runner.entitlements",
        project_path / "ios" / "Runner.xcodeproj" / "project.pbxproj",
    )
    for path in candidates:
        if not path.is_file():
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if "aps-environment" in contents or "com.apple.Push" in contents:
            return True
    return False
