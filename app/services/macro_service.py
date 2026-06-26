import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..config.constants import STORAGE_DIR
from ..utils.validator import validate_macro_data

logger = logging.getLogger("AutoTyperPro")

class MacroService:
    """Manages the persistence, listing, loading, and deletion of automation macros."""
    def __init__(self):
        self.storage_dir = STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def list_macros(self) -> List[str]:
        """Returns names of all saved macro profiles (without .json extension)."""
        try:
            macro_files = self.storage_dir.glob("*.macro.json")
            return [f.name.replace(".macro.json", "") for f in macro_files]
        except Exception as e:
            logger.error(f"Failed to list saved macros: {e}")
            return []

    def load_macro(self, name: str) -> Optional[Dict[str, Any]]:
        """Loads and validates a macro configuration by name."""
        file_path = self.storage_dir / f"{name}.macro.json"
        if not file_path.exists():
            logger.warning(f"Macro file '{name}' does not exist.")
            return None
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if validate_macro_data(data):
                logger.info(f"Successfully loaded macro '{name}' containing {len(data['events'])} events.")
                return data
            else:
                logger.error(f"Macro validation failed for '{name}'. File content is corrupted.")
                return None
        except Exception as e:
            logger.error(f"Error loading macro '{name}': {e}")
            return None

    def save_macro(self, name: str, events: List[Dict[str, Any]]) -> bool:
        """Saves a list of recorded events as a macro JSON profile."""
        if not name or not name.strip():
            logger.warning("Empty name provided for saving macro.")
            return False
            
        # Clean name for safe filename
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_", " ")).strip()
        if not safe_name:
            logger.warning("Invalid macro name after cleaning.")
            return False
            
        file_path = self.storage_dir / f"{safe_name}.macro.json"
        
        macro_data = {
            "name": safe_name,
            "created_at": datetime.now().isoformat(),
            "events": events
        }
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(macro_data, f, indent=4)
            logger.info(f"Macro '{safe_name}' saved successfully to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save macro '{safe_name}': {e}")
            return False

    def delete_macro(self, name: str) -> bool:
        """Deletes a saved macro configuration file."""
        file_path = self.storage_dir / f"{name}.macro.json"
        if not file_path.exists():
            logger.warning(f"Attempted to delete non-existent macro '{name}'.")
            return False
            
        try:
            file_path.unlink()
            logger.info(f"Macro '{name}' deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete macro '{name}': {e}")
            return False
