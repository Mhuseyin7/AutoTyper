import os
import logging
import threading
import tracemalloc
from typing import Tuple

logger = logging.getLogger("AutoTyperPro")

class ResourceProfiler:
    """Provides memory allocation and active thread tracking for performance auditing."""
    _tracemalloc_started = False

    @classmethod
    def start_profiling(cls):
        """Starts python's standard library tracemalloc profiler."""
        if not cls._tracemalloc_started:
            try:
                tracemalloc.start()
                cls._tracemalloc_started = True
                logger.info("Resource performance profiling enabled (tracemalloc active).")
            except Exception as e:
                logger.error(f"Failed to start memory profiling: {e}")

    @classmethod
    def get_memory_usage_mb(cls) -> float:
        """Returns the current RAM usage of the process in MB."""
        if not cls._tracemalloc_started:
            return 0.0
        try:
            current, peak = tracemalloc.get_traced_memory()
            # Convert bytes to Megabytes
            return current / (1024.0 * 1024.0)
        except Exception:
            return 0.0

    @classmethod
    def get_active_threads_info(cls) -> Tuple[int, list[str]]:
        """Returns active thread counts and their names."""
        threads = threading.enumerate()
        thread_names = [t.name for t in threads]
        return len(threads), thread_names

    @classmethod
    def log_profile_summary(cls):
        """Writes current performance stats to the application log."""
        mem_mb = cls.get_memory_usage_mb()
        thread_cnt, thread_names = cls.get_active_threads_info()
        logger.info(
            f"--- Performance Profile ---\n"
            f"Memory Footprint: {mem_mb:.3f} MB\n"
            f"Active Thread Count: {thread_cnt}\n"
            f"Thread Names: {', '.join(thread_names)}\n"
            f"---------------------------"
        )
