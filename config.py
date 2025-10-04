# config.py
import json
import os
import logging
from error_logger import setup_global_logger

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "language": "de",
    "gta_path": "",
    "mic_device": "",
    "log_level": "INFO"
}

def load_config():
    """Lädt die Konfiguration"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
        except Exception as e:
            print(f"Fehler beim Laden der Konfiguration: {e}")
            config = DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()
        save_config(config)
    
    log_level = getattr(logging, config.get("log_level", "INFO"))
    
    # Logger einrichten
    setup_global_logger(log_level=log_level)
    
    logger = get_logger()
    logger.log_system_info()
    logger.log_success("Konfiguration geladen")
    logger.log_debug(f"Log Level: {config.get('log_level', 'INFO')}")
    
    return config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logger = get_logger()
        logger.log_success("Konfiguration gespeichert")
        return True
    except Exception as e:
        logger = get_logger()
        logger.log_error("Fehler beim Speichern der Konfiguration", exc_info=e)
        return False

def get_logger():
    from error_logger import get_logger as get_global_logger
    return get_global_logger()