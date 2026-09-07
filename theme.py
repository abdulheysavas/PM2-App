# -*- coding: utf-8 -*-
"""Visual theme for pm2-app — "black → shadow → iron → white" monochrome look."""

# ---- palette ---------------------------------------------------------------
BLACK_0 = "#070708"     # deepest black (window top)
BLACK_1 = "#0d0d10"     # window bottom
IRON_0 = "#15161a"      # panel surface
IRON_1 = "#1b1d22"      # panel hover
IRON_2 = "#20232a"      # card hover / pressed
STEEL_0 = "#23262d"     # borders
STEEL_1 = "#34373f"     # borders hover
TEXT = "#f6f7f8"        # white text
TEXT_DIM = "#a6abb5"    # silver
TEXT_FAINT = "#666c77"  # faint gray
GLOSS_A = "#ffffff"     # glossy primary
GLOSS_B = "#b9bfc9"
OK = "#2fd08a"
OK_DIM = "#7fe3b4"
WARN = "#f2b04a"
ERR = "#ef5350"
ERR_DIM = "#f29694"

QSS = """
* { font-family: "Ubuntu", "Noto Sans Arabic UI", "Noto Sans", "DejaVu Sans", sans-serif; }
QMainWindow, QWidget#centralRoot { background: transparent; }

/* ---------- root: black -> iron ---------- */
#centralRoot {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0a0a0c, stop:1 #121317);
}
#pageBody { background: transparent; }

/* ---------- generic buttons ---------- */
QPushButton {
    background: rgba(255,255,255,0.045);
    color: #e8eaee;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 9px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton:hover { background: rgba(255,255,255,0.10); border-color: rgba(255,255,255,0.20); }
QPushButton:pressed { background: rgba(255,255,255,0.03); }
QPushButton:disabled { color: #5a5f69; background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.04); }

/* glossy white primary button */
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #c3c9d2);
    color: #101114;
    border: none;
    border-radius: 10px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 800;
}
QPushButton#primaryBtn:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #d7dce3); }
QPushButton#primaryBtn:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d9dde4, stop:1 #aeb4be); }
QPushButton#primaryBtn:disabled { background: rgba(255,255,255,0.25); color: rgba(0,0,0,0.55); }

QPushButton#ghostBtn { background: transparent; border: 1px solid #3a3e47; color: #c9cdd5; }
QPushButton#ghostBtn:hover { background: rgba(255,255,255,0.07); border-color: #5a5f6a; }

QPushButton#dangerBtn { background: rgba(239,83,80,0.12); color: #f7a09e; border: 1px solid rgba(239,83,80,0.3); }
QPushButton#dangerBtn:hover { background: rgba(239,83,80,0.22); }

QPushButton#okBtn { background: rgba(47,208,138,0.12); color: #9beac4; border: 1px solid rgba(47,208,138,0.32); }
QPushButton#okBtn:hover { background: rgba(47,208,138,0.22); }

/* small action button inside app cards */
QPushButton.cardBtn {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 7px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: 600;
    color: #ccd1d9;
}
QPushButton.cardBtn:hover { background: rgba(255,255,255,0.12); }
QPushButton.cardBtn[variant="danger"]:hover { background: rgba(239,83,80,0.25); color: #ffd2d0; border-color: rgba(239,83,80,0.45); }
QPushButton.cardBtn[variant="ok"]:hover { background: rgba(47,208,138,0.22); color: #bff2d9; border-color: rgba(47,208,138,0.45); }

/* ---------- language switch ---------- */
#langShell {
    background: rgba(0,0,0,0.45);
    border: 1px solid #2c2f36;
    border-radius: 12px;
}
QPushButton.langBtn {
    background: transparent; border: none; color: #858b95;
    border-radius: 9px; padding: 5px 12px; font-size: 12px; font-weight: 600;
}
QPushButton.langBtn:hover { color: #e5e7eb; }
QPushButton.langBtn[active="true"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #c9ced6);
    color: #0b0c0e;
}

/* ---------- status chip (PM2) ---------- */
#pm2Chip {
    background: rgba(47,208,138,0.1);
    border: 1px solid rgba(47,208,138,0.3);
    border-radius: 12px;
    padding: 4px 12px;
    color: #9beac4;
    font-size: 12px;
    font-weight: 700;
}
#pm2Chip[state="bad"] { background: rgba(239,83,80,0.1); border-color: rgba(239,83,80,0.35); color: #f7a09e; }

/* ---------- labels ---------- */
#bigTitle { color: #ffffff; font-size: 21px; font-weight: 800; letter-spacing: 0.3px; }
#subTitle { color: #878d98; font-size: 12px; }
#sectionTitle { color: #f0f2f4; font-size: 13px; font-weight: 700; }
#mutedLabel { color: #7d838e; font-size: 11px; }
#whiteLabel { color: #f0f2f5; font-size: 12px; }
#appNameLabel { color: #ffffff; font-size: 14px; font-weight: 700; }
#appPathLabel { color: #6f757f; font-size: 10.5px; }

/* ---------- drop zone (glowing silver) ---------- */
#dropZone {
    background: rgba(255,255,255,0.025);
    border: 2px dashed rgba(220,225,235,0.45);
    border-radius: 18px;
}
#dropZone[active="true"] {
    background: rgba(255,255,255,0.09);
    border: 2px solid #ffffff;
}
#dropTitle { color: #f2f4f6; font-size: 16px; font-weight: 700; }
#dropSub { color: #8b919c; font-size: 12px; }
QLabel#dropIcon { font-size: 30px; color: #d7dbe1; }

/* ---------- cards & panels: iron ---------- */
#panel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255,255,255,0.035), stop:1 rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
}
.appcard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #17181d, stop:1 #141519);
    border: 1px solid #282b32;
    border-radius: 13px;
}
.appcard:hover { background: #1b1d23; border-color: #3a3e48; }
.appcard[selected="true"] { border: 1px solid #e8eaee; background: #1d1f25; }

/* status pills */
QLabel#statusPill {
    border-radius: 9px; padding: 2px 9px; font-size: 11px; font-weight: 700;
}
QLabel#statusPill[state="online"] { background: rgba(47,208,138,0.13); color: #9beac4; }
QLabel#statusPill[state="stopped"] { background: rgba(150,157,168,0.15); color: #aab0ba; }
QLabel#statusPill[state="errored"] { background: rgba(239,83,80,0.14); color: #f8a6a4; }
QLabel#statusPill[state="busy"] { background: rgba(242,176,74,0.13); color: #f8cd8d; }
QLabel#statusPill[state="unknown"] { background: rgba(150,157,168,0.1); color: #7d838e; }

QLabel.metaChip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 7px;
    padding: 1px 8px;
    color: #a2a8b2;
    font-size: 10.5px;
}

/* boot switch pill */
#bootPill {
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 700;
}
#bootPill[state="on"] { background: rgba(47,208,138,0.13); border: 1px solid rgba(47,208,138,0.35); color: #9beac4; }
#bootPill[state="off"] { background: rgba(255,255,255,0.05); border: 1px solid #33373f; color: #8d939e; }

/* ---------- console ---------- */
#console {
    background: #060607;
    border: 1px solid #22252b;
    border-radius: 10px;
    color: #c9ccd2;
    font-family: "Ubuntu Mono", "DejaVu Sans Mono", monospace;
    font-size: 11.5px;
    selection-background-color: #5a5f6a;
    padding: 4px;
}
#consoleEmpty {
    color: #5d636d;
    font-size: 12px;
}

/* ---------- scrollbars ---------- */
QScrollBar:vertical {
    background: transparent; width: 10px; margin: 2px;
}
QScrollBar::handle:vertical {
    background: rgba(255,255,255,0.14); border-radius: 5px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.25); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: rgba(255,255,255,0.14); border-radius: 5px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }

/* ---------- input ---------- */
QLineEdit {
    background: #101114; border: 1px solid #2a2d34; border-radius: 8px;
    color: #eef0f3; padding: 5px 10px; font-size: 12px;
    selection-background-color: #5a5f6a;
}
QLineEdit:focus { border-color: #e8eaee; }

/* ---------- dialog / message box ---------- */
QMessageBox { background: #15161a; }
QMessageBox QLabel { color: #f0f2f5; font-size: 12.5px; }
QMessageBox QPushButton { min-width: 84px; }
QDialog#stdDialog { background: #121317; }

/* QToolTip */
QToolTip {
    background: #1b1d22; color: #eef0f3;
    border: 1px solid #3a3e47; border-radius: 6px; padding: 4px 8px; font-size: 11px;
}

QCheckBox { color: #e0e3e8; font-size: 12px; spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 5px; border: 1px solid #3f434c; background: #101114; }
QCheckBox::indicator:checked { background: #e8eaee; border-color: #e8eaee; }
"""
