import time
import json
import logging
from typing import Callable, Optional
from ..config.constants import STORAGE_DIR

logger = logging.getLogger("AutoTyperPro")

class StatsService:
    """Tracks, aggregates, and persists session execution metrics and WPM/CPM rates."""
    def __init__(self):
        self.stats_file = STORAGE_DIR / "stats.json"
        
        # In-memory metrics
        self.total_chars_typed = 0
        self.total_repeats = 0
        self.success_count = 0
        self.attempt_count = 0
        self.total_run_duration = 0.0 # seconds
        
        # Session state tracking
        self._session_start_time: Optional[float] = None
        self._session_typed_chars = 0
        
        self.listeners: list[Callable[[], None]] = []
        self.load_stats()

    def add_listener(self, callback: Callable[[], None]):
        if callback not in self.listeners:
            self.listeners.append(callback)

    def _notify(self):
        for cb in self.listeners:
            try:
                cb()
            except Exception:
                pass

    def load_stats(self):
        """Restores aggregate telemetry history from disk."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.total_chars_typed = data.get("total_chars_typed", 0)
                self.total_repeats = data.get("total_repeats", 0)
                self.success_count = data.get("success_count", 0)
                self.attempt_count = data.get("attempt_count", 0)
                self.total_run_duration = data.get("total_run_duration", 0.0)
            else:
                self.save_stats()
        except Exception as e:
            logger.error(f"Failed to load statistics: {e}")

    def save_stats(self):
        """Persists stats to disk."""
        try:
            data = {
                "total_chars_typed": self.total_chars_typed,
                "total_repeats": self.total_repeats,
                "success_count": self.success_count,
                "attempt_count": self.attempt_count,
                "total_run_duration": self.total_run_duration
            }
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")

    def start_session(self):
        """Marks session start timestamp to compute active WPM/CPM rates."""
        self._session_start_time = time.perf_counter()
        self._session_typed_chars = 0
        logger.debug("Telemetry statistics session started.")

    def stop_session(self, success: bool = True):
        """Closes session, aggregates active time, increments repeat counts, and saves."""
        if self._session_start_time is not None:
            elapsed = time.perf_counter() - self._session_start_time
            self.total_run_duration += elapsed
            self._session_start_time = None
            
        self.attempt_count += 1
        if success:
            self.success_count += 1
            
        self.save_stats()
        self._notify()
        logger.debug("Telemetry statistics session completed and saved.")

    def record_char_typed(self, count: int = 1):
        """Increments typing counter."""
        self.total_chars_typed += count
        self._session_typed_chars += count
        self._notify()

    def record_repeat(self):
        """Increments loop counters."""
        self.total_repeats += 1
        self._notify()

    def get_cpm(self) -> float:
        """Returns Characters Per Minute (CPM) dynamically based on active session time."""
        if self._session_start_time is None:
            return 0.0
            
        elapsed_sec = time.perf_counter() - self._session_start_time
        if elapsed_sec < 1.0:
            return 0.0
            
        return (self._session_typed_chars / elapsed_sec) * 60.0

    def get_wpm(self) -> float:
        """Returns Words Per Minute (WPM) standard (Word = 5 Characters)."""
        return self.get_cpm() / 5.0

    def get_success_rate(self) -> float:
        """Returns automation success percentage."""
        if self.attempt_count == 0:
            return 100.0
        return (self.success_count / self.attempt_count) * 100.0

    def reset_all(self):
        """Clears all telemetry counters."""
        self.total_chars_typed = 0
        self.total_repeats = 0
        self.success_count = 0
        self.attempt_count = 0
        self.total_run_duration = 0.0
        self._session_start_time = None
        self._session_typed_chars = 0
        self.save_stats()
        self._notify()
        logger.info("Application statistics reset.")
