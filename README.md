# Flutter iOS Readiness Analyzer

A concise CLI report for checking whether a Flutter project is structurally
ready for an iOS build.

## Features

- validates the project and parses `pubspec.yaml`;
- checks the iOS folder, `Info.plist`, and Podfile;
- classifies dependencies as compatible, warning, critical, or unknown;
- calculates a readiness score and status;
- prints prioritized issues and recommended actions;
- provides filtered and verbose plugin reports.

The analyzer does not yet validate permission declarations, Firebase files, or
deployment targets, and it does not modify projects automatically.

## Install

Python 3.11 or newer is required.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

This installs the `flutter-ios-check` command.

## Commands

Scan the current Flutter project:

```powershell
flutter-ios-check scan
```

Scan another project:

```powershell
flutter-ios-check scan C:\Projects\MyFlutterApp
```

Show detailed diagnostics:

```powershell
flutter-ios-check scan C:\Projects\MyFlutterApp --verbose
```

Show plugin compatibility:

```powershell
flutter-ios-check plugins C:\Projects\MyFlutterApp
flutter-ios-check plugins C:\Projects\MyFlutterApp --known
flutter-ios-check plugins C:\Projects\MyFlutterApp --unknown
```

The original invocation remains supported:

```powershell
python main.py C:\Projects\MyFlutterApp
```

## Default report

The default scan avoids listing every dependency:

```text
🍎 Flutter iOS Readiness Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: my_app
Version: 1.0.0+1

Status: NOT READY
Readiness Score: 65/100

Checks
─────────────────────────────
✅ iOS Folder
✅ Info.plist
❌ Podfile

Plugin Support
─────────────────────────────
Known Compatible: 2
Unknown: 13

Critical Issues
─────────────────────────────
❌ Missing Podfile

Recommended Actions
─────────────────────────────
1. Run 'flutter create .', then run 'pod install' inside ios/.
2. Re-scan project
Result: NOT READY FOR iOS BUILD
Tip: Run 'python main.py plugins <project_path>' for details.
```

## Scoring

The score starts at 100 and applies bounded deductions:

- missing iOS folder: `-40`;
- missing `Info.plist`: `-25`;
- missing Podfile: `-25`;
- known warning plugins: `-5` each, up to `-15`;
- known critical plugins: `-15` each, up to `-30`;
- unknown plugins: `-2` each, up to `-10`.

Statuses:

- `90–100`: Ready
- `70–89`: Needs Attention
- `0–69`: Not Ready

This is currently a structural-readiness score. Future checks can extend the
engine without changing the console reporter.

## Plugin rules

Plugin metadata lives in `rules/plugins.json`:

```json
{
  "camera": {
    "category": "Permission",
    "status": "warning",
    "note": "Requires camera and microphone usage descriptions when used."
  }
}
```

Supported statuses are `compatible`, `warning`, and `critical`. Dependencies
without a database entry are classified as `unknown`.

## Run tests

```powershell
python -m unittest discover -s tests -v
```
