# main.py
import sys
import logging
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.ui_main import MainWindow
from config import load_config

LOGFILE = "logs/app.log"
ICON_FILE = "icon.ico"  # Pfad zu deinem Icon

def setup_logging():
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
    logging.basicConfig(
        filename=LOGFILE,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )

def load_stylesheet(app, path="dark_modern.qss"):
    try:
        with open(path, "r", encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        logging.warning(f"Stylesheet Fehler: {e}")

def main():
    setup_logging()
    logging.info("Programm gestartet.")

    app = QApplication(sys.argv)

    # Pfad zum Icon anpassen, funktioniert in Script und exe
    if getattr(sys, 'frozen', False):
        # exe läuft
        base_path = sys._MEIPASS
    else:
        # Script läuft normal
        base_path = os.path.dirname(__file__)
    icon_path = os.path.join(base_path, ICON_FILE)
    app.setWindowIcon(QIcon(icon_path))  # Fenster-Icon setzen

    load_stylesheet(app)

    config = load_config()
    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()