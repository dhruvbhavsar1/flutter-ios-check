"""Unit tests for scoring, findings, and plugin classification."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analyzers.rule_engine import (
    RuleEngineError,
    build_analysis_report,
    calculate_readiness_score,
    classify_plugins,
    load_plugin_rules,
    readiness_status,
)
from models.analysis_report import ReadinessStatus
from models.finding import Severity
from models.plugin_info import PluginStatus
from models.project_info import ProjectInfo


class RuleEngineTests(unittest.TestCase):
    def test_complete_project_with_compatible_plugins_is_ready(self) -> None:
        project = self.make_project_info(
            dependencies=["firebase_core", "url_launcher"],
            ios_folder_exists=True,
            podfile_exists=True,
            plist_exists=True,
        )

        report = build_analysis_report(project)

        self.assertEqual(report.score, 100)
        self.assertEqual(report.status, ReadinessStatus.READY)
        severities_by_title = {
            finding.title: finding.severity for finding in report.findings
        }
        self.assertEqual(severities_by_title["Deployment Target"], Severity.PASS)
        self.assertEqual(severities_by_title["Bundle Identifier"], Severity.PASS)
        self.assertEqual(severities_by_title["Display Name"], Severity.PASS)
        self.assertEqual(severities_by_title["ATS Configuration"], Severity.PASS)
        self.assertEqual(severities_by_title["URL Schemes"], Severity.PASS)
        self.assertEqual(severities_by_title["Permissions Found"], Severity.INFO)

    def test_missing_files_generate_actionable_findings_and_low_score(self) -> None:
        report = build_analysis_report(self.make_project_info())

        self.assertEqual(report.score, 10)
        self.assertEqual(report.status, ReadinessStatus.NOT_READY)
        self.assertEqual(report.findings[0].severity, Severity.CRITICAL)
        self.assertEqual(report.findings[0].title, "Missing iOS Folder")
        self.assertIn("flutter create .", report.findings[0].recommendation)
        self.assertEqual(report.findings[1].severity, Severity.ERROR)
        self.assertEqual(report.findings[2].severity, Severity.ERROR)
        self.assertIn("Deployment Target", [finding.title for finding in report.findings])
        self.assertIn("Bundle Identifier", [finding.title for finding in report.findings])

    def test_plugins_are_classified_and_permission_findings_are_added(self) -> None:
        project = self.make_project_info(
            dependencies=["firebase_core", "camera", "custom_package"],
            ios_folder_exists=True,
            podfile_exists=True,
            plist_exists=True,
        )

        report = build_analysis_report(project)

        self.assertEqual(
            [plugin.status for plugin in report.plugins],
            [
                PluginStatus.COMPATIBLE,
                PluginStatus.WARNING,
                PluginStatus.UNKNOWN,
            ],
        )
        self.assertEqual(
            [finding.title for finding in report.findings],
            [
                "iOS Folder",
                "Info.plist",
                "Podfile",
                "Deployment Target",
                "Bundle Identifier",
                "Display Name",
                "ATS Configuration",
                "URL Schemes",
                "Permissions Found",
                "Firebase detected",
                "Missing GoogleService-Info.plist",
                "Firebase initialization",
                "firebase_core dependency",
                "Plugin permission: camera",
                "Plugin warning: camera",
            ],
        )
        self.assertEqual(report.score, 93)
        self.assertEqual(report.status, ReadinessStatus.READY)

    def test_plugin_permissions_pass_when_all_required_keys_are_present(self) -> None:
        report = build_analysis_report(
            self.make_project_info(
                dependencies=["camera", "image_picker", "geolocator"],
                ios_folder_exists=True,
                podfile_exists=True,
                plist_exists=True,
                permissions=[
                    "NSCameraUsageDescription",
                    "NSMicrophoneUsageDescription",
                    "NSPhotoLibraryUsageDescription",
                    "NSLocationWhenInUseUsageDescription",
                ],
            )
        )

        self.assertFalse(
            any(
                finding.title.startswith("Plugin permission: ")
                for finding in report.findings
            )
        )

    def test_plugin_permissions_report_every_missing_key_for_multiple_plugins(self) -> None:
        report = build_analysis_report(
            self.make_project_info(
                dependencies=["camera", "image_picker", "custom_package"],
                ios_folder_exists=True,
                podfile_exists=True,
                plist_exists=True,
                permissions=["NSCameraUsageDescription"],
            )
        )

        permission_findings = [
            finding
            for finding in report.findings
            if finding.title.startswith("Plugin permission: ")
        ]
        self.assertEqual(len(permission_findings), 2)
        self.assertTrue(
            all(finding.severity is Severity.WARNING for finding in permission_findings)
        )
        self.assertEqual(
            {finding.message for finding in permission_findings},
            {
                'Plugin "camera" requires NSMicrophoneUsageDescription but it was not found in Info.plist.',
                'Plugin "image_picker" requires NSPhotoLibraryUsageDescription but it was not found in Info.plist.',
            },
        )

    def test_unknown_plugins_do_not_create_permission_findings(self) -> None:
        report = build_analysis_report(
            self.make_project_info(
                dependencies=["custom_package"],
                ios_folder_exists=True,
                podfile_exists=True,
                plist_exists=True,
                permissions=[],
            )
        )

        self.assertFalse(
            any(
                finding.title.startswith("Plugin permission: ")
                for finding in report.findings
            )
        )

    def test_plugin_permission_validation_skips_projects_without_info_plist(self) -> None:
        report = build_analysis_report(
            self.make_project_info(dependencies=["camera"])
        )

        self.assertFalse(
            any(
                finding.title.startswith("Plugin permission: ")
                for finding in report.findings
            )
        )

    def test_projects_without_firebase_do_not_get_firebase_findings(self) -> None:
        report = build_analysis_report(
            self.make_project_info(
                dependencies=["url_launcher"],
                ios_folder_exists=True,
                podfile_exists=True,
                plist_exists=True,
            )
        )

        self.assertFalse(
            any("Firebase" in finding.title for finding in report.findings)
        )

    def test_firebase_project_with_static_configuration_passes_core_checks(self) -> None:
        report = build_analysis_report(
            self.make_project_info(
                dependencies=["firebase_core", "firebase_auth"],
                ios_folder_exists=True,
                podfile_exists=True,
                plist_exists=True,
                google_service_info_exists=True,
                firebase_initialization_detected=True,
            )
        )
        findings = {finding.title: finding for finding in report.findings}

        self.assertEqual(findings["GoogleService-Info.plist"].severity, Severity.PASS)
        self.assertEqual(findings["Firebase initialization"].severity, Severity.PASS)
        self.assertEqual(findings["firebase_core dependency"].severity, Severity.PASS)

    def test_firebase_missing_configuration_produces_actionable_findings(self) -> None:
        report = build_analysis_report(
            self.make_project_info(
                dependencies=["firebase_auth"],
                ios_folder_exists=True,
                podfile_exists=True,
                plist_exists=True,
            )
        )
        findings = {finding.title: finding for finding in report.findings}

        self.assertEqual(
            findings["Missing GoogleService-Info.plist"].severity, Severity.ERROR
        )
        self.assertEqual(findings["Firebase initialization"].severity, Severity.WARNING)
        self.assertEqual(findings["Missing firebase_core"].severity, Severity.ERROR)

    def test_firebase_project_without_ios_files_is_handled_gracefully(self) -> None:
        report = build_analysis_report(
            self.make_project_info(dependencies=["firebase_core"])
        )
        findings = {finding.title: finding for finding in report.findings}

        self.assertEqual(
            findings["Missing GoogleService-Info.plist"].severity, Severity.ERROR
        )
        self.assertEqual(findings["Firebase initialization"].severity, Severity.WARNING)

    def test_firebase_messaging_reports_static_and_manual_checks(self) -> None:
        report = build_analysis_report(
            self.make_project_info(
                dependencies=["firebase_core", "firebase_messaging"],
                ios_folder_exists=True,
                podfile_exists=True,
                plist_exists=True,
                google_service_info_exists=True,
                firebase_initialization_detected=True,
                background_modes=["remote-notification"],
                push_notifications_capability_detected=False,
            )
        )
        findings = {finding.title: finding for finding in report.findings}

        self.assertEqual(
            findings["Firebase messaging background mode"].severity, Severity.PASS
        )
        self.assertEqual(
            findings["Push notification capability"].severity, Severity.INFO
        )

    def test_ios_configuration_validation_findings_are_generated(self) -> None:
        project = self.make_project_info(
            ios_folder_exists=True,
            podfile_exists=True,
            plist_exists=True,
            ios_deployment_target="11.0",
            bundle_identifier="bad",
            display_name="",
            ats_settings={"NSAllowsArbitraryLoads": True},
            url_schemes=["app", "app", ""],
            permissions=["NSCameraUsageDescription", "NSMicrophoneUsageDescription"],
        )

        report = build_analysis_report(project)
        findings_by_title = {
            finding.title: finding for finding in report.findings
        }

        self.assertEqual(findings_by_title["Deployment Target"].severity, Severity.WARNING)
        self.assertEqual(findings_by_title["Bundle Identifier"].severity, Severity.ERROR)
        self.assertEqual(findings_by_title["Display Name"].severity, Severity.WARNING)
        self.assertEqual(findings_by_title["ATS Configuration"].severity, Severity.WARNING)
        self.assertEqual(findings_by_title["URL Schemes"].severity, Severity.WARNING)
        self.assertEqual(findings_by_title["Permissions Found"].severity, Severity.INFO)
        self.assertIn("iOS 13.0", findings_by_title["Deployment Target"].recommendation)
        self.assertIn("reverse-domain", findings_by_title["Bundle Identifier"].recommendation)

    def test_score_is_bounded_and_status_thresholds_are_correct(self) -> None:
        unknown_plugins = [
            *classify_plugins([f"unknown_{index}" for index in range(20)])
        ]
        score = calculate_readiness_score(self.make_project_info(), unknown_plugins)

        self.assertEqual(score, 0)
        self.assertEqual(readiness_status(90), ReadinessStatus.READY)
        self.assertEqual(readiness_status(89), ReadinessStatus.NEEDS_ATTENTION)
        self.assertEqual(readiness_status(70), ReadinessStatus.NEEDS_ATTENTION)
        self.assertEqual(readiness_status(69), ReadinessStatus.NOT_READY)

    def test_initial_database_contains_metadata_for_required_plugins(self) -> None:
        rules = load_plugin_rules()

        self.assertEqual(
            set(rules),
            {
                "camera",
                "image_picker",
                "geolocator",
                "permission_handler",
                "firebase_core",
                "firebase_messaging",
                "flutter_local_notifications",
                "url_launcher",
            },
        )
        self.assertEqual(rules["firebase_core"].status, PluginStatus.COMPATIBLE)
        self.assertEqual(rules["camera"].status, PluginStatus.WARNING)

    def test_missing_plugin_database_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_path = Path(temporary_directory) / "missing.json"

            with self.assertRaisesRegex(RuleEngineError, "Unable to read plugin rules"):
                load_plugin_rules(missing_path)

    def test_invalid_plugin_status_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            rules_path = Path(temporary_directory) / "plugins.json"
            rules_path.write_text(
                '{"camera": {"category": "Permission", "status": "maybe"}}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuleEngineError, "invalid status for camera"):
                load_plugin_rules(rules_path)

    @staticmethod
    def make_project_info(
        *,
        dependencies: list[str] | None = None,
        ios_folder_exists: bool = False,
        podfile_exists: bool = False,
        plist_exists: bool = False,
        ios_deployment_target: str | None = None,
        bundle_identifier: str | None = None,
        display_name: str | None = None,
        ats_settings: dict[str, object] | None = None,
        url_schemes: list[str] | None = None,
        permissions: list[str] | None = None,
        background_modes: list[str] | None = None,
        google_service_info_exists: bool = False,
        firebase_initialization_detected: bool = False,
        push_notifications_capability_detected: bool = False,
    ) -> ProjectInfo:
        effective_deployment_target = ios_deployment_target
        if effective_deployment_target is None and podfile_exists:
            effective_deployment_target = "13.0"

        effective_bundle_identifier = bundle_identifier
        if effective_bundle_identifier is None and plist_exists:
            effective_bundle_identifier = "com.example.app"

        effective_display_name = display_name
        if effective_display_name is None and plist_exists:
            effective_display_name = "Example App"

        return ProjectInfo(
            project_name="example_app",
            version="1.0.0",
            sdk_constraint=">=3.0.0 <4.0.0",
            dependencies=dependencies or [],
            ios_folder_exists=ios_folder_exists,
            podfile_exists=podfile_exists,
            plist_exists=plist_exists,
            ios_deployment_target=effective_deployment_target,
            bundle_identifier=effective_bundle_identifier,
            display_name=effective_display_name,
            ats_settings=ats_settings,
            url_schemes=url_schemes or (["exampleapp"] if plist_exists else []),
            permissions=(
                permissions
                if permissions is not None
                else (["NSCameraUsageDescription"] if plist_exists else [])
            ),
            background_modes=background_modes or [],
            google_service_info_exists=google_service_info_exists,
            firebase_initialization_detected=firebase_initialization_detected,
            push_notifications_capability_detected=push_notifications_capability_detected,
        )


if __name__ == "__main__":
    unittest.main()
