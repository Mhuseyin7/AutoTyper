import sys
import os
import logging
import traceback
import threading
import customtkinter as ctk

from .config.constants import APP_NAME, VERSION
from .services.log_service import setup_logging
from .services.config_service import ConfigService
from .services.notification_service import NotificationService
from .services.macro_service import MacroService
from .services.hotkey_service import HotkeyService
from .services.language_service import LanguageService
from .services.stats_service import StatsService
from .services.backup_service import BackupService
from .services.update_service import UpdateService

from .core.hooks import InputHookListener
from .core.typer import AutoTyperRunner
from .core.clicker import AutoClickerRunner
from .core.recorder import MacroPlaybackRunner

from .ui.main_window import MainWindow
from .ui.splash_screen import SplashScreen
from .utils.profiler import ResourceProfiler
from .utils.recovery import SessionRecovery

# Initialize dynamic logging config
logger = setup_logging("INFO")

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.critical(f"Uncaught exception: {exc_value}\n{err_msg}")
    
    try:
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(
            title="Application Error",
            message=f"A critical error occurred:\n{exc_value}\n\nPlease check logs/autotyperpro.log for details.",
            icon="cancel"
        )
    except Exception:
        pass

def global_thread_exception_handler(args):
    err_msg = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_trace))
    logger.critical(f"Uncaught thread exception in {args.thread.name}: {args.exc_value}\n{err_msg}")

sys.excepthook = global_exception_handler
threading.excepthook = global_thread_exception_handler

