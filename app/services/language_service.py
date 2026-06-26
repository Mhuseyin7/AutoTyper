import logging
from typing import Callable, Dict, Any

logger = logging.getLogger("AutoTyperPro")

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_title": "Auto Typer Pro",
        "tab_typer": "  ⌨  Auto Typer",
        "tab_clicker": "  🖱  Auto Clicker",
        "tab_macro": "  🔄  Macro Recorder",
        "tab_settings": "  ⚙  Settings",
        
        # Status Card
        "engine_typer": "Auto Typer Engine",
        "engine_clicker": "Auto Clicker Engine",
        "engine_macro": "Macro Engine",
        "trigger_shortcut": "Trigger Shortcut",
        "status_idle": "IDLE",
        "status_running": "RUNNING",
        "status_paused": "PAUSED",
        "status_error": "ERROR",
        
        # Typer Page
        "typer_header_title": "Auto Typer Dashboard",
        "typer_header_subtitle": "Automate character typing, word typing, or paste block text with human delays.",
        "typing_mode": "Typing Mode",
        "mode_simulate": "Simulate Typing",
        "mode_write": "Fast Write",
        "mode_paste": "Instant Paste",
        
        "char_delay": "Character Delay",
        "word_delay": "Word Delay",
        "line_delay": "Line Delay",
        "loop_delay": "Loop Delay",
        
        "human_like": "Human-Like Typing",
        "delay_variance": "Delay Variance (Randomness)",
        "punc_delay": "Punctuation Pause Delay",
        "spelling_error_rate": "Spelling Error Rate",
        
        "target_window": "Target Window",
        "active_window": "Active Window",
        "specific_window": "Specific Window",
        "open_windows": "Open Windows List",
        
        "iteration_count": "Iteration Count (0 = Infinite)",
        "loop_delay_sec": "Delay between iterations (seconds)",
        "start_typing": "START TYPING",
        "stop": "STOP",
        "pause": "PAUSE",
        "resume": "RESUME",
        "txt_placeholder": "Type or paste text here...",
        "import_file": "IMPORT FILE (TXT/CSV)",
        "typing_flow": "Typing Flow Mode",
        "flow_entire": "Type Entire Text",
        "flow_line": "Type Line-by-Line",
        "flow_random": "Type Random Lines",
        
        # Clicker Page
        "clicker_header_title": "Auto Clicker Dashboard",
        "clicker_header_subtitle": "Trigger rapid or structured mouse clicks at preset screen coordinates.",
        "mouse_button": "Mouse Button",
        "btn_left": "Left Click",
        "btn_right": "Right Click",
        "btn_middle": "Middle Click",
        "click_type": "Click Type",
        "type_single": "Single Click",
        "type_double": "Double Click",
        "type_triple": "Triple Click",
        "cursor_pos_mode": "Cursor Position Mode",
        "pos_follow": "Follow Mouse",
        "pos_fixed": "Fixed Coordinates",
        "pick_coords": "PICK COORDINATES",
        "click_interval": "Clicking Interval Delay",
        "hours": "Hours",
        "minutes": "Minutes",
        "seconds": "Seconds",
        "milliseconds": "Milliseconds",
        "start_clicking": "START CLICKING",
        
        # Macro Page
        "macro_header_title": "Macro Recorder & Playback",
        "macro_header_subtitle": "Record mouse movements, mouse clicks, and keystrokes, then play them back exactly.",
        "rec_filters": "Recording Filters",
        "rec_mouse": "Record Mouse Actions",
        "rec_keyboard": "Record Keyboard Events",
        "saved_macros": "Saved Macro Profiles",
        "load": "LOAD",
        "delete": "DELETE",
        "duplicate": "DUPLICATE",
        "export": "EXPORT",
        "import": "IMPORT",
        "timeline_speed": "Speed Multiplier",
        "timeline_loops": "Loops (0=Inf)",
        "timeline_delay": "Loop Delay (s)",
        "record": "RECORD (F8)",
        "stop_record": "STOP RECORD",
        "play": "PLAY BACK (F9)",
        "save_current": "SAVE CURRENT",
        "no_macros_msg": "-- No actions recorded in this session. --\n\nTips:\n- Click RECORD or press F8 to begin logging.\n- Toggle mouse/keyboard capture settings on the left.\n- Load a saved profile configuration.",
        
        # Settings Page
        "settings_header_title": "Application Settings",
        "settings_header_subtitle": "Configure global appearance profiles, change shortcut keybindings, and inspect logs.",
        "appearance": "Appearance & Styles",
        "theme_dark": "Dark Mode",
        "theme_light": "Light Mode",
        "theme_system": "System Preference",
        "autosave": "Enable Automatic Settings Save",
        "shortcuts": "Shortcut Keybindings",
        "sc_typer": "Auto Typer Start/Stop:",
        "sc_clicker": "Auto Clicker Start/Stop:",
        "sc_record": "Record Macro:",
        "sc_play": "Playback Macro:",
        "diagnostics": "Diagnostics Console",
        "refresh": "REFRESH",
        
        # Settings Upgrades
        "theme_editor": "Theme Designer",
        "color_primary": "Primary Accent:",
        "color_bg": "Panel Background:",
        "font_editor": "Font Configurator",
        "font_family": "Font Family:",
        "font_size": "Font Size:",
        "backup_system": "Backup System",
        "trigger_backup": "BACKUP NOW",
        "restore_latest": "RESTORE LATEST",
        "lang_system": "Language / Dil",
        
        # Status Bar / Extra
        "status_ready": "System Ready",
        "last_backup": "Last backup",
        "cpm": "CPM",
        "wpm": "WPM",
        "duration": "Duration",
        "chars_typed": "Typed Characters",
        "success_rate": "Success Rate",
        "total_repeats": "Repeats",
        "auto_update": "Auto Update Check",
        "check_update_btn": "CHECK FOR UPDATES",
        
        # Toast notifications
        "toast_lang_changed": "Language changed to English.",
        "toast_backup_success": "Configuration backup successfully completed.",
        "toast_backup_restored": "Backup successfully restored! Reloading application...",
        "toast_save_success": "Saved successfully.",
        "toast_no_update": "You are running the latest version."
    },
    "tr": {
        "app_title": "Auto Typer Pro",
        "tab_typer": "  ⌨  Yazıcı",
        "tab_clicker": "  🖱  Tıklayıcı",
        "tab_macro": "  🔄  Makro Kaydedici",
        "tab_settings": "  ⚙  Ayarlar",
        
        # Status Card
        "engine_typer": "Yazıcı Motoru",
        "engine_clicker": "Tıklayıcı Motoru",
        "engine_macro": "Makro Motoru",
        "trigger_shortcut": "Tetikleyici Kısayol",
        "status_idle": "BOŞTA",
        "status_running": "ÇALIŞIYOR",
        "status_paused": "DURAKLATILDI",
        "status_error": "HATA",
        
        # Typer Page
        "typer_header_title": "Otomatik Yazıcı Paneli",
        "typer_header_subtitle": "Karakter, kelime yazımını otomatikleştirin veya insan gecikmesiyle metin yapıştırın.",
        "typing_mode": "Yazım Modu",
        "mode_simulate": "Yazımı Simüle Et",
        "mode_write": "Hızlı Yaz",
        "mode_paste": "Anında Yapıştır",
        
        "char_delay": "Karakter Gecikmesi",
        "word_delay": "Kelime Gecikmesi",
        "line_delay": "Satır Gecikmesi",
        "loop_delay": "Tekrar Gecikmesi",
        
        "human_like": "İnsan Benzeri Yazım",
        "delay_variance": "Gecikme Varyansı (Rastgelelik)",
        "punc_delay": "Noktalama İşareti Gecikmesi",
        "spelling_error_rate": "Yazım Hatası Oranı",
        
        "target_window": "Hedef Pencere",
        "active_window": "Aktif Pencere",
        "specific_window": "Belirli Pencere",
        "open_windows": "Açık Pencereler Listesi",
        
        "iteration_count": "Tekrar Sayısı (0 = Sonsuz)",
        "loop_delay_sec": "Tekrarlar arası gecikme (saniye)",
        "start_typing": "YAZMAYA BAŞLA",
        "stop": "DURDUR",
        "pause": "DURAKLAT",
        "resume": "DEVAM ET",
        "txt_placeholder": "Metni buraya yazın veya yapıştırın...",
        "import_file": "DOSYADAN AKTAR (TXT/CSV)",
        "typing_flow": "Yazım Akış Modu",
        "flow_entire": "Tüm Metni Yaz",
        "flow_line": "Satır Satır Yaz",
        "flow_random": "Rastgele Satır Yaz",
        
        # Clicker Page
        "clicker_header_title": "Otomatik Tıklayıcı Paneli",
        "clicker_header_subtitle": "Önceden ayarlanmış ekran koordinatlarında hızlı veya yapılandırılmış fare tıklamaları yapın.",
        "mouse_button": "Fare Düğmesi",
        "btn_left": "Sol Tık",
        "btn_right": "Sağ Tık",
        "btn_middle": "Orta Tık",
        "click_type": "Tıklama Türü",
        "type_single": "Tek Tıklama",
        "type_double": "Çift Tıklama",
        "type_triple": "Üçlü Tıklama",
        "cursor_pos_mode": "İmleç Pozisyon Modu",
        "pos_follow": "Fareyi Takip Et",
        "pos_fixed": "Sabit Koordinatlar",
        "pick_coords": "KOORDİNAT SEÇ",
        "click_interval": "Tıklama Aralığı Gecikmesi",
        "hours": "Saat",
        "minutes": "Dakika",
        "seconds": "Saniye",
        "milliseconds": "Milisaniye",
        "start_clicking": "TIKLAMAYI BAŞLAT",
        
        # Macro Page
        "macro_header_title": "Makro Kayıt & Oynatma",
        "macro_header_subtitle": "Fare hareketlerini, tıklamalarını ve klavye tuşlarını kaydedin ve tam olarak oynatın.",
        "rec_filters": "Kayıt Filtreleri",
        "rec_mouse": "Fare Hareketlerini Kaydet",
        "rec_keyboard": "Klavye Tuşlarını Kaydet",
        "saved_macros": "Kayıtlı Makro Profilleri",
        "load": "YÜKLE",
        "delete": "SİL",
        "duplicate": "ÇOĞALT",
        "export": "DIŞA AKTAR",
        "import": "İÇE AKTAR",
        "timeline_speed": "Hız Çarpanı",
        "timeline_loops": "Tekrar (0=Sonsuz)",
        "timeline_delay": "Tekrar Gecikmesi (sn)",
        "record": "KAYDET (F8)",
        "stop_record": "KAYDI DURDUR",
        "play": "OYNAT (F9)",
        "save_current": "GÜNCELİ KAYDET",
        "no_macros_msg": "-- Bu oturumda hiçbir işlem kaydedilmedi. --\n\nİpuçları:\n- Kayda başlamak için KAYDET veya F8'e basın.\n- Soldan fare/klavye yakalama ayarlarını değiştirin.\n- Kayıtlı bir profil yapılandırması yükleyin.",
        
        # Settings Page
        "settings_header_title": "Uygulama Ayarları",
        "settings_header_subtitle": "Genel görünüm profillerini yapılandırın, kısayol tuşlarını değiştirin ve günlükleri inceleyin.",
        "appearance": "Görünüm ve Stiller",
        "theme_dark": "Karanlık Tema",
        "theme_light": "Aydınlık Tema",
        "theme_system": "Sistem Tercihi",
        "autosave": "Ayarları Otomatik Kaydetmeyi Etkinleştir",
        "shortcuts": "Kısayol Tuş Kombinasyonları",
        "sc_typer": "Yazıcı Başlat/Durdur:",
        "sc_clicker": "Tıklayıcı Başlat/Durdur:",
        "sc_record": "Makro Kaydet:",
        "sc_play": "Makro Oynat:",
        "diagnostics": "Tanılama Konsolu",
        "refresh": "YENİLE",
        
        # Settings Upgrades
        "theme_editor": "Tema Tasarımcısı",
        "color_primary": "Birincil Vurgu:",
        "color_bg": "Panel Arka Planı:",
        "font_editor": "Yazı Tipi Yapılandırması",
        "font_family": "Yazı Tipi Ailesi:",
        "font_size": "Yazı Tipi Boyutu:",
        "backup_system": "Yedekleme Sistemi",
        "trigger_backup": "ŞİMDİ YEDEKLE",
        "restore_latest": "EN SON YEDEĞİ YÜKLE",
        "lang_system": "Language / Dil",
        
        # Status Bar / Extra
        "status_ready": "Sistem Hazır",
        "last_backup": "Son yedekleme",
        "cpm": "CPM",
        "wpm": "WPM",
        "duration": "Çalışma Süresi",
        "chars_typed": "Yazılan Karakter",
        "success_rate": "Başarı Oranı",
        "total_repeats": "Tekrar Sayısı",
        "auto_update": "Otomatik Güncelleme Denetimi",
        "check_update_btn": "GÜNCELLEMELERİ DENETLE",
        
        # Toast notifications
        "toast_lang_changed": "Dil Türkçe olarak değiştirildi.",
        "toast_backup_success": "Yapılandırma yedekleme işlemi başarıyla tamamlandı.",
        "toast_backup_restored": "Yedekleme başarıyla geri yüklendi! Uygulama yeniden yükleniyor...",
        "toast_save_success": "Başarıyla kaydedildi.",
        "toast_no_update": "Zaten en güncel sürümü çalıştırıyorsunuz."
    }
}

class LanguageService:
    """Provides UI string localizations and manages multi-language toggle observers."""
    def __init__(self, config_service):
        self.config = config_service
        self.current_lang = self.config.get("language") or "en"
        self.listeners: list[Callable[[], None]] = []

    def get(self, key: str) -> str:
        """Returns the localized string corresponding to the key."""
        lang_dict = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

    def set_language(self, lang_code: str):
        """Sets active language and alerts registered interface elements."""
        if lang_code not in ("en", "tr"):
            logger.warning(f"Unsupported language code requested: {lang_code}")
            return
            
        self.current_lang = lang_code
        self.config.set("language", lang_code)
        logger.info(f"Language changed globally to: {lang_code}")
        self._notify_listeners()

    def add_listener(self, callback: Callable[[], None]):
        """Binds observer widget redraw hooks."""
        if callback not in self.listeners:
            self.listeners.append(callback)

    def remove_listener(self, callback: Callable[[], None]):
        """Unbinds observer widgets."""
        if callback in self.listeners:
            self.listeners.remove(callback)

    def _notify_listeners(self):
        """Alerts all active observers to redraw labels."""
        for callback in self.listeners:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error notifying language change listener: {e}")
