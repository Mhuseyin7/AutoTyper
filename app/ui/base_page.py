import customtkinter as ctk

class BasePage(ctk.CTkFrame):
    """Abstract-like base frame that application dashboard pages inherit."""
    def __init__(self, master, services: dict, **kwargs):
        # Configure standard page layout
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self.services = services
        self.config_service = services.get("config")
        self.notification_service = services.get("notification")
        self.hotkey_service = services.get("hotkey")
        self.lang = services.get("language")
        self.stats = services.get("stats_service")
        
        # Grid weight settings for page container layout
        self.grid_rowconfigure(0, weight=0) # Page Header
        self.grid_rowconfigure(1, weight=1) # Page Content
        self.grid_columnconfigure(0, weight=1)
        
        # Headers widget references
        self.header_frame = None
        self.title_label = None
        self.subtitle_label = None
        self.divider = None

    def on_show(self):
        """Called when page enters user visibility."""
        pass

    def on_hide(self):
        """Called when page leaves user visibility."""
        pass

    def refresh_language(self):
        """Force UI labels translation updates on language changes."""
        pass

    def create_header(self, title_key: str, subtitle_key: str):
        """Standardized page header constructor that supports localizations."""
        self.title_key = title_key
        self.subtitle_key = subtitle_key

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=25, pady=(20, 15), sticky="ew")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.lang.get(title_key),
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color=("#1A1A1A", "#FFFFFF")
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text=self.lang.get(subtitle_key),
            font=ctk.CTkFont(family="Inter", size=13),
            text_color=("#666666", "#AAAAAA")
        )
        self.subtitle_label.pack(anchor="w", pady=(3, 0))
        
        # Horizontal divider line
        self.divider = ctk.CTkFrame(self, height=1, fg_color=("#E5E5E5", "#2D2D2D"))
        self.divider.grid(row=0, column=0, padx=25, pady=(0, 0), sticky="esw")

    def update_header_text(self):
        """Updates header text dynamically based on translation keys."""
        if self.title_label and self.subtitle_label:
            self.title_label.configure(text=self.lang.get(self.title_key))
            self.subtitle_label.configure(text=self.lang.get(self.subtitle_key))
