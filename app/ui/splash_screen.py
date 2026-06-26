import time
import customtkinter as ctk
from typing import Callable

class SplashScreen(ctk.CTk):
    """A premium borderless initialization screen showing dynamic loader steps."""
    def __init__(self, on_complete: Callable[[], None]):
        super().__init__()
        self.on_complete = on_complete
        
        # Borderless window configuration
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        # Sizing and placement
        self.width = 460
        self.height = 280
        self._center_window()

        # Premium Dark Background matching themes
        self.configure(fg_color="#0C0C0F")

        # Container Frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        # Title Label
        self.lbl_logo = ctk.CTkLabel(
            self.main_frame,
            text="AUTO TYPER PRO",
            font=ctk.CTkFont(family="Outfit", size=26, weight="bold"),
            text_color="#3A9AD9"
        )
        self.lbl_logo.pack(pady=(20, 2))

        # Premium Edition Badge
        self.lbl_badge = ctk.CTkLabel(
            self.main_frame,
            text="P R E M I U M   E D I T I O N",
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            text_color="#F1C40F" # Premium Gold
        )
        self.lbl_badge.pack(pady=(0, 30))

        # Progress Status Detail
        self.lbl_status = ctk.CTkLabel(
            self.main_frame,
            text="Initializing services...",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#888888"
        )
        self.lbl_status.pack(anchor="w", padx=10, pady=(0, 5))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame,
            width=390,
            height=6,
            corner_radius=3,
            progress_color="#3A9AD9",
            fg_color="#1E1E24"
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(pady=(0, 20))

        # Launch progress loop sequence
        self.steps = [
            (0.15, "Verifying settings schema...", 150),
            (0.35, "Configuring native Win32 APIs...", 200),
            (0.55, "Registering global system hotkeys...", 150),
            (0.75, "Bootstrapping background watchdog supervisor...", 200),
            (0.90, "Restoring last session checkpoint...", 150),
            (1.00, "Ready!", 100)
        ]
        
        self.step_idx = 0
        self.after(200, self._process_loading_step)

    def _center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def _process_loading_step(self):
        """Iterates through loading checkpoints sequentially updating progress visuals."""
        if self.step_idx < len(self.steps):
            progress, text, delay = self.steps[self.step_idx]
            
            self.progress_bar.set(progress)
            self.lbl_status.configure(text=text)
            self.step_idx += 1
            
            self.after(delay, self._process_loading_step)
        else:
            # Short wait on completion before destroying splash
            self.after(150, self._exit_splash)

    def _exit_splash(self):
        self.destroy()
        # Callback to trigger main dashboard bootstrapper
        self.on_complete()
