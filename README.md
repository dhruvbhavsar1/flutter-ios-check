# Flutter iOS Readiness Analyzer

Flutter iOS Readiness Analyzer is an open-source command-line tool that checks
whether a Flutter project can be loaded for future iOS readiness analysis.

This repository currently implements **Phase 1 only**. It validates that:

- the supplied project folder exists;
- the folder contains a `pubspec.yaml` file; and
- `pubspec.yaml` can be opened and read.

It does not inspect plugins, Firebase, Podfiles, `Info.plist`, or calculate a
readiness score.

## Requirements

- Python 3.11 or newer

Phase 1 has no third-party runtime dependencies.

## Project structure

```text
flutter-ios-checker/
├── main.py
├── requirements.txt
├── README.md
├── analyzers/
│   ├── __init__.py
│   └── project_validator.py
├── rules/
│   └── __init__.py
└── tests/
    ├── __init__.py
    ├── test_main.py
    └── test_project_validator.py
```

## Run locally

Clone the repository or open a terminal in its root folder. Optionally create
and activate a virtual environment:

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the analyzer with the path to a Flutter project:

```powershell
python main.py C:\Projects\MyFlutterApp
```

On macOS or Linux:

```bash
python3 main.py /path/to/MyFlutterApp
```

Successful validation prints:

```text
## Flutter iOS Readiness Analyzer

✓ Folder Found

✓ Flutter Project Detected

✓ pubspec.yaml Loaded

Ready For Analysis
```

Validation failures print a clear message and return exit code `1`.

## Run tests

No additional test framework is required:

```powershell
python -m unittest discover -s tests -v
```
