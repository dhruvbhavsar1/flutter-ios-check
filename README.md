# Flutter iOS Readiness Analyzer

Flutter iOS Readiness Analyzer is an open-source CLI that inspects a Flutter
project before iOS testing.

The repository currently implements Phases 1 and 2:

- validates that the project folder exists;
- detects and reads `pubspec.yaml`;
- extracts the project name, version, Dart SDK constraint, and dependency names;
- detects `ios/`, `ios/Podfile`, and `ios/Runner/Info.plist`.

It does not perform plugin intelligence, permission or Firebase analysis,
scoring, reporting, automation, UI, AI, or cloud features.

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
|   |-- __init__.py
|   |-- project_validator.py
|   `-- project_scanner.py
|-- models/
|   |-- __init__.py
|   `-- project_info.py
|-- rules/
|   `-- __init__.py
`-- tests/
    |-- __init__.py
    |-- test_main.py
    |-- test_project_scanner.py
    `-- test_project_validator.py
```

## Install and run

From the repository root, optionally create a virtual environment and install
the dependency:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Pass the Flutter project's root folder—the folder containing `pubspec.yaml`:

```powershell
python main.py C:\Projects\MyFlutterApp
```

If the current folder is the Flutter project:

```powershell
python main.py .
```

Example output:

```text
## Flutter iOS Readiness Analyzer

✓ Folder Found

✓ Flutter Project Detected

✓ pubspec.yaml Loaded

Project Information

Name: my_app

Version: 1.0.0+1

SDK Constraint: >=3.0.0 <4.0.0

Dependencies:
camera
image_picker

✓ iOS Folder Found

✓ Podfile Found

✓ Info.plist Found
```

Missing optional iOS files are reported but do not make the scan fail.
Validation or YAML parsing failures return exit code `1`.

## Run tests

```powershell
python -m unittest discover -s tests -v
```
