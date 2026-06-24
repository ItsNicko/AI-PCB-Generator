"""Theme stylesheet & dynamic color provider for the application."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor


# =====================================================================
# Dynamic color palette — used by widgets that can't rely on global QSS
# (QGraphicsScene backgrounds, pyqtgraph, custom-painted widgets, etc.)
# =====================================================================

class _Colors:
    """Named color set for one theme variant."""

    __slots__ = (
        "bg", "bg_secondary", "bg_input", "surface",
        "text", "text_dim", "border", "border_light",
        "accent", "accent_hover",
        "success", "warning", "error", "info",
        "scene_bg", "scene_grid", "scene_text",
        "view3d_bg_top", "view3d_bg_mid", "view3d_bg_bottom", "view3d_grid",
        "bar_bg", "bar_border",
        "header_bg", "header_text",
        "hover_bg", "selected_bg",
        "button_green", "button_green_hover",
    )

    def __init__(self, **kw: str):
        for k, v in kw.items():
            setattr(self, k, v)


_DARK = _Colors(
    bg="#2c2c2c",          bg_secondary="#3d3d3d",   bg_input="#1a1a1a",
    surface="#333333",     text="#e0e0e0",           text_dim="#a0a0a0",
    border="#555555",      border_light="#888888",
    accent="#00ffcc",      accent_hover="#33ffdd",
    success="#2ecc71",     warning="#f1c40f",        error="#e74c3c",
    info="#3498db",
    scene_bg="#121212",    scene_grid="#252525",     scene_text="#e0e0e0",
    view3d_bg_top="#2c2c2c",  view3d_bg_mid="#252525",
    view3d_bg_bottom="#1a1a1a", view3d_grid="#333333",
    bar_bg="#3d3d3d",      bar_border="#555555",
    header_bg="#333333",   header_text="#a0a0a0",
    hover_bg="#4d4d4d",    selected_bg="#00ffcc",
    button_green="#27ae60", button_green_hover="#2ecc71",
)

_LIGHT = _Colors(
    bg="#d1d1d1",          bg_secondary="#e0e0e0",   bg_input="#ffffff",
    surface="#e8e8e8",     text="#2c2c2c",            text_dim="#666666",
    border="#a0a0a0",      border_light="#ffffff",
    accent="#007acc",      accent_hover="#009eff",
    success="#27ae60",     warning="#f39c12",         error="#c0392b",
    info="#2980b9",
    scene_bg="#f0f0f0",    scene_grid="#d0d0d0",      scene_text="#2c2c2c",
    view3d_bg_top="#e0e0e0",  view3d_bg_mid="#d1d1d1",
    view3d_bg_bottom="#c0c0c0", view3d_grid="#b0b0b0",
    bar_bg="#e8e8e8",      bar_border="#a0a0a0",
    header_bg="#dcdcdc",   header_text="#666666",
    hover_bg="#f0f0f0",    selected_bg="#007acc",
    button_green="#2ecc71", button_green_hover="#27ae60",
)


class ThemeManager(QObject):
    """Singleton that tracks the active theme and emits on change."""

    theme_changed = Signal()
    _instance: ThemeManager | None = None

    def __init__(self):
        super().__init__()
        self._dark = True

    @classmethod
    def instance(cls) -> ThemeManager:
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    @property
    def is_dark(self) -> bool:
        return self._dark

    def set_dark(self, dark: bool) -> None:
        if dark != self._dark:
            self._dark = dark
            self.theme_changed.emit()

    @property
    def colors(self) -> _Colors:
        return _DARK if self._dark else _LIGHT


def tc() -> _Colors:
    """Module-level shortcut — returns the active color set."""
    return ThemeManager.instance().colors


# =====================================================================
# Global QSS stylesheets
# =====================================================================

DARK_THEME = """
QMainWindow, QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #4a4a4a, stop:1 #2a2a2a);
    color: #e0e0e0;
}

QWidget {
    background: transparent;
    color: #e0e0e0;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}

/* Metal Panels */
QGroupBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #3d3d3d, stop:1 #2d2d2d);
    border: 2px solid #555555;
    border-top-color: #888888;
    border-left-color: #888888;
    border-bottom-color: #111111;
    border-right-color: #111111;
    border-radius: 8px;
    margin-top: 20px;
    padding-top: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #aaaaaa;
}

QMenuBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #555555, stop:1 #333333);
    color: #e0e0e0;
    border-bottom: 2px solid #111111;
}

QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #444444, stop:1 #222222);
    border-bottom: 2px solid #000000;
    spacing: 6px;
    padding: 4px;
}

/* Tactile Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #666666, stop:1 #444444);
    color: #ffffff;
    border: 2px solid #333333;
    border-top-color: #888888;
    border-left-color: #888888;
    border-bottom-color: #111111;
    border-right-color: #111111;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #777777, stop:1 #555555);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #222222, stop:1 #444444);
    border-top-color: #111111;
    border-left-color: #111111;
    border-bottom-color: #888888;
    border-right-color: #888888;
    padding-top: 10px;
    padding-left: 10px;
}

QPushButton#secondaryButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #555555, stop:1 #333333);
}

QPushButton#dangerButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #c0392b, stop:1 #8e44ad);
}

/* Inset Inputs */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
    background: #1a1a1a;
    color: #d0d0d0;
    border: 2px solid #333333;
    border-top-color: #111111;
    border-left-color: #111111;
    border-bottom-color: #555555;
    border-right-color: #555555;
    border-radius: 4px;
    padding: 6px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #00ffcc;
}

