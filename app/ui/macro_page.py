import json
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from .base_page import BasePage
from ..widgets.status_card import StatusCard
from ..widgets.drag_list_widget import DragListWidget
from ..utils.win32_helper import get_cursor_position

class MacroPage(BasePage):
    """Timeline dashboard page to capture inputs, record coordinates, insert delay blocks, and visually reorder items."""
    def __init__(self, master, services: dict, **kwargs):
        super().__init__(master, services, **kwargs)
        self.macro_service = services.get("macro_service")
        self.hook_listener = services.get("hook_listener")
        self.playback_runner = services.get("playback_runner")
        
        self.current_events = []
        self.hook_listener.on_event_recorded = self._on_event_intercepted

        self.create_header(
            title_key="macro_header_title",
            subtitle_key="macro_header_subtitle"
        )

        # Page grid layout
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, padx=25, pady=15, sticky="nsew")
        self.body_frame.grid_columnconfigure(0, weight=4) # Config Panel
        self.body_frame.grid_columnconfigure(1, weight=5) # Timeline Panel
        self.body_frame.grid_rowconfigure(0, weight=1)

        # Left Column: Config Panel
        self.left_col = ctk.CTkScrollableFrame(self.body_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.left_col.grid_columnconfigure(0, weight=1)

        # Status Card
        hotkey_str = self.config_service.get("hotkeys", "macro_record_start_stop")
        self.status_card = StatusCard(self.left_col, title=self.lang.get("engine_macro"), hotkey=hotkey_str)
        self.status_card.grid(row=0, column=0, pady=(0, 15), sticky="ew")

        # Record settings card
        self.record_config = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.record_config.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.record_config.grid_columnconfigure(0, weight=1)

        self.lbl_rec_options = ctk.CTkLabel(
            self.record_config, text=self.lang.get("rec_filters"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_rec_options.pack(anchor="w", padx=15, pady=(15, 2))

        self.chk_mouse = ctk.CTkCheckBox(
            self.record_config, text=self.lang.get("rec_mouse"), command=self._on_filter_changed
        )
        self.chk_mouse.pack(anchor="w", padx=15, pady=5)

        self.chk_keyboard = ctk.CTkCheckBox(
            self.record_config, text=self.lang.get("rec_keyboard"), command=self._on_filter_changed
        )
        self.chk_keyboard.pack(anchor="w", padx=15, pady=(5, 15))

        # Profile Files Card
        self.profile_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.profile_card.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.profile_card.grid_columnconfigure(0, weight=1)

        self.lbl_profiles = ctk.CTkLabel(
            self.profile_card, text=self.lang.get("saved_macros"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_profiles.pack(anchor="w", padx=15, pady=(15, 2))

        self.opt_profiles = ctk.CTkOptionMenu(
            self.profile_card,
            values=[],
            command=self._on_profile_selected
        )
        self.opt_profiles.pack(fill="x", padx=15, pady=(0, 12))

        # Profile Action Buttons Grid
        self.profile_btn_frame = ctk.CTkFrame(self.profile_card, fg_color="transparent")
        self.profile_btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.profile_btn_frame.grid_columnconfigure(0, weight=1)
        self.profile_btn_frame.grid_columnconfigure(1, weight=1)

        self.btn_load_prof = ctk.CTkButton(
            self.profile_btn_frame, text=self.lang.get("load"), height=30, command=self._load_selected_profile
        )
        self.btn_load_prof.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_del_prof = ctk.CTkButton(
            self.profile_btn_frame, text=self.lang.get("delete"), fg_color="#E74C3C", hover_color="#C0392B", height=30, command=self._delete_selected_profile
        )
        self.btn_del_prof.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # Duplicate, Export, Import Action Row
        self.extra_btn_frame = ctk.CTkFrame(self.profile_card, fg_color="transparent")
        self.extra_btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        for col_idx in range(3):
            self.extra_btn_frame.grid_columnconfigure(col_idx, weight=1)

        self.btn_dup = ctk.CTkButton(
            self.extra_btn_frame, text=self.lang.get("duplicate"), font=ctk.CTkFont(size=10, weight="bold"), height=26, command=self._duplicate_profile
        )
        self.btn_dup.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        self.btn_exp = ctk.CTkButton(
            self.extra_btn_frame, text=self.lang.get("export"), font=ctk.CTkFont(size=10, weight="bold"), fg_color="#3498DB", hover_color="#2980B9", height=26, command=self._export_profile
        )
        self.btn_exp.grid(row=0, column=1, padx=2, sticky="ew")

        self.btn_imp = ctk.CTkButton(
            self.extra_btn_frame, text=self.lang.get("import"), font=ctk.CTkFont(size=10, weight="bold"), fg_color="#3498DB", hover_color="#2980B9", height=26, command=self._import_profile
        )
        self.btn_imp.grid(row=0, column=2, padx=(2, 0), sticky="ew")


        # Right Column: Macro Recording visual timeline reordering
        self.right_col = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        self.right_col.grid_columnconfigure(0, weight=1)
        self.right_col.grid_rowconfigure(0, weight=1) # Drag List
        self.right_col.grid_rowconfigure(1, weight=0) # Insert Designer Row
        self.right_col.grid_rowconfigure(2, weight=0) # Playback Speed/Loops Frame
        self.right_col.grid_rowconfigure(3, weight=0) # Master Run Actions

        # Reorderable Drag List Widget (with double-click edit callback)
        self.drag_list = DragListWidget(
            self.right_col,
            on_list_changed=self._on_timeline_reordered,
            on_edit_item=self._on_edit_timeline_item
        )
        self.drag_list.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # Context Menu
        self.drag_list.bind("<Button-3>", self._show_context_menu)

        # Macro designer insertion buttons
        self.insert_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.insert_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for col_idx in range(3):
            self.insert_frame.grid_columnconfigure(col_idx, weight=1)

        self.btn_add_key = ctk.CTkButton(
            self.insert_frame, text="+ KEY BLOCK", font=ctk.CTkFont(size=10, weight="bold"), height=28, command=self._add_key_block
        )
        self.btn_add_key.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_add_click = ctk.CTkButton(
            self.insert_frame, text="+ CLICK BLOCK", font=ctk.CTkFont(size=10, weight="bold"), height=28, command=self._add_click_block
        )
        self.btn_add_click.grid(row=0, column=1, padx=4, sticky="ew")

        self.btn_add_delay = ctk.CTkButton(
            self.insert_frame, text="+ DELAY BLOCK", font=ctk.CTkFont(size=10, weight="bold"), height=28, command=self._add_delay_block
        )
        self.btn_add_delay.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # Playback configuration panel
        self.playback_opts_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.playback_opts_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        for col_idx in range(3):
            self.playback_opts_frame.grid_columnconfigure(col_idx, weight=1)

        # Speed
        self.lbl_speed = ctk.CTkLabel(
            self.playback_opts_frame, text=self.lang.get("timeline_speed"), font=ctk.CTkFont(family="Inter", size=11, weight="bold")
        )
        self.lbl_speed.grid(row=0, column=0, padx=5, sticky="w")
        self.opt_speed = ctk.CTkOptionMenu(
            self.playback_opts_frame,
            values=["0.5x", "1.0x", "2.0x", "5.0x", "10.0x"],
            command=self._on_speed_selected
        )
        self.opt_speed.grid(row=1, column=0, padx=5, pady=(2, 0), sticky="ew")

        # Loop
        self.lbl_play_loop = ctk.CTkLabel(
            self.playback_opts_frame, text=self.lang.get("timeline_loops"), font=ctk.CTkFont(family="Inter", size=11, weight="bold")
        )
        self.lbl_play_loop.grid(row=0, column=1, padx=5, sticky="w")
        self.entry_play_loop = ctk.CTkEntry(self.playback_opts_frame, height=28)
        self.entry_play_loop.grid(row=1, column=1, padx=5, pady=(2, 0), sticky="ew")
        self.entry_play_loop.bind("<KeyRelease>", self._on_playback_loops_changed)

        # Loop Delay
        self.lbl_play_delay = ctk.CTkLabel(
            self.playback_opts_frame, text=self.lang.get("timeline_delay"), font=ctk.CTkFont(family="Inter", size=11, weight="bold")
        )
        self.lbl_play_delay.grid(row=0, column=2, padx=5, sticky="w")
        self.entry_play_delay = ctk.CTkEntry(self.playback_opts_frame, height=28)
        self.entry_play_delay.grid(row=1, column=2, padx=5, pady=(2, 0), sticky="ew")
        self.entry_play_delay.bind("<KeyRelease>", self._on_playback_loops_changed)


        # Macro control buttons (Start, Pause/Resume, Stop, Save)
        self.action_btn_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.action_btn_frame.grid(row=3, column=0, sticky="ew")
        for col_idx in range(4):
            self.action_btn_frame.grid_columnconfigure(col_idx, weight=1)

        self.btn_record = ctk.CTkButton(
            self.action_btn_frame,
            text=self.lang.get("record"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            height=38,
            command=self.toggle_recording
        )
        self.btn_record.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        self.btn_play = ctk.CTkButton(
            self.action_btn_frame,
            text=self.lang.get("play"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#2ECC71",
            hover_color="#27AE60",
            height=38,
            command=self.toggle_playback
        )
        self.btn_play.grid(row=0, column=1, padx=3, sticky="ew")

        self.btn_pause = ctk.CTkButton(
            self.action_btn_frame,
            text=self.lang.get("pause"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#F39C12",
            hover_color="#D35400",
            height=38,
            command=self.toggle_pause
        )
        self.btn_pause.grid(row=0, column=2, padx=3, sticky="ew")

        self.btn_save_macro = ctk.CTkButton(
            self.action_btn_frame,
            text=self.lang.get("save_current"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#3498DB",
            hover_color="#2980B9",
            height=38,
            command=self._prompt_save_macro
        )
        self.btn_save_macro.grid(row=0, column=3, padx=(3, 0), sticky="ew")

        self.config_service.add_listener(self._on_external_config_changed)

    def on_show(self):
        self._load_from_config()
        self._refresh_profile_list()
        self.drag_list.set_events(self.current_events)
        self._update_runner_status()

    def on_hide(self):
        self._save_to_config()

    def refresh_language(self):
        self.update_header_text()
        self.lbl_rec_options.configure(text=self.lang.get("rec_filters"))
        self.chk_mouse.configure(text=self.lang.get("rec_mouse"))
        self.chk_keyboard.configure(text=self.lang.get("rec_keyboard"))
        self.lbl_profiles.configure(text=self.lang.get("saved_macros"))
        self.btn_load_prof.configure(text=self.lang.get("load"))
        self.btn_del_prof.configure(text=self.lang.get("delete"))
        self.btn_dup.configure(text=self.lang.get("duplicate"))
        self.btn_exp.configure(text=self.lang.get("export"))
        self.btn_imp.configure(text=self.lang.get("import"))
        self.lbl_speed.configure(text=self.lang.get("timeline_speed"))
        self.lbl_play_loop.configure(text=self.lang.get("timeline_loops"))
        self.lbl_play_delay.configure(text=self.lang.get("timeline_delay"))
        self.btn_save_macro.configure(text=self.lang.get("save_current"))
        
        if self.hook_listener.is_recording:
            self.btn_record.configure(text=self.lang.get("stop_record"))
        else:
            self.btn_record.configure(text=self.lang.get("record"))
            
        if self.playback_runner.is_running():
            self.btn_play.configure(text=self.lang.get("stop"))
        else:
            self.btn_play.configure(text=self.lang.get("play"))
            
        self._update_pause_btn_text()
        self.drag_list.configure(label_text=self.lang.get("tab_macro"))
        self.drag_list.refresh_list()
        self._on_external_config_changed(self.config_service.settings)

    def _load_from_config(self):
        self.chk_mouse.select() if self.config_service.get("macro", "record_mouse") else self.chk_mouse.deselect()
        self.chk_keyboard.select() if self.config_service.get("macro", "record_keyboard") else self.chk_keyboard.deselect()

        speed_val = f'{self.config_service.get("macro", "speed"):.1f}x'
        self.opt_speed.set(speed_val if speed_val in self.opt_speed.cget("values") else "1.0x")

        self.entry_play_loop.delete(0, tk.END)
        self.entry_play_loop.insert(0, str(self.config_service.get("macro", "loop")))

        self.entry_play_delay.delete(0, tk.END)
        self.entry_play_delay.insert(0, f'{self.config_service.get("macro", "loop_delay"):.2f}')

    def _save_to_config(self):
        try:
            loops = int(self.entry_play_loop.get().strip() or "1")
            self.config_service.set(["macro", "loop"], loops, save_immediately=False)
        except ValueError:
            pass
        try:
            loop_del = float(self.entry_play_delay.get().strip() or "0.5")
            self.config_service.set(["macro", "loop_delay"], loop_del, save_immediately=False)
        except ValueError:
            pass
        self.config_service.save_settings()

    def _refresh_profile_list(self):
        profiles = self.macro_service.list_macros()
        self.opt_profiles.configure(values=profiles)
        
        if profiles:
            self.opt_profiles.set(profiles[0])
            self.btn_load_prof.configure(state="normal")
            self.btn_del_prof.configure(state="normal")
            self.btn_dup.configure(state="normal")
            self.btn_exp.configure(state="normal")
        else:
            self.opt_profiles.set("No saved macros")
            self.btn_load_prof.configure(state="disabled")
            self.btn_del_prof.configure(state="disabled")
            self.btn_dup.configure(state="disabled")
            self.btn_exp.configure(state="disabled")

    def _on_filter_changed(self):
        rec_mouse = bool(self.chk_mouse.get())
        rec_kbd = bool(self.chk_keyboard.get())
        self.config_service.set(["macro", "record_mouse"], rec_mouse, save_immediately=False)
        self.config_service.set(["macro", "record_keyboard"], rec_kbd, save_immediately=True)

    def _on_speed_selected(self, speed_text: str):
        speed = float(speed_text.replace("x", ""))
        self.config_service.set(["macro", "speed"], speed)

    def _on_playback_loops_changed(self, event):
        try:
            loops = int(self.entry_play_loop.get().strip() or "1")
            self.config_service.set(["macro", "loop"], loops, save_immediately=False)
        except ValueError:
            pass
        try:
            loop_del = float(self.entry_play_delay.get().strip() or "0.5")
            self.config_service.set(["macro", "loop_delay"], loop_del, save_immediately=False)
        except ValueError:
            pass

    def _on_profile_selected(self, name: str):
        pass

    def _on_timeline_reordered(self, reordered_events: list):
        self.current_events = reordered_events
        last_offset = 0.0
        for idx, event in enumerate(self.current_events):
            if idx > 0:
                last_offset += 0.1
            event["time_offset"] = last_offset

    # --- Macro Timeline Step Parameter Editor (Premium Upgrade) ---

    def _on_edit_timeline_item(self, idx: int, event: dict):
        """Dispatches an interactive dialog popup box allowing direct editing of event parameters."""
        etype = event["type"]
        
        if etype == "delay":
            dialog = ctk.CTkInputDialog(text=f"Enter new delay duration in milliseconds (Current: {event.get('delay_ms', 1000)}ms):", title="Edit Delay Step")
            val = dialog.get_input()
            if val and val.strip().isdigit():
                event["delay_ms"] = int(val.strip())
                self.drag_list.set_events(self.current_events)
                self.notification_service.show_toast("Delay step updated.", level="success")
                
        elif etype in ("key_down", "key_up"):
            dialog = ctk.CTkInputDialog(text=f"Enter key to trigger (Current: '{event['key']}'):", title="Edit Keyboard Step")
            val = dialog.get_input()
            if val and val.strip():
                event["key"] = val.strip()
                self.drag_list.set_events(self.current_events)
                self.notification_service.show_toast("Keyboard step updated.", level="success")
                
        elif etype in ("click", "move"):
            dialog = ctk.CTkInputDialog(text=f"Enter target coordinates as X,Y (Current: {event['x']},{event['y']}):", title="Edit Mouse Coordinates")
            val = dialog.get_input()
            if val and "," in val:
                try:
                    parts = val.split(",")
                    x = int(parts[0].strip())
                    y = int(parts[1].strip())
                    event["x"] = x
                    event["y"] = y
                    self.drag_list.set_events(self.current_events)
                    self.notification_service.show_toast("Mouse coordinates updated.", level="success")
                except ValueError:
                    self.notification_service.show_error("Format Error", "Coordinates must be numerical integers (e.g. 300,450).")

    # --- Macro Designer Blocks Insertions ---

    def _add_key_block(self):
        dialog = ctk.CTkInputDialog(text="Enter key to tap (e.g. A, Enter, Tab, F5, win):", title="Insert Key")
        key = dialog.get_input()
        if key and key.strip():
            offset = self.current_events[-1]["time_offset"] + 0.1 if self.current_events else 0.0
            self.current_events.append({
                "type": "key_down",
                "key": key.strip(),
                "time_offset": offset
            })
            self.current_events.append({
                "type": "key_up",
                "key": key.strip(),
                "time_offset": offset + 0.05
            })
            self.drag_list.set_events(self.current_events)
            self.notification_service.show_toast(f"Inserted Keystroke: {key.strip()}", level="success")

    def _add_click_block(self):
        x, y = get_cursor_position()
        offset = self.current_events[-1]["time_offset"] + 0.1 if self.current_events else 0.0
        self.current_events.append({
            "type": "click",
            "x": x,
            "y": y,
            "button": "left",
            "pressed": True,
            "time_offset": offset
        })
        self.current_events.append({
            "type": "click",
            "x": x,
            "y": y,
            "button": "left",
            "pressed": False,
            "time_offset": offset + 0.05
        })
        self.drag_list.set_events(self.current_events)
        self.notification_service.show_toast(f"Inserted click: Left ({x}, {y})", level="success")

    def _add_delay_block(self):
        dialog = ctk.CTkInputDialog(text="Enter delay duration (milliseconds):", title="Insert Delay")
        duration = dialog.get_input()
        if duration and duration.strip().isdigit():
            ms = int(duration.strip())
            offset = self.current_events[-1]["time_offset"] + 0.1 if self.current_events else 0.0
            self.current_events.append({
                "type": "delay",
                "delay_ms": ms,
                "time_offset": offset
            })
            self.drag_list.set_events(self.current_events)
            self.notification_service.show_toast(f"Inserted Delay wait: {ms}ms", level="success")

    # --- Actions ---

    def toggle_recording(self):
        if self.playback_runner.is_running():
            return
            
        if self.hook_listener.is_recording:
            recorded = self.hook_listener.stop_recording()
            self.current_events = recorded
            self._update_runner_status()
            self.btn_record.configure(text=self.lang.get("record"), fg_color="#E74C3C")
            self.btn_play.configure(state="normal")
            self.btn_save_macro.configure(state="normal")
            
            self.drag_list.set_events(self.current_events)
            self.notification_service.show_toast(f"Recorded {len(self.current_events)} actions.", level="success")
        else:
            self.current_events.clear()
            self.drag_list.set_events([])
            self.btn_play.configure(state="disabled")
            self.btn_save_macro.configure(state="disabled")
            
            self.btn_record.configure(text=self.lang.get("stop_record"), fg_color="#F39C12")
            self.status_card.update_status("running")
            
            rec_mouse = self.config_service.get("macro", "record_mouse")
            rec_kbd = self.config_service.get("macro", "record_keyboard")
            self.hook_listener.start_recording(rec_mouse, rec_kbd)
            self.notification_service.show_toast("Recording... Press F8 to save.", level="warning")

    def toggle_playback(self):
        if self.hook_listener.is_recording:
            return
            
        if self.playback_runner.is_running():
            self.playback_runner.stop()
            self._update_runner_status()
            self.notification_service.show_toast("Playback stopped.", level="warning")
        else:
            if not self.current_events:
                self.notification_service.show_error("No Macro Actions", "Please record actions or load a profile.")
                return
                
            self.btn_record.configure(state="disabled")
            self.status_card.update_status("running")
            
            def completed():
                self.btn_record.configure(state="normal")
                self._update_runner_status()
                
            self.playback_runner.on_status_changed = lambda status: self.master.after(0, self._on_playback_status_changed, status, completed)
            self.playback_runner.start(self.current_events)
            self._update_runner_status()
            self.notification_service.show_toast("Playback started.", level="success")

    def toggle_pause(self):
        if not self.playback_runner.is_running():
            return
            
        if self.playback_runner.is_paused():
            self.playback_runner.resume()
            self.notification_service.show_toast("Playback resumed.", level="success")
        else:
            self.playback_runner.pause()
            self.notification_service.show_toast("Playback paused.", level="warning")
        self._update_runner_status()

    def _on_playback_status_changed(self, status: str, complete_cb):
        if status in ("idle", "error"):
            complete_cb()

    def _on_event_intercepted(self, event: dict):
        self.current_events.append(event)
        self.master.after(0, lambda: self.drag_list.set_events(self.current_events))

    def _update_runner_status(self):
        if self.playback_runner.is_running():
            if self.playback_runner.is_paused():
                self.status_card.update_status("paused")
            else:
                self.status_card.update_status("running")
            self.btn_play.configure(text=self.lang.get("stop"), fg_color="#F39C12")
        else:
            self.status_card.update_status("idle")
            self.btn_play.configure(text=self.lang.get("play"), fg_color="#2ECC71")
            self.btn_record.configure(state="normal")
            
        self._update_pause_btn_text()

    def _update_pause_btn_text(self):
        if self.playback_runner.is_running() and self.playback_runner.is_paused():
            self.btn_pause.configure(text=self.lang.get("resume"))
        else:
            self.btn_pause.configure(text=self.lang.get("pause"))

    # --- Profile Actions ---

    def _load_selected_profile(self):
        name = self.opt_profiles.get()
        if not name or name == "No saved macros":
            return
            
        data = self.macro_service.load_macro(name)
        if data:
            self.current_events = data.get("events", [])
            self.drag_list.set_events(self.current_events)
            self.notification_service.show_toast(f"Loaded macro profile: {name}", level="success")

    def _delete_selected_profile(self):
        name = self.opt_profiles.get()
        if not name or name == "No saved macros":
            return
            
        if self.macro_service.delete_macro(name):
            self._refresh_profile_list()
            self.current_events.clear()
            self.drag_list.set_events([])
            self.notification_service.show_toast(f"Deleted profile: {name}", level="warning")

    def _duplicate_profile(self):
        name = self.opt_profiles.get()
        if not name or name == "No saved macros":
            return
            
        dialog = ctk.CTkInputDialog(text="Enter duplicate profile name:", title="Duplicate Macro")
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            if self.macro_service.save_macro(new_name.strip(), self.current_events):
                self._refresh_profile_list()
                self.opt_profiles.set(new_name.strip())
                self.notification_service.show_toast(f"Duplicated to: {new_name.strip()}", level="success")

    def _export_profile(self):
        if not self.current_events:
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Macro File",
            defaultextension=".macro.json",
            filetypes=[("Macro Files", "*.macro.json")]
        )
        if file_path:
            try:
                macro_data = {
                    "name": Path(file_path).name.replace(".macro.json", ""),
                    "events": self.current_events
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(macro_data, f, indent=4)
                self.notification_service.show_toast("Macro exported successfully.", level="success")
            except Exception as e:
                self.notification_service.show_error("Export Failed", str(e))

    def _import_profile(self):
        file_path = filedialog.askopenfilename(
            title="Import Macro File",
            filetypes=[("Macro Files", "*.macro.json")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                from ..utils.validator import validate_macro_data
                if validate_macro_data(data):
                    name = data.get("name", Path(file_path).name.replace(".macro.json", ""))
                    self.macro_service.save_macro(name, data["events"])
                    self._refresh_profile_list()
                    self.opt_profiles.set(name)
                    self.current_events = data["events"]
                    self.drag_list.set_events(self.current_events)
                    self.notification_service.show_toast(f"Imported: {name}", level="success")
                else:
                    self.notification_service.show_error("Import Error", "Selected file format is invalid.")
            except Exception as e:
                self.notification_service.show_error("Import Failed", str(e))

    def _prompt_save_macro(self):
        if not self.current_events:
            return
        dialog = ctk.CTkInputDialog(text="Enter a name for this macro:", title="Save Macro")
        name = dialog.get_input()
        if name and name.strip():
            if self.macro_service.save_macro(name.strip(), self.current_events):
                self._refresh_profile_list()
                self.opt_profiles.set(name.strip())
                self.notification_service.show_toast(f"Saved macro: {name.strip()}", level="success")

    # --- Context Menu ---

    def _show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0, bg="#111115", fg="#FFFFFF", activebackground="#1F6AA5", activeforeground="#FFFFFF")
        menu.add_command(label="Clear Timeline", command=self._clear_timeline)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _clear_timeline(self):
        self.current_events.clear()
        self.drag_list.set_events([])
        self._on_timeline_reordered([])

    def _on_external_config_changed(self, settings: dict):
        try:
            hotkey_str = settings.get("hotkeys", {}).get("macro_record_start_stop", "F8")
            self.status_card.update_hotkey(hotkey_str)
        except Exception:
            pass
