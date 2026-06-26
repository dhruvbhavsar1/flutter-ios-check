# Flutter iOS Readiness Analyzer

A Python CLI that extracts Flutter and iOS project configuration before you
test a Flutter app on iPhone or macOS.

Phase 4 is strictly a data-extraction phase. The tool does not validate
permissions, Firebase setup, deployment targets, plugin compatibility, or make
automatic fixes.

## Features

- validates the project folder and `pubspec.yaml`;
- extracts project name, version, Dart SDK constraint, and dependencies;
- checks whether `ios/`, `ios/Podfile`, and `ios/Runner/Info.plist` exist;
- parses the Podfile deployment target when present;
- parses `Info.plist` with Python's built-in `plistlib`;
- extracts display name, bundle identifier, permission keys, URL schemes, and
  App Transport Security settings;
- keeps the default report concise, with full extracted values available in
  verbose mode.

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

Show every extracted iOS configuration value:

```powershell
flutter-ios-check scan C:\Projects\MyFlutterApp --verbose
```

Show plugin classifications from the rule database:

```powershell
flutter-ios-check plugins C:\Projects\MyFlutterApp
```

Show only known or unknown plugins:

```powershell
flutter-ios-check plugins C:\Projects\MyFlutterApp --known
flutter-ios-check plugins C:\Projects\MyFlutterApp --unknown
```

The original invocation remains supported:

```powershell
python main.py C:\Projects\MyFlutterApp
```

## Default report

The default report is summary-focused:

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

## Verbose report

Verbose mode lists the extracted values:

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
```

## Plugin rules

Plugin metadata lives in `rules/plugins.json`. The plugin command is preserved
from the earlier rule-engine phase, but the default scan report does not use
plugin compatibility to validate the project.

## Run tests

```powershell
python -m unittest discover -s tests -v
```