/* Metal Tabs */
QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #555555, stop:1 #333333);
    color: #aaaaaa;
    border: 1px solid #222222;
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #3d3d3d, stop:1 #2d2d2d);
    color: #ffffff;
    border-bottom: 2px solid #00ffcc;
}

/* Table and Lists */
QTableWidget, QTableView {
    background: #1a1a1a;
    color: #d0d0d0;
    border: 2px solid #333333;
    gridline-color: #333333;
    selection-background-color: #444444;
    border-radius: 4px;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #555555, stop:1 #333333);
    color: #eeeeee;
    border: 1px solid #111111;
    padding: 6px;
    font-weight: bold;
}

QScrollBar:vertical {
    background: #222222;
    width: 12px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                stop:0 #555555, stop:1 #333333);
    border: 1px solid #111111;
    border-radius: 6px;
}

QLabel#titleLabel {
    font-size: 22px;
    font-weight: bold;
    color: #ffffff;
    text-shadow: 1px 1px 2px #000000;
}
"""


LIGHT_THEME = """
QMainWindow, QDialog {
    background-color: #f6f8fa;
    color: #24292f;
}

QWidget {
    background-color: #f6f8fa;
    color: #24292f;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}

QMenuBar {
    background-color: #ffffff;
    color: #24292f;
    border-bottom: 1px solid #d0d7de;
    padding: 2px;
}

QMenuBar::item:selected {
    background-color: #e2e8f0;
    border-radius: 4px;
}

QMenu {
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
}

QMenu::item:selected {
    background-color: #dbeafe;
    color: #1e40af;
}

QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #d0d7de;
    spacing: 4px;
    padding: 2px;
}

QToolButton {
    background-color: transparent;
    color: #24292f;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

QToolButton:hover {
    background-color: #e2e8f0;
    border: 1px solid #6d28d9;
}

QToolButton:pressed {
    background-color: #ddd6fe;
}

QStatusBar {
    background-color: #ffffff;
    color: #57606a;
    border-top: 1px solid #d0d7de;
}

QSplitter::handle {
    background-color: #d0d7de;
    width: 2px;
    height: 2px;
}

QTabWidget::pane {
    border: 1px solid #d0d7de;
    background-color: #f6f8fa;
}

QTabBar::tab {
    background-color: #eaeef2;
    color: #57606a;
    border: 1px solid #d0d7de;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #f6f8fa;
    color: #24292f;
    border-bottom-color: #f6f8fa;
}

QTabBar::tab:hover {
    background-color: #dbeafe;
}

QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 8px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 13px;
    selection-background-color: #bfdbfe;
}

QLineEdit {
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 10px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #6d28d9;
}

QPushButton {
    background-color: #6d28d9;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #7c3aed;
}

QPushButton:pressed {
    background-color: #5b21b6;
}

QPushButton:disabled {
    background-color: #c4b5fd;
    color: #f5f3ff;
}

QPushButton#secondaryButton {
    background-color: #e2e8f0;
    color: #334155;
}

QPushButton#secondaryButton:hover {
    background-color: #cbd5e1;
}

QPushButton#dangerButton {
    background-color: #dc2626;
}

QPushButton#dangerButton:hover {
    background-color: #ef4444;
}

QTableWidget, QTableView {
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
    gridline-color: #eaeef2;
    selection-background-color: #dbeafe;
    border-radius: 6px;
    alternate-background-color: #f6f8fa;
}

QTableWidget::item {
    padding: 4px 8px;
}

QHeaderView::section {
    background-color: #eaeef2;
    color: #24292f;
    border: 1px solid #d0d7de;
    padding: 6px;
    font-weight: bold;
}

QScrollBar:vertical {
    background-color: #f6f8fa;
    width: 10px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #c1c7cd;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9ca3af;
}

QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f6f8fa;
    height: 10px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #c1c7cd;
    border-radius: 5px;
    min-width: 30px;
}

QGroupBox {
    border: 1px solid #d0d7de;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #57606a;
}

QComboBox {
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 10px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
    selection-background-color: #dbeafe;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #d0d7de;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #6d28d9;
    border-color: #6d28d9;
}

QProgressBar {
    border: 1px solid #d0d7de;
    border-radius: 4px;
    text-align: center;
    background-color: #eaeef2;
    color: #24292f;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #6d28d9;
    border-radius: 3px;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #24292f;
}

QLabel#subtitleLabel {
    font-size: 12px;
    color: #57606a;
}

QLabel#warningLabel {
    color: #b45309;
}

QLabel#errorLabel {
    color: #dc2626;
}

QLabel#successLabel {
    color: #16a34a;
}
"""
