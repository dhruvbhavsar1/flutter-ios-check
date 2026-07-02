# 🍎 Flutter iOS Readiness Analyzer

**Inspect and validate the iOS configuration inside a Flutter project before Xcode surprises you.**

Flutter iOS Readiness Analyzer is a Python CLI that reads a Flutter project, extracts important iOS configuration, and now performs basic iOS configuration validation. It is designed to help developers quickly understand what is present, what is missing, and what should be reviewed before testing on a real iPhone or Mac.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-active%20development-orange.svg)](#roadmap)

---

## Current status: Phase 5

Phase 5 adds **iOS configuration validation** on top of the existing project scanner and iOS parser.

The tool now validates:

- iOS deployment target;
- bundle identifier format;
- display name presence;
- App Transport Security configuration;
- duplicate or empty URL schemes;
- permission description count.

This phase does **not** compare Flutter plugins with permissions. Plugin-to-permission validation belongs to a future phase.

---

## What it can do today

| Area | Capability |
| --- | --- |
| Project validation | Verify the folder exists and contains a readable `pubspec.yaml` |
| Flutter metadata | Extract project name, version, Dart SDK constraint, and dependencies |
| iOS structure | Detect `ios/`, `ios/Podfile`, and `ios/Runner/Info.plist` |
| Podfile parsing | Extract the iOS deployment target |
| Info.plist parsing | Extract display name, bundle identifier, permissions, URL schemes, and ATS settings |
| iOS validation | Generate `PASS`, `INFO`, `WARNING`, and `ERROR` findings |
| Reporting | Show a concise default report and detailed verbose findings |
| Plugins | Keep informational plugin classification available through the `plugins` command |

---

## What it does not do yet

The analyzer currently does not:

- validate permissions against Flutter plugins;
- validate Firebase configuration;
- validate plugin compatibility;
- generate HTML reports;
- run GitHub Actions workflows;
- modify or fix project files automatically;
- use AI or cloud services.

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

You can also run the project directly without installing:

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

Show all extracted configuration values and complete finding details:

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

Validation Summary
────────────────────────────────────
✓ Deployment Target
✓ Bundle Identifier
✓ Display Name
⚠ ATS Configuration
✓ URL Schemes
ℹ Permissions Found: 4

Warnings
────────────────────────────────────
⚠ ATS allows arbitrary network loads. This may reduce application security.

Analysis Complete
```

---

## Example verbose report

Verbose mode includes extracted configuration details plus full findings and recommendations.

```text
Permissions
────────────────────────────────────
✓ NSCameraUsageDescription
✓ NSPhotoLibraryUsageDescription

URL Schemes
────────────────────────────────────
myapp
google123456

ATS Configuration
────────────────────────────────────
NSAllowsArbitraryLoads: true

Validation Details
────────────────────────────────────
⚠ ATS Configuration
  Severity       : WARNING
  Message        : ATS allows arbitrary network loads. This may reduce application security.
  Recommendation : Avoid NSAllowsArbitraryLoads=true unless the app has a specific need.
```

---

## Validation rules

Phase 5 validates only iOS configuration values that were already extracted in Phase 4.

| Rule | Result |
| --- | --- |
| Missing deployment target | `WARNING` |
| Deployment target below iOS 13.0 | `WARNING` |
| Deployment target 13.0 or higher | `PASS` |
| Missing or empty bundle identifier | `ERROR` |
| Basic reverse-domain bundle identifier | `PASS` |
| Missing or empty display name | `WARNING` |
| Present display name | `PASS` |
| `NSAllowsArbitraryLoads=true` | `WARNING` |
| ATS missing or restrictive | `PASS` |
| Duplicate URL schemes | `WARNING` |
| Empty URL scheme values | `WARNING` |
| Permission descriptions found | `INFO` |

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
│   ├── rule_engine.py
│   └── validators/
│       ├── deployment_target_validator.py
│       ├── bundle_identifier_validator.py
│       ├── display_name_validator.py
│       ├── ats_validator.py
│       ├── url_scheme_validator.py
│       └── permission_summary_validator.py
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

The architecture keeps responsibilities separated:

- `project_validator.py` handles Phase 1 project validation.
- `project_scanner.py` reads `pubspec.yaml` and builds the core project model.
- `ios_config_parser.py` extracts iOS-specific configuration.
- `validators/` contains one focused validator per iOS configuration rule.
- `rule_engine.py` collects findings through the existing rule-engine flow.
- `reporters/console.py` formats clean CLI output.
- `models/` contains structured dataclasses used across the analyzer.

---

## Run tests

```powershell
python -m unittest discover -s tests -v
```

Expected result:

```text
Ran 24 tests

OK
```

---

## Roadmap

Future phases may add:

- plugin-to-permission validation;
- Firebase iOS configuration checks;
- plugin compatibility validation;
- readiness scoring in the default report;
- actionable fix workflows;
- richer report formats.

These are intentionally not part of Phase 5.

---

## Contributing

Contributions are welcome, especially around:

- Podfile parsing edge cases;
- `Info.plist` parsing edge cases;
- additional iOS configuration validators;
- tests using real Flutter iOS project layouts;
- improvements to documentation and CLI examples.

If you want to add plugin-specific validation, open an issue first so the scope stays aligned with the roadmap.
