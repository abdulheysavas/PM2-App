# -*- coding: utf-8 -*-
"""Main window of pm2-app."""

import os

from PyQt6.QtCore import QObject, QProcess, Qt, QThread, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QFrame, QGraphicsOpacityEffect, QHBoxLayout,
    QLabel, QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

import pm2svc
from i18n import LANG_NATIVE, LANGS, t

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(APP_DIR, "icon.png")

STATUS_KEYS = {
    "online": ("online", "status.online"),
    "stopped": ("stopped", "status.stopped"),
    "stopping": ("busy", "status.stopping"),
    "launching": ("busy", "status.launching"),
    "one-launch-status": ("busy", "status.launching"),
    "waiting-restart": ("busy", "status.launching"),
    "errored": ("errored", "status.errored"),
    "error": ("errored", "status.errored"),
}
UNKNOWN_STATUS = ("unknown", "status.unknown")


def classify_status(status):
    return STATUS_KEYS.get(status, UNKNOWN_STATUS)


def fmt_uptime(seconds):
    if seconds is None:
        return "—"
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {mins}m"
    if mins:
        return f"{mins}m {secs}s"
    return f"{secs}s"


def fmt_mem(value):
    if not isinstance(value, (int, float)) or value <= 0:
        return "—"
    value = float(value)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024:
            if unit == "B":
                return f"{value:.0f} B"
            text = f"{value:.1f} {unit}"
            return text.replace(".0 ", " ")
        value /= 1024
    return f"{value:.2f} TB"


def elide_path(path, limit=70):
    path = path or ""
    if len(path) <= limit:
        return path
    return path[:32] + "…" + path[-(limit - 33):]


