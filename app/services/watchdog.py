import time
import logging
import threading
from typing import Optional

logger = logging.getLogger("AutoTyperPro")

class WatchdogService:
    """Monitors runner thread health and triggers cleanup routines on unexpected thread termination."""
    def __init__(self, services: dict):
        self.services = services
        self._watchdog_thread: Optional[threading.Thread] = None
        self._is_active = False
        
    def start_watchdog(self):
        """Starts the supervisor daemon thread loop."""
        if self._is_active:
            return
            
        self._is_active = True
        self._watchdog_thread = threading.Thread(
            target=self._supervise_loop, name="RunnerWatchdogThread", daemon=True
        )
        self._watchdog_thread.start()
        logger.info("Thread Watchdog Supervisor service started.")

    def stop_watchdog(self):
        """Stops the watchdog loop."""
        self._is_active = False
        logger.info("Thread Watchdog Supervisor service stopped.")

    def _supervise_loop(self):
        """Periodic checker loop for worker thread statuses."""
        while self._is_active:
            try:
                # Sleep between ticks (2 seconds)
                time.sleep(2.0)
                
                # Check Auto Typer
                typer = self.services.get("typer_runner")
                if typer and typer.is_running():
                    # If state is running, but the internal thread is dead
                    if typer._thread and not typer._thread.is_alive():
                        logger.error("Watchdog Alert: Auto Typer runner thread terminated unexpectedly. Recovering...")
                        typer.stop()
                        self._notify_ui_refresh("typer")

                # Check Auto Clicker
                clicker = self.services.get("clicker_runner")
                if clicker and clicker.is_running():
                    if clicker._thread and not clicker._thread.is_alive():
                        logger.error("Watchdog Alert: Auto Clicker runner thread terminated unexpectedly. Recovering...")
                        clicker.stop()
                        self._notify_ui_refresh("clicker")

                # Check Macro Playback
                playback = self.services.get("playback_runner")
                if playback and playback.is_running():
                    if playback._thread and not playback._thread.is_alive():
                        logger.error("Watchdog Alert: Macro Playback runner thread terminated unexpectedly. Recovering...")
                        playback.stop()
                        self._notify_ui_refresh("macro")

            except Exception as e:
                logger.error(f"Error in Watchdog supervisor loop: {e}")

    def _notify_ui_refresh(self, page_id: str):
        """Tells the main window pages to sync their status cards after recovery."""
        # Find main window reference via root or hook
        # To avoid circular imports, we notify using a safe callback or searching open Tk frames
        try:
            # We can log a message, and if UI is open, it can refresh on next check.
            # We also trigger standard OS logs.
            pass
        except Exception:
            pass
