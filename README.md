# Flutter iOS Readiness Analyzer

Flutter iOS Readiness Analyzer is an open-source Python CLI that inspects a
Flutter project before iOS testing.

The repository currently implements Phases 1 through 3:

- validates the project folder and `pubspec.yaml`;
- extracts project name, version, Dart SDK constraint, and dependencies;
- detects `ios/`, `ios/Podfile`, and `ios/Runner/Info.plist`;
- applies a rule engine and produces PASS, INFO, and ERROR findings;
- classifies dependencies using a small JSON plugin database.

The tool does not validate permissions, Firebase configuration, deployment
targets, or calculate a readiness score. It also has no HTML reporting,
automation, editor extension, desktop UI, AI, or cloud functionality.

## Requirements

- Python 3.11 or newer
- PyYAML 6.x

## Project structure

```text
flutter-ios-checker/
|-- main.py
|-- requirements.txt
|-- README.md
|-- analyzers/
|   |-- project_validator.py
|   |-- project_scanner.py
|   `-- rule_engine.py
|-- models/
|   |-- project_info.py
|   `-- finding.py
|-- rules/
|   `-- plugins.json
`-- tests/
    |-- test_main.py
    |-- test_project_validator.py
    |-- test_project_scanner.py
    `-- test_rule_engine.py
```

## Install and run

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Pass the Flutter project root—the folder containing `pubspec.yaml`:

```powershell
python main.py C:\Projects\MyFlutterApp
```

Use `.` when the current directory is the Flutter project:

```powershell
python main.py .
```

The report includes project information, detected plugins, and findings:

```text
## Flutter iOS Readiness Analyzer

Project Information

Name: my_app
Version: 1.0.0+1
SDK Constraint: >=3.0.0 <4.0.0

Detected Plugins:
camera
custom_package

Analysis Findings

✓ iOS Folder Found
The Flutter project contains an iOS directory.

ℹ Plugin Detected
camera

ℹ Known iOS Plugin
camera
Category: permission

ℹ Plugin Detected
custom_package

ℹ Unknown Plugin
custom_package
No rule currently exists.

Analysis Complete
```

Categories in `rules/plugins.json` are labels for future rules. Phase 3 does
not perform category-specific validation.

## Run tests

```powershell
python -m unittest discover -s tests -v
```
