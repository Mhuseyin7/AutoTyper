import customtkinter as ctk
import tkinter as tk
from .base_page import BasePage
from ..widgets.hotkey_entry import HotkeyEntry
from ..services.log_service import get_recent_logs

class SettingsPage(BasePage):
    """Configuration page containing global settings, hotkey rebinds, theme colors, font editors, and backup modules."""
    def __init__(self, master, services: dict, **kwargs):
        super().__init__(master, services, **kwargs)
        self.backup_service = services.get("backup_service")
        self.update_service = services.get("update_service")
        
        self.create_header(
            title_key="settings_header_title",
            subtitle_key="settings_header_subtitle"
        )

        # Page grid layout
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, padx=25, pady=15, sticky="nsew")
        self.body_frame.grid_columnconfigure(0, weight=1) # Left Config
        self.body_frame.grid_columnconfigure(1, weight=1) # Right Logs/Console
        self.body_frame.grid_rowconfigure(0, weight=1)

        # Left Column: Configuration Controls
        self.left_col = ctk.CTkScrollableFrame(self.body_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.left_col.grid_columnconfigure(0, weight=1)

        # 1. Language Card
        self.lang_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.lang_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.lang_card.grid_columnconfigure(0, weight=1)
        self.lang_card.grid_columnconfigure(1, weight=1)

        self.lbl_lang_title = ctk.CTkLabel(
            self.lang_card, text=self.lang.get("lang_system"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_lang_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 8))

        self.btn_lang_en = ctk.CTkButton(
            self.lang_card, text="English (EN)", height=32, command=lambda: self._switch_lang("en")
        )
        self.btn_lang_en.grid(row=1, column=0, padx=(15, 5), pady=(0, 15), sticky="ew")

        self.btn_lang_tr = ctk.CTkButton(
            self.lang_card, text="Türkçe (TR)", height=32, command=lambda: self._switch_lang("tr")
        )
        self.btn_lang_tr.grid(row=1, column=1, padx=(5, 15), pady=(0, 15), sticky="ew")


        # 2. Appearance & Colors Card
        self.appearance_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.appearance_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.appearance_card.grid_columnconfigure(0, weight=1)

        self.lbl_appearance = ctk.CTkLabel(
            self.appearance_card, text=self.lang.get("appearance"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_appearance.pack(anchor="w", padx=15, pady=(15, 2))

        self.opt_theme = ctk.CTkOptionMenu(
            self.appearance_card,
            values=[self.lang.get("theme_dark"), self.lang.get("theme_light"), self.lang.get("theme_system")],
            command=self._on_theme_changed
        )
        self.opt_theme.pack(fill="x", padx=15, pady=(0, 12))

        # Accent Color Chooser presets
        self.lbl_accent = ctk.CTkLabel(
            self.appearance_card, text=self.lang.get("color_primary"), font=ctk.CTkFont(family="Inter", size=11, weight="bold")
        )
        self.lbl_accent.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.colors_frame = ctk.CTkFrame(self.appearance_card, fg_color="transparent")
        self.colors_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        accent_presets = [
            ("#1F6AA5", "Blue"),
            ("#2ECC71", "Green"),
            ("#E74C3C", "Red"),
            ("#E67E22", "Orange"),
            ("#9B59B6", "Purple")
        ]
        
        for idx, (color, name) in enumerate(accent_presets):
            btn_col = ctk.CTkButton(
                self.colors_frame, text="", fg_color=color, hover_color=color, width=28, height=28,
                corner_radius=14, border_width=1, border_color="#FFFFFF",
                command=lambda c=color: self._set_accent_color(c)
            )
            btn_col.pack(side="left", padx=5)

        self.chk_autosave = ctk.CTkCheckBox(
            self.appearance_card, text=self.lang.get("autosave"), command=self._on_autosave_changed
        )
        self.chk_autosave.pack(anchor="w", padx=15, pady=(0, 15))


        # 3. Font Configurator Card
        self.font_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.font_card.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.font_card.grid_columnconfigure(0, weight=1)
        self.font_card.grid_columnconfigure(1, weight=1)

        self.lbl_font_title = ctk.CTkLabel(
            self.font_card, text=self.lang.get("font_editor"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_font_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 8))

        # Font Family
        self.lbl_ff = ctk.CTkLabel(self.font_card, text=self.lang.get("font_family"), font=ctk.CTkFont(size=11))
        self.lbl_ff.grid(row=1, column=0, padx=(15, 5), pady=(0, 2), sticky="w")
        self.opt_font_family = ctk.CTkOptionMenu(
            self.font_card,
            values=["Consolas", "Segoe UI", "Arial", "Courier New", "Lucida Console"],
            command=self._on_font_changed
        )
        self.opt_font_family.grid(row=2, column=0, padx=(15, 5), pady=(0, 15), sticky="ew")

        # Font Size
        self.lbl_fs = ctk.CTkLabel(self.font_card, text=self.lang.get("font_size"), font=ctk.CTkFont(size=11))
        self.lbl_fs.grid(row=1, column=1, padx=(5, 15), pady=(0, 2), sticky="w")
        self.opt_font_size = ctk.CTkOptionMenu(
            self.font_card,
            values=["10", "11", "12", "13", "14", "16", "18"],
            command=self._on_font_changed
        )
        self.opt_font_size.grid(row=2, column=1, padx=(5, 15), pady=(0, 15), sticky="ew")


        # 4. Hotkeys Rebindings Card
        self.hotkeys_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.hotkeys_card.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        self.hotkeys_card.grid_columnconfigure(0, weight=1)
        self.hotkeys_card.grid_columnconfigure(1, weight=1)

        self.lbl_hotkeys_title = ctk.CTkLabel(
            self.hotkeys_card, text=self.lang.get("shortcuts"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_hotkeys_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        rebind_actions = [
            ("auto_typer_start_stop", "sc_typer"),
            ("auto_clicker_start_stop", "sc_clicker"),
            ("macro_record_start_stop", "sc_record"),
            ("macro_play_start_stop", "sc_play")
        ]
        
        self.hotkey_widgets = {}
        self.hotkey_labels = []
        
        for idx, (action, trans_key) in enumerate(rebind_actions):
            lbl = ctk.CTkLabel(self.hotkeys_card, text="", font=ctk.CTkFont(family="Inter", size=11))
            lbl.grid(row=idx+1, column=0, padx=(15, 5), pady=8, sticky="w")
            # Cache keys to translate dynamically
            self.hotkey_labels.append((lbl, trans_key))
            
            entry = HotkeyEntry(
                self.hotkeys_card,
                on_hotkey_recorded=lambda val, act=action: self._on_hotkey_rebound(act, val)
            )
            entry.grid(row=idx+1, column=1, padx=(5, 15), pady=8, sticky="ew")
            self.hotkey_widgets[action] = entry


        # 5. Backup & Updates Card
        self.extra_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.extra_card.grid(row=4, column=0, sticky="ew")
        self.extra_card.grid_columnconfigure(0, weight=1)
        self.extra_card.grid_columnconfigure(1, weight=1)

        self.lbl_backup_title = ctk.CTkLabel(
            self.extra_card, text=self.lang.get("backup_system"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_backup_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 8))

        self.btn_backup = ctk.CTkButton(
            self.extra_card, text=self.lang.get("trigger_backup"), fg_color="#2ECC71", hover_color="#27AE60", height=32, command=self._trigger_backup
        )
        self.btn_backup.grid(row=1, column=0, padx=(15, 5), pady=(0, 12), sticky="ew")

        self.btn_restore = ctk.CTkButton(
            self.extra_card, text=self.lang.get("restore_latest"), fg_color="#F39C12", hover_color="#D35400", height=32, command=self._trigger_restore
        )
        self.btn_restore.grid(row=1, column=1, padx=(5, 15), pady=(0, 12), sticky="ew")

        # Auto Update Button
        self.btn_check_update = ctk.CTkButton(
            self.extra_card,
            text=self.lang.get("check_update_btn"),
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color=("#3498DB", "#2980B9"),
            hover_color=("#2980B9", "#2471A3"),
            height=32,
            command=self._check_for_updates
        )
        self.btn_check_update.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")


        # Right Column: Console Log
        self.right_col = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        self.right_col.grid_columnconfigure(0, weight=1)
        self.right_col.grid_rowconfigure(0, weight=1)

        self.logs_card = ctk.CTkFrame(
            self.right_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#FFFFFF", "#141414")
        )
        self.logs_card.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        self.logs_card.grid_columnconfigure(0, weight=1)
        self.logs_card.grid_rowconfigure(1, weight=1)

        # Header Console
        self.logs_header = ctk.CTkFrame(self.logs_card, fg_color="transparent")
        self.logs_header.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")
        self.logs_header.grid_columnconfigure(0, weight=1)
        
        self.lbl_console = ctk.CTkLabel(
            self.logs_header, text=self.lang.get("diagnostics"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_console.grid(row=0, column=0, sticky="w")
        
        self.btn_refresh_logs = ctk.CTkButton(
            self.logs_header, text=self.lang.get("refresh"), width=70, height=24, font=ctk.CTkFont(size=10, weight="bold"), command=self._refresh_logs
        )
        self.btn_refresh_logs.grid(row=0, column=1, sticky="e")

        self.txt_logs = ctk.CTkTextbox(
            self.logs_card,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color="transparent",
            text_color=("#222222", "#AAAAAA"),
            wrap="word"
        )
        self.txt_logs.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.txt_logs.configure(state="disabled")

        self.config_service.add_listener(self._on_external_config_changed)

    def on_show(self):
        self._load_from_config()
        self._refresh_logs()

    def refresh_language(self):
        self.update_header_text()
        self.lbl_lang_title.configure(text=self.lang.get("lang_system"))
        self.lbl_appearance.configure(text=self.lang.get("appearance"))
        self.chk_autosave.configure(text=self.lang.get("autosave"))
        self.lbl_font_title.configure(text=self.lang.get("font_editor"))
        self.lbl_ff.configure(text=self.lang.get("font_family"))
        self.lbl_fs.configure(text=self.lang.get("font_size"))
        self.lbl_hotkeys_title.configure(text=self.lang.get("shortcuts"))
        self.lbl_backup_title.configure(text=self.lang.get("backup_system"))
        self.btn_backup.configure(text=self.lang.get("trigger_backup"))
        self.btn_restore.configure(text=self.lang.get("restore_latest"))
        self.btn_check_update.configure(text=self.lang.get("check_update_btn"))
        self.lbl_console.configure(text=self.lang.get("diagnostics"))
        self.btn_refresh_logs.configure(text=self.lang.get("refresh"))
        
        # OptionMenu values redraw
        theme_val = self.config_service.get("theme")
        theme_map = {"dark": "theme_dark", "light": "theme_light", "system": "theme_system"}
        self.opt_theme.configure(values=[self.lang.get("theme_dark"), self.lang.get("theme_light"), self.lang.get("theme_system")])
        self.opt_theme.set(self.lang.get(theme_map.get(theme_val, "theme_dark")))
        
        # Shortcuts labels update
        for label_widget, key in self.hotkey_labels:
            label_widget.configure(text=self.lang.get(key))

        self._on_external_config_changed(self.config_service.settings)

    def _load_from_config(self):
        theme_val = self.config_service.get("theme")
        theme_map = {"dark": "theme_dark", "light": "theme_light", "system": "theme_system"}
        self.opt_theme.set(self.lang.get(theme_map.get(theme_val, "theme_dark")))

        self.chk_autosave.select() if self.config_service.get("auto_save") else self.chk_autosave.deselect()

        # Font configuration values
        family = self.config_service.get("font_config", "family")
        size = str(self.config_service.get("font_config", "size"))
        self.opt_font_family.set(family)
        self.opt_font_size.set(size)

        for action, entry_widget in self.hotkey_widgets.items():
            hotkey_str = self.config_service.get("hotkeys", action)
            entry_widget.set_hotkey(hotkey_str)

    def _switch_lang(self, lang_code: str):
        self.lang.set_language(lang_code)
        self.notification_service.show_toast(self.lang.get("toast_lang_changed"), level="success")

    def _on_theme_changed(self, theme_text: str):
        theme_map = {self.lang.get("theme_dark"): "dark", self.lang.get("theme_light"): "light", self.lang.get("theme_system"): "system"}
        theme = theme_map.get(theme_text, "dark")
        self.config_service.set("theme", theme)
        ctk.set_appearance_mode(theme)
        self.notification_service.show_toast("Appearance theme reloaded.", level="success")

    def _set_accent_color(self, hex_color: str):
        self.config_service.set(["theme_colors", "primary"], hex_color)
        # Apply accent highlight dynamically if needed, or notify user to restart
        # Standard CTk widgets use Theme settings, but custom accents can update borders
        self.notification_service.show_toast("Primary Accent Color updated successfully.", level="success")

    def _on_font_changed(self, font_param: str):
        """Saves family/size variables and reloads font configurations."""
        family = self.opt_font_family.get()
        try:
            size = int(self.opt_font_size.get())
        except ValueError:
            size = 12
            
        self.config_service.set(["font_config", "family"], family, save_immediately=False)
        self.config_service.set(["font_config", "size"], size, save_immediately=True)
        
        # Apply font update dynamically to logs display console
        self.txt_logs.configure(font=ctk.CTkFont(family=family, size=size-2 if size > 10 else 9))
        self.notification_service.show_toast("Font configurations updated.", level="success")

    def _on_autosave_changed(self):
        val = bool(self.chk_autosave.get())
        self.config_service.set("auto_save", val)

    def _on_hotkey_rebound(self, action_name: str, value: str):
        if not value:
            return
        self.config_service.set(["hotkeys", action_name], value)
        self.notification_service.show_toast(f"Bound shortcut: {value}", level="success")

    def _trigger_backup(self):
        if self.backup_service.create_backup():
            self.notification_service.show_toast(self.lang.get("toast_backup_success"), level="success")
            # Trigger main window status refresh
            try:
                self.master.winfo_toplevel()._update_status_bar()
            except Exception:
                pass
        else:
            self.notification_service.show_error("Backup Failed", "Failed to write backup ZIP archive.")

    def _trigger_restore(self):
        if self.backup_service.restore_latest_backup():
            self.notification_service.show_toast(self.lang.get("toast_backup_restored"), level="success")
            # Auto reload settings from the restored file
            self.config_service.load_settings()
            self._load_from_config()
        else:
            self.notification_service.show_error("Restore Failed", "No backup zip found in storage folder.")

    def _check_for_updates(self):
        self.notification_service.show_toast("Checking for updates...", level="info")
        from ..config.constants import VERSION
        
        def complete(has_update, latest_ver):
            if not has_update:
                self.master.after(0, lambda: self.notification_service.show_info("Auto Update Checker", self.lang.get("toast_no_update")))
                
        self.update_service.check_for_updates(VERSION, complete)

    def _refresh_logs(self):
        logs = get_recent_logs(80)
        self.txt_logs.configure(state="normal")
        self.txt_logs.delete("1.0", tk.END)
        self.txt_logs.insert("1.0", logs)
        self.txt_logs.configure(state="disabled")
        self.txt_logs.see(tk.END)

    def _on_external_config_changed(self, settings: dict):
        for action, entry_widget in self.hotkey_widgets.items():
            hotkey_str = settings.get("hotkeys", {}).get(action, "")
            if entry_widget.get_hotkey() != hotkey_str:
                entry_widget.set_hotkey(hotkey_str)
