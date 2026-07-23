"""Unit tests for Phase 2 project scanning."""

from __future__ import annotations

import tempfile
import unittest
import plistlib
from pathlib import Path

from analyzers.project_scanner import ProjectScanError, scan_project


class ProjectScannerTests(unittest.TestCase):
    def test_scanner_collects_pubspec_and_ios_information(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "name: sample_app\n"
                "version: 2.1.0+7\n"
                "environment:\n"
                "  sdk: '>=3.2.0 <4.0.0'\n"
                "dependencies:\n"
                "  image_picker: ^1.0.0\n"
                "  flutter:\n"
                "    sdk: flutter\n"
                "  camera: ^0.11.0\n",
                encoding="utf-8",
            )
            runner_path = project_path / "ios" / "Runner"
            runner_path.mkdir(parents=True)
            (project_path / "ios" / "Podfile").write_text(
                "platform :ios, '13.0'\n", encoding="utf-8"
            )
            with (runner_path / "Info.plist").open("wb") as plist_file:
                plistlib.dump(
                    {
                        "CFBundleDisplayName": "Sample App",
                        "CFBundleIdentifier": "com.example.sample",
                        "NSCameraUsageDescription": "Camera access",
                        "NSPhotoLibraryUsageDescription": "Photos access",
                        "CFBundleURLTypes": [
                            {"CFBundleURLSchemes": ["sample", "oauth"]}
                        ],
                        "NSAppTransportSecurity": {
                            "NSAllowsArbitraryLoads": False,
                            "NSAllowsLocalNetworking": True,
                        },
                    },
                    plist_file,
                )

            project_info = scan_project(project_path)

            self.assertEqual(project_info.project_name, "sample_app")
            self.assertEqual(project_info.version, "2.1.0+7")
            self.assertEqual(project_info.sdk_constraint, ">=3.2.0 <4.0.0")
            self.assertEqual(
                project_info.dependencies, ["camera", "flutter", "image_picker"]
            )
            self.assertTrue(project_info.ios_folder_exists)
            self.assertTrue(project_info.podfile_exists)
            self.assertTrue(project_info.plist_exists)
            self.assertEqual(project_info.ios_deployment_target, "13.0")
            self.assertEqual(project_info.display_name, "Sample App")
            self.assertEqual(project_info.bundle_identifier, "com.example.sample")
            self.assertEqual(
                project_info.permissions,
                ["NSCameraUsageDescription", "NSPhotoLibraryUsageDescription"],
            )
            self.assertEqual(project_info.url_schemes, ["sample", "oauth"])
            self.assertEqual(
                project_info.ats_settings,
                {
                    "NSAllowsArbitraryLoads": False,
                    "NSAllowsLocalNetworking": True,
                },
            )

    def test_missing_optional_values_and_ios_files_use_safe_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "name: sample_app\n", encoding="utf-8"
            )

            project_info = scan_project(project_path)

            self.assertEqual(project_info.project_name, "sample_app")
            self.assertEqual(project_info.version, "")
            self.assertEqual(project_info.sdk_constraint, "")
            self.assertEqual(project_info.dependencies, [])
            self.assertFalse(project_info.ios_folder_exists)
            self.assertFalse(project_info.podfile_exists)
            self.assertFalse(project_info.plist_exists)
            self.assertIsNone(project_info.ios_deployment_target)
            self.assertIsNone(project_info.display_name)
            self.assertIsNone(project_info.bundle_identifier)
            self.assertEqual(project_info.permissions, [])
            self.assertEqual(project_info.url_schemes, [])
            self.assertIsNone(project_info.ats_settings)

    def test_scanner_detects_firebase_files_initialization_and_background_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "name: firebase_app\ndependencies:\n  firebase_core: ^3.0.0\n",
                encoding="utf-8",
            )
            runner_path = project_path / "ios" / "Runner"
            runner_path.mkdir(parents=True)
            (runner_path / "GoogleService-Info.plist").write_bytes(b"placeholder")
            with (runner_path / "Info.plist").open("wb") as plist_file:
                plistlib.dump({"UIBackgroundModes": ["remote-notification"]}, plist_file)
            lib_path = project_path / "lib"
            lib_path.mkdir()
            (lib_path / "main.dart").write_text(
                "await Firebase.initializeApp();", encoding="utf-8"
            )

            project_info = scan_project(project_path)

            self.assertTrue(project_info.google_service_info_exists)
            self.assertTrue(project_info.firebase_initialization_detected)
            self.assertEqual(project_info.background_modes, ["remote-notification"])

    def test_invalid_yaml_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "dependencies: [invalid", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                ProjectScanError, "Unable to parse pubspec.yaml"
            ):
                scan_project(project_path)

    def test_non_mapping_pubspec_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_path = Path(temporary_directory)
            (project_path / "pubspec.yaml").write_text(
                "- not\n- a\n- mapping\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(ProjectScanError, "expected a YAML mapping"):
                scan_project(project_path)


if __name__ == "__main__":
    unittest.main()
