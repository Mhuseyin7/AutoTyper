import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from .base_page import BasePage
from ..widgets.status_card import StatusCard

class TyperPage(BasePage):
    """Dashboard page to configure Auto Typer parameters, load files, trigger emulations, and inspect telemetry."""
    def __init__(self, master, services: dict, **kwargs):
        super().__init__(master, services, **kwargs)
        self.runner = services.get("typer_runner")
        
        self.create_header(
            title_key="typer_header_title",
            subtitle_key="typer_header_subtitle"
        )

        # Page grid layout
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, padx=25, pady=15, sticky="nsew")
        self.body_frame.grid_columnconfigure(0, weight=4) # Left Config
        self.body_frame.grid_columnconfigure(1, weight=5) # Right Metin & Eylemler
        self.body_frame.grid_rowconfigure(0, weight=1)

        # Left Column: Configuration Controls
        self.left_col = ctk.CTkScrollableFrame(self.body_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.left_col.grid_columnconfigure(0, weight=1)

        # Status Card
        hotkey_str = self.config_service.get("hotkeys", "auto_typer_start_stop")
        self.status_card = StatusCard(self.left_col, title=self.lang.get("engine_typer"), hotkey=hotkey_str)
        self.status_card.grid(row=0, column=0, pady=(0, 15), sticky="ew")

        # Typing settings card
        self.config_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.config_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.config_card.grid_columnconfigure(0, weight=1)

        # Mode Selector
        self.lbl_mode = ctk.CTkLabel(
            self.config_card, text=self.lang.get("typing_mode"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_mode.pack(anchor="w", padx=15, pady=(15, 2))
        self.opt_mode = ctk.CTkOptionMenu(
            self.config_card,
            values=[self.lang.get("mode_simulate"), self.lang.get("mode_write"), self.lang.get("mode_paste")],
            command=self._on_mode_selected
        )
        self.opt_mode.pack(fill="x", padx=15, pady=(0, 10))

        # Flow Selector
        self.lbl_flow = ctk.CTkLabel(
            self.config_card, text=self.lang.get("typing_flow"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_flow.pack(anchor="w", padx=15, pady=(5, 2))
        self.opt_flow = ctk.CTkOptionMenu(
            self.config_card,
            values=[self.lang.get("flow_entire"), self.lang.get("flow_line"), self.lang.get("flow_random")],
            command=self._on_flow_selected
        )
        self.opt_flow.pack(fill="x", padx=15, pady=(0, 15))

        # Delays Card
        self.delay_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.delay_card.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.delay_card.grid_columnconfigure(0, weight=1)

        # Sliders
        # Initial Delay
        self.lbl_initial_delay = ctk.CTkLabel(self.delay_card, text="Initial Delay (0.5s)", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_initial_delay.pack(anchor="w", padx=15, pady=(10, 2))
        self.slider_initial = ctk.CTkSlider(self.delay_card, from_=0.0, to=5.0, command=self._on_initial_delay_changed)
        self.slider_initial.pack(fill="x", padx=15, pady=(0, 10))

        # Character Delay
        self.lbl_char_delay = ctk.CTkLabel(self.delay_card, text="Character Delay (0.05s)", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_char_delay.pack(anchor="w", padx=15, pady=(5, 2))
        self.slider_char = ctk.CTkSlider(self.delay_card, from_=0.0, to=1.0, command=self._on_char_delay_changed)
        self.slider_char.pack(fill="x", padx=15, pady=(0, 10))

        # Word Delay
        self.lbl_word_delay = ctk.CTkLabel(self.delay_card, text="Word Delay (0.15s)", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_word_delay.pack(anchor="w", padx=15, pady=(5, 2))
        self.slider_word = ctk.CTkSlider(self.delay_card, from_=0.0, to=2.0, command=self._on_word_delay_changed)
        self.slider_word.pack(fill="x", padx=15, pady=(0, 10))

        # Line Delay
        self.lbl_line_delay = ctk.CTkLabel(self.delay_card, text="Line Delay (0.5s)", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_line_delay.pack(anchor="w", padx=15, pady=(5, 2))
        self.slider_line = ctk.CTkSlider(self.delay_card, from_=0.0, to=5.0, command=self._on_line_delay_changed)
        self.slider_line.pack(fill="x", padx=15, pady=(0, 15))

        # Human Emulation Card
        self.human_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.human_card.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        self.human_card.grid_columnconfigure(0, weight=1)

        self.chk_human = ctk.CTkCheckBox(
            self.human_card, text=self.lang.get("human_like"), command=self._on_human_toggled
        )
        self.chk_human.pack(anchor="w", padx=15, pady=(15, 10))

        self.lbl_variance = ctk.CTkLabel(self.human_card, text="Delay Randomness (25%)", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_variance.pack(anchor="w", padx=15, pady=(5, 2))
        self.slider_variance = ctk.CTkSlider(self.human_card, from_=0.0, to=1.0, command=self._on_variance_changed)
        self.slider_variance.pack(fill="x", padx=15, pady=(0, 10))

        self.lbl_punc = ctk.CTkLabel(self.human_card, text="Punctuation Delay (0.3s)", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_punc.pack(anchor="w", padx=15, pady=(5, 2))
        self.slider_punc = ctk.CTkSlider(self.human_card, from_=0.0, to=2.0, command=self._on_punc_changed)
        self.slider_punc.pack(fill="x", padx=15, pady=(0, 10))

        # Spelling Error Rate (Premium)
        self.lbl_error_rate = ctk.CTkLabel(self.human_card, text="Spelling Error Rate (2%)", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_error_rate.pack(anchor="w", padx=15, pady=(5, 2))
        self.slider_error_rate = ctk.CTkSlider(self.human_card, from_=0.0, to=0.10, command=self._on_error_rate_changed)
        self.slider_error_rate.pack(fill="x", padx=15, pady=(0, 15))

        # Loops Card
        self.loop_card = ctk.CTkFrame(
            self.left_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1E1E1E")
        )
        self.loop_card.grid(row=4, column=0, sticky="ew")
        self.loop_card.grid_columnconfigure(0, weight=1)

        self.lbl_loop = ctk.CTkLabel(
            self.loop_card, text=self.lang.get("iteration_count"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_loop.pack(anchor="w", padx=15, pady=(15, 2))
        self.entry_loop = ctk.CTkEntry(self.loop_card, placeholder_text="1")
        self.entry_loop.pack(fill="x", padx=15, pady=(0, 10))
        self.entry_loop.bind("<KeyRelease>", self._on_loop_settings_changed)

        self.lbl_loop_delay = ctk.CTkLabel(
            self.loop_card, text=self.lang.get("loop_delay_sec"), font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.lbl_loop_delay.pack(anchor="w", padx=15, pady=(5, 2))
        self.entry_loop_delay = ctk.CTkEntry(self.loop_card, placeholder_text="1.0")
        self.entry_loop_delay.pack(fill="x", padx=15, pady=(0, 15))
        self.entry_loop_delay.bind("<KeyRelease>", self._on_loop_settings_changed)


        # Right Column: Text Input, Telemetry & Actions
        self.right_col = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        self.right_col.grid_columnconfigure(0, weight=1)
        self.right_col.grid_rowconfigure(0, weight=0) # File Import Header
        self.right_col.grid_rowconfigure(1, weight=1) # Text Box
        self.right_col.grid_rowconfigure(2, weight=0) # Telemetry Grid
        self.right_col.grid_rowconfigure(3, weight=0) # Trigger Buttons

        # File Import Header
        self.file_header_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.file_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.file_header_frame.grid_columnconfigure(0, weight=1)

        self.btn_import = ctk.CTkButton(
            self.file_header_frame,
            text=self.lang.get("import_file"),
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color=("#3498DB", "#2980B9"),
            hover_color=("#2980B9", "#2471A3"),
            height=28,
            command=self._import_file
        )
        self.btn_import.grid(row=0, column=1, sticky="e")

        # Text Frame
        self.text_frame = ctk.CTkFrame(
            self.right_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#FFFFFF", "#141414")
        )
        self.text_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1)

        self.txt_area = ctk.CTkTextbox(
            self.text_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="transparent",
            text_color=("#111111", "#EEEEEE"),
            wrap="word"
        )
        self.txt_area.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.txt_area.bind("<KeyRelease>", self._on_text_changed)

        # Telemetry Display Grid
        self.telemetry_frame = ctk.CTkFrame(
            self.right_col,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#2D2D2D"),
            fg_color=("#F9F9F9", "#1A1A1E")
        )
        self.telemetry_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        for col_idx in range(4):
            self.telemetry_frame.grid_columnconfigure(col_idx, weight=1)

        # Stats Labels
        self.lbl_stat_cpm = ctk.CTkLabel(self.telemetry_frame, text="CPM: 0", font=ctk.CTkFont(family="Inter", size=11, weight="bold"))
        self.lbl_stat_cpm.grid(row=0, column=0, padx=10, pady=10)
        
        self.lbl_stat_chars = ctk.CTkLabel(self.telemetry_frame, text="Chars: 0", font=ctk.CTkFont(family="Inter", size=11, weight="bold"))
        self.lbl_stat_chars.grid(row=0, column=1, padx=10, pady=10)

        self.lbl_stat_loops = ctk.CTkLabel(self.telemetry_frame, text="Loops: 0", font=ctk.CTkFont(family="Inter", size=11, weight="bold"))
        self.lbl_stat_loops.grid(row=0, column=2, padx=10, pady=10)

        self.lbl_stat_rate = ctk.CTkLabel(self.telemetry_frame, text="Rate: 100%", font=ctk.CTkFont(family="Inter", size=11, weight="bold"))
        self.lbl_stat_rate.grid(row=0, column=3, padx=10, pady=10)

        # Trigger Action Buttons (Start, Pause/Resume, Stop)
        self.btn_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, sticky="ew")
        for col_idx in range(3):
            self.btn_frame.grid_columnconfigure(col_idx, weight=1)

        self.btn_start = ctk.CTkButton(
            self.btn_frame,
            text=self.lang.get("start_typing"),
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

        # Config listener
        self.config_service.add_listener(self._on_external_config_changed)
        
        # Telemetry updates listener
        if self.stats:
            self.stats.add_listener(self._update_telemetry_ui)

    def on_show(self):
        self._load_from_config()
        self._update_runner_status()
        self._update_telemetry_ui()

    def on_hide(self):
        self._save_to_config()

    def refresh_language(self):
        """Redraws page localizations."""
        self.update_header_text()
        self.lbl_mode.configure(text=self.lang.get("typing_mode"))
        self.lbl_flow.configure(text=self.lang.get("typing_flow"))
        self.chk_human.configure(text=self.lang.get("human_like"))
        self.lbl_loop.configure(text=self.lang.get("iteration_count"))
        self.lbl_loop_delay.configure(text=self.lang.get("loop_delay_sec"))
        self.btn_import.configure(text=self.lang.get("import_file"))
        self.btn_start.configure(text=self.lang.get("start_typing"))
        self.btn_stop.configure(text=self.lang.get("stop"))

        # Update slider label texts
        init_d = self.slider_initial.get()
        self.lbl_initial_delay.configure(text=f"Initial Delay ({init_d:.2f}s)")
        
        char_d = self.slider_char.get()
        self.lbl_char_delay.configure(text=f"{self.lang.get('char_delay')} ({char_d:.3f}s)")
        
        word_d = self.slider_word.get()
        self.lbl_word_delay.configure(text=f"{self.lang.get('word_delay')} ({word_d:.2f}s)")
        
        line_d = self.slider_line.get()
        self.lbl_line_delay.configure(text=f"{self.lang.get('line_delay')} ({line_d:.2f}s)")
        
        variance = self.slider_variance.get()
        self.lbl_variance.configure(text=f"{self.lang.get('delay_variance')} ({int(variance*100)}%)")
        
        punc_d = self.slider_punc.get()
        self.lbl_punc.configure(text=f"Punctuation Delay ({punc_d:.2f}s)")
        
        err_rate = self.slider_error_rate.get()
        self.lbl_error_rate.configure(text=f"{self.lang.get('spelling_error_rate')} ({int(err_rate*100)}%)")
        
        # Update mode option menu values translation
        mode_val = self.config_service.get("auto_typer", "mode")
        mode_map = {"simulate": "mode_simulate", "write": "mode_write", "paste": "mode_paste"}
        self.opt_mode.configure(values=[self.lang.get("mode_simulate"), self.lang.get("mode_write"), self.lang.get("mode_paste")])
        self.opt_mode.set(self.lang.get(mode_map.get(mode_val, "mode_simulate")))
        
        # Update flow values
        flow_val = self.config_service.get("auto_typer", "typing_flow")
        flow_map = {"entire": "flow_entire", "line": "flow_line", "random": "flow_random"}
        self.opt_flow.configure(values=[self.lang.get("flow_entire"), self.lang.get("flow_line"), self.lang.get("flow_random")])
        self.opt_flow.set(self.lang.get(flow_map.get(flow_val, "flow_entire")))
        
        # Pause status label
        self._update_pause_btn_text()
        self._on_external_config_changed(self.config_service.settings)

    def _load_from_config(self):
        """Loads and syncs UI settings components."""
        # Text
        text = self.config_service.get("auto_typer", "text")
        self.txt_area.delete("1.0", tk.END)
        self.txt_area.insert("1.0", text)

        # Mode & flow options menu settings
        mode_val = self.config_service.get("auto_typer", "mode")
        mode_map = {"simulate": "mode_simulate", "write": "mode_write", "paste": "mode_paste"}
        self.opt_mode.set(self.lang.get(mode_map.get(mode_val, "mode_simulate")))
        self._toggle_delay_controls(mode_val)

        flow_val = self.config_service.get("auto_typer", "typing_flow")
        flow_map = {"entire": "flow_entire", "line": "flow_line", "random": "flow_random"}
        self.opt_flow.set(self.lang.get(flow_map.get(flow_val, "flow_entire")))

        # Delays
        init_d = self.config_service.get("auto_typer", "initial_delay")
        self.slider_initial.set(init_d)
        self.lbl_initial_delay.configure(text=f"Initial Delay ({init_d:.2f}s)")

        char_d = self.config_service.get("auto_typer", "char_delay")
        self.slider_char.set(char_d)
        self.lbl_char_delay.configure(text=f"{self.lang.get('char_delay')} ({char_d:.3f}s)")

        word_d = self.config_service.get("auto_typer", "word_delay")
        self.slider_word.set(word_d)
        self.lbl_word_delay.configure(text=f"{self.lang.get('word_delay')} ({word_d:.2f}s)")

        line_d = self.config_service.get("auto_typer", "line_delay")
        self.slider_line.set(line_d)
        self.lbl_line_delay.configure(text=f"{self.lang.get('line_delay')} ({line_d:.2f}s)")

        # Human Emulation
        human_enabled = self.config_service.get("auto_typer", "human_like")
        self.chk_human.select() if human_enabled else self.chk_human.deselect()
        self._toggle_human_controls(human_enabled)

        variance = self.config_service.get("auto_typer", "delay_variance")
        self.slider_variance.set(variance)
        self.lbl_variance.configure(text=f"{self.lang.get('delay_variance')} ({int(variance*100)}%)")

        punc_d = self.config_service.get("auto_typer", "punc_delay")
        self.slider_punc.set(punc_d)
        self.lbl_punc.configure(text=f"Punctuation Delay ({punc_d:.2f}s)")

        err_rate = self.config_service.get("auto_typer", "spelling_error_rate") or 0.02
        self.slider_error_rate.set(err_rate)
        self.lbl_error_rate.configure(text=f"Spelling Error Rate ({int(err_rate*100)}%)")

        # Loops
        self.entry_loop.delete(0, tk.END)
        self.entry_loop.insert(0, str(self.config_service.get("auto_typer", "loop")))

        self.entry_loop_delay.delete(0, tk.END)
        self.entry_loop_delay.insert(0, f'{self.config_service.get("auto_typer", "loop_delay"):.2f}')

    def _save_to_config(self):
        text = self.txt_area.get("1.0", tk.END).strip()
        self.config_service.set(["auto_typer", "text"], text, save_immediately=False)
        self.config_service.save_settings()

    def _toggle_delay_controls(self, mode: str):
        """Hides typing speed delays when using clipboard paste mode."""
        if mode == "paste":
            self.slider_char.configure(state="disabled")
            self.slider_word.configure(state="disabled")
            self.slider_line.configure(state="disabled")
            self.chk_human.configure(state="disabled")
            self._toggle_human_controls(False)
        else:
            self.slider_char.configure(state="normal")
            self.slider_word.configure(state="normal")
            self.slider_line.configure(state="normal")
            self.chk_human.configure(state="normal")
            self._toggle_human_controls(self.chk_human.get())

    def _toggle_human_controls(self, enabled: bool):
        if enabled:
            self.slider_variance.configure(state="normal")
            self.slider_punc.configure(state="normal")
            self.slider_error_rate.configure(state="normal")
        else:
            self.slider_variance.configure(state="disabled")
            self.slider_punc.configure(state="disabled")
            self.slider_error_rate.configure(state="disabled")

    # --- Sliders Callbacks ---

    def _on_mode_selected(self, mode_text: str):
        mode_map = {self.lang.get("mode_simulate"): "simulate", self.lang.get("mode_write"): "write", self.lang.get("mode_paste"): "paste"}
        mode = mode_map.get(mode_text, "simulate")
        self.config_service.set(["auto_typer", "mode"], mode)
        self._toggle_delay_controls(mode)

    def _on_flow_selected(self, flow_text: str):
        flow_map = {self.lang.get("flow_entire"): "entire", self.lang.get("flow_line"): "line", self.lang.get("flow_random"): "random"}
        flow = flow_map.get(flow_text, "entire")
        self.config_service.set(["auto_typer", "typing_flow"], flow)

    def _on_initial_delay_changed(self, val: float):
        self.lbl_initial_delay.configure(text=f"Initial Delay ({val:.2f}s)")
        self.config_service.set(["auto_typer", "initial_delay"], float(val))

    def _on_char_delay_changed(self, val: float):
        self.lbl_char_delay.configure(text=f"{self.lang.get('char_delay')} ({val:.3f}s)")
        self.config_service.set(["auto_typer", "char_delay"], float(val))

    def _on_word_delay_changed(self, val: float):
        self.lbl_word_delay.configure(text=f"{self.lang.get('word_delay')} ({val:.2f}s)")
        self.config_service.set(["auto_typer", "word_delay"], float(val))

    def _on_line_delay_changed(self, val: float):
        self.lbl_line_delay.configure(text=f"{self.lang.get('line_delay')} ({val:.2f}s)")
        self.config_service.set(["auto_typer", "line_delay"], float(val))

    def _on_human_toggled(self):
        val = bool(self.chk_human.get())
        self.config_service.set(["auto_typer", "human_like"], val)
        self._toggle_human_controls(val)

    def _on_variance_changed(self, val: float):
        self.lbl_variance.configure(text=f"{self.lang.get('delay_variance')} ({int(val*100)}%)")
        self.config_service.set(["auto_typer", "delay_variance"], float(val))

    def _on_punc_changed(self, val: float):
        self.lbl_punc.configure(text=f"Punctuation Delay ({val:.2f}s)")
        self.config_service.set(["auto_typer", "punc_delay"], float(val))

    def _on_error_rate_changed(self, val: float):
        self.lbl_error_rate.configure(text=f"Spelling Error Rate ({int(val*100)}%)")
        self.config_service.set(["auto_typer", "spelling_error_rate"], float(val))

    def _on_loop_settings_changed(self, event):
        try:
            loops = int(self.entry_loop.get().strip() or "1")
            self.config_service.set(["auto_typer", "loop"], loops, save_immediately=False)
        except ValueError:
            pass
        try:
            delay = float(self.entry_loop_delay.get().strip() or "1.0")
            self.config_service.set(["auto_typer", "loop_delay"], delay, save_immediately=False)
        except ValueError:
            pass

    def _on_text_changed(self, event):
        text = self.txt_area.get("1.0", tk.END).strip()
        self.config_service.set(["auto_typer", "text"], text, save_immediately=False)

    # --- Actions ---

    def _import_file(self):
        """Launches Win32 file selector to import TXT/CSV text directly."""
        file_path = filedialog.askopenfilename(
            title="Import text sequence",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            imported_text = self.runner.load_text_from_file(file_path)
            if imported_text:
                self.txt_area.delete("1.0", tk.END)
                self.txt_area.insert("1.0", imported_text)
                self._save_to_config()
                self.notification_service.show_toast(f"Successfully loaded: {Path(file_path).name}", level="success")
            else:
                self.notification_service.show_error("Import Error", "Failed to extract text from selected file.")

    def start_runner(self):
        if self.runner.is_running():
            return
        self._save_to_config()
        success = self.runner.start()
        if success:
            self._update_runner_status()
            self.notification_service.show_toast("Auto Typer active.", level="success")

    def stop_runner(self):
        if not self.runner.is_running():
            return
        self.runner.stop()
        self._update_runner_status()
        self.notification_service.show_toast("Auto Typer idle.", level="warning")

    def toggle_pause(self):
        if not self.runner.is_running():
            return
            
        if self.runner.is_paused():
            self.runner.resume()
            self.notification_service.show_toast("Auto Typer resumed.", level="success")
        else:
            self.runner.pause()
            self.notification_service.show_toast("Auto Typer paused.", level="warning")
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

    def _update_telemetry_ui(self):
        """Redraws stats dashboard cards dynamically."""
        if not self.stats:
            return
        self.lbl_stat_cpm.configure(text=f"{self.lang.get('cpm')}: {int(self.stats.get_cpm())}")
        self.lbl_stat_chars.configure(text=f"{self.lang.get('chars_typed')}: {self.stats.total_chars_typed}")
        self.lbl_stat_loops.configure(text=f"{self.lang.get('total_repeats')}: {self.stats.total_repeats}")
        self.lbl_stat_rate.configure(text=f"{self.lang.get('success_rate')}: {self.stats.get_success_rate():.1f}%")

    def _on_external_config_changed(self, settings: dict):
        try:
            hotkey_str = settings.get("hotkeys", {}).get("auto_typer_start_stop", "F7")
            self.status_card.update_hotkey(hotkey_str)
        except Exception:
            pass
