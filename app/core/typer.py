import time
import csv
import random
import logging
import threading
import win32clipboard
from pathlib import Path
from typing import Callable, Optional, List
import pynput
from ..utils.thread_helper import StoppableThread
from ..utils.win32_helper import focus_window, get_all_open_windows, send_paste_command

logger = logging.getLogger("AutoTyperPro")

# QWERTY adjacent key neighbors mapping for typing error emulation
NEIGHBORS = {
    'a': 'qwsz', 'b': 'vghn', 'c': 'xdfv', 'd': 'ersfxc', 'e': 'wsdr',
    'f': 'rtgvcd', 'g': 'tyhbvf', 'h': 'yujnbg', 'i': 'ujko', 'j': 'uikmnh',
    'k': 'ijlm', 'l': 'okp', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
    'p': 'ol', 'q': 'wa', 'r': 'edft', 's': 'wedxza', 't': 'rfgy',
    'u': 'yhji', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc', 'y': 'tghu',
    'z': 'asx',
    # Turkish layout adjustments
    'ç': 'xö', 'ğ': 'püı', 'ı': 'ouşğ', 'ö': 'çlmn', 'ş': 'ıliğ', 'ü': 'ğış'
}

class AutoTyperRunner:
    """Advanced execution runner for typing text block sequences with human typing emulation."""
    def __init__(self, services: dict, on_status_changed: Optional[Callable[[str], None]] = None):
        self.config = services.get("config")
        self.stats = services.get("stats_service")
        self.on_status_changed = on_status_changed
        
        self._thread: Optional[StoppableThread] = None
        self.keyboard_controller = pynput.keyboard.Controller()
        
        # Thread Gates for pausing
        self._pause_gate = threading.Event()
        self._pause_gate.set() # Unpaused initially

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def is_paused(self) -> bool:
        return not self._pause_gate.is_set()

    def start(self) -> bool:
        """Launches the auto-typer runner thread."""
        if self.is_running():
            logger.warning("Auto Typer is already active.")
            return False

        self._pause_gate.set() # Clear any pause locks
        self._thread = StoppableThread(name="AutoTyperRunnerThread")
        self._thread.run = self._run_loop
        self._thread.start()
        
        if self.on_status_changed:
            self.on_status_changed("running")
            
        if self.stats:
            self.stats.start_session()
            
        logger.info("Auto Typer active.")
        return True

    def stop(self):
        """Kills the auto-typer thread."""
        if self.is_running():
            self._thread.stop()
            self._pause_gate.set() # Release pause lock to let thread exit
            self._thread = None
            if self.on_status_changed:
                self.on_status_changed("idle")
            if self.stats:
                self.stats.stop_session(success=True)
            logger.info("Auto Typer deactivated.")

    def pause(self):
        """Pauses the typing thread execution mid-character."""
        if self.is_running() and not self.is_paused():
            self._pause_gate.clear()
            if self.on_status_changed:
                self.on_status_changed("paused")
            logger.info("Auto Typer execution paused.")

    def resume(self):
        """Resumes the typing thread execution."""
        if self.is_running() and self.is_paused():
            self._pause_gate.set()
            if self.on_status_changed:
                self.on_status_changed("running")
            logger.info("Auto Typer execution resumed.")

    def load_text_from_file(self, file_path_str: str) -> str:
        """Utility to parse text from an external .txt or .csv file path."""
        path = Path(file_path_str)
        if not path.exists():
            logger.error(f"Import file not found: {file_path_str}")
            return ""
            
        try:
            if path.suffix.lower() == ".csv":
                rows = []
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        rows.append(", ".join(row))
                return "\n".join(rows)
            else: # Fallback to standard TXT
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path_str}: {e}")
            return ""

    def _run_loop(self):
        """Deep execution flow supporting pausing, initial delay, human-emulation delay, and loop delays."""
        try:
            # Load Configurations
            text = self.config.get("auto_typer", "text")
            mode = self.config.get("auto_typer", "mode")          # "simulate", "write", "paste"
            flow = self.config.get("auto_typer", "typing_flow")   # "entire", "line", "random"
            
            initial_delay = self.config.get("auto_typer", "initial_delay")
            char_delay = self.config.get("auto_typer", "char_delay")
            word_delay = self.config.get("auto_typer", "word_delay")
            line_delay = self.config.get("auto_typer", "line_delay")
            loop_limit = self.config.get("auto_typer", "loop")
            loop_delay = self.config.get("auto_typer", "loop_delay")
            
            human_like = self.config.get("auto_typer", "human_like")
            variance = self.config.get("auto_typer", "delay_variance")
            punc_delay = self.config.get("auto_typer", "punc_delay")
            error_rate = self.config.get("auto_typer", "spelling_error_rate") or 0.0
            
            target_mode = self.config.get("auto_typer", "target_mode")
            target_title = self.config.get("auto_typer", "target_window")

            thread = self._thread

            # 1. Target Specific Window if configured
            if target_mode == "specific" and target_title:
                focused = self._focus_target_window(target_title)
                if not focused:
                    logger.error(f"Target window focus failed: '{target_title}'")
                    if self.on_status_changed:
                        self.on_status_changed("error")
                    if self.stats:
                        self.stats.stop_session(success=False)
                    return
                time.sleep(0.3)

            # 2. Start Initial Delay (cancellable)
            if initial_delay > 0:
                if thread.wait(initial_delay):
                    return

            current_loop = 0
            
            # Prepare lines for line-by-line flow options
            raw_lines = text.splitlines()
            # Clean empty lines
            lines_pool = [line for line in raw_lines if line.strip()]
            if not lines_pool:
                lines_pool = [text] # Fallback if text has no line breaks

            while not thread.is_stopped():
                # Check pause gate
                self._pause_gate.wait()
                if thread.is_stopped():
                    break

                # 3. Process according to typing flow mode
                if flow == "line":
                    for line in lines_pool:
                        self._pause_gate.wait()
                        if thread.is_stopped():
                            break
                        self._type_segment(line, mode, char_delay, word_delay, human_like, variance, punc_delay, error_rate, thread)
                        # Add Line Delay
                        if line_delay > 0 and not thread.is_stopped():
                            if mode != "paste":
                                self.keyboard_controller.tap(pynput.keyboard.Key.enter)
                            if thread.wait(line_delay):
                                break
                                
                elif flow == "random":
                    random_line = random.choice(lines_pool)
                    self._type_segment(random_line, mode, char_delay, word_delay, human_like, variance, punc_delay, error_rate, thread)
                    if mode != "paste" and not thread.is_stopped():
                        self.keyboard_controller.tap(pynput.keyboard.Key.enter)
                        
                else: # "entire"
                    self._type_segment(text, mode, char_delay, word_delay, human_like, variance, punc_delay, error_rate, thread)

                # Increment statistics loops
                current_loop += 1
                if self.stats:
                    self.stats.record_repeat()

                # Check repeat count bounds
                if loop_limit > 0 and current_loop >= loop_limit:
                    logger.info(f"Typing complete. Iteration limit ({loop_limit}) reached.")
                    break
                    
                # Loop Delay Wait
                if not thread.is_stopped() and loop_delay > 0:
                    if thread.wait(loop_delay):
                        break

        except Exception as e:
            logger.error(f"Critical error during Auto Typer execution: {e}")
            if self.on_status_changed:
                self.on_status_changed("error")
            if self.stats:
                self.stats.stop_session(success=False)
            return

        if self.on_status_changed:
            self.on_status_changed("idle")

    def _type_segment(self, segment: str, mode: str, char_delay: float, word_delay: float, 
                      human_like: bool, variance: float, punc_delay: float, error_rate: float, thread: StoppableThread):
        """Simulates character strokes on a string segment with precision delays and error emulations."""
        if mode == "paste":
            self._paste_text(segment)
            if self.stats:
                self.stats.record_char_typed(len(segment))
        elif mode == "write":
            self.keyboard_controller.type(segment)
            if self.stats:
                self.stats.record_char_typed(len(segment))
        else: # "simulate"
            length = len(segment)
            for idx, char in enumerate(segment):
                # Check pause gate
                self._pause_gate.wait()
                if thread.is_stopped():
                    break
                    
                # Spelling Error Emulation (Premium)
                is_letter = char.lower() in NEIGHBORS
                if human_like and error_rate > 0 and is_letter and random.random() < error_rate:
                    self._simulate_typo_and_correction(char, char_delay, variance, thread)

                # Emit correct key tap
                try:
                    self.keyboard_controller.tap(char)
                except ValueError:
                    try:
                        self.keyboard_controller.press(char)
                        self.keyboard_controller.release(char)
                    except Exception:
                        pass
                
                # Telemetry record
                if self.stats:
                    self.stats.record_char_typed(1)
                    
                # Calculate sleep delay
                is_space = (char == ' ')
                is_punc = (char in ('.', ',', '?', '!'))
                is_newline = (char == '\n')
                
                delay = char_delay
                if human_like:
                    # Cadence: slightly faster inside words (idx - boundary check)
                    is_middle_word = not is_space and not is_punc and idx > 0 and idx < length - 1 and segment[idx-1] != ' ' and segment[idx+1] != ' '
                    
                    delay = random.uniform(char_delay * (1.0 - variance), char_delay * (1.0 + variance))
                    if is_middle_word:
                        delay *= 0.82 # Faster middle-word typing flow
                    else:
                        delay *= 1.18 # Slower word start/end transition
                        
                    if is_space:
                        delay += word_delay + random.uniform(0.01, 0.06)
                    elif is_punc:
                        delay += punc_delay + random.uniform(0.05, 0.15)
                    elif is_newline:
                        delay += 1.2 + random.uniform(0.2, 0.6) # Paragraph pause
                else:
                    if is_space:
                        delay += word_delay
                    elif is_punc:
                        delay += punc_delay
                    elif is_newline:
                        delay += 0.8
                        
                if delay > 0:
                    time.sleep(delay)

    def _simulate_typo_and_correction(self, correct_char: str, base_delay: float, variance: float, thread: StoppableThread):
        """Types a neighboring key, enters a pause, hits backspace, and waits before correcting."""
        try:
            char_lower = correct_char.lower()
            typo_pool = NEIGHBORS.get(char_lower, 'qwsz')
            typo_char = random.choice(typo_pool)
            
            # Match casing
            if correct_char.isupper():
                typo_char = typo_char.upper()
                
            # Type error
            self.keyboard_controller.tap(typo_char)
            if self.stats:
                self.stats.record_char_typed(1)
                
            # Typing mistake shock pause
            time.sleep(base_delay * random.uniform(1.2, 1.8))
            
            # Hit Backspace
            self._pause_gate.wait()
            if not thread.is_stopped():
                self.keyboard_controller.tap(pynput.keyboard.Key.backspace)
                
            # Wait after correction backspace
            time.sleep(base_delay * random.uniform(1.5, 2.2))
        except Exception as e:
            logger.debug(f"Failed typo simulation: {e}")

    def _focus_target_window(self, title: str) -> bool:
        windows = get_all_open_windows()
        for w in windows:
            if title.lower() in w["title"].lower():
                return focus_window(w["hwnd"])
        return False

    def _paste_text(self, text: str):
        prior_text = None
        win32clipboard.OpenClipboard()
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                prior_text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except Exception:
            pass
        finally:
            win32clipboard.CloseClipboard()

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        except Exception as e:
            logger.error(f"Clipboard paste set failed: {e}")
            win32clipboard.CloseClipboard()
            return
        finally:
            win32clipboard.CloseClipboard()

        send_paste_command()
        time.sleep(0.15)

        if prior_text is not None:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(prior_text, win32clipboard.CF_UNICODETEXT)
            except Exception:
                pass
            finally:
                win32clipboard.CloseClipboard()
