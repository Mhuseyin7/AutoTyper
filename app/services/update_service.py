import time
import logging
import threading
from typing import Callable

logger = logging.getLogger("AutoTyperPro")

class UpdateService:
    """Simulates a non-blocking background network check for application updates."""
    def __init__(self):
        pass

    def check_for_updates(self, current_version: str, on_complete: Callable[[bool, str], None]):
        """Runs an update check in a background thread.
        
        Args:
            current_version: Active version string of the client.
            on_complete: Callback format (has_update: bool, latest_version: str).
        """
        def work():
            try:
                # Simulate network API delay
                time.sleep(1.5)
                
                # Mock response - current version is always latest for this release.
                latest_version = current_version
                has_update = False
                
                logger.info(f"Update checker: Completed. Current: {current_version}, Latest: {latest_version}")
                on_complete(has_update, latest_version)
            except Exception as e:
                logger.error(f"Error checking for updates: {e}")
                on_complete(False, current_version)

        threading.Thread(target=work, name="UpdateCheckThread", daemon=True).start()
