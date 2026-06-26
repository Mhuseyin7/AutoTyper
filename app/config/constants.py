import os
from pathlib import Path

# Paths
APP_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = APP_DIR.parent
STORAGE_DIR = BASE_DIR / "storage"
LOGS_DIR = BASE_DIR / "logs"
THEMES_DIR = APP_DIR / "themes"

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
THEMES_DIR.mkdir(parents=True, exist_ok=True)

# App Info
APP_NAME = "Auto Typer Pro"
VERSION = "1.0.0"
AUTHOR = "Antigravity Architect"

# Configuration File Name
CONFIG_FILE_NAME = "settings.json"
CONFIG_PATH = STORAGE_DIR / CONFIG_FILE_NAME

# Default Settings Schema
DEFAULT_SETTINGS = {
    "theme": "dark",        # "dark", "light", "system"
    "language": "en",       # "en", "tr"
    "auto_save": True,
    "log_level": "INFO",
    "theme_colors": {
        "primary": "#1F6AA5",  # accent color
        "panel_bg": "#1E1E1E"  # container backgrounds (for theme editor)
    },
    "font_config": {
        "family": "Consolas",
        "size": 12
    },
    "hotkeys": {
        "auto_typer_start_stop": "F7",
        "auto_clicker_start_stop": "F6",
        "macro_record_start_stop": "F8",
        "macro_play_start_stop": "F9",
    },
    "auto_typer": {
        "text": "Hello World! This is Auto Typer Pro.\nHere is a second line of text.\nAnd a third one!",
        "mode": "simulate",        # "simulate", "write", "paste"
        "typing_flow": "entire",   # "entire" (full text), "line" (line by line), "random" (random lines)
        
        # Delay Profiles
        "initial_delay": 0.5,      # delay before typing starts (seconds)
        "char_delay": 0.05,        # delay between characters (seconds)
        "word_delay": 0.15,        # delay after typing a space (seconds)
        "line_delay": 0.5,         # delay after typing a line break (seconds)
        "loop": 1,                 # 0 means infinite loop
        "loop_delay": 1.0,         # delay between loops (seconds)
        
        # Human Emulation
        "human_like": True,
        "delay_variance": 0.25,     # percent variance (e.g. 0.25 = +/- 25% random speed fluctuations)
        "punc_delay": 0.3,         # pause duration at punctuation marks . , ? ! (seconds)
        
        # Spelling Mistakes Emulation (Premium)
        "spelling_error_rate": 0.02, # 2% chance of typos
        
        "target_mode": "active",   # "active", "specific"
        "target_window": ""
    },
    "auto_clicker": {
        "interval_ms": 100,
        "button": "left",
        "click_type": "single",
        "position_mode": "cursor",
        "fixed_x": 0,
        "fixed_y": 0,
        "loop": 0
    },
    "macro": {
        "speed": 1.0,
        "loop": 1,
        "loop_delay": 0.5,
        "record_mouse": True,
        "record_keyboard": True
    }
}
