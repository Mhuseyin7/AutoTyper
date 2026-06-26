import json
import logging
from typing import Any, Callable, Dict
from ..config.constants import CONFIG_PATH, DEFAULT_SETTINGS
from ..utils.validator import validate_settings

logger = logging.getLogger("AutoTyperPro")

class ConfigService:
    """Manages application configurations with validation, persistence, and observer callbacks."""
    def __init__(self):
        self.settings: Dict[str, Any] = {}
        self.listeners: list[Callable[[Dict[str, Any]], None]] = []
        self.load_settings()

    def load_settings(self):
        """Loads and validates settings from the storage JSON path."""
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                self.settings = validate_settings(loaded_data, DEFAULT_SETTINGS)
            else:
                logger.info("Configuration file not found. Creating default settings.")
                self.settings = DEFAULT_SETTINGS.copy()
                self.save_settings()
        except Exception as e:
            logger.error(f"Error loading settings: {e}. Restoring defaults.")
            self.settings = DEFAULT_SETTINGS.copy()
            self.save_settings()

    def save_settings(self):
        """Saves current settings state to disk and triggers listeners."""
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logger.debug("Settings successfully saved to disk.")
            self._notify_listeners()
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def get(self, *keys) -> Any:
        """Helper to fetch values deep inside the nested settings dictionary.
        
        Example: config.get("hotkeys", "auto_clicker_start_stop")
        """
        curr = self.settings
        for key in keys:
            if isinstance(curr, dict) and key in curr:
                curr = curr[key]
            else:
                # Resolve key from DEFAULT_SETTINGS if key path got lost somehow
                curr_def = DEFAULT_SETTINGS
                for k in keys:
                    if isinstance(curr_def, dict) and k in curr_def:
                        curr_def = curr_def[k]
                    else:
                        return None
                return curr_def
        return curr

    def set(self, key_path: list[str] | str, value: Any, save_immediately: bool = True):
        """Sets a configuration value and saves to disk.
        
        Args:
            key_path: A list of keys leading to target, or a string if it's root level.
            value: The new configuration value.
            save_immediately: If true, write to disk now.
        """
        keys = [key_path] if isinstance(key_path, str) else key_path
        if not keys:
            return
            
        curr = self.settings
        for key in keys[:-1]:
            if key not in curr or not isinstance(curr[key], dict):
                curr[key] = {}
            curr = curr[key]
            
        curr[keys[-1]] = value
        
        if save_immediately:
            self.save_settings()

    def add_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Registers a listener to receive configuration updates."""
        if callback not in self.listeners:
            self.listeners.append(callback)

    def remove_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Removes a registered configuration listener."""
        if callback in self.listeners:
            self.listeners.remove(callback)

    def _notify_listeners(self):
        """Notifies all observers that settings have changed (Hot reload dynamic styling/hotkeys)."""
        for listener in self.listeners:
            try:
                listener(self.settings)
            except Exception as e:
                logger.error(f"Failed to trigger config listener: {e}")