def main():
    logger.info(f"Starting {APP_NAME} v{VERSION}...")

    # Start performance resource profiling
    ResourceProfiler.start_profiling()

    # 1. Initialize Configuration Service
    config_service = ConfigService()
    
    # Reload log level if different in settings
    log_level = config_service.get("log_level")
    setup_logging(log_level)

    # 2. Initialize Infrastructure Services
    notification_service = NotificationService()
    macro_service = MacroService()
    
    # 3. New Telemetry, Localization, and Backup Services
    language_service = LanguageService(config_service)
    stats_service = StatsService()
    backup_service = BackupService()
    update_service = UpdateService()

    # Trigger initial backup on startup for safety
    backup_service.create_backup()

    # 4. Initialize Core Engines
    hook_listener = InputHookListener()
    
    # Create DI Container
    services = {
        "config": config_service,
        "notification": notification_service,
        "macro_service": macro_service,
        "hotkey": None, # Will be set below
        "hook_listener": hook_listener,
        "language": language_service,
        "stats_service": stats_service,
        "backup_service": backup_service,
        "update_service": update_service,
        "typer_runner": None, # Set below
        "clicker_runner": None, # Set below
        "playback_runner": None,  # Set below
        "watchdog": None
    }

    # Instantiate runners using services container references
    typer_runner = AutoTyperRunner(services)
    clicker_runner = AutoClickerRunner(services)
    playback_runner = MacroPlaybackRunner(services)
    
    services["typer_runner"] = typer_runner
    services["clicker_runner"] = clicker_runner
    services["playback_runner"] = playback_runner

    # 5. Initialize Hotkey Register Service
    hotkey_service = HotkeyService(config_service)
    services["hotkey"] = hotkey_service

    # Define the UI launch callback
    def launch_main_app():
        # Start watchdog supervisor
        from .services.watchdog import WatchdogService
        watchdog = WatchdogService(services)
        services["watchdog"] = watchdog
        watchdog.start_watchdog()

        # 6. Boot UI Window Container
        main_win = MainWindow(services)

        # Start periodic resource profiling updates (every 30s)
        def log_perf():
            ResourceProfiler.log_profile_summary()
            if main_win.winfo_exists():
                main_win.after(30000, log_perf)

        main_win.after(15000, log_perf)

        # 7. Setup Hotkey Toggle Handlers
        # Typer Toggle
        def toggle_typer_hotkey():
            if typer_runner.is_running():
                typer_runner.stop()
                main_win.after(0, lambda: notification_service.show_toast(language_service.get("status_idle") + " (Auto Typer)", level="warning"))
            else:
                success = typer_runner.start()
                if success:
                    main_win.after(0, lambda: notification_service.show_toast(language_service.get("status_running") + " (Auto Typer)", level="success"))
            # Force sync state if page is currently visible
            if main_win.active_page_id == "typer":
                main_win.after(0, main_win.pages["typer"]._update_runner_status)

        # Clicker Toggle
        def toggle_clicker_hotkey():
            if clicker_runner.is_running():
                clicker_runner.stop()
                main_win.after(0, lambda: notification_service.show_toast(language_service.get("status_idle") + " (Auto Clicker)", level="warning"))
            else:
                success = clicker_runner.start()
                if success:
                    main_win.after(0, lambda: notification_service.show_toast(language_service.get("status_running") + " (Auto Clicker)", level="success"))
            if main_win.active_page_id == "clicker":
                main_win.after(0, main_win.pages["clicker"]._update_runner_status)

        # Macro Record Toggle
        def toggle_macro_record_hotkey():
            if main_win.active_page_id == "macro":
                main_win.after(0, main_win.pages["macro"].toggle_recording)
            else:
                main_win.after(0, lambda: notification_service.show_toast(language_service.get("toast_lang_changed"), level="info"))

        # Macro Playback Toggle
        def toggle_macro_play_hotkey():
            if main_win.active_page_id == "macro":
                main_win.after(0, main_win.pages["macro"].toggle_playback)
            else:
                if playback_runner.is_running():
                    playback_runner.stop()
                    main_win.after(0, lambda: notification_service.show_toast(language_service.get("status_idle") + " (Playback)", level="warning"))
                else:
                    events = main_win.pages["macro"].current_events
                    if events:
                        playback_runner.start(events)
                        main_win.after(0, lambda: notification_service.show_toast(language_service.get("status_running") + " (Playback)", level="success"))
                    else:
                        main_win.after(0, lambda: notification_service.show_toast("No macro events cached to play.", level="error"))

        # Emergency Stop Trigger
        def emergency_stop_hotkey():
            logger.warning("EMERGENCY STOP TRIGGERED!")
            typer_runner.stop()
            clicker_runner.stop()
            playback_runner.stop()
            hook_listener.stop_recording()
            
            main_win.after(0, lambda: notification_service.show_toast("EMERGENCY STOP TRIPPED!", level="error"))
            
            # Synchronize UI
            if main_win.active_page_id == "typer":
                main_win.after(0, main_win.pages["typer"]._update_runner_status)
            elif main_win.active_page_id == "clicker":
                main_win.after(0, main_win.pages["clicker"]._update_runner_status)
            elif main_win.active_page_id == "macro":
                main_win.after(0, main_win.pages["macro"]._update_runner_status)

        # Register hotkey bindings
        hotkey_service.register_action_hotkey("auto_typer_start_stop", toggle_typer_hotkey)
        hotkey_service.register_action_hotkey("auto_clicker_start_stop", toggle_clicker_hotkey)
        hotkey_service.register_action_hotkey("macro_record_start_stop", toggle_macro_record_hotkey)
        hotkey_service.register_action_hotkey("macro_play_start_stop", toggle_macro_play_hotkey)
        
        # Global ESC Emergency Stop binding
        import keyboard
        try:
            keyboard.add_hotkey("esc", emergency_stop_hotkey)
            logger.info("Global Emergency Stop bound to 'Esc' key.")
        except Exception as e:
            logger.error(f"Failed to bind global emergency stop: {e}")

        # 8. Safe Window Closure handler
        def on_window_closing():
            logger.info("Closing application... Cleaning up resources.")
            typer_runner.stop()
            clicker_runner.stop()
            playback_runner.stop()
            hook_listener.stop_recording()
            
            # Stop watchdog
            watchdog.stop_watchdog()

            # Clear session checkpoint
            SessionRecovery.clear_session_checkpoint()
            
            hotkey_service.unregister_all()
            try:
                keyboard.unhook_all()
            except Exception:
                pass
                
            main_win.destroy()
            logger.info("Application exited successfully.")
            sys.exit(0)

        main_win.protocol("WM_DELETE_WINDOW", on_window_closing)

        # Restoring last session checkpoint
        session_data = SessionRecovery.load_session_checkpoint()
        if session_data:
            active_page = session_data.get("active_page", "typer")
            main_win.select_page(active_page)
            typer_text = session_data.get("typer_text")
            if typer_text and "typer" in main_win.pages:
                main_win.pages["typer"].txt_area.delete("1.0", ctk.END)
                main_win.pages["typer"].txt_area.insert("1.0", typer_text)
            
            main_win.after(1000, lambda: notification_service.show_toast(
                "Restored previous session checkpoint after crash.", level="info"
            ))

        # Start session checkpointing loop
        def save_checkpoint():
            try:
                data = {
                    "active_page": main_win.active_page_id,
                }
                if "typer" in main_win.pages:
                    data["typer_text"] = main_win.pages["typer"].txt_area.get("1.0", "end-1c")
                SessionRecovery.save_session_checkpoint(data)
            except Exception:
                pass
            if main_win.winfo_exists():
                main_win.after(5000, save_checkpoint)

        main_win.after(5000, save_checkpoint)

        # 9. Start main event loop
        main_win.mainloop()

    # Launch splash screen first
    splash = SplashScreen(on_complete=launch_main_app)
    splash.mainloop()

if __name__ == "__main__":
    main()
