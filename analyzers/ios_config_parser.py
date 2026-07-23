"""Parse iOS project configuration files without validating their contents."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any
import plistlib
import re

from models.project_info import ProjectInfo


class IOSConfigParseError(Exception):
    """Raised when an existing iOS configuration file cannot be parsed."""


_DEPLOYMENT_TARGET_PATTERN = re.compile(
    r"^\s*platform\s*(?::ios\s*)?,\s*['\"](?P<target>[^'\"]+)['\"]",
    re.MULTILINE,
)


def parse_ios_configuration(project_path: Path, project_info: ProjectInfo) -> ProjectInfo:
    """Return ``project_info`` enriched with parsed iOS configuration values."""
    deployment_target = None
    display_name = None
    bundle_identifier = None
    permissions: list[str] = []
    url_schemes: list[str] = []
    ats_settings: dict[str, Any] | None = None
    background_modes: list[str] = []

    podfile_path = project_path / "ios" / "Podfile"
    if project_info.podfile_exists:
        deployment_target = parse_podfile_deployment_target(podfile_path)

    plist_path = project_path / "ios" / "Runner" / "Info.plist"
    if project_info.plist_exists:
        plist_data = parse_info_plist(plist_path)
        display_name = _optional_string(
            plist_data.get("CFBundleDisplayName") or plist_data.get("CFBundleName")
        )
        bundle_identifier = _optional_string(plist_data.get("CFBundleIdentifier"))
        permissions = _extract_permission_keys(plist_data)
        url_schemes = _extract_url_schemes(plist_data)
        ats_settings = _extract_ats_settings(plist_data)
        background_modes = _extract_background_modes(plist_data)

    return replace(
        project_info,
        ios_deployment_target=deployment_target,
        display_name=display_name,
        bundle_identifier=bundle_identifier,
        permissions=permissions,
        url_schemes=url_schemes,
        ats_settings=ats_settings,
        background_modes=background_modes,
    )


def parse_podfile_deployment_target(podfile_path: Path) -> str | None:
    """Extract the iOS deployment target from a Podfile, if declared."""
    try:
        contents = podfile_path.read_text(encoding="utf-8")
    except OSError as error:
        raise IOSConfigParseError(f"Unable to read Podfile: {error}") from error

    match = _DEPLOYMENT_TARGET_PATTERN.search(contents)
    if match is None:
        return None
    return match.group("target").strip()


def parse_info_plist(plist_path: Path) -> dict[str, Any]:
    """Parse Info.plist using Python's built-in plist parser."""
    try:
        with plist_path.open("rb") as plist_file:
            parsed = plistlib.load(plist_file)
    except (OSError, plistlib.InvalidFileException, ValueError) as error:
        raise IOSConfigParseError(f"Unable to parse Info.plist: {error}") from error

    if not isinstance(parsed, dict):
        raise IOSConfigParseError("Unable to parse Info.plist: expected a dictionary")
    return parsed


def _extract_permission_keys(plist_data: dict[str, Any]) -> list[str]:
    """Collect iOS permission usage-description keys from Info.plist."""
    return sorted(
        key
        for key in plist_data
        if key.startswith("NS") and key.endswith("UsageDescription")
    )


def _extract_url_schemes(plist_data: dict[str, Any]) -> list[str]:
    """Extract every URL scheme from CFBundleURLTypes in source order."""
    url_types = plist_data.get("CFBundleURLTypes")
    if not isinstance(url_types, list):
        return []

    schemes: list[str] = []
    for url_type in url_types:
        if not isinstance(url_type, dict):
            continue
        bundle_schemes = url_type.get("CFBundleURLSchemes")
        if not isinstance(bundle_schemes, list):
            continue
        schemes.extend(str(scheme) for scheme in bundle_schemes if scheme is not None)
    return schemes


def _extract_ats_settings(plist_data: dict[str, Any]) -> dict[str, Any] | None:
    ats_settings = plist_data.get("NSAppTransportSecurity")
    if not isinstance(ats_settings, dict):
        return None
    return dict(ats_settings)


def _extract_background_modes(plist_data: dict[str, Any]) -> list[str]:
    """Extract UIBackgroundModes entries from Info.plist."""
    modes = plist_data.get("UIBackgroundModes")
    if not isinstance(modes, list):
        return []
    return [str(mode) for mode in modes if mode is not None]


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
