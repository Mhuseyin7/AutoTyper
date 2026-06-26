import threading
import logging
import traceback
from typing import Callable, Any, Optional

logger = logging.getLogger("AutoTyperPro")

class SafeWorkerThread(threading.Thread):
    """A worker thread that catches exceptions and reports them via callbacks."""
    def __init__(
        self,
        target: Callable[..., Any],
        args: tuple = (),
        kwargs: dict = None,
        on_complete: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception, str], None]] = None,
        name: str = "SafeWorkerThread"
    ):
        super().__init__(name=name, daemon=True)
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.on_complete = on_complete
        self.on_error = on_error
        
    def run(self):
        try:
            self.target(*self.args, **self.kwargs)
            if self.on_complete:
                try:
                    self.on_complete()
                except Exception as cb_exc:
                    logger.error(f"Callback error in complete function: {cb_exc}")
        except Exception as exc:
            err_trace = traceback.format_exc()
            logger.error(f"Thread execution error in '{self.name}': {exc}\n{err_trace}")
            if self.on_error:
                try:
                    self.on_error(exc, err_trace)
                except Exception as cb_exc:
                    logger.error(f"Callback error in error function: {cb_exc}")

class StoppableThread(threading.Thread):
    """A thread with support for cooperative stopping via a threading.Event flag."""
    def __init__(self, name: str = "StoppableThread"):
        super().__init__(name=name, daemon=True)
        self._stop_event = threading.Event()
        
    def stop(self):
        """Signals the thread to stop execution."""
        self._stop_event.set()
        
    def is_stopped(self) -> bool:
        """Returns True if the thread has been signaled to stop."""
        return self._stop_event.is_set()
        
    def wait(self, timeout: float) -> bool:
        """Waits for the stop event or timeout. Returns True if stopped, False if timed out."""
        return self._stop_event.wait(timeout)
