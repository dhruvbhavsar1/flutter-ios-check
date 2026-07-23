# 🍎 Flutter iOS Check

Flutter iOS Check is a local command-line tool for inspecting a Flutter project's iOS readiness before opening Xcode or testing on a device. It reads project files, applies static validation rules, and reports actionable findings.

The analyzer does not modify the target project, contact Firebase or Apple services, run Xcode, or make network requests.

## Project Status

🚧 **Status: Active Development**

The core functionality of Flutter iOS Check is now implemented.

The project is stable enough for community testing and feedback, while new validation rules, plugin support, and quality improvements will continue to be added.

Current focus:

- Improving validation coverage
- Supporting more Flutter plugins
- Reducing false positives
- Enhancing CLI output and documentation

## Requirements

- Python 3.11 or later
- A Flutter project containing a readable `pubspec.yaml`

Install dependencies from this repository root:

```powershell
python -m pip install -r requirements.txt
```

## Quick start

Run the scanner from this repository root. The supported command is `python main.py`.

```powershell
# Scan a Flutter project
python main.py scan C:\flutter\App_for_charity\Charity_app

# Include all extracted values and finding recommendations
python main.py scan C:\flutter\App_for_charity\Charity_app --verbose
```

## Commands

```powershell
# Display available commands and options
python main.py --help

# Scan the current working directory
python main.py scan

# Scan a specified Flutter project
python main.py scan C:\path\to\flutter_project

# Detailed scan output
python main.py scan C:\path\to\flutter_project --verbose

# Path-only scan shorthand
python main.py C:\path\to\flutter_project

# List all detected dependency classifications
python main.py plugins C:\path\to\flutter_project

# List only known or only unknown dependency classifications
python main.py plugins C:\path\to\flutter_project --known
python main.py plugins C:\path\to\flutter_project --unknown
```

## What the scanner reads

| Source | Extracted information |
| --- | --- |
| `pubspec.yaml` | Project name, version, Dart SDK constraint, and dependency names |
| `ios/Podfile` | iOS deployment target |
| `ios/Runner/Info.plist` | Display name, bundle identifier, permission usage-description keys, URL schemes, ATS settings, and background modes |
| `ios/Runner/GoogleService-Info.plist` | Firebase iOS configuration file presence |
| `lib/**/*.dart` | Static occurrence of `Firebase.initializeApp()` |
| Runner entitlements / Xcode project | Local Push Notifications capability markers, if present |

## Validation rules

### Project structure

The analyzer reports the presence of `ios/`, `ios/Podfile`, and `ios/Runner/Info.plist`.

| Condition | Finding severity |
| --- | --- |
| Missing iOS folder | `CRITICAL` |
| Missing Info.plist | `ERROR` |
| Missing Podfile | `ERROR` |

### iOS configuration

| Check | Expected result |
| --- | --- |
| Podfile deployment target | iOS 13.0 or later is recommended |
| Bundle identifier | Basic reverse-domain value, such as `com.example.app` |
| Display name | `CFBundleDisplayName` or `CFBundleName` is present |
| App Transport Security | `NSAllowsArbitraryLoads` is not `true` |
| URL schemes | No empty or duplicate values |
| Permission descriptions | Reports the number of detected `NS*UsageDescription` keys |

### Plugin classification

The `plugins` command classifies dependencies using [rules/plugins.json](rules/plugins.json) as compatible, warning, critical, or unknown. Unknown packages are reported but do not cause the scanner to fail.

Current known plugin entries include:

`camera`, `image_picker`, `geolocator`, `permission_handler`, `firebase_core`, `firebase_messaging`, `flutter_local_notifications`, and `url_launcher`.

### Plugin permission validation

When `Info.plist` is available, the scanner compares mapped plugin requirements with detected usage-description keys. Missing keys produce `WARNING` findings.

| Plugin | Required Info.plist keys |
| --- | --- |
| `camera` | `NSCameraUsageDescription`, `NSMicrophoneUsageDescription` |
| `image_picker` | `NSCameraUsageDescription`, `NSPhotoLibraryUsageDescription` |
| `geolocator` | `NSLocationWhenInUseUsageDescription` |

The mapping is data-driven. Add a `required_permissions` list to an entry in `rules/plugins.json` to extend it without changing validation logic.

### Firebase validation

Firebase validation starts only when one or more Firebase packages are detected. Supported Firebase package detection includes:

`firebase_core`, `firebase_auth`, `cloud_firestore`, `firebase_messaging`, `firebase_storage`, `firebase_crashlytics`, `firebase_analytics`, `firebase_remote_config`, and `firebase_app_check`.

| Check | Success | Finding when missing or unresolved |
| --- | --- | --- |
| Firebase configuration file | `ios/Runner/GoogleService-Info.plist` exists | `ERROR` |
| Firebase initialization | `Firebase.initializeApp()` appears in `lib/**/*.dart` | `WARNING` |
| Dependency consistency | `firebase_core` is present with other Firebase plugins | `ERROR` |
| Messaging background mode | `remote-notification` found in `UIBackgroundModes` | `INFO` manual verification guidance |
| Push capability | Local entitlements/Xcode marker found | `INFO` manual verification guidance |

For `firebase_messaging`, absence of a local capability marker is not reported as a build failure: static files cannot reliably prove every Xcode signing and Apple Developer setting. Confirm Push Notifications and Remote notifications for the Runner target in Xcode when your app uses background notifications.

## Reporting

`scan` produces a concise report with project details, iOS file status, validation summary, and actionable warnings. `--verbose` additionally prints extracted permissions, URL schemes, ATS values, and all findings with recommendations.

Findings use these severities:

| Severity | Meaning |
| --- | --- |
| `PASS` | The static rule is satisfied |
| `INFO` | Context or a manual verification recommendation |
| `WARNING` | A likely configuration issue or incomplete static evidence |
| `ERROR` | A required configuration file or setting is missing |
| `CRITICAL` | Required iOS project structure is missing |

## Scope and limitations

The tool intentionally does not:

- Validate Android permissions;
- Call Firebase APIs or verify cloud services;
- Verify Firestore, Authentication, Storage, Analytics, Remote Config, or App Check at runtime;
- Check APNs certificates, Apple Developer portal configuration, provisioning profiles, or notification delivery;
- Run Flutter, CocoaPods, or Xcode builds;
- Modify project files automatically.

## Architecture

```text
analyzers/
  project_validator.py       # Flutter project validation
  project_scanner.py         # pubspec and project file discovery
  ios_config_parser.py       # Podfile and Info.plist extraction
  firebase_config_parser.py  # local Firebase source and capability discovery
  rule_engine.py             # combines all findings
  validators/                # focused iOS, plugin, and Firebase rules
models/                       # project, plugin, finding, and report data models
reporters/console.py          # CLI output
rules/plugins.json            # plugin classification and permission mapping
tests/                        # unit tests
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

The suite covers project detection, parsing, iOS configuration rules, plugin classifications, plugin permissions, Firebase checks, Firebase Messaging guidance, CLI output, and partial iOS projects.

## Contributing

Keep additions modular and static. New checks should reuse the existing scanner, rule engine, `Finding` model, and console reporter, with focused tests for both passing and failing cases.
