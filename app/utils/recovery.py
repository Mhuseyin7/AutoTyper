import json
import logging
from pathlib import Path
from ..config.constants import STORAGE_DIR

logger = logging.getLogger("AutoTyperPro")

SESSION_FILE = STORAGE_DIR / "session.json"

class SessionRecovery:
    """Manages periodic checkpointing and restoration of the application's visual session state."""
    @staticmethod
    def save_session_checkpoint(data: dict) -> bool:
        """Saves active state parameters (text buffer, page tabs, coordinates) to a json session file."""
        try:
            SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.debug("Session checkpoint successfully created.")
            return True
        except Exception as e:
            logger.error(f"Failed to write session checkpoint: {e}")
            return False

    @staticmethod
    def load_session_checkpoint() -> dict:
        """Loads and returns the last saved session data, or returns empty dict if none exists."""
        if not SESSION_FILE.exists():
            return {}
            
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Restored session checkpoint from last run.")
            return data
        except Exception as e:
            logger.error(f"Failed to read session checkpoint: {e}. Clearing corrupted session.")
            SessionRecovery.clear_session_checkpoint()
            return {}

    @staticmethod
    def clear_session_checkpoint():
        """Deletes the session file (clean teardown)."""
        try:
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
                logger.debug("Session checkpoint cleared.")
        except Exception as e:
            logger.error(f"Failed to clear session checkpoint: {e}")
