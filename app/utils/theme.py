import os
import sys
from PySide6.QtWidgets import QApplication


def aplicar_tema(app: QApplication):
    """Carrega e aplica o QSS no aplicativo."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    qss_path = os.path.join(base, "styles", "dark_theme.qss")

    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Arquivo de tema não encontrado.")
