import time
import logging
from typing import Callable, List, Dict, Any, Optional
import pynput

logger = logging.getLogger("AutoTyperPro")

class InputHookListener:
    """Listens to global system-wide mouse and keyboard inputs to record automation macros."""
    def __init__(self, on_event_recorded: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.on_event_recorded = on_event_recorded
        self.recorded_events: List[Dict[str, Any]] = []
        self.start_time: float = 0.0
        self.is_recording: bool = False
        
        self._mouse_listener: Optional[pynput.mouse.Listener] = None
        self._keyboard_listener: Optional[pynput.keyboard.Listener] = None
        
        # Throttling mouse move events (seconds) to prevent massive memory footprint
        self._last_move_time: float = 0.0
        self._move_throttle: float = 0.015  # ~60 FPS sampling rate for movements

    def start_recording(self, record_mouse: bool = True, record_keyboard: bool = True):
        """Starts capturing system input events."""
        if self.is_recording:
            return
            
        self.recorded_events.clear()
        self.start_time = time.perf_counter()
        self.is_recording = True
        self._last_move_time = 0.0
        
        logger.info(f"Input recording started. Mouse: {record_mouse}, Keyboard: {record_keyboard}")

        if record_mouse:
            self._mouse_listener = pynput.mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click
            )
            self._mouse_listener.start()

        if record_keyboard:
            self._keyboard_listener = pynput.keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self._keyboard_listener.start()

    def stop_recording(self) -> List[Dict[str, Any]]:
        """Stops capturing inputs and returns the sequence of recorded events."""
        if not self.is_recording:
            return []

        self.is_recording = False
        
        if self._mouse_listener:
            try:
                self._mouse_listener.stop()
            except Exception:
                pass
            self._mouse_listener = None

        if self._keyboard_listener:
            try:
                self._keyboard_listener.stop()
            except Exception:
                pass
            self._keyboard_listener = None

        logger.info(f"Input recording stopped. Recorded {len(self.recorded_events)} events.")
        return self.recorded_events

    def _get_elapsed_time(self) -> float:
        """Returns elapsed time in seconds since recording started."""
        return time.perf_counter() - self.start_time

    def _add_event(self, event: Dict[str, Any]):
        """Saves an event and triggers callback."""
        if not self.is_recording:
            return
        self.recorded_events.append(event)
        if self.on_event_recorded:
            try:
                self.on_event_recorded(event)
            except Exception as e:
                logger.error(f"Error in hook event callback: {e}")

    # --- Mouse Callbacks ---

    def _on_mouse_move(self, x: int, y: int):
        now = time.perf_counter()
        if now - self._last_move_time >= self._move_throttle:
            self._last_move_time = now
            self._add_event({
                "type": "move",
                "x": x,
                "y": y,
                "time_offset": self._get_elapsed_time()
            })

    def _on_mouse_click(self, x: int, y: int, button: pynput.mouse.Button, pressed: bool):
        # We record separate press and release events for clicking
        event_type = "click"
        self._add_event({
            "type": event_type,
            "x": x,
            "y": y,
            "button": button.name, # "left", "right", etc.
            "pressed": pressed,    # True = Down, False = Up
            "time_offset": self._get_elapsed_time()
        })

    # --- Keyboard Callbacks ---

    def _serialize_key(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode) -> str:
        """Helper to convert pynput Key objects into clean JSON-serializable strings."""
        if isinstance(key, pynput.keyboard.Key):
            return key.name
        elif hasattr(key, 'char') and key.char is not None:
            return key.char
        else:
            return str(key)

    def _on_key_press(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode):
        self._add_event({
            "type": "key_down",
            "key": self._serialize_key(key),
            "time_offset": self._get_elapsed_time()
        })

    def _on_key_release(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode):
        self._add_event({
            "type": "key_up",
            "key": self._serialize_key(key),
            "time_offset": self._get_elapsed_time()
        })
