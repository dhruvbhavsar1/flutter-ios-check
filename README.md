# 🍎 Flutter iOS Readiness Analyzer

**Know what's actually in your Flutter project's iOS configuration — before Xcode tells you the hard way.**

A Python CLI that extracts and reports on Flutter and iOS project configuration, so you can catch missing files, misconfigured permissions, and setup gaps before you try to build, run, or ship to an iPhone or Mac.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active%20development-orange.svg)](#planned-capabilities)

---

## Why This Tool Exists

Flutter's "write once, run anywhere" promise breaks down the moment you target iOS. A project can build fine on Android and still fail — or silently misbehave — on iOS because of:

- A missing or misconfigured `Info.plist` permission key
- An iOS deployment target that doesn't match your plugins' requirements
- A `Podfile` that's out of sync with your Flutter dependencies
- Plugins with known iOS quirks, deprecations, or manual setup steps

Most of these problems are invisible until you're staring at a cryptic Xcode build error or an App Store rejection. This tool surfaces the underlying configuration **before** that happens, in plain text, in seconds.

It's not a linter and it's not a build tool. It's a fast, read-only inspector that tells you exactly what your project currently looks like from Flutter's and iOS's point of view.

---

## What It Can Do Today

The current release (**Phase 4**) is a focused, **data-extraction-only** tool. It reads your project and reports facts — it does not validate, judge, or fix anything yet.

| Area | Capability |
|---|---|
| Flutter project | Validates the project folder and `pubspec.yaml` |
| Flutter project | Extracts project name, version, Dart SDK constraint, and dependencies |
| iOS structure | Checks whether `ios/`, `ios/Podfile`, and `ios/Runner/Info.plist` exist |
| Podfile | Parses the iOS deployment target when present |
| Info.plist | Parses with Python's built-in `plistlib` (no fragile regex/XML parsing) |
| Info.plist | Extracts display name, bundle identifier, permission usage keys |
| Info.plist | Extracts URL schemes |
| Info.plist | Extracts App Transport Security (ATS) settings |
| Reporting | Concise default report, full detail available with `--verbose` |
| Plugins | Reports plugin classifications from a rules database (informational only) |

**What it explicitly does *not* do (yet):** validate permissions, check Firebase setup, judge deployment target compatibility, assess plugin compatibility, or make any automatic fixes. Phase 4 reports what's there — it doesn't tell you if it's *correct*.

---

## Planned Capabilities

These aren't scheduled or committed — just the natural next layer once extraction is solid:

- **Permission validation** — cross-check requested permissions against what plugins actually require
- **Deployment target analysis** — flag mismatches between `Podfile`, plugins, and Flutter's minimum iOS support
- **Plugin compatibility checks** — turn the existing plugin rules database from informational into actionable warnings
- **Firebase / GoogleService-Info.plist checks** — detect missing or misconfigured Firebase iOS setup
- **Guided fixes** — suggested (not automatic) remediation steps for common misconfigurations

If you're interested in any of these, see [Contributing](#contributing) below.

---

## Installation

Requires **Python 3.11+**.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

This installs the `flutter-ios-check` command on your PATH.

> Linux users: use `python3.11 -m venv .venv` and `source .venv/bin/activate` instead.

---

## Usage

### Scan the current Flutter project

```powershell
flutter-ios-check scan
```

### Scan a specific project

```powershell
flutter-ios-check scan C:\Projects\MyFlutterApp
```

### Show every extracted iOS configuration value

```powershell
flutter-ios-check scan C:\Projects\MyFlutterApp --verbose
```

### Show plugin classifications

```powershell
flutter-ios-check plugins C:\Projects\MyFlutterApp
flutter-ios-check plugins C:\Projects\MyFlutterApp --known
flutter-ios-check plugins C:\Projects\MyFlutterApp --unknown
```

### Legacy invocation (still supported)

```powershell
python main.py C:\Projects\MyFlutterApp
```

---

## Example Output

### Default report

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
```

### Verbose report (additional sections)

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
NSAllowsArbitraryLoads: false
```

---

## Project Architecture

```text
flutter-ios-readiness-analyzer/
├── main.py                  # Legacy entry point (still supported)
├── rules/
│   └── plugins.json         # Plugin classification rule database
├── src/                     # CLI commands and extraction logic
│   ├── scan.py              # pubspec.yaml + iOS file/config extraction
│   └── plugins.py           # Plugin rule lookups
├── tests/                   # Unit tests
└── pyproject.toml           # Package + console-script entry point
```

The design intentionally separates **extraction** (reading project files into structured data) from **reporting** (formatting that data for the terminal). This keeps the door open for validation logic to be layered on top in later phases without rewriting the parsing core.

---

## Run Tests

```powershell
python -m unittest discover -s tests -v
```

---

## Contributing

Issues and pull requests are welcome — especially around:

- Expanding the plugin rules database in `rules/plugins.json`
- Edge cases in `Info.plist` or `Podfile` parsing
- Ideas or early implementations for the [Planned Capabilities](#planned-capabilities) above

If you're proposing a new validation feature, please open an issue first to discuss scope, since Phase 4 was deliberately kept extraction-only.

---


