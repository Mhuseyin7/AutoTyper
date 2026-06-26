import sys
import importlib
from pathlib import Path

# Setup paths
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

REQUIRED_PACKAGES = [
    ("customtkinter", "customtkinter"),
    ("CTkMessagebox", "CTkMessagebox"),
    ("pynput", "pynput"),
    ("keyboard", "keyboard"),
    ("win32gui", "pywin32"),
    ("win32api", "pywin32"),
    ("win32con", "pywin32"),
    ("win32process", "pywin32"),
    ("win32clipboard", "pywin32"),
    ("PIL", "pillow")
]

def verify_dependencies() -> bool:
    print("=== Verification 1: Dependencies ===")
    all_ok = True
    for module_name, pip_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(module_name)
            print(f"[OK] Module '{module_name}' imported successfully.")
        except ImportError:
            print(f"[FAIL] Module '{module_name}' is MISSING (Install using: pip install {pip_name})")
            all_ok = False
    return all_ok

def verify_codebase_imports() -> bool:
    print("\n=== Verification 2: Application Imports ===")
    app_modules = [
        "app.config.constants",
        "app.utils.win32_helper",
        "app.utils.thread_helper",
        "app.utils.validator",
        "app.services.log_service",
        "app.services.config_service",
        "app.services.notification_service",
        "app.services.macro_service",
        "app.services.hotkey_service",
        "app.services.language_service",
        "app.services.stats_service",
        "app.services.backup_service",
        "app.services.update_service",
        "app.core.hooks",
        "app.core.typer",
        "app.core.clicker",
        "app.core.recorder",
        "app.widgets.hotkey_entry",
        "app.widgets.status_card",
        "app.widgets.drag_list_widget",
        "app.ui.base_page",
        "app.ui.typer_page",
        "app.ui.clicker_page",
        "app.ui.macro_page",
        "app.ui.settings_page",
        "app.ui.main_window"
    ]
    
    all_ok = True
    for mod in app_modules:
        try:
            importlib.import_module(mod)
            print(f"[OK] Code integrity pass for: {mod}")
        except Exception as e:
            print(f"[FAIL] Code integrity error in {mod}: {e}")
            all_ok = False
    return all_ok

if __name__ == "__main__":
    print("Auto Typer Pro - System Integration integrity check\n")
    deps_status = verify_dependencies()
    code_status = verify_codebase_imports()
    
    print("\n=== Verification Summary ===")
    if deps_status and code_status:
        print("[SUCCESS] All checks passed! You can run the application with: python run.py")
        sys.exit(0)
    else:
        print("[WARNING] Verification issues detected. Please install missing modules or fix syntax errors.")
        sys.exit(1)
