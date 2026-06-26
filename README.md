# 🍎 Flutter iOS Readiness Analyzer

**Know what is inside your Flutter project’s iOS configuration before Xcode tells you the hard way.**

Flutter iOS Readiness Analyzer is a Python CLI that inspects a Flutter project and reports the iOS configuration it finds. It helps you quickly see project metadata, iOS files, Podfile settings, `Info.plist` values, permissions, URL schemes, and App Transport Security settings before you try to build or run on iPhone or macOS.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-active%20development-orange.svg)](#roadmap)

---

## Why this tool exists

Flutter projects can work perfectly on Android and still fail on iOS because important configuration lives outside Dart code.

Common iOS surprises include:

- missing `ios/` project files;
- missing or incomplete `Info.plist` values;
- unclear permission usage keys;
- missing URL schemes;
- Podfile deployment target confusion;
- plugin setup requirements that are easy to overlook.

This tool is designed to make that configuration visible in a fast, readable, developer-friendly report.

It is not a build tool, not a linter, and not an automatic fixer. At the current stage, it is a read-only inspector.

---

## Current status: Phase 4

Phase 4 is strictly focused on **data extraction**.

The analyzer reads project files and reports what exists. It does not yet decide whether the extracted configuration is correct.

### What it can do today

| Area | Capability |
| --- | --- |
| Flutter project | Validate the project folder and `pubspec.yaml` |
| Flutter project | Extract project name, version, Dart SDK constraint, and dependencies |
| iOS structure | Detect `ios/`, `ios/Podfile`, and `ios/Runner/Info.plist` |
| Podfile | Extract the iOS deployment target when present |
| Info.plist | Parse using Python’s built-in `plistlib` |
| Info.plist | Extract display name and bundle identifier |
| Info.plist | Extract iOS permission usage keys |
| Info.plist | Extract URL schemes |
| Info.plist | Extract App Transport Security settings |
| Reporting | Show a concise default report and detailed verbose report |
| Plugins | Show informational plugin classifications from `rules/plugins.json` |

### What it does not do yet

The tool currently does not:

- validate permission correctness;
- validate Firebase configuration;
- validate deployment target compatibility;
- validate plugin compatibility;
- generate readiness scores in the default scan report;
- modify or fix project files automatically.

---

## Installation

Python 3.11 or newer is required.

From the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

This installs the `flutter-ios-check` command locally.

If you do not install the package, you can still run the tool with:

```powershell
python main.py scan C:\Projects\MyFlutterApp
```

---

## Usage

Scan the current Flutter project:

```powershell
flutter-ios-check scan
```

Scan a specific Flutter project:

```powershell
flutter-ios-check scan C:\Projects\MyFlutterApp
```

Show all extracted iOS configuration values:

```powershell
flutter-ios-check scan C:\Projects\MyFlutterApp --verbose
```

Show plugin classifications:

```powershell
flutter-ios-check plugins C:\Projects\MyFlutterApp
```

Show only known or unknown plugins:

```powershell
flutter-ios-check plugins C:\Projects\MyFlutterApp --known
flutter-ios-check plugins C:\Projects\MyFlutterApp --unknown
```

Legacy path-only usage is still supported:

```powershell
python main.py C:\Projects\MyFlutterApp
```

---

## Example default report

The default report is intentionally concise.

```text
🍎 Flutter iOS Readiness Analyzer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project
────────────────────────────────────
Name           : my_app
Version        : 1.0.0+1
SDK Constraint : >=3.0.0 <4.0.0

iOS Configuration
────────────────────────────────────
Deployment Target : 13.0
Display Name      : My App
Bundle Identifier : com.example.myapp

Project Files
────────────────────────────────────
✅ iOS Folder
✅ Info.plist
✅ Podfile

Configuration Summary
────────────────────────────────────
Permissions : 3
URL Schemes : 2
ATS         : Present

Analysis Complete

Tip: Run 'flutter-ios-check scan --verbose' for full details.
```

---

## Example verbose report

Verbose mode adds the full extracted lists.

```text
Permissions
────────────────────────────────────
✓ NSCameraUsageDescription
✓ NSPhotoLibraryUsageDescription
✓ NSMicrophoneUsageDescription

URL Schemes
────────────────────────────────────
myapp
google123456

ATS Configuration
────────────────────────────────────
NSAllowsArbitraryLoads: false
NSAllowsLocalNetworking: true
```

---

## Project architecture

```text
flutter-ios-checker/
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── analyzers/
│   ├── project_validator.py
│   ├── project_scanner.py
│   ├── ios_config_parser.py
│   └── rule_engine.py
├── models/
│   ├── project_info.py
│   ├── finding.py
│   ├── plugin_info.py
│   └── analysis_report.py
├── reporters/
│   └── console.py
├── rules/
│   └── plugins.json
└── tests/
```

The architecture separates responsibilities:

- `project_validator.py` handles Phase 1 project validation.
- `project_scanner.py` reads `pubspec.yaml` and builds the core project model.
- `ios_config_parser.py` extracts iOS-specific configuration.
- `rule_engine.py` preserves the rule-engine foundation from Phase 3.
- `reporters/console.py` formats clean CLI output.
- `models/` contains structured dataclasses used across the analyzer.

---

## Run tests

```powershell
python -m unittest discover -s tests -v
```

Expected result:

```text
Ran 23 tests

OK
```

---

## Roadmap

Future phases may add:

- permission validation;
- Firebase iOS configuration checks;
- deployment target compatibility checks;
- plugin compatibility warnings;
- readiness scoring;
- actionable recommendations;
- richer reports.

These features are intentionally not part of Phase 4. The current version focuses on extracting reliable structured data first.

---

## Contributing

Contributions are welcome, especially around:

- improving Podfile parsing edge cases;
- improving `Info.plist` extraction edge cases;
- expanding `rules/plugins.json`;
- adding tests for real Flutter iOS project layouts;
- improving documentation and CLI examples.

If you want to add validation logic, open an issue first so the scope stays aligned with the project phases.