import customtkinter as ctk

class StatusCard(ctk.CTkFrame):
    """A premium visual dashboard card displaying process execution states and hotkeys."""
    def __init__(self, master, title: str, hotkey: str = "None", **kwargs):
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", ("#E0E0E0", "#2D2D2D"))
        kwargs.setdefault("fg_color", ("#F9F9F9", "#1E1E1E"))
        super().__init__(master, **kwargs)
        
        self.title_text = title
        self.hotkey_text = hotkey
        self.status_state = "idle" # "idle", "running", "error"

        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Left Column: Info
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.title_label = ctk.CTkLabel(
            self.info_frame,
            text=self.title_text,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=("#333333", "#E0E0E0")
        )
        self.title_label.pack(anchor="w")
        
        self.hotkey_label = ctk.CTkLabel(
            self.info_frame,
            text=f"Trigger Shortcut: {self.hotkey_text}",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color=("#666666", "#888888")
        )
        self.hotkey_label.pack(anchor="w", pady=(4, 0))

        # Right Column: Visual Indicator
        self.indicator_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.indicator_frame.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # We can draw the dot using a small CTkFrame with corner radius, or a label
        self.status_dot = ctk.CTkFrame(
            self.indicator_frame,
            width=12,
            height=12,
            corner_radius=6,
            fg_color="#7F8C8D" # Idle gray
        )
        self.status_dot.pack(side="left", padx=(0, 8))
        
        self.status_label = ctk.CTkLabel(
            self.indicator_frame,
            text="IDLE",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color=("#7F8C8D", "#95A5A6")
        )
        self.status_label.pack(side="right")

    def update_status(self, state: str):
        """Updates the status card visuals according to active runner state."""
        self.status_state = state.lower()
        
        if self.status_state == "running":
            # Vibrant Green
            dot_color = "#2ECC71"
            text_color = "#2ECC71"
            label_text = "RUNNING"
            self.configure(border_color=("#2ECC71", "#1B3B26"))
        elif self.status_state == "error":
            # Premium Red
            dot_color = "#E74C3C"
            text_color = "#E74C3C"
            label_text = "ERROR"
            self.configure(border_color=("#E74C3C", "#3C1E20"))
        else:
            # Idle Gray
            dot_color = ("#7F8C8D", "#7F8C8D")
            text_color = ("#7F8C8D", "#95A5A6")
            label_text = "IDLE"
            self.configure(border_color=("#E0E0E0", "#2D2D2D"))
            
        self.status_dot.configure(fg_color=dot_color)
        self.status_label.configure(text=label_text, text_color=text_color)

    def update_hotkey(self, hotkey: str):
        """Updates the trigger shortcut label display."""
        self.hotkey_text = hotkey
        self.hotkey_label.configure(text=f"Trigger Shortcut: {self.hotkey_text}")
