import customtkinter as ctk
import tkinter as tk

class HotkeyEntry(ctk.CTkEntry):
    """A custom CustomTkinter Entry widget that records key combinations for global hotkeys."""
    def __init__(self, master, on_hotkey_recorded=None, **kwargs):
        # Default styling to look premium
        kwargs.setdefault("width", 150)
        kwargs.setdefault("justify", "center")
        kwargs.setdefault("placeholder_text", "Click to bind...")
        super().__init__(master, **kwargs)
        
        self.on_hotkey_recorded = on_hotkey_recorded
        self.current_modifiers = set()
        
        # Track focus bindings
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<KeyRelease>", self._on_key_release)
        
        # Read-only configuration
        self.configure(state="normal")
        self._recorded_hotkey = ""

    def get_hotkey(self) -> str:
        """Returns the currently set hotkey string."""
        return self._recorded_hotkey

    def set_hotkey(self, hotkey_str: str):
        """Programmatically sets the displayed hotkey."""
        self._recorded_hotkey = hotkey_str
        self.configure(state="normal")
        self.delete(0, tk.END)
        self.insert(0, hotkey_str)
        # Keep read-only style
        self.configure(state="readonly")

    def _on_focus_in(self, event):
        self.configure(state="normal")
        self.delete(0, tk.END)
        self.insert(0, "Press hotkey...")
        self.configure(text_color=("#1F6AA5", "#3A9AD9")) # Highlights focused capture state
        self.current_modifiers.clear()

    def _on_focus_out(self, event):
        self.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        if not self._recorded_hotkey:
            self.set_hotkey("")
        else:
            self.set_hotkey(self._recorded_hotkey)

    def _on_key_press(self, event):
        keysym = event.keysym
        
        # Suppress normal character input
        if keysym == "Tab":
            return # Let user tab out if they want
            
        # Parse modifiers
        if keysym in ("Control_L", "Control_R", "Control"):
            self.current_modifiers.add("Ctrl")
            self._update_display("Ctrl + ...")
            return "break"
        elif keysym in ("Alt_L", "Alt_R", "Alt"):
            self.current_modifiers.add("Alt")
            self._update_display("Alt + ...")
            return "break"
        elif keysym in ("Shift_L", "Shift_R", "Shift"):
            self.current_modifiers.add("Shift")
            self._update_display("Shift + ...")
            return "break"

        # Map special Tkinter keysym names to clean formats
        key_mapping = {
            "space": "Space",
            "Return": "Enter",
            "Escape": "Esc",
            "BackSpace": "Backspace",
            "Delete": "Delete",
            "Prior": "PageUp",
            "Next": "PageDown",
            "Home": "Home",
            "End": "End",
            "Left": "Left",
            "Up": "Up",
            "Right": "Right",
            "Down": "Down",
        }
        
        display_key = key_mapping.get(keysym, keysym)
        
        # If it is a character, make it uppercase for professional representation
        if len(display_key) == 1:
            display_key = display_key.upper()
            
        # If it's a function key (F1-F12), preserve it
        # Tkinter represents function keys as F1, F2, etc., which is perfect
        
        # Construct final hotkey combination
        combo = list(self.current_modifiers)
        if display_key not in ("Ctrl", "Alt", "Shift"):
            combo.append(display_key)
            
        final_hotkey = "+".join(combo)
        
        # Update state and set readonly
        self._recorded_hotkey = final_hotkey
        self.set_hotkey(final_hotkey)
        
        # Trigger callback
        if self.on_hotkey_recorded:
            self.on_hotkey_recorded(final_hotkey)
            
        # Lose focus to save
        self.master.focus_set()
        return "break"

    def _on_key_release(self, event):
        keysym = event.keysym
        if keysym in ("Control_L", "Control_R", "Control"):
            self.current_modifiers.discard("Ctrl")
        elif keysym in ("Alt_L", "Alt_R", "Alt"):
            self.current_modifiers.discard("Alt")
        elif keysym in ("Shift_L", "Shift_R", "Shift"):
            self.current_modifiers.discard("Shift")
        return "break"

    def _update_display(self, text: str):
        self.configure(state="normal")
        self.delete(0, tk.END)
        self.insert(0, text)
