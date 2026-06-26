import logging
import threading
from typing import Callable, Dict
import keyboard

logger = logging.getLogger("AutoTyperPro")

class HotkeyService:
    """Safely registers, modifies, and intercepts global OS hotkeys without blocking hook loops."""
    def __init__(self, config_service):
        self.config = config_service
        self.active_hooks: Dict[str, str] = {} # action_name -> registered_hotkey_string
        self.callbacks: Dict[str, Callable[[], None]] = {}
        
        # Listen for config changes to hot-reload hotkeys
        self.config.add_listener(self._on_config_changed)

    def register_action_hotkey(self, action_name: str, callback: Callable[[], None]):
        """Binds an action name (e.g. 'auto_clicker_start_stop') to a callback.
        
        The hotkey sequence is looked up from settings.
        """
        self.callbacks[action_name] = callback
        self._bind_action(action_name)

    def _bind_action(self, action_name: str):
        """Binds a single action to its configured hotkey."""
        hotkey_str = self.config.get("hotkeys", action_name)
        if not hotkey_str:
            logger.warning(f"No hotkey configured for action '{action_name}'")
            return

        # Unbind previous if exists
        self._unbind_action(action_name)

        def safe_trigger():
            logger.info(f"Hotkey '{hotkey_str}' triggered for action '{action_name}'")
            callback = self.callbacks.get(action_name)
            if callback:
                # Trigger on a new daemon thread to prevent freezing the OS hook thread
                threading.Thread(target=callback, daemon=True).start()

        try:
            # keyboard module requires lowercase keys usually, e.g. "ctrl+alt+s" or "f6"
            normalized_hotkey = hotkey_str.lower().strip()
            keyboard.add_hotkey(normalized_hotkey, safe_trigger)
            self.active_hooks[action_name] = normalized_hotkey
            logger.info(f"Registered global hotkey '{hotkey_str}' for action '{action_name}'")
        except Exception as e:
            logger.error(f"Failed to register hotkey '{hotkey_str}' for action '{action_name}': {e}")

    def _unbind_action(self, action_name: str):
        """Unbinds a hotkey hook from the keyboard module."""
        if action_name in self.active_hooks:
            hotkey_str = self.active_hooks[action_name]
            try:
                keyboard.remove_hotkey(hotkey_str)
                logger.info(f"Unregistered global hotkey for '{action_name}'")
            except Exception as e:
                logger.error(f"Failed to unregister hotkey '{hotkey_str}': {e}")
            self.active_hooks.pop(action_name, None)

    def unregister_all(self):
        """Removes all registered hotkey handlers."""
        actions = list(self.active_hooks.keys())
        for action in actions:
            self._unbind_action(action)
        keyboard.unhook_all()
        logger.info("All global hotkeys cleaned up.")

    def _on_config_changed(self, settings: Dict):
        """Rebinds hotkeys if they were changed in the configuration settings."""
        for action_name in self.callbacks:
            new_hotkey = settings.get("hotkeys", {}).get(action_name, "").lower().strip()
            old_hotkey = self.active_hooks.get(action_name, "")
            
            if new_hotkey != old_hotkey:
                logger.info(f"Hotkey change detected for '{action_name}': '{old_hotkey}' -> '{new_hotkey}'. Re-binding.")
                self._bind_action(action_name)
