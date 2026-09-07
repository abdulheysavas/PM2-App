# -*- coding: utf-8 -*-
"""pm2-app — run & manage your bots in the background with PM2.

Usage:  python3 main.py [--lang en|ar|id]
"""

import json
import os
import sys

os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

import pm2svc  # noqa: E402
from theme import QSS  # noqa: E402

SETTINGS_PATH = os.path.join(pm2svc.CONFIG_DIR, "settings.json")


def detect_lang():
    """Chosen language: --lang flag > saved settings > system locale > English."""
    for i, arg in enumerate(sys.argv):
        if arg == "--lang" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as fh:
            saved = json.load(fh).get("lang")
        if saved:
            return saved
    except (OSError, ValueError):
        pass
    lang_env = os.environ.get("LANG", "") or os.environ.get("LC_ALL", "")
    lowered = lang_env.lower()
    if lowered.startswith("ar") or "_ar" in lowered:
        return "ar"
    if lowered.startswith("id") or lowered.startswith("in_") or "_id" in lowered:
        return "id"
    return "en"


def save_lang(lang):
    try:
        pm2svc.ensure_dirs()
        with open(SETTINGS_PATH, "w", encoding="utf-8") as fh:
            json.dump({"lang": lang}, fh, ensure_ascii=False, indent=2)
    except OSError:
        pass


def main():
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QColor, QPalette
    from PyQt6.QtWidgets import QApplication, QStyleFactory

    from i18n import LANGS
    from mainwindow import MainWindow

    lang = detect_lang()
    if lang not in LANGS:
        lang = "en"

    app = QApplication(sys.argv)
    app.setApplicationName("PM2 App")
    app.setOrganizationName("pm2-app")
    app.setStyle(QStyleFactory.create("Fusion"))

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d0d10"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#f6f7f8"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#101114"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#191a1f"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#f6f7f8"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#17181d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e6e8ec"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#e8eaee"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#0b0c0e"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1b1d22"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#f0f2f5"))
    app.setPalette(palette)

    app.setStyleSheet(QSS)
    app.setLayoutDirection(
        Qt.LayoutDirection.RightToLeft if lang == "ar"
        else Qt.LayoutDirection.LeftToRight)

    window = MainWindow(lang)

    # Persist the language whenever the user changes it.
    from PyQt6.QtWidgets import QWidget

    original = MainWindow._switch_lang

    def _switch_and_save(self, code):
        original(self, code)
        save_lang(code)

    MainWindow._switch_lang = _switch_and_save

    window.show()
    code = app.exec()
    save_lang(window.lang)
    return code


if __name__ == "__main__":
    sys.exit(main())
