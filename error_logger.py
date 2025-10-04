# error_logger.py
import logging
import sys
import os
import platform
from datetime import datetime

class CustomLogger:
    def __init__(self, name: str = "RAGEMP_Toolbox"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Verhindere doppelte Handler
        if self.logger.handlers:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File Handler
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/app.log", encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
    def log_system_info(self):
        """Systeminformationen loggen"""
        try:
            system_info = [
                "🚀 RAGEMP Toolbox Gestartet",
                f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"💻 System: {platform.system()} {platform.release()}",
                f"🐍 Python: {platform.python_version()}",
                f"📁 Arbeitsverzeichnis: {os.getcwd()}",
                f"👤 Benutzer: {os.getenv('USERNAME', 'Unknown')}",
                "─" * 40
            ]
            
            for info in system_info:
                self.logger.info(info)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Loggen der Systeminfo: {e}")
    
    def log_debug(self, message: str):
        self.logger.debug(f"🔧 {message}")
    
    def log_info(self, message: str):
        self.logger.info(f"ℹ️ {message}")
    
    def log_success(self, message: str):
        self.logger.info(f"✅ {message}")
    
    def log_warning(self, message: str):
        self.logger.warning(f"⚠️ {message}")
    
    def log_error(self, message: str, exc_info=None):
        self.logger.error(f"❌ {message}", exc_info=exc_info)
    
    def log_critical(self, message: str, exc_info=None):
        self.logger.critical(f"💥 {message}", exc_info=exc_info)

# Globale Logger Instanz
_global_logger = None

def setup_global_logger(log_level=logging.INFO):
    """Globalen Logger einrichten"""
    global _global_logger
    if _global_logger is None:
        _global_logger = CustomLogger()
        
        # Log-Level setzen
        _global_logger.logger.setLevel(log_level)
        for handler in _global_logger.logger.handlers:
            handler.setLevel(log_level)
    
    return _global_logger

def get_logger():
    """Gibt den globalen Logger zurück"""
    global _global_logger
    if _global_logger is None:
        setup_global_logger()
    return _global_logger