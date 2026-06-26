import logging
from typing import Any, Dict

logger = logging.getLogger("AutoTyperPro")

def validate_settings(settings: Dict[str, Any], default_settings: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively validates and repairs a settings dictionary using a default schema.
    
    If key-value pairs are missing, they are filled in from default_settings.
    If the type does not match, the default value is restored.
    """
    repaired = {}
    for key, def_val in default_settings.items():
        if key not in settings:
            logger.warning(f"Configuration key '{key}' missing. Restoring default: {def_val}")
            repaired[key] = def_val
        elif isinstance(def_val, dict):
            if not isinstance(settings[key], dict):
                logger.warning(f"Configuration type mismatch for '{key}'. Restoring default dict.")
                repaired[key] = def_val
            else:
                repaired[key] = validate_settings(settings[key], def_val)
        else:
            # Type verification
            if type(settings[key]) is not type(def_val) and def_val is not None:
                # Attempt conversion if possible
                try:
                    if isinstance(def_val, bool):
                        repaired[key] = bool(settings[key])
                    elif isinstance(def_val, int):
                        repaired[key] = int(settings[key])
                    elif isinstance(def_val, float):
                        repaired[key] = float(settings[key])
                    elif isinstance(def_val, str):
                        repaired[key] = str(settings[key])
                    else:
                        raise TypeError()
                except (ValueError, TypeError):
                    logger.warning(f"Configuration type mismatch for '{key}'. Expected {type(def_val)}, got {type(settings[key])}. Restoring default.")
                    repaired[key] = def_val
            else:
                repaired[key] = settings[key]
    return repaired

def validate_macro_data(macro_data: Any) -> bool:
    """Validates that a macro structure conforms to the required event array format."""
    if not isinstance(macro_data, dict):
        return False
        
    if "events" not in macro_data or not isinstance(macro_data["events"], list):
        return False
        
    required_keys = {"type", "time_offset"}
    valid_types = {"move", "click", "key_down", "key_up"}
    
    for idx, event in enumerate(macro_data["events"]):
        if not isinstance(event, dict):
            logger.error(f"Macro event at index {idx} is not a dictionary.")
            return False
        if not required_keys.issubset(event.keys()):
            logger.error(f"Macro event at index {idx} is missing required fields {required_keys}.")
            return False
        if event["type"] not in valid_types:
            logger.error(f"Macro event at index {idx} has invalid event type: {event['type']}")
            return False
        if not isinstance(event["time_offset"], (int, float)):
            logger.error(f"Macro event at index {idx} has invalid time_offset: {event['time_offset']}")
            return False
            
    return True
