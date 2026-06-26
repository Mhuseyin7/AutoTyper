import os
import shutil
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from ..config.constants import STORAGE_DIR

logger = logging.getLogger("AutoTyperPro")

class BackupService:
    """Manages archiving and restoring settings and profiles using rolling ZIP directories."""
    def __init__(self):
        self.storage_dir = STORAGE_DIR
        self.backup_dir = STORAGE_DIR / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> bool:
        """Compresses all user profiles and settings into a zip backup file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"autotyper_backup_{timestamp}.zip"
            
            # Find all files to backup (settings.json, *.macro.json)
            files_to_backup = list(self.storage_dir.glob("*.json"))
            
            if not files_to_backup:
                logger.warning("No storage configuration files found to backup.")
                return False
                
            with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files_to_backup:
                    # Skip files inside subdirectories (like the backups folder itself!)
                    if file_path.parent == self.storage_dir:
                        zipf.write(file_path, arcname=file_path.name)
                        
            logger.info(f"Backup created successfully: {backup_file.name}")
            self._prune_old_backups()
            return True
        except Exception as e:
            logger.error(f"Failed to create configuration backup: {e}")
            return False

    def get_latest_backup(self) -> Path | None:
        """Returns the path to the newest zip backup file."""
        try:
            backups = sorted(self.backup_dir.glob("autotyper_backup_*.zip"), key=os.path.getmtime)
            if backups:
                return backups[-1]
        except Exception as e:
            logger.error(f"Failed to query backup list: {e}")
        return None

    def restore_latest_backup(self) -> bool:
        """Restores configurations and macro profiles from the latest available zip backup."""
        latest = self.get_latest_backup()
        if not latest:
            logger.warning("No backup file found to restore.")
            return False
            
        try:
            with zipfile.ZipFile(latest, "r") as zipf:
                # Extract all files directly back to the storage directory
                zipf.extractall(self.storage_dir)
            logger.info(f"Successfully restored configuration state from: {latest.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

    def _prune_old_backups(self, max_backups: int = 5):
        """Keeps only the most recent N backup files to optimize disk storage space."""
        try:
            backups = sorted(self.backup_dir.glob("autotyper_backup_*.zip"), key=os.path.getmtime)
            if len(backups) > max_backups:
                to_delete = backups[:-max_backups]
                for file_path in to_delete:
                    file_path.unlink()
                    logger.info(f"Deleted old backup archive: {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to prune old backups: {e}")
            
    def get_last_backup_time_str(self) -> str:
        """Returns a string representation of the last backup date."""
        latest = self.get_latest_backup()
        if not latest:
            return "N/A"
        try:
            mtime = os.path.getmtime(latest)
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return "N/A"
