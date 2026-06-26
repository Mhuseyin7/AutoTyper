# Changelog

All notable changes to **Auto Typer Pro** will be documented in this file.

## [1.0.0] - 2026-06-26

### Added
- **Real human-like typing emulation**: QWERTY layout spelling mistake generator (with automatic backspace corrections), word speed fluctuations, punctuation pause buffers, and paragraph/newline transition shifts.
- **Visual Macro Designer & Timeline Editor**: Drag-and-drop event reordering, event insertion parameters double-click editor dialogs, profile export/imports.
- **System Watchdog Supervisor**: Daemon monitor checking typing/clicking threads and auto-releasing hooks on thread exceptions.
- **Resource Performance Profiler**: RAM allocation tracking (via `tracemalloc`) and thread usage metrics dumped directly to settings diagnostics console.
- **Session Recovery & Crash Control**: Periodic Visual state saving checkpoint (`session.json`) and automatic layout load on unexpected shutdown recovery.
- **Borderless Animated Splash Screen**: Dynamic progressive services loader on boot sequence.
- **Backup Service System**: Rolling automatic `.zip` configuration archives (pruned to 5 rolling copies).
- **Automated Test Suite**: Full coverage testing validation framework (`test_suite.py`).
