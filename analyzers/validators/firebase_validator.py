"""Static Firebase iOS configuration validation rules."""

from __future__ import annotations

from models.finding import Finding, Severity
from models.project_info import ProjectInfo

FIREBASE_PLUGINS = frozenset(
    {
        "firebase_core",
        "firebase_auth",
        "cloud_firestore",
        "firebase_messaging",
        "firebase_storage",
        "firebase_crashlytics",
        "firebase_analytics",
        "firebase_remote_config",
        "firebase_app_check",
    }
)


def validate_firebase_configuration(project: ProjectInfo) -> list[Finding]:
    """Generate static Firebase configuration findings, or none when unused."""
    firebase_plugins = sorted(set(project.dependencies) & FIREBASE_PLUGINS)
    if not firebase_plugins:
        return []

    findings = [
        Finding(
            Severity.INFO,
            "Firebase detected",
            f"Firebase dependencies detected: {', '.join(firebase_plugins)}.",
        ),
        _google_service_info_finding(project.google_service_info_exists),
        _initialization_finding(project.firebase_initialization_detected),
    ]
    findings.extend(_core_dependency_findings(firebase_plugins))
    if "firebase_messaging" in firebase_plugins:
        findings.extend(_messaging_findings(project))
    return findings


def _google_service_info_finding(exists: bool) -> Finding:
    if exists:
        return Finding(
            Severity.PASS,
            "GoogleService-Info.plist",
            "Firebase iOS configuration file was found.",
        )
    return Finding(
        Severity.ERROR,
        "Missing GoogleService-Info.plist",
        "Firebase detected but GoogleService-Info.plist is missing.",
        "Add GoogleService-Info.plist to ios/Runner and include it in the Runner target.",
    )


def _initialization_finding(detected: bool) -> Finding:
    if detected:
        return Finding(
            Severity.PASS,
            "Firebase initialization",
            "Firebase.initializeApp() was detected in lib/ source code.",
        )
    return Finding(
        Severity.WARNING,
        "Firebase initialization",
        "Firebase.initializeApp() was not detected in lib/ source code.",
        "Initialize Firebase before using Firebase services.",
    )


def _core_dependency_findings(firebase_plugins: list[str]) -> list[Finding]:
    if "firebase_core" in firebase_plugins:
        return [
            Finding(
                Severity.PASS,
                "firebase_core dependency",
                "firebase_core is configured.",
            )
        ]
    return [
        Finding(
            Severity.ERROR,
            "Missing firebase_core",
            f"Firebase plugin '{plugin}' requires firebase_core.",
            "Add firebase_core to pubspec.yaml dependencies.",
        )
        for plugin in firebase_plugins
    ]


def _messaging_findings(project: ProjectInfo) -> list[Finding]:
    findings: list[Finding] = []
    if "remote-notification" in project.background_modes:
        findings.append(
            Finding(
                Severity.PASS,
                "Firebase messaging background mode",
                "remote-notification background mode is configured.",
            )
        )
    else:
        findings.append(
            Finding(
                Severity.INFO,
                "Firebase messaging background mode",
                "Background notification handling requires manual verification.",
                "If background messages are needed, enable Remote notifications in Xcode.",
            )
        )

    if project.push_notifications_capability_detected:
        findings.append(
            Finding(
                Severity.PASS,
                "Push notification capability",
                "A local push-notification capability marker was detected.",
            )
        )
    else:
        findings.append(
            Finding(
                Severity.INFO,
                "Push notification capability",
                "Push notification capability requires manual verification.",
                "Confirm Push Notifications is enabled for the Runner target in Xcode.",
            )
        )
    return findings
