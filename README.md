# Auto Typer Pro - Premium Edition

A modern, high-performance, and feature-rich desktop automation suite for Windows built in Python 3.13 and CustomTkinter. Designed with premium visual styling, advanced keyboard/mouse emulation, thread supervision, and crash recovery mechanics.

## Key Features

### ⌨️ Advanced Auto Typer
- **Real Typo Emulation**: Simulates spelling mistakes based on QWERTY keyboard adjacent neighbor maps, pausing to automatically delete mistakes with Backspace and retype corrections.
- **Natural Cadence Emulation**: Speed fluctuations at word boundaries, delays at punctuation marks, and multi-second pauses at line breaks/paragraph boundaries.
- **Multiple Typing Modes**: Choose between *Simulate Typing* (character-by-character), *Fast Write* (word-by-word), or *Instant Paste* (clipboard injection).
- **Flexible Flow**: Automate the entire text at once, line-by-line, or in random line selections.

### 🖱️ Precision Auto Clicker
- Configure Left, Right, or Middle mouse clicks.
- Support for Single, Double, or Triple clicks.
- Coordinate targeting: Choose *Follow Mouse* or lock to *Fixed Coordinates* using a visual coordinate picker.
- Microsecond-level click intervals.

### 🔄 Premium Macro Recorder & Editor
- Visual drag-and-drop recording timeline with support for capturing both mouse movements, clicks, and keystrokes.
- Edit recorded timeline events directly by double-clicking them.
- Profile replication: Duplicate, copy, rename, and load profiles.
- Export and import macro profiles as JSON files.

### 🛡️ Core Reliability & Performance
- **Watchdog Supervisor**: Background daemon thread monitoring active typing/clicking runners, automatically clearing locked input hooks if threads crash.
- **Resource Performance Profiler**: RAM allocation stats (`tracemalloc`) and thread audits updated periodically and output to the diagnostics console.
- **Crash Session Recovery**: Saves visual visual checkpoints to `session.json` every 5 seconds. If the application terminates unexpectedly, the session state is restored upon reboot.
- **Auto Backup**: Creates rolling zip archives of settings and profiles, pruning old backups to optimize storage.

---

## Getting Started

### Prerequisites
- **Windows 10/11**
- **Python 3.11 - 3.13**

### Installation

To set up a local virtual environment, install dependencies, and run validation checks, execute the automated setup script:
```cmd
install.bat
```

### Running the App

Launch the application directly with:
```cmd
run.bat
```

---

## 🛠️ Global Hotkeys
- **Start/Stop Typer**: `F7`
- **Start/Stop Clicker**: `F6`
- **Record Macro**: `F8`
- **Playback Macro**: `F9`
- **Emergency Stop**: `Esc` (Safely aborts all active typer, clicker, or macro actions instantly)

All trigger hotkeys are customizable in the **Settings** page.

---

## 📦 Packaging to Standalone EXE

Compile Auto Typer Pro into a single-file portable Windows executable (`AutoTyperPro.exe`) by executing:
```cmd
build.bat
```
This script runs PyInstaller, embedding the app icon, localization translations, and packaging custom styling components.

---

## 🧪 Automated Testing
Run the comprehensive integration test suite to verify module integrity:
```cmd
python test_suite.py
```
