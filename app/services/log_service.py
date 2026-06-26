import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..config.constants import LOGS_DIR

def setup_logging(log_level_str: str = "INFO") -> logging.Logger:
    """Configures application-wide logging with file rotation and console handlers."""
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Ensure log directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "autotyperpro.log"
    
    logger = logging.getLogger("AutoTyperPro")
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates on reconfiguration
    if logger.hasHandlers():
        logger.handlers.clear()
        
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler (5 MB rotating limit, keep 3 backup files)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    logger.info("Logging service initialized successfully.")
    return logger

def get_recent_logs(num_lines: int = 150) -> str:
    """Reads the last N lines from the active log file to display in the UI settings panel."""
    log_file = LOGS_DIR / "autotyperpro.log"
    if not log_file.exists():
        return "No logs generated yet."
        
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            recent_lines = lines[-num_lines:]
            return "".join(recent_lines)
    except Exception as e:
        return f"Error reading log file: {str(e)}"
