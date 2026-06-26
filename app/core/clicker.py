import time
import logging
import threading
from typing import Callable, Optional
from ..utils.thread_helper import StoppableThread
from ..utils.win32_helper import simulate_click

logger = logging.getLogger("AutoTyperPro")

class AutoClickerRunner:
    """Manages high-performance background mouse click automation with pause controls."""
    def __init__(self, services: dict, on_status_changed: Optional[Callable[[str], None]] = None):
        self.config = services.get("config")
        self.stats = services.get("stats_service")
        self.on_status_changed = on_status_changed
        
        self._thread: Optional[StoppableThread] = None
        self._pause_gate = threading.Event()
        self._pause_gate.set()

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def is_paused(self) -> bool:
        return not self._pause_gate.is_set()

    def start(self) -> bool:
        """Starts the auto clicker execution thread."""
        if self.is_running():
            logger.warning("Auto Clicker is already running.")
            return False

        self._pause_gate.set()
        self._thread = StoppableThread(name="AutoClickerRunnerThread")
        self._thread.run = self._run_loop
        self._thread.start()
        
        if self.on_status_changed:
            self.on_status_changed("running")
            
        if self.stats:
            self.stats.start_session()
            
        logger.info("Auto Clicker runner active.")
        return True

    def stop(self):
        """Stops the auto clicker execution thread."""
        if self.is_running():
            self._thread.stop()
            self._pause_gate.set() # Release pause locks
            self._thread = None
            if self.on_status_changed:
                self.on_status_changed("idle")
            if self.stats:
                self.stats.stop_session(success=True)
            logger.info("Auto Clicker runner deactivated.")

    def pause(self):
        """Pauses clicking loop mid-click."""
        if self.is_running() and not self.is_paused():
            self._pause_gate.clear()
            if self.on_status_changed:
                self.on_status_changed("paused")
            logger.info("Auto Clicker paused.")

    def resume(self):
        """Resumes clicking loop."""
        if self.is_running() and self.is_paused():
            self._pause_gate.set()
            if self.on_status_changed:
                self.on_status_changed("running")
            logger.info("Auto Clicker resumed.")

    def _run_loop(self):
        """High-frequency clicking loop executing inside the background thread."""
        try:
            # Load fresh configurations
            interval_ms = self.config.get("auto_clicker", "interval_ms")
            button = self.config.get("auto_clicker", "button")
            click_type = self.config.get("auto_clicker", "click_type")
            position_mode = self.config.get("auto_clicker", "position_mode") # "cursor", "fixed"
            fixed_x = self.config.get("auto_clicker", "fixed_x")
            fixed_y = self.config.get("auto_clicker", "fixed_y")
            loop_limit = self.config.get("auto_clicker", "loop")

            interval_sec = max(0.001, interval_ms / 1000.0)
            current_clicks = 0
            thread = self._thread

            while not thread.is_stopped():
                # Check pause gate
                self._pause_gate.wait()
                if thread.is_stopped():
                    break

                # Determine click targets
                if position_mode == "fixed":
                    x, y = fixed_x, fixed_y
                else:
                    x, y = None, None  # simulate_click defaults to current cursor

                # Execute win32 click
                simulate_click(x, y, button, click_type)
                
                # Telemetry record (each click registers as 1 action character)
                if self.stats:
                    self.stats.record_char_typed(1)
                    
                current_clicks += 1
                
                # Record loop repeat status
                if self.stats:
                    self.stats.record_repeat()

                # Check limit
                if loop_limit > 0 and current_clicks >= loop_limit:
                    logger.info(f"Click limit of {loop_limit} reached.")
                    break
                    
                # Precise, responsive sleep
                if not thread.is_stopped():
                    # Sleep in small slices to respond to stop/pause rapidly
                    end_time = time.perf_counter() + interval_sec
                    while time.perf_counter() < end_time and not thread.is_stopped():
                        self._pause_gate.wait()
                        time.sleep(0.005)

        except Exception as e:
            logger.error(f"Error in clicker execution loop: {e}")
            if self.on_status_changed:
                self.on_status_changed("error")
            if self.stats:
                self.stats.stop_session(success=False)
            return

        if self.on_status_changed:
            self.on_status_changed("idle")