def set_style_prop(widget, prop, value):
    widget.setProperty(prop, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def set_direction_recursive(widget, direction):
    widget.setLayoutDirection(direction)
    for child in widget.findChildren(QWidget):
        child.setLayoutDirection(direction)


class Toast(QLabel):
    """Fading notification floating at the top of the window."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "QLabel { background: rgba(27,29,34,0.97); color: #f4f5f7;"
            " border: 1px solid #3a3e48; border-radius: 10px; padding: 8px 18px;"
            " font-size: 12px; font-weight: 600; }"
        )
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._effect.setOpacity(0.0)
        self.hide()
        self._fade = QTimer(self)
        self._fade.setInterval(16)
        self._fade.timeout.connect(self._step)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._fade_out)
        self._op = 0.0
        self._target = 0.0

    def show_text(self, text, duration=3200):
        self.setText(text)
        self.adjustSize()
        self._op = 0.0
        self._target = 1.0
        self.show()
        self.raise_()
        self._place()
        self._fade.start()
        self._hide_timer.start(duration)

    def _place(self):
        parent = self.parentWidget()
        if parent:
            self.move((parent.width() - self.width()) // 2, 14)

    def _step(self):
        delta = 0.09 if self._target >= self._op else -0.045
        self._op = max(0.0, min(1.0, self._op + delta))
        self._effect.setOpacity(self._op)
        if abs(self._target - self._op) < 0.01:
            if self._target == 0.0:
                self._fade.stop()
                self.hide()
            else:
                self._target = 0.0

    def _fade_out(self):
        self._target = 0.0
        self._fade.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.isVisible():
            self._place()


def make_dialog(parent, title):
    dlg = QDialog(parent)
    dlg.setObjectName("stdDialog")
    dlg.setWindowTitle(title)
    dlg.setMinimumWidth(520)
    return dlg


class InstallWorker(QThread):
    """Runs `pm2svc.install_pm2_auto` off the UI thread, streaming its output."""

    line = pyqtSignal(str)
    done = pyqtSignal(bool, str, str)  # ok, detail, error-code ("" if none)

    def run(self):
        try:
            ok, detail = pm2svc.install_pm2_auto(progress=self.line.emit)
            self.done.emit(bool(ok), detail or "", "")
        except pm2svc.PM2Error as exc:
            self.done.emit(False, exc.output or "", str(exc))


class LiveLogStream(QObject):
    """Streams a process' log file lines live via `pm2 logs --raw`.

    This is a true console: new lines appear the moment PM2 writes them.
    If the stream cannot start (no PM2, daemon down) it simply dies and the
    UI falls back to reading the log files directly.
    """

    got_line = pyqtSignal(str)
    died = pyqtSignal()

    def __init__(self, pm2_bin, app_name, parent=None):
        super().__init__(parent)
        self._buffer = b""
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.proc.readyRead.connect(self._on_data)
        self.proc.finished.connect(self.died)
        self.proc.errorOccurred.connect(self.died)
        self.proc.start(pm2_bin, ["logs", app_name, "--raw", "--lines", "60"])

    def _on_data(self):
        self._buffer += bytes(self.proc.readAllStandardOutput())
        while b"\n" in self._buffer:
            raw, self._buffer = self._buffer.split(b"\n", 1)
            text = raw.decode("utf-8", errors="replace").rstrip("\r")
            if text.strip():
                self.got_line.emit(text)

    def stop(self):
        if self.proc.state() != QProcess.ProcessState.NotRunning:
            self.proc.terminate()
            if not self.proc.waitForFinished(800):
                self.proc.kill()


# ---------------------------------------------------------------------------
# Pending (ready-to-start) item
# ---------------------------------------------------------------------------
class PendingItem(QFrame):
    def __init__(self, data, on_run, on_remove, lang):
        super().__init__()
        self.setObjectName("panel")
        self.setFixedHeight(64)
        self.data = data
        self.lang = lang
        self._on_run = on_run
        self._on_remove = on_remove

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 10, 6)
        layout.setSpacing(10)

        dot = QLabel("●")
        dot.setStyleSheet("color: #dde1e8; font-size: 14px;")
        layout.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        self.name_label = QLabel()
        self.name_label.setObjectName("appNameLabel")
        self.type_label = QLabel()
        self.type_label.setObjectName("appPathLabel")
        text_col.addWidget(self.name_label)
        text_col.addWidget(self.type_label)
        layout.addLayout(text_col, 1)

        self.run_btn = QPushButton()
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setFixedHeight(30)
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(lambda: self._on_run(self))
        layout.addWidget(self.run_btn)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setToolTip(t(lang, "action.remove"))
        remove_btn.clicked.connect(lambda: self._on_remove(self))
        layout.addWidget(remove_btn)

        self._apply_texts()

    def _apply_texts(self):
        self.name_label.setText(self.data["display"])
        self.type_label.setText(t(self.lang, self.data["label_key"]))
        self.run_btn.setText(t(self.lang, "action.run"))

    def set_lang(self, lang):
        self.lang = lang
        self._apply_texts()


# ---------------------------------------------------------------------------
# Running-app card
# ---------------------------------------------------------------------------
class AppCard(QFrame):
    def __init__(self, app, lang, select_cb):
        super().__init__()
        self.setObjectName("appcard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang = lang
        self.app = app
        self._select_cb = select_cb
        self._build()
        self.update_data(app, lang)

    def _build(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 8, 8, 8)
        outer.setSpacing(12)

        left_col = QVBoxLayout()
        left_col.setSpacing(3)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        self.pill = QLabel()
        self.pill.setObjectName("statusPill")
        self.name_label = QLabel()
        self.name_label.setObjectName("appNameLabel")
        top_row.addWidget(self.pill)
        top_row.addWidget(self.name_label, 1)
        left_col.addLayout(top_row)

        self.path_label = QLabel()
        self.path_label.setObjectName("appPathLabel")
        self.path_label.setCursor(Qt.CursorShape.PointingHandCursor)
        left_col.addWidget(self.path_label)

        chips = QHBoxLayout()
        chips.setSpacing(6)
        self.chip_uptime = QLabel()
        self.chip_restarts = QLabel()
        self.chip_cpu = QLabel()
        self.chip_mem = QLabel()
        for chip in (self.chip_uptime, self.chip_restarts, self.chip_cpu, self.chip_mem):
            chip.setProperty("class", "metaChip")
            chips.addWidget(chip)
        chips.addStretch(1)
        left_col.addLayout(chips)

        outer.addLayout(left_col, 1)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        self.logs_btn = self._make_btn(None)
        self.state_btn = self._make_btn("ok")
        self.restart_btn = self._make_btn(None)
        self.delete_btn = self._make_btn("danger")
        actions.addWidget(self.logs_btn)
        actions.addWidget(self.state_btn)
        actions.addWidget(self.restart_btn)
        actions.addWidget(self.delete_btn)
        outer.addLayout(actions)

    def _make_btn(self, variant):
        btn = QPushButton()
        btn.setProperty("class", "cardBtn")
        btn.setProperty("variant", variant or "")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(28)
        return btn

    def update_data(self, app, lang=None):
        if lang:
            self.lang = lang
        self.app = app
        state_key, text_key = classify_status(app["status"])
        set_style_prop(self.pill, "state", state_key)
        self.pill.setText(t(self.lang, text_key))

        path = app["script"] or app["cwd"] or ""
        self.path_label.setText(elide_path(path))
        self.path_label.setToolTip(t(self.lang, "meta.path", path=path or "—"))

        self.chip_uptime.setText(t(self.lang, "meta.uptime") + "  " + fmt_uptime(app["uptime_sec"]))
        self.chip_restarts.setText(t(self.lang, "meta.restarts") + "  " + str(app["restarts"]))
        cpu = app["cpu"]
        self.chip_cpu.setText(t(self.lang, "meta.cpu") + "  " +
                              (f"{cpu:.1f}%" if isinstance(cpu, (int, float)) else "—"))
        self.chip_mem.setText(t(self.lang, "meta.mem") + "  " + fmt_mem(app["memory"]))

        self.logs_btn.setText(t(self.lang, "action.logs"))
        self.restart_btn.setText(t(self.lang, "action.restart"))
        self.delete_btn.setText("✕")
        self.delete_btn.setToolTip(t(self.lang, "action.delete"))
        self.setToolTip(t(self.lang, "meta.path", path=path or "—"))

        busy = state_key == "busy"
        if app["status"] == "online":
            self.state_btn.setText(t(self.lang, "action.stop"))
            self.state_btn.setEnabled(True)
        elif app["status"] == "stopped":
            self.state_btn.setText(t(self.lang, "action.run"))
            self.state_btn.setEnabled(True)
        else:
            self.state_btn.setText("")
            self.state_btn.setEnabled(False)
        self.restart_btn.setEnabled(not busy)

    def set_lang(self, lang):
        self.update_data(self.app, lang)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._select_cb(self.app["name"])
        super().mousePressEvent(event)


# ---------------------------------------------------------------------------
# Drop zone
# ---------------------------------------------------------------------------
class DropZone(QFrame):
    def __init__(self, on_files):
        super().__init__()
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self._on_files = on_files

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(0)
        lay.addStretch(1)

        icon = QLabel("⬇")
        icon.setObjectName("dropIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon)

        self.title = QLabel()
        self.title.setObjectName("dropTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.title)

        self.sub = QLabel()
        self.sub.setObjectName("dropSub")
        self.sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.sub)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 10, 0, 0)
        btn_row.addStretch(1)
        self.file_btn = QPushButton()
        self.file_btn.setObjectName("ghostBtn")
        self.file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder_btn = QPushButton()
        self.folder_btn.setObjectName("ghostBtn")
        self.folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self.file_btn)
        btn_row.addWidget(self.folder_btn)
        btn_row.addStretch(1)
        lay.addLayout(btn_row)
        lay.addStretch(1)

    def set_lang(self, lang):
        self.title.setText(t(lang, "drop.title"))
        self.sub.setText(t(lang, "drop.subtitle"))
        self.file_btn.setText(t(lang, "drop.browseFile"))
        self.folder_btn.setText(t(lang, "drop.browseFolder"))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            set_style_prop(self, "active", True)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        set_style_prop(self, "active", False)

    def dropEvent(self, event):
        set_style_prop(self, "active", False)
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        if paths:
            self._on_files(paths)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.setWindowTitle("PM2 App")
        self.setObjectName("centralRoot")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWindowIcon(QIcon(ICON_PATH))
        self._pending = []
        self._pending_widgets = []
        self._cards = {}
        self._app_cache = []
        self._selected = None
        self._last_log_text = {}
        self._log_visible_name = None
        self._boot_enabled = False
        self._pm2_ready = False
        self._install_attempted = False
        self._install_worker = None
        self._live = None          # active LiveLogStream, if any
        self._live_name = None
        self._live_ok = False
        self.resize(1080, 700)
        self.setMinimumSize(900, 600)

        self._build()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(4000)
        self.refresh_timer.timeout.connect(self._tick)
        self.log_timer = QTimer(self)
        self.log_timer.setInterval(1300)
        self.log_timer.timeout.connect(self._update_logs)
        self.log_timer.start()

        QTimer.singleShot(200, self._tick)

    # ------------------------------------------------------------------ UI
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 12, 18, 14)
        root.setSpacing(10)

        root.addLayout(self._header())

        self._drop = DropZone(self.add_paths)
        self._drop.file_btn.clicked.connect(self._browse_files)
        self._drop.folder_btn.clicked.connect(self._browse_folder)
        root.addWidget(self._drop)

        root.addWidget(self._queue_panel())
        root.addWidget(self._apps_panel(), 1)
        root.addWidget(self._console_panel())

        self._toast = Toast(self)
        self._apply_lang(self.lang)

    def _header(self):
        row = QHBoxLayout()
        row.setSpacing(10)

        logo = QLabel()
        logo.setPixmap(QIcon(ICON_PATH).pixmap(46, 46))
        logo.setFixedSize(46, 46)
        row.addWidget(logo)

        titles = QVBoxLayout()
        titles.setSpacing(1)
        big_title = QLabel("PM2 App")
        big_title.setObjectName("bigTitle")
        self.sub_title = QLabel()
        self.sub_title.setObjectName("subTitle")
        titles.addWidget(big_title)
        titles.addWidget(self.sub_title)
        row.addLayout(titles)
        row.addStretch(1)

        shell = QFrame()
        shell.setObjectName("langShell")
        shell.setFixedHeight(34)
        lang_lay = QHBoxLayout(shell)
        lang_lay.setContentsMargins(3, 3, 3, 3)
        lang_lay.setSpacing(2)
        self.lang_buttons = {}
        for code in LANGS:
            btn = QPushButton(LANG_NATIVE[code])
            btn.setObjectName("langBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, c=code: self._switch_lang(c))
            lang_lay.addWidget(btn)
            self.lang_buttons[code] = btn
        row.addWidget(shell)

        self.pm2_chip = QPushButton()
        self.pm2_chip.setObjectName("pm2Chip")
        self.pm2_chip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pm2_chip.clicked.connect(self._on_pm2_chip_click)
        row.addWidget(self.pm2_chip)

        self.boot_pill = QPushButton()
        self.boot_pill.setObjectName("bootPill")
        self.boot_pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boot_pill.setToolTip(t(self.lang, "boot.hint"))
        self.boot_pill.clicked.connect(self._on_boot_click)
        row.addWidget(self.boot_pill)

        self.help_btn = QPushButton("?")
        self.help_btn.setObjectName("ghostBtn")
        self.help_btn.setFixedSize(30, 34)
        self.help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_btn.clicked.connect(self._show_help)
        row.addWidget(self.help_btn)
        return row

    def _queue_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedHeight(82)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(6)

        head = QHBoxLayout()
        self.queue_title = QLabel()
        self.queue_title.setObjectName("sectionTitle")
        self.queue_count = QLabel()
        self.queue_count.setObjectName("mutedLabel")
        head.addWidget(self.queue_title)
        head.addWidget(self.queue_count)
        head.addStretch(1)
        self.clear_queue_btn = QPushButton()
        self.clear_queue_btn.setObjectName("ghostBtn")
        self.clear_queue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_queue_btn.clicked.connect(self.clear_pending)
        self.run_all_btn = QPushButton()
        self.run_all_btn.setObjectName("primaryBtn")
        self.run_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_all_btn.clicked.connect(self.run_all_pending)
        head.addWidget(self.clear_queue_btn)
        head.addWidget(self.run_all_btn)
        lay.addLayout(head)

        self.queue_content = QHBoxLayout()
        self.queue_content.setSpacing(8)
        lay.addLayout(self.queue_content, 1)

        self.queue_empty = QLabel()
        self.queue_empty.setObjectName("mutedLabel")
        self.queue_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.queue_empty)
        return panel

    def _apps_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(12, 8, 8, 8)
        lay.setSpacing(6)

        head = QHBoxLayout()
        self.apps_title = QLabel()
        self.apps_title.setObjectName("sectionTitle")
        self.apps_count = QLabel()
        self.apps_count.setObjectName("mutedLabel")
        head.addWidget(self.apps_title)
        head.addWidget(self.apps_count)
        head.addStretch(1)
        refresh_btn = QPushButton("↻")
        refresh_btn.setObjectName("ghostBtn")
        refresh_btn.setFixedSize(30, 28)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setToolTip(t(self.lang, "apps.refresh"))
        refresh_btn.clicked.connect(lambda: self.refresh_apps(force=True))
        head.addWidget(refresh_btn)
        lay.addLayout(head)

        # Body: a scroll list of app cards, replaced visually by the empty state.
        self.apps_scroll = QScrollArea()
        self.apps_scroll.setWidgetResizable(True)
        self.apps_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.apps_scroll.setStyleSheet("QScrollArea { background: transparent; }")
        inner = QWidget()
        inner.setObjectName("innerScroll")
        self.apps_list_lay = QVBoxLayout(inner)
        self.apps_list_lay.setContentsMargins(0, 0, 8, 0)
        self.apps_list_lay.setSpacing(8)
        self.apps_list_lay.addStretch(1)
        self.apps_scroll.setWidget(inner)
        lay.addWidget(self.apps_scroll, 1)

        self.empty_holder = QWidget()
        self.empty_holder.setObjectName("emptyHolder")
        empty_lay = QVBoxLayout(self.empty_holder)
        empty_lay.setContentsMargins(20, 16, 20, 16)
        empty_lay.setSpacing(6)
        self.empty_icon = QLabel("🤖")
        self.empty_icon.setStyleSheet("font-size: 40px;")
        self.empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_title = QLabel()
        self.empty_title.setObjectName("sectionTitle")
        self.empty_title.setStyleSheet("font-size: 14px;")
        self.empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_sub = QLabel()
        self.empty_sub.setObjectName("mutedLabel")
        self.empty_sub.setWordWrap(True)
        self.empty_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_sub.setMaximumWidth(560)
        empty_lay.addWidget(self.empty_icon)
        empty_lay.addWidget(self.empty_title)
        empty_lay.addWidget(self.empty_sub, 0, Qt.AlignmentFlag.AlignHCenter)
        empty_lay.addStretch(1)
        lay.addWidget(self.empty_holder, 1)
        return panel

    def _console_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setFixedHeight(180)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(12, 8, 8, 8)
        lay.setSpacing(6)

        head = QHBoxLayout()
        self.console_title = QLabel()
        self.console_title.setObjectName("sectionTitle")
        head.addWidget(self.console_title)
        head.addStretch(1)
        self.console_copy_btn = QPushButton()
        self.console_copy_btn.setObjectName("ghostBtn")
        self.console_copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.console_copy_btn.clicked.connect(self._copy_logs)
        self.console_clear_btn = QPushButton()
        self.console_clear_btn.setObjectName("ghostBtn")
        self.console_clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.console_clear_btn.clicked.connect(self._clear_logs)
        head.addWidget(self.console_copy_btn)
        head.addWidget(self.console_clear_btn)
        lay.addLayout(head)

        stack = QVBoxLayout()
        stack.setSpacing(0)
        self.console = QPlainTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(3000)
        self.console.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.console.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        stack.addWidget(self.console)
        self.console_empty = QLabel()
        self.console_empty.setObjectName("consoleEmpty")
        self.console_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.console_empty.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        stack.addWidget(self.console_empty)
        lay.addLayout(stack, 1)
        return panel

    # ------------------------------------------------------------------ i18n
    def _switch_lang(self, code):
        if code == self.lang:
            return
        self._apply_lang(code)
        self.refresh_apps(force=True)
        self.rebuild_pending()
        self._update_logs(force=True)

    def _apply_lang(self, lang):
        self.lang = lang
        direction = (Qt.LayoutDirection.RightToLeft if lang == "ar"
                     else Qt.LayoutDirection.LeftToRight)
        QApplication.instance().setLayoutDirection(direction)
        set_direction_recursive(self, direction)
        # Log/console text stays left-to-right in every language.
        self.console.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.console_empty.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.sub_title.setText(t(lang, "app.tagline"))
        for code, btn in self.lang_buttons.items():
            set_style_prop(btn, "active", "true" if code == lang else "false")

        self.console_copy_btn.setText(t(lang, "logs.copy"))
        self.console_clear_btn.setText(t(lang, "logs.clear"))
        self.help_btn.setToolTip(t(lang, "help.title"))
        self._drop.set_lang(lang)
        self.queue_title.setText(t(lang, "queue.title"))
        self.queue_empty.setText(t(lang, "queue.empty"))
        self.clear_queue_btn.setText(t(lang, "queue.clear"))
        self.run_all_btn.setText(t(lang, "queue.runAll"))
        self.apps_title.setText(t(lang, "apps.title"))
        self.empty_title.setText(t(lang, "apps.emptyTitle"))
        self.empty_sub.setText(t(lang, "apps.emptySub"))
        for w in self._pending_widgets:
            w.set_lang(lang)
        for card in self._cards.values():
            card.set_lang(lang)
        self._update_chip_texts()
        self._update_logs(force=True)

    def _update_chip_texts(self):
        if self._pm2_ready:
            self.pm2_chip.setText("● " + t(self.lang, "pm2.ready"))
            set_style_prop(self.pm2_chip, "state", "ok")
        else:
            self.pm2_chip.setText("● " + t(self.lang, "pm2.missing"))
            set_style_prop(self.pm2_chip, "state", "bad")
        state = "on" if self._boot_enabled else "off"
        self.boot_pill.setText(t(self.lang, "boot.label") + " · " + t(self.lang, "boot." + state))
        set_style_prop(self.boot_pill, "state", state)

    # ------------------------------------------------------------------ pm2
    @property
    def _installing(self):
        return bool(self._install_worker and self._install_worker.isRunning())

    def _tick(self):
        self.refresh_apps(force=False)
        self._update_logs(force=False)
        # First launch: if PM2 is missing, install it automatically.
        if (not self._pm2_ready and not self._install_attempted
                and not self._installing):
            self._install_attempted = True
            QTimer.singleShot(400, self._auto_install_pm2)

    def _apps_projection(self, apps):
        return [
            (a["id"], a["name"], a["status"], a["pid"], a["restarts"],
             round(a["cpu"] or 0, 1), round((a["memory"] or 0) / 1048576))
            for a in apps
        ]

    def refresh_apps(self, force=False):
        apps = pm2svc.list_apps()
        ready = pm2svc.is_pm2_ready()
        if ready != self._pm2_ready:
            self._pm2_ready = ready
            self._update_chip_texts()
        boot = pm2svc.boot_enabled()
        if boot != self._boot_enabled:
            self._boot_enabled = boot
            self._update_chip_texts()
        changed = self._apps_projection(apps) != self._apps_projection(self._app_cache)
        if force or changed:
            self._app_cache = apps
            self._render_apps(apps)
        self.apps_count.setText(t(self.lang, "apps.count", n=len(apps)))

    def _render_apps(self, apps):
        current_names = {a["name"] for a in apps}
        for name in list(self._cards):
            if name not in current_names:
                widget = self._cards.pop(name)
                widget.setParent(None)
                widget.deleteLater()
        if self._selected not in current_names:
            self._selected = None
        for app in apps:
            name = app["name"]
            card = self._cards.get(name)
            if card is None:
                card = AppCard(app, self.lang, self._select_app)
                self._cards[name] = card
                self.apps_list_lay.insertWidget(self.apps_list_lay.count() - 1, card)
                card.logs_btn.clicked.connect(lambda _=False, n=name: self._select_app(n))
                card.state_btn.clicked.connect(lambda _=False, c=card: self._on_card_state(c))
                card.restart_btn.clicked.connect(lambda _=False, c=card: self._on_card_restart(c))
                card.delete_btn.clicked.connect(lambda _=False, c=card: self._on_card_delete(c))
                card.path_label.mousePressEvent = (
                    lambda event, c=card: self._open_folder(c))
            else:
                card.update_data(app, self.lang)
            set_style_prop(card, "selected", "true" if name == self._selected else "false")

        empty = not bool(apps)
        self.apps_scroll.setVisible(not empty)
        self.empty_holder.setVisible(empty)
        if self._selected is None and apps:
            # Auto-select the first app so its live console shows immediately.
            self._select_app(apps[0]["name"])
        elif self._selected is None:
            self._log_visible_name = None

    def _select_app(self, name):
        self._selected = name
        self._log_visible_name = name
        for cname, card in self._cards.items():
            set_style_prop(card, "selected", "true" if cname == name else "false")
        self._last_log_text.clear()
        self._update_logs(force=True)

    def _open_folder(self, card):
        folder = card.app["cwd"] or os.path.dirname(card.app["script"])
        if folder and os.path.isdir(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    # ------------------------------------------------------------- actions
    def _on_card_state(self, card):
        app = card.app
        name = app["name"]
        if app["status"] == "online":
            if not self._confirm(
                    t(self.lang, "confirm.stopTitle"),
                    t(self.lang, "confirm.stopMsg", name=name)):
                return
            try:
                pm2svc.stop_app(name)
            except pm2svc.PM2Error as exc:
                self._show_pm2_error(t(self.lang, "err.pm2"), exc)
                return
            self._toast.show_text(t(self.lang, "toast.stopped", name=name))
        else:
            try:
                pm2svc.restart_app(name)
            except pm2svc.PM2Error as exc:
                self._show_pm2_error(t(self.lang, "err.pm2"), exc)
                return
            self._toast.show_text(t(self.lang, "toast.started", name=name))
        QTimer.singleShot(400, lambda: self.refresh_apps(force=True))

    def _on_card_restart(self, card):
        name = card.app["name"]
        try:
            pm2svc.restart_app(name)
        except pm2svc.PM2Error as exc:
            self._show_pm2_error(t(self.lang, "err.pm2"), exc)
            return
        self._toast.show_text(t(self.lang, "toast.restarted", name=name))
        QTimer.singleShot(400, lambda: self.refresh_apps(force=True))

    def _on_card_delete(self, card):
        app = card.app
        name = app["name"]
        if not self._confirm(
                t(self.lang, "confirm.deleteTitle"),
                t(self.lang, "confirm.deleteMsg", name=name)):
            return
        try:
            pm2svc.delete_app(name)
        except pm2svc.PM2Error as exc:
            self._show_pm2_error(t(self.lang, "err.pm2"), exc)
            return
        self._toast.show_text(t(self.lang, "toast.deleted", name=name))
        QTimer.singleShot(400, lambda: self.refresh_apps(force=True))

    # ------------------------------------------------------------ browsing
    def _browse_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, t(self.lang, "drop.browseFile"), os.path.expanduser("~"))
        if paths:
            self.add_paths(paths)

    def _browse_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, t(self.lang, "drop.browseFolder"), os.path.expanduser("~"))
        if path:
            self.add_paths([path])

    # ------------------------------------------------------------ pending
    def add_paths(self, paths):
        errors = []
        added = False
        for path in paths:
            try:
                script, kind, cwd, label_key = pm2svc.prepare_entry(path)
            except pm2svc.PM2Error as exc:
                msg = str(exc)
                if msg == "not_found":
                    errors.append(t(self.lang, "err.notFound", path=path))
                elif msg == "no_entry":
                    errors.append(path + "\n" + t(self.lang, "err.noEntry"))
                elif msg == "unsupported":
                    errors.append(path + "\n" + t(self.lang, "err.unsupported"))
                continue
            display = os.path.basename(os.path.normpath(path))
            self._pending.append({
                "script": script,
                "kind": kind,
                "cwd": cwd,
                "display": display,
                "label_key": "entry." + label_key,
            })
            added = True
        if errors:
            QMessageBox.warning(
                self, t(self.lang, "err.dropTitle"),
                "\n\n".join(errors))
        if added or (not self._pending):
            self.rebuild_pending()

    def rebuild_pending(self):
        for w in self._pending_widgets:
            w.setParent(None)
            w.deleteLater()
        self._pending_widgets = []
        if not self._pending:
            self.queue_empty.show()
            self.queue_count.setText("")
            self.clear_queue_btn.setEnabled(False)
            self.run_all_btn.setEnabled(False)
            return
        self.queue_empty.hide()
        for data in self._pending:
            item = PendingItem(data, self._run_pending_item, self._remove_pending_item, self.lang)
            self._pending_widgets.append(item)
            self.queue_content.addWidget(item)
        self.queue_count.setText(f"({len(self._pending)})")
        self.clear_queue_btn.setEnabled(True)
        self.run_all_btn.setEnabled(True)

    def _remove_pending_item(self, item):
        if item.data in self._pending:
            self._pending.remove(item.data)
        self.rebuild_pending()

    def clear_pending(self):
        self._pending.clear()
        self.rebuild_pending()

    def run_all_pending(self):
        for item in list(self._pending_widgets):
            if item.isEnabled():
                self._run_pending_item(item)
        self.refresh_apps(force=True)

    def _run_pending_item(self, item):
        if not item.isEnabled():
            return
        item.setEnabled(False)
        data = item.data
        try:
            name = pm2svc.start_app(data["script"], data["cwd"], data["kind"], data["display"])
        except pm2svc.PM2Error as exc:
            item.setEnabled(True)
            self._show_pm2_error(
                t(self.lang, "err.startFailed", name=data["display"]), exc)
            return
        if data in self._pending:
            self._pending.remove(data)
        self.rebuild_pending()
        self._toast.show_text(t(self.lang, "toast.started", name=name))
        QTimer.singleShot(400, lambda: self.refresh_apps(force=True))

    # ------------------------------------------------------------- logs
    def _stop_live(self):
        live = self._live
        self._live = None
        self._live_name = None
        self._live_ok = False
        if live is not None:
            live.stop()
            live.deleteLater()

    def _ensure_live(self, name):
        """Keep exactly one live stream open for the selected app."""
        if self._live is not None and self._live_name == name and self._live_ok:
            return
        self._stop_live()
        pm2_bin = pm2svc.pm2_path()
        if not pm2_bin:
            return
        self._live = LiveLogStream(pm2_bin, name)
        self._live_name = name
        self._live_ok = True
        self._live.got_line.connect(self._on_live_line)
        self._live.died.connect(self._on_live_died)

    def _on_live_line(self, line):
        if self._live_name is None:
            return
        name = self._live_name
        if self.console_title.text() != t(self.lang, "logs.title") + " — " + name:
            self.console_title.setText(t(self.lang, "logs.title") + " — " + name)
        self.console_empty.hide()
        self.console.show()
        self.console.appendPlainText(line)
        sb = self.console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_live_died(self):
        # Stream ended (app deleted, daemon stopped…); file polling takes over.
        if self._live is not None:
            self._live.deleteLater()
            self._live = None
        self._live_ok = False

    def _update_logs(self, force=False):
        name = self._log_visible_name
        if not name:
            self._stop_live()
            self.console.hide()
            self.console_empty.show()
            if force or self.console_empty.text() != t(self.lang, "logs.none"):
                self.console_empty.setText(t(self.lang, "logs.none"))
                self.console_title.setText(
                    t(self.lang, "logs.title") + " — " + t(self.lang, "logs.none"))
            return
        app = next((a for a in self._app_cache if a["name"] == name), None)
        if not app:
            self._stop_live()
            return
        self._ensure_live(name)
        if self._live is not None and self._live_ok:
            # Live stream is attached; new lines are appended as they arrive.
            self.console_title.setText(t(self.lang, "logs.title") + " — " + name)
            self.console_empty.hide()
            self.console.show()
            return
        # Fallback: poll the log files while no stream is running.
        if force or self._last_log_text.get(name) is None:
            self.console.setPlainText("")
        parts = []
        for log_path in (app["out_log"], app["err_log"]):
            if log_path and os.path.isfile(log_path) and log_path not in parts:
                parts.append(log_path)
        text = "\n".join(pm2svc.read_tail(p) for p in parts)
        if not text:
            text = t(self.lang, "logs.noFile")
        if force or self._last_log_text.get(name) != text:
            self._last_log_text[name] = text
            self.console.setPlainText(text)
            sb = self.console.verticalScrollBar()
            sb.setValue(sb.maximum())
            self.console_title.setText(t(self.lang, "logs.title") + " — " + name)
        self.console_empty.hide()
        self.console.show()

    def _copy_logs(self):
        QApplication.clipboard().setText(self.console.toPlainText())

    def _clear_logs(self):
        self.console.clear()
        self._last_log_text.clear()

    # ------------------------------------------------------------ dialogs
    def _confirm(self, title, message):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setIcon(QMessageBox.Icon.Question)
        box.setText(message)
        yes = box.addButton(t(self.lang, "btn.yes"), QMessageBox.ButtonRole.YesRole)
        box.addButton(t(self.lang, "btn.cancel"), QMessageBox.ButtonRole.NoRole)
        box.setDefaultButton(yes)
        box.exec()
        return box.clickedButton() is yes

    def _show_pm2_error(self, title, exc):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setText(title)
        box.setInformativeText(t(self.lang, "err.pm2"))
        if exc.output:
            box.setDetailedText(str(exc.output)[:6000])
        box.addButton(t(self.lang, "btn.close"), QMessageBox.ButtonRole.AcceptRole)
        box.exec()

    def _show_help(self):
        dlg = make_dialog(self, t(self.lang, "help.title"))
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(14)
        title = QLabel(t(self.lang, "help.title"))
        title.setObjectName("sectionTitle")
        title.setStyleSheet("font-size: 16px;")
        lay.addWidget(title)
        for i in range(1, 5):
            label = QLabel(f"{i}.  " + t(self.lang, f"help.p{i}"))
            label.setObjectName("whiteLabel")
            label.setWordWrap(True)
            lay.addWidget(label)
        close_btn = QPushButton(t(self.lang, "btn.close"))
        close_btn.setObjectName("primaryBtn")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dlg.accept)
        lay.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)
        dlg.exec()

    def _on_pm2_chip_click(self):
        if self._installing:
            return
        if pm2svc.is_pm2_ready():
            self._pm2_ready = True
            self._update_chip_texts()
            self._toast.show_text(t(self.lang, "pm2.ready"))
            return
        self._auto_install_pm2(retry=True)

    def _auto_install_pm2(self, retry=False):
        """Install PM2 automatically, streaming progress to a small dialog."""
        if self._installing:
            return
        if not retry and pm2svc.is_pm2_ready():
            self._pm2_ready = True
            self._update_chip_texts()
            return

        dlg = make_dialog(self, t(self.lang, "pm2.autoTitle"))
        dlg.setMinimumWidth(560)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)

        msg = QLabel(t(self.lang, "pm2.autoMsg"))
        msg.setObjectName("whiteLabel")
        msg.setWordWrap(True)
        lay.addWidget(msg)

        console = QPlainTextEdit()
        console.setObjectName("console")
        console.setReadOnly(True)
        console.setMaximumBlockCount(1500)
        console.setFixedHeight(150)
        console.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        lay.addWidget(console)

        row = QHBoxLayout()
        copy_btn = QPushButton(t(self.lang, "btn.copyCmd"))
        copy_btn.setObjectName("ghostBtn")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.hide()
        close_btn = QPushButton(t(self.lang, "btn.close"))
        close_btn.setObjectName("primaryBtn")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.hide()
        row.addWidget(copy_btn)
        row.addStretch(1)
        row.addWidget(close_btn)
        lay.addLayout(row)

        copy_target = {"cmd": ""}

        def on_line(line):
            console.appendPlainText(line)

        def on_done(ok, detail, code):
            self._install_worker = None
            if ok:
                self._pm2_ready = True
                self._update_chip_texts()
                dlg.accept()
                self._toast.show_text(t(self.lang, "pm2.installedToast"), 4500)
                self.refresh_apps(force=True)
                return
            # Installation failed -> give the exact command to run manually.
            if code == "node_missing":
                msg.setText(t(self.lang, "err.needNode"))
                copy_target["cmd"] = "sudo apt update && sudo apt install -y nodejs npm"
            else:
                msg.setText(t(self.lang, "err.installFailedTitle") +
                            "\n\n" + t(self.lang, "install.msg"))
                copy_target["cmd"] = "sudo npm install -g pm2"
            console.setPlainText((console.toPlainText() + "\n" + detail).strip())
            copy_btn.show()
            close_btn.show()
            self._pm2_ready = False
            self._update_chip_texts()

        worker = InstallWorker()
        worker.line.connect(on_line)
        worker.done.connect(on_done)
        copy_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(copy_target["cmd"]))
        close_btn.clicked.connect(dlg.reject)
        worker.finished.connect(worker.deleteLater)
        self._install_worker = worker
        worker.start()
        dlg.exec()
        self.refresh_apps(force=True)

    def _on_boot_click(self):
        try:
            pm2svc.save_list()
        except pm2svc.PM2Error:
            pass
        if self._boot_enabled:
            self._toast.show_text(t(self.lang, "boot.enabledToast"))
            return
        cmd = pm2svc.startup_sudo_command()
        QApplication.clipboard().setText(cmd)
        dlg = make_dialog(self, t(self.lang, "boot.dialogTitle"))
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)
        msg = QLabel(t(self.lang, "boot.dialogMsg", cmd=cmd))
        msg.setObjectName("whiteLabel")
        msg.setWordWrap(True)
        lay.addWidget(msg)
        row = QHBoxLayout()
        later = QPushButton(t(self.lang, "boot.later"))
        later.setCursor(Qt.CursorShape.PointingHandCursor)
        later.clicked.connect(dlg.reject)
        done = QPushButton(t(self.lang, "boot.done"))
        done.setObjectName("primaryBtn")
        done.setCursor(Qt.CursorShape.PointingHandCursor)
        done.clicked.connect(dlg.accept)
        row.addWidget(later)
        row.addStretch(1)
        row.addWidget(done)
        lay.addLayout(row)
        dlg.exec()
        if dlg.result() == QDialog.DialogCode.Accepted:
            self._boot_enabled = pm2svc.boot_enabled()
            self._update_chip_texts()
            if self._boot_enabled:
                self._toast.show_text(t(self.lang, "boot.enabledToast"), 4200)
            else:
                self._toast.show_text(t(self.lang, "boot.savedToast"), 4200)

    # ------------------------------------------------------------ window
    def closeEvent(self, event):
        self._stop_live()
        self.refresh_timer.stop()
        self.log_timer.stop()
        super().closeEvent(event)

