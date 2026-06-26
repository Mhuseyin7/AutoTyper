import customtkinter as ctk
import tkinter as tk
from .base_page import BasePage
from ..widgets.status_card import StatusCard
from ..utils.win32_helper import get_cursor_position

class ClickerPage(BasePage):
    """Dashboard page to configure, pick coordinates, and control the Auto Clicker engine."""
    def __init__(self, master, services: dict, **kwargs):
        super().__init__(master, services, **kwargs)
        self.runner = services.get("clicker_runner")
        
        self.create_header(
            title_key="clicker_header_title",
            subtitle_key="clicker_header_subtitle"
        )

        # Page grid config
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, padx=25, pady=15, sticky="nsew")
        self.body_frame.grid_columnconfigure(0, weight=1) # Panel Left
        self.body_frame.grid_columnconfigure(1, weight=1) # Panel Right
        self.body_frame.grid_rowconfigure(0, weight=1)

        # Left Column: Coordinates & Click Types
        self.left_col = ctk.CTkScrollableFrame(self.body_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.left_col.grid_columnconfigure(0, weight=1)

        # Status Card
        hotkey_str = self.config_service.get("hotkeys", "auto_clicker_start_stop")
        self.status_card = StatusCard(self.left_col, title=self.lang.get("engine_clicker"), hotkey=hotkey_str)
        self.status_card.grid(row=0, column=0, pady=(0, 15), sticky="ew")

        # Click Config Card
        self.config_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.config_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.config_card.grid_columnconfigure(0, weight=1)

        # Button selector
        self.lbl_btn = ctk.CTkLabel(
            self.config_card, text=self.lang.get("mouse_button"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_btn.pack(anchor="w", padx=15, pady=(15, 2))
        self.opt_button = ctk.CTkOptionMenu(
            self.config_card,
            values=[self.lang.get("btn_left"), self.lang.get("btn_right"), self.lang.get("btn_middle")],
            command=self._on_button_selected
        )
        self.opt_button.pack(fill="x", padx=15, pady=(0, 10))

        # Click type select
        self.lbl_click_type = ctk.CTkLabel(
            self.config_card, text=self.lang.get("click_type"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_click_type.pack(anchor="w", padx=15, pady=(5, 2))
        self.opt_click_type = ctk.CTkOptionMenu(
            self.config_card,
            values=[self.lang.get("type_single"), self.lang.get("type_double"), self.lang.get("type_triple")],
            command=self._on_click_type_selected
        )
        self.opt_click_type.pack(fill="x", padx=15, pady=(0, 15))

        # Coordinate selection card
        self.coord_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.coord_card.grid(row=2, column=0, sticky="ew")
        self.coord_card.grid_columnconfigure(0, weight=1)

        self.lbl_pos_mode = ctk.CTkLabel(
            self.coord_card, text=self.lang.get("cursor_pos_mode"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_pos_mode.pack(anchor="w", padx=15, pady=(15, 2))
        self.opt_pos_mode = ctk.CTkOptionMenu(
            self.coord_card,
            values=[self.lang.get("pos_follow"), self.lang.get("pos_fixed")],
            command=self._on_pos_mode_selected
        )
        self.opt_pos_mode.pack(fill="x", padx=15, pady=(0, 12))

        # Coordinates entry fields
        self.coords_entry_frame = ctk.CTkFrame(self.coord_card, fg_color="transparent")
        self.coords_entry_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.coords_entry_frame.grid_columnconfigure(0, weight=1)
        self.coords_entry_frame.grid_columnconfigure(1, weight=1)

        self.entry_x = ctk.CTkEntry(self.coords_entry_frame, placeholder_text="X")
        self.entry_x.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.entry_x.bind("<KeyRelease>", self._on_coords_changed)

        self.entry_y = ctk.CTkEntry(self.coords_entry_frame, placeholder_text="Y")
        self.entry_y.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        self.entry_y.bind("<KeyRelease>", self._on_coords_changed)

        # Coordinate Picker Button
        self.btn_picker = ctk.CTkButton(
            self.coord_card,
            text=self.lang.get("pick_coords"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color=("#3498DB", "#2980B9"),
            hover_color=("#2980B9", "#2471A3"),
            command=self._start_coord_picker
        )
        self.btn_picker.pack(fill="x", padx=15, pady=(0, 15))


        # Right Column: Intervals & Loops & Actions
        self.right_col = ctk.CTkScrollableFrame(self.body_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        self.right_col.grid_columnconfigure(0, weight=1)

        # Interval Card
        self.interval_card = ctk.CTkFrame(
            self.right_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.interval_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.interval_card.grid_columnconfigure(0, weight=1)
        self.interval_card.grid_columnconfigure(1, weight=1)

        self.lbl_int = ctk.CTkLabel(
            self.interval_card, text=self.lang.get("click_interval"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_int.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 2))

        # Hour entry
        self.entry_h = ctk.CTkEntry(self.interval_card, placeholder_text="Hours")
        self.entry_h.grid(row=1, column=0, padx=(15, 5), pady=(0, 10), sticky="ew")
        self.entry_h.bind("<KeyRelease>", self._on_interval_changed)
        self.lbl_h = ctk.CTkLabel(self.interval_card, text=self.lang.get("hours"), font=ctk.CTkFont(size=10))
        self.lbl_h.grid(row=1, column=1, padx=(5, 15), pady=(0, 10), sticky="w")

        # Minute entry
        self.entry_m = ctk.CTkEntry(self.interval_card, placeholder_text="Mins")
        self.entry_m.grid(row=2, column=0, padx=(15, 5), pady=(0, 10), sticky="ew")
        self.entry_m.bind("<KeyRelease>", self._on_interval_changed)
        self.lbl_m = ctk.CTkLabel(self.interval_card, text=self.lang.get("minutes"), font=ctk.CTkFont(size=10))
        self.lbl_m.grid(row=2, column=1, padx=(5, 15), pady=(0, 10), sticky="w")

        # Second entry
        self.entry_s = ctk.CTkEntry(self.interval_card, placeholder_text="Secs")
        self.entry_s.grid(row=3, column=0, padx=(15, 5), pady=(0, 10), sticky="ew")
        self.entry_s.bind("<KeyRelease>", self._on_interval_changed)
        self.lbl_s = ctk.CTkLabel(self.interval_card, text=self.lang.get("seconds"), font=ctk.CTkFont(size=10))
        self.lbl_s.grid(row=3, column=1, padx=(5, 15), pady=(0, 10), sticky="w")

        # Millisecond entry
        self.entry_ms = ctk.CTkEntry(self.interval_card, placeholder_text="Ms")
        self.entry_ms.grid(row=4, column=0, padx=(15, 5), pady=(0, 15), sticky="ew")
        self.entry_ms.bind("<KeyRelease>", self._on_interval_changed)
        self.lbl_ms = ctk.CTkLabel(self.interval_card, text=self.lang.get("milliseconds"), font=ctk.CTkFont(size=10))
        self.lbl_ms.grid(row=4, column=1, padx=(5, 15), pady=(0, 15), sticky="w")

        # Loops Card
        self.loop_card = ctk.CTkFrame(
            self.right_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.loop_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.loop_card.grid_columnconfigure(0, weight=1)

        self.lbl_loop = ctk.CTkLabel(
            self.loop_card, text=self.lang.get("iteration_count"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_loop.pack(anchor="w", padx=15, pady=(15, 2))
        self.entry_loop = ctk.CTkEntry(self.loop_card, placeholder_text="0")
        self.entry_loop.pack(fill="x", padx=15, pady=(0, 15))
        self.entry_loop.bind("<KeyRelease>", self._on_loop_changed)

        # Action Buttons (Start, Pause/Resume, Stop)
        self.btn_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, sticky="ew")
        for col_idx in range(3):
            self.btn_frame.grid_columnconfigure(col_idx, weight=1)

        self.btn_start = ctk.CTkButton(
            self.btn_frame,
            text=self.lang.get("start_clicking"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#2ECC71",
            hover_color="#27AE60",
            text_color="#FFFFFF",
            height=38,
            command=self.start_runner
        )
        self.btn_start.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_pause = ctk.CTkButton(
            self.btn_frame,
            text=self.lang.get("pause"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#F39C12",
            hover_color="#D35400",
            text_color="#FFFFFF",
            height=38,
            command=self.toggle_pause
        )
        self.btn_pause.grid(row=0, column=1, padx=4, sticky="ew")

        self.btn_stop = ctk.CTkButton(
            self.btn_frame,
            text=self.lang.get("stop"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            text_color="#FFFFFF",
            height=38,
            command=self.stop_runner
        )
        self.btn_stop.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        self.config_service.add_listener(self._on_external_config_changed)

    def on_show(self):
        self._load_from_config()
        self._update_runner_status()

    def on_hide(self):
        self._save_to_config()

    def refresh_language(self):
        self.update_header_text()
        self.lbl_btn.configure(text=self.lang.get("mouse_button"))
        self.lbl_click_type.configure(text=self.lang.get("click_type"))
        self.lbl_pos_mode.configure(text=self.lang.get("cursor_pos_mode"))
        self.btn_picker.configure(text=self.lang.get("pick_coords"))
        self.lbl_int.configure(text=self.lang.get("click_interval"))
        self.lbl_h.configure(text=self.lang.get("hours"))
        self.lbl_m.configure(text=self.lang.get("minutes"))
        self.lbl_s.configure(text=self.lang.get("seconds"))
        self.lbl_ms.configure(text=self.lang.get("milliseconds"))
        self.lbl_loop.configure(text=self.lang.get("iteration_count"))
        self.btn_start.configure(text=self.lang.get("start_clicking"))
        self.btn_stop.configure(text=self.lang.get("stop"))
        
        # Option Menu values redraw
        # Button
        button_val = self.config_service.get("auto_clicker", "button")
        button_map = {"left": "btn_left", "right": "btn_right", "middle": "btn_middle"}
        self.opt_button.configure(values=[self.lang.get("btn_left"), self.lang.get("btn_right"), self.lang.get("btn_middle")])
        self.opt_button.set(self.lang.get(button_map.get(button_val, "btn_left")))
        
        # Type
        type_val = self.config_service.get("auto_clicker", "click_type")
        type_map = {"single": "type_single", "double": "type_double", "triple": "type_triple"}
        self.opt_click_type.configure(values=[self.lang.get("type_single"), self.lang.get("type_double"), self.lang.get("type_triple")])
        self.opt_click_type.set(self.lang.get(type_map.get(type_val, "type_single")))

        # Pos
        pos_val = self.config_service.get("auto_clicker", "position_mode")
        self.opt_pos_mode.configure(values=[self.lang.get("pos_follow"), self.lang.get("pos_fixed")])
        self.opt_pos_mode.set(self.lang.get("pos_follow") if pos_val == "cursor" else self.lang.get("pos_fixed"))
        
        self._update_pause_btn_text()
        self._on_external_config_changed(self.config_service.settings)

    def _load_from_config(self):
        button_val = self.config_service.get("auto_clicker", "button")
        button_map = {"left": "btn_left", "right": "btn_right", "middle": "btn_middle"}
        self.opt_button.set(self.lang.get(button_map.get(button_val, "btn_left")))

        type_val = self.config_service.get("auto_clicker", "click_type")
        type_map = {"single": "type_single", "double": "type_double", "triple": "type_triple"}
        self.opt_click_type.set(self.lang.get(type_map.get(type_val, "type_single")))

        pos_val = self.config_service.get("auto_clicker", "position_mode")
        self.opt_pos_mode.set(self.lang.get("pos_follow") if pos_val == "cursor" else self.lang.get("pos_fixed"))
        self._toggle_coords_entry(pos_val)

        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, str(self.config_service.get("auto_clicker", "fixed_x")))
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(self.config_service.get("auto_clicker", "fixed_y")))

        total_ms = self.config_service.get("auto_clicker", "interval_ms")
        h = total_ms // 3600000
        total_ms %= 3600000
        m = total_ms // 60000
        total_ms %= 60000
        s = total_ms // 1000
        ms = total_ms % 1000

        self.entry_h.delete(0, tk.END)
        self.entry_h.insert(0, str(h) if h > 0 else "")
        self.entry_m.delete(0, tk.END)
        self.entry_m.insert(0, str(m) if m > 0 else "")
        self.entry_s.delete(0, tk.END)
        self.entry_s.insert(0, str(s) if s > 0 else "")
        self.entry_ms.delete(0, tk.END)
        self.entry_ms.insert(0, str(ms) if ms > 0 else "")

        self.entry_loop.delete(0, tk.END)
        self.entry_loop.insert(0, str(self.config_service.get("auto_clicker", "loop")))

    def _save_to_config(self):
        try:
            x = int(self.entry_x.get().strip() or "0")
            y = int(self.entry_y.get().strip() or "0")
            self.config_service.set(["auto_clicker", "fixed_x"], x, save_immediately=False)
            self.config_service.set(["auto_clicker", "fixed_y"], y, save_immediately=False)
        except ValueError:
            pass

        try:
            h = int(self.entry_h.get().strip() or "0")
            m = int(self.entry_m.get().strip() or "0")
            s = int(self.entry_s.get().strip() or "0")
            ms = int(self.entry_ms.get().strip() or "0")
            total_ms = (h * 3600000) + (m * 60000) + (s * 1000) + ms
            self.config_service.set(["auto_clicker", "interval_ms"], max(1, total_ms), save_immediately=False)
        except ValueError:
            pass

        try:
            loops = int(self.entry_loop.get().strip() or "0")
            self.config_service.set(["auto_clicker", "loop"], loops, save_immediately=False)
        except ValueError:
            pass

        self.config_service.save_settings()

    def _on_button_selected(self, btn_text: str):
        btn_map = {self.lang.get("btn_left"): "left", self.lang.get("btn_right"): "right", self.lang.get("btn_middle"): "middle"}
        self.config_service.set(["auto_clicker", "button"], btn_map.get(btn_text, "left"))

    def _on_click_type_selected(self, type_text: str):
        type_map = {self.lang.get("type_single"): "single", self.lang.get("type_double"): "double", self.lang.get("type_triple"): "triple"}
        self.config_service.set(["auto_clicker", "click_type"], type_map.get(type_text, "single"))

    def _on_pos_mode_selected(self, mode_text: str):
        mode = "cursor" if mode_text == self.lang.get("pos_follow") else "fixed"
        self.config_service.set(["auto_clicker", "position_mode"], mode)
        self._toggle_coords_entry(mode)

    def _toggle_coords_entry(self, mode: str):
        if mode == "cursor":
            self.entry_x.configure(state="disabled")
            self.entry_y.configure(state="disabled")
            self.btn_picker.configure(state="disabled")
        else:
            self.entry_x.configure(state="normal")
            self.entry_y.configure(state="normal")
            self.btn_picker.configure(state="normal")

    def _on_coords_changed(self, event):
        try:
            x = int(self.entry_x.get().strip() or "0")
            self.config_service.set(["auto_clicker", "fixed_x"], x, save_immediately=False)
        except ValueError:
            pass
        try:
            y = int(self.entry_y.get().strip() or "0")
            self.config_service.set(["auto_clicker", "fixed_y"], y, save_immediately=False)
        except ValueError:
            pass

    def _on_interval_changed(self, event):
        try:
            h = int(self.entry_h.get().strip() or "0")
            m = int(self.entry_m.get().strip() or "0")
            s = int(self.entry_s.get().strip() or "0")
            ms = int(self.entry_ms.get().strip() or "0")
            total_ms = (h * 3600000) + (m * 60000) + (s * 1000) + ms
            self.config_service.set(["auto_clicker", "interval_ms"], max(1, total_ms), save_immediately=False)
        except ValueError:
            pass

    def _on_loop_changed(self, event):
        try:
            loops = int(self.entry_loop.get().strip() or "0")
            self.config_service.set(["auto_clicker", "loop"], loops, save_immediately=False)
        except ValueError:
            pass

    def _start_coord_picker(self):
        top_window = self.master.winfo_toplevel()
        top_window.withdraw()

        picker = tk.Toplevel()
        picker.attributes("-fullscreen", True)
        picker.attributes("-alpha", 0.4)
        picker.attributes("-topmost", True)
        picker.config(cursor="crosshair", bg="#1E1E24")

        hud_frame = tk.Frame(picker, bg="#111115", bd=2, relief="solid")
        hud_frame.pack(pady=150)
        
        instructions = tk.Label(
            hud_frame,
            text=f"COORDINATE PICKER MODE\n\n1. Click anywhere on your screen to lock location.\n2. Press [ESC] key to cancel and return.",
            font=("Consolas", 14, "bold"),
            fg="#2ECC71",
            bg="#111115",
            padx=30,
            pady=20
        )
        instructions.pack()

        def on_click(event):
            x, y = get_cursor_position()
            self.entry_x.configure(state="normal")
            self.entry_y.configure(state="normal")
            self.entry_x.delete(0, tk.END)
            self.entry_x.insert(0, str(x))
            self.entry_y.delete(0, tk.END)
            self.entry_y.insert(0, str(y))

            self.config_service.set(["auto_clicker", "fixed_x"], x, save_immediately=False)
            self.config_service.set(["auto_clicker", "fixed_y"], y, save_immediately=True)

            picker.destroy()
            top_window.deiconify()
            self.notification_service.show_toast(f"Captured coordinate: ({x}, {y})", level="success")

        def on_cancel(event):
            picker.destroy()
            top_window.deiconify()

        picker.bind("<Button-1>", on_click)
        picker.bind("<Escape>", on_cancel)

    def start_runner(self):
        if self.runner.is_running():
            return
        self._save_to_config()
        success = self.runner.start()
        if success:
            self._update_runner_status()
            self.notification_service.show_toast("Auto Clicker started.", level="success")

    def stop_runner(self):
        if not self.runner.is_running():
            return
        self.runner.stop()
        self._update_runner_status()
        self.notification_service.show_toast("Auto Clicker stopped.", level="warning")

    def toggle_pause(self):
        if not self.runner.is_running():
            return
            
        if self.runner.is_paused():
            self.runner.resume()
            self.notification_service.show_toast("Auto Clicker resumed.", level="success")
        else:
            self.runner.pause()
            self.notification_service.show_toast("Auto Clicker paused.", level="warning")
        self._update_runner_status()

    def _update_runner_status(self):
        if self.runner.is_running():
            if self.runner.is_paused():
                self.status_card.update_status("paused")
            else:
                self.status_card.update_status("running")
        else:
            self.status_card.update_status("idle")
        self._update_pause_btn_text()

    def _update_pause_btn_text(self):
        if self.runner.is_running() and self.runner.is_paused():
            self.btn_pause.configure(text=self.lang.get("resume"))
        else:
            self.btn_pause.configure(text=self.lang.get("pause"))

    def _on_external_config_changed(self, settings: dict):
        try:
            hotkey_str = settings.get("hotkeys", {}).get("auto_clicker_start_stop", "F6")
            self.status_card.update_hotkey(hotkey_str)
        except Exception:
            pass
