import customtkinter as ctk
from .typer_page import TyperPage
from .clicker_page import ClickerPage
from .macro_page import MacroPage
from .settings_page import SettingsPage
from ..config.constants import APP_NAME, VERSION

class MainWindow(ctk.CTk):
    """The master dashboard shell hosting navigation sidebars, pages, and real-time status bars."""
    def __init__(self, services: dict):
        super().__init__()
        
        self.services = services
        self.config_service = services.get("config")
        self.notification_service = services.get("notification")
        self.lang = services.get("language")
        self.backup = services.get("backup_service")
        
        # Link notification service root reference
        self.notification_service.set_root(self)

        # Set Window Properties
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1020x680")
        self.minimum_size = (950, 600)
        self.minsize(*self.minimum_size)
        
        self._center_window()

        # Apply Loaded Settings Theme
        theme_val = self.config_service.get("theme")
        ctk.set_appearance_mode(theme_val)
        
        # Main Grid Layout: Sidebar + Main Content Frame + Status Bar
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Content
        self.grid_rowconfigure(0, weight=1)    # Content height stretches
        self.grid_rowconfigure(1, weight=0)    # Status Bar

        # 1. Sidebar Panel
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            border_width=0,
            fg_color=("#F2F2F2", "#111115")
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Push version to footer

        # Logo text
        self.lbl_logo = ctk.CTkLabel(
            self.sidebar_frame,
            text=APP_NAME.upper(),
            font=ctk.CTkFont(family="Outfit", size=18, weight="bold"),
            text_color=("#1F6AA5", "#3A9AD9")
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(30, 25), sticky="w")

        # Sidebar Buttons
        self.nav_buttons = {}
        self.nav_items = [
            ("typer", "tab_typer"),
            ("clicker", "tab_clicker"),
            ("macro", "tab_macro"),
            ("settings", "tab_settings")
        ]

        for idx, (page_id, translation_key) in enumerate(self.nav_items):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text="", # set dynamically by refresh_language
                font=ctk.CTkFont(family="Inter", size=13, weight="normal"),
                height=42,
                anchor="w",
                corner_radius=8,
                fg_color="transparent",
                text_color=("#333333", "#CCCCCC"),
                hover_color=("#E0E0E0", "#222228"),
                command=lambda p=page_id: self.select_page(p)
            )
            btn.grid(row=idx+1, column=0, padx=12, pady=5, sticky="ew")
            self.nav_buttons[page_id] = btn

        # Version text
        self.lbl_version = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"Version {VERSION}",
            font=ctk.CTkFont(family="Inter", size=10),
            text_color=("#888888", "#666666")
        )
        self.lbl_version.grid(row=6, column=0, padx=20, pady=20, sticky="sw")

        # 2. Main Content Container
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Initialize dashboard pages
        self.pages = {
            "typer": TyperPage(self.content_container, self.services),
            "clicker": ClickerPage(self.content_container, self.services),
            "macro": MacroPage(self.content_container, self.services),
            "settings": SettingsPage(self.content_container, self.services)
        }

        # 3. Modern Footer Status Bar
        self.status_bar = ctk.CTkFrame(
            self,
            height=26,
            corner_radius=0,
            border_width=1,
            border_color=("#E0E0E0", "#1E1E24"),
            fg_color=("#EAEAEA", "#0C0C0E")
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)

        self.lbl_status = ctk.CTkLabel(
            self.status_bar,
            text="", # dynamic
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            text_color=("#555555", "#888888")
        )
        self.lbl_status.grid(row=0, column=0, padx=15, pady=2, sticky="w")

        self.lbl_status_backup = ctk.CTkLabel(
            self.status_bar,
            text="", # dynamic
            font=ctk.CTkFont(family="Inter", size=10),
            text_color=("#777777", "#777777")
        )
        self.lbl_status_backup.grid(row=0, column=1, padx=15, pady=2, sticky="e")

        # Register language change listener
        self.lang.add_listener(self._on_language_changed)

        # Draw localized texts
        self._on_language_changed()

        # Select initial page
        self.active_page_id = None
        self.select_page("typer")

    def _center_window(self):
        self.update_idletasks()
        width = 1020
        height = 680
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def select_page(self, page_id: str):
        if page_id == self.active_page_id:
            return
            
        if self.active_page_id:
            old_page = self.pages[self.active_page_id]
            old_page.grid_forget()
            old_page.on_hide()
            
            # Reset button style
            self.nav_buttons[self.active_page_id].configure(
                fg_color="transparent",
                text_color=("#333333", "#CCCCCC")
            )

        new_page = self.pages[page_id]
        new_page.grid(row=0, column=0, sticky="nsew")
        new_page.on_show()
        
        # Highlight button style
        self.nav_buttons[page_id].configure(
            fg_color=("#D0D0D0", "#1F6AA5"),
            text_color=("#111111", "#FFFFFF")
        )

        self.active_page_id = page_id
        self._update_status_bar()

    def _update_status_bar(self):
        """Redraws localized details in the footer bar."""
        # Ready status
        status_text = self.lang.get("status_ready")
        self.lbl_status.configure(text=f"●  {status_text}")
        
        # Backup status
        backup_time = self.backup.get_last_backup_time_str() if self.backup else "N/A"
        backup_lbl = self.lang.get("last_backup")
        self.lbl_status_backup.configure(text=f"{backup_lbl}: {backup_time}  |  Language: {self.lang.current_lang.upper()}")

    def _on_language_changed(self):
        """Dispatches language translation triggers to UI buttons, footer, and sub-pages."""
        # Redraw sidebar buttons
        for page_id, translation_key in self.nav_items:
            translated_text = self.lang.get(translation_key)
            self.nav_buttons[page_id].configure(text=translated_text)

        # Trigger redraw inside all instantiated sub pages
        for page in self.pages.values():
            try:
                page.refresh_language()
            except Exception as e:
                logger.error(f"Failed to refresh language for subpage: {e}")

        # Redraw Status Bar
        self._update_status_bar()
