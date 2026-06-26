import time
import logging
import threading
from typing import Callable, Dict, List, Any, Optional
import pynput
from ..utils.thread_helper import StoppableThread

logger = logging.getLogger("AutoTyperPro")

class MacroPlaybackRunner:
    """Controls background macro playbacks with pauses, loop parameters, and modifiers support."""
    def __init__(self, services: dict, on_status_changed: Optional[Callable[[str], None]] = None):
        self.config = services.get("config")
        self.stats = services.get("stats_service")
        self.on_status_changed = on_status_changed
        
        self._thread: Optional[StoppableThread] = None
        self.mouse_controller = pynput.mouse.Controller()
        self.keyboard_controller = pynput.keyboard.Controller()
        
        # Thread Gates
        self._pause_gate = threading.Event()
        self._pause_gate.set()

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def is_paused(self) -> bool:
        return not self._pause_gate.is_set()

    def start(self, events: List[Dict[str, Any]]) -> bool:
        """Launches the background playback thread for the provided event list."""
        if not events:
            logger.warning("No events to play back.")
            return False
            
        if self.is_running():
            logger.warning("Playback runner already active.")
            return False

        self._pause_gate.set()
        self._thread = StoppableThread(name="MacroPlaybackRunnerThread")
        self._thread.run = lambda: self._run_playback(events)
        self._thread.start()
        
        if self.on_status_changed:
            self.on_status_changed("running")
            
        if self.stats:
            self.stats.start_session()
            
        logger.info("Macro playback activated.")
        return True

    def stop(self):
        """Kills macro playback immediately."""
        if self.is_running():
            self._thread.stop()
            self._pause_gate.set() # Release pause lock
            self._thread = None
            if self.on_status_changed:
                self.on_status_changed("idle")
            if self.stats:
                self.stats.stop_session(success=True)
            logger.info("Macro playback deactivated.")

    def pause(self):
        """Pauses timeline execution."""
        if self.is_running() and not self.is_paused():
            self._pause_gate.clear()
            if self.on_status_changed:
                self.on_status_changed("paused")
            logger.info("Macro playback paused.")

    def resume(self):
        """Resumes timeline execution."""
        if self.is_running() and self.is_paused():
            self._pause_gate.set()
            if self.on_status_changed:
                self.on_status_changed("running")
            logger.info("Macro playback resumed.")

    def _deserialize_key(self, key_str: str) -> pynput.keyboard.Key | str:
        """Decodes string keys to pynput Key objects (includes modifiers, Arrows, F1-F24, WinKey)."""
        # Case insensitive mapping
        key_lower = key_str.lower().strip()
        
        # WinKey mappings
        if key_lower in ("win", "windows", "cmd", "cmd_l", "cmd_r"):
            return pynput.keyboard.Key.cmd
            
        # Modifiers
        if key_lower in ("ctrl", "control", "control_l", "control_r"):
            return pynput.keyboard.Key.ctrl
        if key_lower in ("alt", "alt_l", "alt_r", "menu"):
            return pynput.keyboard.Key.alt
        if key_lower in ("shift", "shift_l", "shift_r"):
            return pynput.keyboard.Key.shift
            
        # Common controls
        if key_lower in ("enter", "return"):
            return pynput.keyboard.Key.enter
        if key_lower == "space":
            return pynput.keyboard.Key.space
        if key_lower == "tab":
            return pynput.keyboard.Key.tab
        if key_lower in ("esc", "escape"):
            return pynput.keyboard.Key.esc
        if key_lower in ("backspace", "back"):
            return pynput.keyboard.Key.backspace
        if key_lower in ("delete", "del"):
            return pynput.keyboard.Key.delete
            
        # Navigation
        if key_lower == "up":
            return pynput.keyboard.Key.up
        if key_lower == "down":
            return pynput.keyboard.Key.down
        if key_lower == "left":
            return pynput.keyboard.Key.left
        if key_lower == "right":
            return pynput.keyboard.Key.right
            
        # Standard function mapping (f1 to f24)
        if key_lower.startswith("f") and len(key_lower) > 1:
            try:
                num = int(key_lower[1:])
                if 1 <= num <= 24:
                    return getattr(pynput.keyboard.Key, f"f{num}")
            except ValueError:
                pass

        if key_str in pynput.keyboard.Key.__members__:
            return pynput.keyboard.Key[key_str]
        
        # Single char keys
        if len(key_str) == 3 and key_str.startswith("'") and key_str.endswith("'"):
            return key_str[1]
            
        return key_str

    def _run_playback(self, events: List[Dict[str, Any]]):
        """Sequences and executes macro actions in real-time."""
        try:
            speed_mult = self.config.get("macro", "speed")
            loop_limit = self.config.get("macro", "loop")
            loop_delay = self.config.get("macro", "loop_delay")
            
            speed = max(0.05, min(100.0, speed_mult))
            current_loop = 0
            thread = self._thread

            while not thread.is_stopped():
                self._pause_gate.wait()
                if thread.is_stopped():
                    break
                    
                last_event_time = 0.0
                
                for idx, event in enumerate(events):
                    # Check pause gate
                    self._pause_gate.wait()
                    if thread.is_stopped():
                        break
                        
                    # Calculate wait offset
                    elapsed_in_record = event["time_offset"] - last_event_time
                    last_event_time = event["time_offset"]
                    
                    # Apply speed factor
                    wait_time = elapsed_in_record / speed
                    
                    # Sleep responsive to stop/pause gates
                    if idx > 0 and wait_time > 0:
                        end_sleep = time.perf_counter() + wait_time
                        while time.perf_counter() < end_sleep and not thread.is_stopped():
                            self._pause_gate.wait()
                            time.sleep(0.005)
                            
                    # Dispatch action
                    if not thread.is_stopped():
                        self._dispatch_event(event)
                        
                    # Telemetry count
                    if self.stats:
                        self.stats.record_char_typed(1)

                current_loop += 1
                if self.stats:
                    self.stats.record_repeat()
                    
                # Loop limits check
                if loop_limit > 0 and current_loop >= loop_limit:
                    logger.info(f"Playback finished. Loop limit ({loop_limit}) reached.")
                    break
                    
                # Loop Delay wait
                if not thread.is_stopped() and loop_delay > 0:
                    if thread.wait(loop_delay):
                        break

        except Exception as e:
            logger.error(f"Critical error in macro playback execution: {e}")
            if self.on_status_changed:
                self.on_status_changed("error")
            if self.stats:
                self.stats.stop_session(success=False)
            return

        if self.on_status_changed:
            self.on_status_changed("idle")

    def _dispatch_event(self, event: Dict[str, Any]):
        """Executes a single timeline step: keystroke, click, move, or delay blocks."""
        etype = event["type"]
        
        try:
            if etype == "move":
                self.mouse_controller.position = (event["x"], event["y"])
                
            elif etype == "click":
                self.mouse_controller.position = (event["x"], event["y"])
                button_name = event.get("button", "left").lower()
                if button_name in pynput.mouse.Button.__members__:
                    button = pynput.mouse.Button[button_name]
                else:
                    button = pynput.mouse.Button.left
                    
                pressed = event.get("pressed", True)
                if pressed:
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
                    
            elif etype == "key_down":
                key = self._deserialize_key(event["key"])
                self.keyboard_controller.press(key)
                
            elif etype == "key_up":
                key = self._deserialize_key(event["key"])
                self.keyboard_controller.release(key)
                
            elif etype == "delay":
                # Custom Delay Block
                delay_ms = event.get("delay_ms", 1000)
                time.sleep(max(0.001, delay_ms / 1000.0))
                
        except Exception as e:
            logger.debug(f"Failed to play back event {event}: {e}")
