from PySide6.QtGui import QPalette, QColor

def apply_theme(app, theme_name):
    if theme_name == "dark":
        # Etwas hellere Farben
        dark_colors = {
            QPalette.Window: QColor(70, 70, 70),
            QPalette.WindowText: QColor(240, 240, 240),
            QPalette.Base: QColor(60, 60, 60),
            QPalette.AlternateBase: QColor(85, 85, 85),
            QPalette.ToolTipBase: QColor(255, 255, 255),
            QPalette.ToolTipText: QColor(0, 0, 0),
            QPalette.Text: QColor(230, 230, 230),
            QPalette.Button: QColor(70, 70, 70),
            QPalette.ButtonText: QColor(240, 3, 240),
            QPalette.BrightText: QColor(255, 80, 80),
            QPalette.Highlight: QColor(160, 90, 210),
            QPalette.HighlightedText: QColor(0, 0, 0),
        }
        palette = QPalette()
        for role, color in dark_colors.items():
            palette.setColor(role, color)
        app.setPalette(palette)
    else:
        app.setPalette(app.style().standardPalette())
