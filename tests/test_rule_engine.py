"""Unit tests for the Phase 3 rule engine."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analyzers.rule_engine import RuleEngineError, analyze_project, load_plugin_rules
from models.finding import Severity
from models.project_info import ProjectInfo


class RuleEngineTests(unittest.TestCase):
    def test_existing_ios_files_generate_pass_findings(self) -> None:
        project_info = self.make_project_info(
            ios_folder_exists=True,
            podfile_exists=True,
            plist_exists=True,
        )

        findings = analyze_project(project_info)

        self.assertEqual(
            [(finding.severity, finding.title) for finding in findings],
            [
                (Severity.PASS, "iOS Folder Found"),
                (Severity.PASS, "Podfile Found"),
                (Severity.PASS, "Info.plist Found"),
            ],
        )

    def test_missing_ios_files_generate_error_findings(self) -> None:
        findings = analyze_project(self.make_project_info())

        self.assertEqual(
            [(finding.severity, finding.title) for finding in findings],
            [
                (Severity.ERROR, "iOS Folder Missing"),
                (Severity.ERROR, "Missing Podfile"),
                (Severity.ERROR, "Missing Info.plist"),
            ],
        )
        self.assertEqual(
            findings[0].message, "This project cannot be built for iOS."
        )

    def test_known_and_unknown_plugins_generate_info_findings(self) -> None:
        project_info = self.make_project_info(
            dependencies=["camera", "custom_package"]
        )

        findings = analyze_project(project_info)
        plugin_findings = findings[3:]

        self.assertEqual(len(plugin_findings), 4)
        self.assertEqual(plugin_findings[0].severity, Severity.INFO)
        self.assertEqual(plugin_findings[0].title, "Plugin Detected")
        self.assertEqual(plugin_findings[0].message, "camera")
        self.assertEqual(plugin_findings[1].severity, Severity.INFO)
        self.assertEqual(plugin_findings[1].title, "Known iOS Plugin")
        self.assertEqual(plugin_findings[1].message, "camera\nCategory: permission")
        self.assertEqual(plugin_findings[2].severity, Severity.INFO)
        self.assertEqual(plugin_findings[2].title, "Plugin Detected")
        self.assertEqual(plugin_findings[2].message, "custom_package")
        self.assertEqual(plugin_findings[3].severity, Severity.INFO)
        self.assertEqual(plugin_findings[3].title, "Unknown Plugin")
        self.assertIn("No rule currently exists.", plugin_findings[3].message)

    def test_initial_plugin_database_contains_required_plugins(self) -> None:
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

    def test_missing_plugin_database_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_path = Path(temporary_directory) / "missing.json"

            with self.assertRaisesRegex(RuleEngineError, "Unable to read plugin rules"):
                load_plugin_rules(missing_path)

    def test_invalid_plugin_database_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            rules_path = Path(temporary_directory) / "plugins.json"
            rules_path.write_text('{"camera": {}}', encoding="utf-8")

            with self.assertRaisesRegex(RuleEngineError, "missing category for camera"):
                load_plugin_rules(rules_path)

    @staticmethod
    def make_project_info(
        *,
        dependencies: list[str] | None = None,
        ios_folder_exists: bool = False,
        podfile_exists: bool = False,
        plist_exists: bool = False,
    ) -> ProjectInfo:
        return ProjectInfo(
            project_name="example_app",
            version="1.0.0",
            sdk_constraint=">=3.0.0 <4.0.0",
            dependencies=dependencies or [],
            ios_folder_exists=ios_folder_exists,
            podfile_exists=podfile_exists,
            plist_exists=plist_exists,
        )


if __name__ == "__main__":
    unittest.main()
