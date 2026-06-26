import sys
from pathlib import Path

# Resolve the project root folder and insert it at index 0 in sys.path
# This ensures that absolute imports starting with 'app.' work seamlessly.
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    # Import inside block to ensure sys.path configuration is applied first
    from app.main import main
    main()
