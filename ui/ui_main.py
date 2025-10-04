# ui_main.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QTextEdit,
    QFileDialog, QMessageBox, QApplication, QProgressBar,
    QGroupBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QIcon
from logic import find_gta_path, get_default_microphone, set_registry, patch_by_relative_path, restore_backups, fix_connection_issue, delete_localprefs, fix_windows_compatibility
from validators import validate_redux_folder
from translations import LANGUAGES
import logging
import os
import sys

class PatchThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool)
    file_progress = pyqtSignal(str)

    def __init__(self, redux_path, gta_path):
        super().__init__()
        self.redux_path = redux_path
        self.gta_path = gta_path

    def run(self):
        self.log.emit("[INFO] Patch gestartet...")
        try:
            def progress_logger(msg):
                self.log.emit(msg)
                if "Datei gepatcht:" in msg:
                    self.file_progress.emit(msg.split("Datei gepatcht:")[1].strip())
            
            patched = patch_by_relative_path(self.gta_path, self.redux_path, logger_callback=progress_logger)
            self.log.emit(f"[INFO] {len(patched)} Datei(en) gepatcht.")
            self.finished.emit(True)
        except Exception as e:
            self.log.emit(f"[ERROR] Fehler: {e}")
            logging.error(f"Patch Fehler: {e}")
            self.finished.emit(False)

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.language = config.get("language", "de")
        self.lang = LANGUAGES[self.language]
        self.setWindowTitle(self.lang["title"])
        self.setMinimumSize(700, 600)
        self.redux_path = ""
        self.gta_path = config.get("gta_path", "")
        self.setup_dark_theme()
        self.init_ui()

    def setup_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1a1a1a, stop: 1 #2d2d2d);
                color: #ffffff;
            }
        """)

    def init_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        self.header_label = QLabel("RAGEMP TOOLBOX")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y1: 0,
                    stop: 0 #0078d7, stop: 0.5 #106ebe, stop: 1 #005a9e);
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(self.header_label)

        # Language Button
        lang_layout = QHBoxLayout()
        self.lang_switch_btn = QPushButton("🌐 Language: EN/DE")
        self.lang_switch_btn.setProperty("special", "true")
        self.lang_switch_btn.clicked.connect(self.toggle_language)
        lang_layout.addWidget(self.lang_switch_btn)
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)

        # GTA Path Group
        self.gta_group = QGroupBox("🎮 GTA V Installation")
        gta_layout = QVBoxLayout()
        
        gta_path_layout = QHBoxLayout()
        self.gta_edit = QLineEdit(self.gta_path)
        self.gta_edit.setPlaceholderText("Pfad zu GTA V Installation...")
        self.gta_auto_btn = QPushButton("🔍 Auto-Detect")
        self.gta_auto_btn.setProperty("special", "true")
        self.gta_auto_btn.clicked.connect(self.auto_detect_gta)
        
        gta_path_layout.addWidget(self.gta_edit)
        gta_path_layout.addWidget(self.gta_auto_btn)
        gta_layout.addLayout(gta_path_layout)
        
        self.gta_save_btn = QPushButton("💾 GTA-Pfad speichern")
        self.gta_save_btn.clicked.connect(self.save_gta_path)
        gta_layout.addWidget(self.gta_save_btn)
        
        self.gta_group.setLayout(gta_layout)
        main_layout.addWidget(self.gta_group)

        # Microphone Group
        self.mic_group = QGroupBox("🎤 Mikrofon Einstellungen")
        mic_layout = QVBoxLayout()
        
        mic_combo_layout = QHBoxLayout()
        self.mic_combo = QComboBox()
        self.mic_combo.setMinimumWidth(200)
        self.mic_detect_btn = QPushButton("🔊 Mikrofone erkennen")
        self.mic_detect_btn.setProperty("special", "true")
        self.mic_detect_btn.clicked.connect(self.detect_mics)
        
        mic_combo_layout.addWidget(self.mic_combo)
        mic_combo_layout.addWidget(self.mic_detect_btn)
        mic_layout.addLayout(mic_combo_layout)
        
        self.mic_save_btn = QPushButton("💾 Mikrofon speichern")
        self.mic_save_btn.clicked.connect(self.save_mic)
        mic_layout.addWidget(self.mic_save_btn)
        
        self.mic_group.setLayout(mic_layout)
        main_layout.addWidget(self.mic_group)

        # Redux Patcher Group
        self.redux_group = QGroupBox("🎨 Redux Patcher")
        redux_layout = QVBoxLayout()
        
        self.redux_choose_btn = QPushButton("📁 Patch-Ordner wählen")
        self.redux_choose_btn.setProperty("special", "true")
        self.redux_choose_btn.clicked.connect(self.choose_redux_folder)
        redux_layout.addWidget(self.redux_choose_btn)
        
        patch_buttons_layout = QHBoxLayout()
        self.patch_btn = QPushButton("⚡ Patch Redux")
        self.patch_btn.setProperty("special", "true")
        self.patch_btn.clicked.connect(self.start_patch)
        
        self.restore_btn = QPushButton("🔄 Backup zurücksetzen")
        self.restore_btn.setProperty("danger", "true")
        self.restore_btn.clicked.connect(self.start_restore)
        
        patch_buttons_layout.addWidget(self.patch_btn)
        patch_buttons_layout.addWidget(self.restore_btn)
        redux_layout.addLayout(patch_buttons_layout)
        
        self.redux_group.setLayout(redux_layout)
        main_layout.addWidget(self.redux_group)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 10px;
                background-color: #2d2d2d;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00ff88, stop: 0.5 #00cc66, stop: 1 #009944);
                border-radius: 8px;
                border: 1px solid #00cc66;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Current File Label
        self.current_file_label = QLabel("")
        self.current_file_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        self.current_file_label.setVisible(False)
        main_layout.addWidget(self.current_file_label)

        # Fixes Group
        self.fixes_group = QGroupBox("🔧 Fehlerbehebungen")
        fixes_layout = QVBoxLayout()
        
        self.connection_fix_btn = QPushButton("🌐 Connection Fix")
        self.connection_fix_btn.setProperty("special", "true")
        self.connection_fix_btn.clicked.connect(self.fix_connection)
        fixes_layout.addWidget(self.connection_fix_btn)
        
        self.localprefs_fix_btn = QPushButton("🗑️ LocalPrefs Löschen")
        self.localprefs_fix_btn.setProperty("danger", "true")
        self.localprefs_fix_btn.clicked.connect(self.delete_localprefs)
        fixes_layout.addWidget(self.localprefs_fix_btn)
        
        self.compatibility_fix_btn = QPushButton("⚙️ Windows Kompatibilitäts-Fix (Windows 7/8 Problem)")
        self.compatibility_fix_btn.setProperty("special", "true")
        self.compatibility_fix_btn.clicked.connect(self.fix_windows_compatibility)
        fixes_layout.addWidget(self.compatibility_fix_btn)
        
        self.fixes_group.setLayout(fixes_layout)
        main_layout.addWidget(self.fixes_group)

        # Log Output
        self.log_group = QGroupBox("📋 Log-Ausgabe")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(200)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                border: 2px solid #333333;
                border-radius: 8px;
                color: #00ff00;
                font-family: "Consolas", monospace;
                font-size: 10px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_output)
        self.log_group.setLayout(log_layout)
        main_layout.addWidget(self.log_group)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.detect_mics()

    def toggle_language(self):
        # Sprache umschalten
        self.language = "en" if self.language == "de" else "de"
        self.lang = LANGUAGES[self.language]
        self.config["language"] = self.language
        
        # Config speichern
        from config import save_config
        save_config(self.config)
        
        # UI Texte aktualisieren
        self.update_ui_texts()
        
        # Log Nachricht
        self.log_output.append(f"🌐 Sprache geändert zu: {'Englisch' if self.language == 'en' else 'Deutsch'}")

    def update_ui_texts(self):
        """Aktualisiert alle UI-Texte basierend auf der aktuellen Sprache"""
        try:
            # Fenstertitel
            self.setWindowTitle(self.lang["title"])
            
            # Header
            self.header_label.setText(self.lang["title"])
            
            # Language Button Text
            self.lang_switch_btn.setText(f"🌐 {'Sprache: DE/EN' if self.language == 'de' else 'Language: EN/DE'}")
            
            # GTA Gruppe
            self.gta_group.setTitle("🎮 " + self.lang["gta_label"].replace(":", ""))
            self.gta_edit.setPlaceholderText("Path to GTA V installation..." if self.language == "en" else "Pfad zu GTA V Installation...")
            self.gta_auto_btn.setText("🔍 " + self.lang["auto_detect"])
            self.gta_save_btn.setText("💾 " + self.lang["save"])
            
            # Mikrofon Gruppe
            self.mic_group.setTitle("🎤 " + ("Microphone Settings" if self.language == "en" else "Mikrofon Einstellungen"))
            self.mic_detect_btn.setText("🔊 " + self.lang["mic_detect"])
            self.mic_save_btn.setText("💾 " + self.lang["mic_save"])
            
            # Redux Gruppe
            self.redux_group.setTitle("🎨 " + ("Redux Patcher" if self.language == "en" else "Redux Patcher"))
            self.redux_choose_btn.setText("📁 " + self.lang["choose_patch"])
            self.patch_btn.setText("⚡ " + self.lang["patch_btn"])
            self.restore_btn.setText("🔄 " + self.lang["restore_button"])
            
            # Fixes Gruppe
            self.fixes_group.setTitle("🔧 " + self.lang["fix_label"])
            self.connection_fix_btn.setText("🌐 " + self.lang["connection_fix_btn"])
            self.localprefs_fix_btn.setText("🗑️ " + self.lang["localprefs_fix_btn"])
            self.compatibility_fix_btn.setText("⚙️ " + self.lang["compatibility_fix_btn"])
            
            # Log Gruppe
            self.log_group.setTitle("📋 " + ("Log Output" if self.language == "en" else "Log-Ausgabe"))
            
        except Exception as e:
            self.log_output.append(f"❌ Fehler beim Sprachwechsel: {e}")

    def fix_connection(self):
        self.log_output.append("🔧 " + ("Starting Connection Fix..." if self.language == "en" else "Starte Connection Fix..."))
        success = fix_connection_issue(self.log_output.append)
        if success:
            QMessageBox.information(self, self.lang["success"], 
                                   "✅ " + ("Connection Fix successful!\n\nChannel set to '11_test_1907'.\nRestart RAGEMP to apply changes." 
                                           if self.language == "en" else 
                                           "Connection Fix erfolgreich!\n\nDer Channel wurde auf '11_test_1907' gesetzt.\nStarten Sie RAGEMP neu um die Änderung zu übernehmen."))
        else:
            QMessageBox.warning(self, self.lang["info"], 
                               "⚠️ " + ("Connection Fix could not be completed.\n\nCheck log for details." 
                                       if self.language == "en" else 
                                       "Connection Fix konnte nicht durchgeführt werden.\n\nÜberprüfen Sie die Log-Ausgabe für Details."))

    def delete_localprefs(self):
        self.log_output.append("🗑️ " + ("Starting LocalPrefs cleanup..." if self.language == "en" else "Starte LocalPrefs Bereinigung..."))
        success = delete_localprefs(self.log_output.append)
        if success:
            QMessageBox.information(self, self.lang["success"], 
                                   "✅ " + ("LocalPrefs cleanup completed!\n\nSystem is clean." 
                                           if self.language == "en" else 
                                           "LocalPrefs Bereinigung abgeschlossen!\n\nSystem ist bereinigt."))
        else:
            QMessageBox.warning(self, self.lang["info"], 
                               "⚠️ " + ("LocalPrefs cleanup failed.\n\nCheck log for details." 
                                       if self.language == "en" else 
                                       "LocalPrefs Bereinigung fehlgeschlagen.\n\nÜberprüfen Sie die Log-Ausgabe für Details."))

    def fix_windows_compatibility(self):
        self.log_output.append("⚙️ " + ("Starting Windows Compatibility Fix..." if self.language == "en" else "Starte Windows Kompatibilitäts-Fix..."))
        success = fix_windows_compatibility(self.log_output.append)
        if success:
            QMessageBox.information(self, self.lang["success"], 
                                   "✅ " + ("Windows Compatibility Fix completed!\n\nRestart recommended." 
                                           if self.language == "en" else 
                                           "Windows Kompatibilitäts-Fix durchgeführt!\n\nNeustart empfohlen."))
        else:
            QMessageBox.warning(self, self.lang["info"], 
                               "⚠️ " + ("Windows Compatibility Fix failed.\n\nAdmin rights required?" 
                                       if self.language == "en" else 
                                       "Kompatibilitäts-Fix fehlgeschlagen.\n\nAdmin-Rechte benötigt?"))

    def start_restore(self):
        gta_path = self.gta_edit.text().strip()
        if not os.path.isdir(gta_path):
            QMessageBox.warning(self, self.lang["error"], "❌ " + self.lang["invalid_path"])
            return

        self.log_output.append("[INFO] 🔄 " + ("Starting backup restoration..." if self.language == "en" else "Backup-Rücksetzung gestartet..."))
        try:
            restored = restore_backups(gta_path, logger_callback=self.log_output.append)
            if restored:
                QMessageBox.information(self, self.lang["success"], 
                                       f"✅ {len(restored)} " + ("backup(s) restored." if self.language == "en" else "Backup(s) zurückgespielt."))
            else:
                QMessageBox.information(self, self.lang["info"], 
                                       "ℹ️ " + ("No backups found to restore." if self.language == "en" else "Keine Backups zum Zurücksetzen gefunden."))
        except Exception as e:
            self.log_output.append(f"[ERROR] ❌ " + ("Error:" if self.language == "en" else "Fehler:") + f" {e}")
            QMessageBox.critical(self, self.lang["error"], 
                               f"❌ " + ("Error during restoration:" if self.language == "en" else "Fehler beim Zurücksetzen:") + f" {e}")    

    def auto_detect_gta(self):
        path = find_gta_path()
        if path:
            self.gta_edit.setText(path)
            self.log_output.append(f"[INFO] ✅ {self.lang['gta_found']} {path}")
        else:
            self.log_output.append("[WARN] ❌ " + ("GTA path not found." if self.language == "en" else "GTA Pfad nicht gefunden."))

    def save_gta_path(self):
        path = self.gta_edit.text().strip()
        if not os.path.isfile(os.path.join(path, "GTA5.exe")):
            QMessageBox.warning(self, self.lang["error"], self.lang["invalid_path"])
            return
        self.config["gta_path"] = path
        from config import save_config
        save_config(self.config)
        set_registry("GTAPath", path)
        QMessageBox.information(self, self.lang["success"], "✅ " + self.lang["success_gta"])

    def detect_mics(self):
        self.mic_combo.clear()
        from logic import list_microphones
        mics = list_microphones()
        self.mic_combo.addItems(mics)
        default_mic = get_default_microphone()
        if default_mic and default_mic in mics:
            index = mics.index(default_mic)
            self.mic_combo.setCurrentIndex(index)

    def save_mic(self):
        mic = self.mic_combo.currentText()
        self.config["mic_device"] = mic
        from config import save_config
        save_config(self.config)
        set_registry("MicDevice", mic)
        QMessageBox.information(self, self.lang["success"], f"✅ {self.lang['mic_found']} {mic}")

    def choose_redux_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.lang["select_folder"])
        if folder and validate_redux_folder(folder):
            self.redux_path = folder
            self.log_output.append(f"[INFO] 📁 " + ("Redux folder selected:" if self.language == "en" else "Redux-Ordner gewählt:") + f" {folder}")
        else:
            QMessageBox.warning(self, self.lang["error"], "❌ " + ("Invalid Redux folder." if self.language == "en" else "Ungültiger Redux-Ordner."))

    def start_patch(self):
        if not self.redux_path:
            QMessageBox.warning(self, self.lang["error"], "❌ " + ("Redux folder not set." if self.language == "en" else "Redux-Ordner nicht gesetzt."))
            return
        gta_path = self.gta_edit.text().strip()
        if not os.path.isdir(gta_path):
            QMessageBox.warning(self, self.lang["error"], "❌ " + self.lang["invalid_path"])
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.current_file_label.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.patch_thread = PatchThread(self.redux_path, gta_path)
        self.patch_thread.log.connect(self.log_output.append)
        self.patch_thread.file_progress.connect(self.update_current_file)
        self.patch_thread.finished.connect(self.on_patch_finished)
        self.patch_thread.start()
        self.log_output.append("🚀 " + self.lang["patch_started"])

    def update_current_file(self, filename):
        text = f"Current file: {filename}" if self.language == "en" else f"Aktuelle Datei: {filename}"
        self.current_file_label.setText(text)

    @pyqtSlot(bool)
    def on_patch_finished(self, success):
        self.progress_bar.setVisible(False)
        self.current_file_label.setVisible(False)
        
        if success:
            QMessageBox.information(self, self.lang["success"], "✅ " + self.lang["patch_finished"])
            logging.info("Redux patch erfolgreich.")
        else:
            QMessageBox.critical(self, self.lang["error"], "❌ " + ("Patch failed." if self.language == "en" else "Patch fehlgeschlagen."))