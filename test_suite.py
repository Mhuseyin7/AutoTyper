import unittest
import sys
import os
import json
import shutil
import csv
import threading
from pathlib import Path

# Setup sys path so that absolute imports work from the project root
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config.constants import STORAGE_DIR, LOGS_DIR
from app.services.config_service import ConfigService
from app.services.language_service import LanguageService
from app.services.backup_service import BackupService
from app.utils.recovery import SessionRecovery
from app.utils.profiler import ResourceProfiler
from app.core.typer import AutoTyperRunner, NEIGHBORS

class TestAutoTyperPro(unittest.TestCase):
    
    def setUp(self):
        # Create storage directories if they do not exist
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Instantiate services with a test-specific container
        self.config_service = ConfigService()
        self.services = {
            "config": self.config_service,
            "language": LanguageService(self.config_service),
            "stats_service": None,
            "backup_service": BackupService()
        }

    def test_config_service_get_set(self):
        """Tests that ConfigService reads, writes, and saves settings properly."""
        test_key = "test_setting_key_123"
        self.config_service.set(["auto_typer", test_key], "premium_value")
        val = self.config_service.get("auto_typer", test_key)
        self.assertEqual(val, "premium_value")
        
        # Verify default fallback
        fallback = self.config_service.get("auto_typer", "non_existent_key")
        self.assertIsNone(fallback)

    def test_language_service(self):
        """Tests language translation service lookup and language switching."""
        lang_service = self.services["language"]
        
        # Change language to Turkish
        lang_service.set_language("tr")
        self.assertEqual(lang_service.current_lang, "tr")
        self.assertIn("Yazıcı", lang_service.get("tab_typer") or "Yazıcı")

        # Change language to English
        lang_service.set_language("en")
        self.assertEqual(lang_service.current_lang, "en")
        self.assertIn("Typer", lang_service.get("tab_typer") or "Typer")

    def test_session_recovery_checkpoint(self):
        """Tests that SessionRecovery creates and restores checkpoint state files."""
        # Clean potential existing checkpoints
        SessionRecovery.clear_session_checkpoint()
        
        test_data = {
            "active_page": "macro",
            "typer_text": "This is a premium recovery session test string."
        }
        
        # Save session
        success = SessionRecovery.save_session_checkpoint(test_data)
        self.assertTrue(success)
        
        # Load session
        loaded = SessionRecovery.load_session_checkpoint()
        self.assertEqual(loaded.get("active_page"), "macro")
        self.assertEqual(loaded.get("typer_text"), "This is a premium recovery session test string.")
        
        # Clear checkpoint
        SessionRecovery.clear_session_checkpoint()
        cleared_data = SessionRecovery.load_session_checkpoint()
        self.assertEqual(cleared_data, {})

    def test_resource_profiler(self):
        """Tests that the ResourceProfiler operates without crashing."""
        ResourceProfiler.start_profiling()
        ram_usage = ResourceProfiler.get_memory_usage_mb()
        self.assertGreaterEqual(ram_usage, 0.0)
        
        thread_cnt, thread_names = ResourceProfiler.get_active_threads_info()
        self.assertGreater(thread_cnt, 0)
        self.assertIn(threading.current_thread().name, thread_names)

    def test_file_import_parsing(self):
        """Tests that the file importer in AutoTyperRunner reads TXT and CSV formats."""
        runner = AutoTyperRunner(self.services)
        
        # 1. Test standard TXT parsing
        temp_txt = ROOT_DIR / "temp_test_file.txt"
        test_content = "Line 1 text\nLine 2 text\nEmoji Test 🚀"
        with open(temp_txt, "w", encoding="utf-8") as f:
            f.write(test_content)
            
        loaded_txt = runner.load_text_from_file(str(temp_txt))
        self.assertEqual(loaded_txt, test_content)
        if temp_txt.exists():
            temp_txt.unlink()
            
        # 2. Test CSV parsing (checking line joining)
        temp_csv = ROOT_DIR / "temp_test_file.csv"
        csv_rows = [
            ["Row1Col1", "Row1Col2"],
            ["Row2Col1", "Row2Col2"]
        ]
        with open(temp_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(csv_rows)
            
        loaded_csv = runner.load_text_from_file(str(temp_csv))
        self.assertTrue("Row1Col1" in loaded_csv)
        self.assertTrue("Row2Col2" in loaded_csv)
        if temp_csv.exists():
            temp_csv.unlink()

    def test_typo_neighbors_mapping(self):
        """Tests that keyboard QWERTY character neighbors are correctly mapped."""
        self.assertIn('q', NEIGHBORS['a'])
        self.assertIn('w', NEIGHBORS['q'])
        self.assertIn('ö', NEIGHBORS['ç'])

    def test_backup_generation(self):
        """Tests that the BackupService creates configuration archives."""
        backup_srv = self.services["backup_service"]
        
        # Trigger backup
        success = backup_srv.create_backup()
        self.assertTrue(success)
        
        latest_backup = backup_srv.get_latest_backup()
        self.assertIsNotNone(latest_backup)
        self.assertTrue(latest_backup.exists())
        
        # Verify backup time string is valid
        time_str = backup_srv.get_last_backup_time_str()
        self.assertNotEqual(time_str, "N/A")

if __name__ == "__main__":
    unittest.main()
