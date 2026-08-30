import sys
import os
import platform
import subprocess
import json
import ctypes
import requests
import threading
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSlider, QSpinBox, QLineEdit,
    QFrame, QFileDialog, QGroupBox, QGridLayout, QSizePolicy,
    QListWidget, QListWidgetItem, QAbstractItemView, QCompleter,
    QStyledItemDelegate, QCheckBox, QDialog, QTextEdit, QProgressBar, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, QSettings, QMimeData, QDir, QStringListModel, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent, QStandardItemModel, QStandardItem, QColor, QPalette, QAction
from PIL import Image, PngImagePlugin

# Increase PIL limits
PngImagePlugin.MAX_TEXT_CHUNK = 50 * (1024**2)  # 50MB limit
Image.MAX_IMAGE_PIXELS = None  # Disable DoS check for large images

CURRENT_VERSION = "2.2.0"
GITHUB_REPO = "ReiKatari/STORM_MULTI-ICO_CONVERT"

try:
    myappid = 'STORM.MultiIcoConverter.v200'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except:
        pass

# Supported image extensions
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff', '.tif', '.ico'}

# --- SIZE PRESETS BY ASPECT RATIO ---
SIZE_GROUPS = {
    "1:1 (Квадрат)": ["16×16", "24×24", "32×32", "48×48", "64×64", "96×96", "128×128", "256×256", "512×512", "1024×1024"],
    "3:2": ["480×320", "720×480", "1080×720", "1440×960", "1920×1280", "2160×1440"],
    "4:3": ["320×240", "640×480", "800×600", "1024×768", "1280×960", "1600×1200", "2048×1536"],
    "5:4": ["1280×1024", "2560×2048"],
    "16:10": ["1280×800", "1440×900", "1680×1050", "1920×1200", "2560×1600"],
    "16:9": ["854×480", "1280×720", "1366×768", "1600×900", "1920×1080", "2560×1440", "3840×2160"],
    "21:9": ["2560×1080", "3440×1440", "5120×2160"]
}

# --- LOCALIZATION ---
LOCALE = {
    "ru": {
        "window_title": f"STORM MULTI-ICO CONVERTER v{CURRENT_VERSION}",
        "subtitle": "Универсальный конвертер изображений",
        "btn_select": "📂 Файлы",
        "btn_select_folder": "📁 Папка",
        "btn_clear": "🗑",
        "drop_hint": "Перетащите изображения или папки сюда",
        "grp_input": "Входные файлы",
        "grp_output": "Параметры вывода",
        "grp_transparency": "Прозрачность",
        "lbl_format": "Формат",
        "lbl_size": "Размер",
        "lbl_width": "Ширина",
        "lbl_height": "Высота",
        "lbl_opacity": "Непрозрачность",
        "btn_convert": "🚀 КОНВЕРТИРОВАТЬ",
        "btn_multi_ico": "🎯 СОЗДАТЬ MULTI-ICO",
        "btn_open": "📁 Открыть папку",
        "status_wait": "Ожидание файлов...",
        "status_ready": "Готов к конвертации ({count} файлов)",
        "status_proc": "Обработка {current}/{total}...",
        "status_done": "✅ Успешно: {count} файлов обработано",
        "error_ext": "❌ Формат не поддерживается",
        "error_gen": "❌ Ошибка",
        "theme": "Тема:",
        "lang": "Язык:",
        "auto_update": "Авто-обновление",
        "upd_title": "Доступно обновление",
        "upd_msg": "Обнаружена новая версия: <b>{}</b><br>Хотите скачать и обновить сейчас?",
        "upd_btn": "🚀 Обновить",
        "upd_skip": "Позже",
        "upd_err": "❌ Ошибка проверки обновлений",
        "upd_downloading": "📥 Скачивание обновления... {}%",
        "upd_no_new": "✅ Установлена последняя версия"
    },
    "en": {
        "window_title": f"STORM MULTI-ICO CONVERTER v{CURRENT_VERSION}",
        "subtitle": "Universal Image Converter",
        "btn_select": "📂 Files",
        "btn_select_folder": "📁 Folder",
        "btn_clear": "🗑",
        "drop_hint": "Drop images or folders here",
        "grp_input": "Input Files",
        "grp_output": "Output Settings",
        "grp_transparency": "Transparency",
        "lbl_format": "Format",
        "lbl_size": "Size",
        "lbl_width": "Width",
        "lbl_height": "Height",
        "lbl_opacity": "Opacity",
        "btn_convert": "🚀 CONVERT",
        "btn_multi_ico": "🎯 CREATE MULTI-ICO",
        "btn_open": "📁 Open Folder",
        "status_wait": "Waiting for files...",
        "status_ready": "Ready to convert ({count} files)",
        "status_proc": "Processing {current}/{total}...",
        "status_done": "✅ Success: {count} files processed",
        "error_ext": "❌ Format not supported",
        "error_gen": "❌ Error",
        "theme": "Theme:",
        "lang": "Language:",
        "auto_update": "Auto-Update",
        "upd_title": "Update Available",
        "upd_msg": "New version found: <b>{}</b><br>Do you want to download and update now?",
        "upd_btn": "🚀 Update",
        "upd_skip": "Later",
        "upd_err": "❌ Update Check Failed",
        "upd_downloading": "📥 Downloading update... {}%",
        "upd_no_new": "✅ You have the latest version"
    }
}

# --- THEMES ---
THEMES = {
    "Dark (Default)": {"bg": "#121212", "fg": "#e0e0e0", "input_bg": "#252525", "input_fg": "white", "input_border": "#444", "btn_bg": "#2d2d2d", "btn_fg": "white", "accent": "#3B8ED0", "type": "dark"},
    "Polar White": {"bg": "#ffffff", "fg": "#333333", "input_bg": "#f7f7f7", "input_fg": "#333", "input_border": "#ccc", "btn_bg": "#f0f0f0", "btn_fg": "#333", "accent": "#2980b9", "type": "light"},
    "Dracula": {"bg": "#282a36", "fg": "#f8f8f2", "input_bg": "#44475a", "input_fg": "#f8f8f2", "input_border": "#6272a4", "btn_bg": "#44475a", "btn_fg": "#f8f8f2", "accent": "#bd93f9", "type": "dark"},
    "Solarized Dark": {"bg": "#002b36", "fg": "#839496", "input_bg": "#073642", "input_fg": "#93a1a1", "input_border": "#586e75", "btn_bg": "#073642", "btn_fg": "#93a1a1", "accent": "#268bd2", "type": "dark"},
    "Solarized Light": {"bg": "#fdf6e3", "fg": "#657b83", "input_bg": "#eee8d5", "input_fg": "#586e75", "input_border": "#93a1a1", "btn_bg": "#eee8d5", "btn_fg": "#586e75", "accent": "#2aa198", "type": "light"},
    "Monokai": {"bg": "#272822", "fg": "#f8f8f2", "input_bg": "#3e3d32", "input_fg": "#f8f8f2", "input_border": "#75715e", "btn_bg": "#3e3d32", "btn_fg": "#f8f8f2", "accent": "#f92672", "type": "dark"},
    "Nord": {"bg": "#2e3440", "fg": "#d8dee9", "input_bg": "#3b4252", "input_fg": "#e5e9f0", "input_border": "#4c566a", "btn_bg": "#3b4252", "btn_fg": "#e5e9f0", "accent": "#88c0d0", "type": "dark"},
    "Cyberpunk": {"bg": "#0b0c15", "fg": "#00ff9f", "input_bg": "#1c1c2e", "input_fg": "#f0f0f0", "input_border": "#ff003c", "btn_bg": "#1c1c2e", "btn_fg": "#00ff9f", "accent": "#ff003c", "type": "dark"},
    "Matrix": {"bg": "#000000", "fg": "#00ff00", "input_bg": "#111111", "input_fg": "#00ff00", "input_border": "#004400", "btn_bg": "#0a0a0a", "btn_fg": "#00ff00", "accent": "#00ff00", "type": "dark"},
    "Deep Ocean": {"bg": "#0f172a", "fg": "#e2e8f0", "input_bg": "#1e293b", "input_fg": "#f1f5f9", "input_border": "#334155", "btn_bg": "#1e293b", "btn_fg": "#e2e8f0", "accent": "#38bdf8", "type": "dark"},
    "Forest": {"bg": "#1a2f1c", "fg": "#e0f2e1", "input_bg": "#2d4a30", "input_fg": "#ffffff", "input_border": "#4caf50", "btn_bg": "#2d4a30", "btn_fg": "#e0f2e1", "accent": "#4caf50", "type": "dark"},
    "Midnight Blue": {"bg": "#000033", "fg": "#cccccc", "input_bg": "#000055", "input_fg": "#ffffff", "input_border": "#000077", "btn_bg": "#000055", "btn_fg": "#cccccc", "accent": "#3B8ED0", "type": "dark"},
    "Sunset": {"bg": "#2d1b2e", "fg": "#ffd1dc", "input_bg": "#4a2c4e", "input_fg": "#ffffff", "input_border": "#b56576", "btn_bg": "#4a2c4e", "btn_fg": "#ffd1dc", "accent": "#ff6b6b", "type": "dark"},
    "Grey": {"bg": "#333333", "fg": "#eeeeee", "input_bg": "#444444", "input_fg": "#ffffff", "input_border": "#555555", "btn_bg": "#444444", "btn_fg": "#eeeeee", "accent": "#3B8ED0", "type": "dark"},
    "Discord": {"bg": "#36393f", "fg": "#dcddde", "input_bg": "#40444b", "input_fg": "#ffffff", "input_border": "#202225", "btn_bg": "#40444b", "btn_fg": "#dcddde", "accent": "#7289da", "type": "dark"},
    "Ubuntu": {"bg": "#300a24", "fg": "#ffffff", "input_bg": "#471336", "input_fg": "#ffffff", "input_border": "#77216f", "btn_bg": "#5e2750", "btn_fg": "#ffffff", "accent": "#E95420", "type": "dark"},
    "Mint": {"bg": "#212121", "fg": "#00ffcc", "input_bg": "#333333", "input_fg": "#00ffcc", "input_border": "#009688", "btn_bg": "#333333", "btn_fg": "#00ffcc", "accent": "#009688", "type": "dark"},
    "Coffee": {"bg": "#2d241f", "fg": "#d6c3b6", "input_bg": "#42362e", "input_fg": "#f0e6dd", "input_border": "#6b5446", "btn_bg": "#42362e", "btn_fg": "#d6c3b6", "accent": "#c4a77d", "type": "dark"},
    "Steel": {"bg": "#1c2329", "fg": "#b0c4de", "input_bg": "#2a343d", "input_fg": "#ffffff", "input_border": "#4682b4", "btn_bg": "#2a343d", "btn_fg": "#b0c4de", "accent": "#4682b4", "type": "dark"},
    "High Contrast": {"bg": "#000000", "fg": "#ffffff", "input_bg": "#000000", "input_fg": "#ffffff", "input_border": "#ffffff", "btn_bg": "#000000", "btn_fg": "#ffffff", "accent": "#ffffff", "type": "dark"},
    "Hackerman": {"bg": "#0d0208", "fg": "#008f11", "input_bg": "#1a0410", "input_fg": "#00ff41", "input_border": "#003b00", "btn_bg": "#1a0410", "btn_fg": "#00ff41", "accent": "#00ff41", "type": "dark"},
    "Red Velvet": {"bg": "#2b0000", "fg": "#ffdddd", "input_bg": "#450000", "input_fg": "#ffffff", "input_border": "#800000", "btn_bg": "#450000", "btn_fg": "#ffdddd", "accent": "#ff4d4d", "type": "dark"},
    "Purple Haze": {"bg": "#1a0b2e", "fg": "#e0b0ff", "input_bg": "#2d164f", "input_fg": "#ffffff", "input_border": "#663399", "btn_bg": "#2d164f", "btn_fg": "#e0b0ff", "accent": "#9b59b6", "type": "dark"},
    "Gold": {"bg": "#1a1a10", "fg": "#ffd700", "input_bg": "#2b2b1a", "input_fg": "#ffeb3b", "input_border": "#b8860b", "btn_bg": "#2b2b1a", "btn_fg": "#ffd700", "accent": "#ffd700", "type": "dark"},
    "Carbon": {"bg": "#181818", "fg": "#b0b0b0", "input_bg": "#252525", "input_fg": "#e0e0e0", "input_border": "#3a3a3a", "btn_bg": "#252525", "btn_fg": "#b0b0b0", "accent": "#607d8b", "type": "dark"},
    "Slate": {"bg": "#23272e", "fg": "#abb2bf", "input_bg": "#2c313a", "input_fg": "#ffffff", "input_border": "#5c6370", "btn_bg": "#2c313a", "btn_fg": "#abb2bf", "accent": "#61afef", "type": "dark"},
    "Navy": {"bg": "#001f3f", "fg": "#7fdbff", "input_bg": "#003366", "input_fg": "#ffffff", "input_border": "#0074d9", "btn_bg": "#003366", "btn_fg": "#7fdbff", "accent": "#0074d9", "type": "dark"},
    "Pinky": {"bg": "#290015", "fg": "#ff99cc", "input_bg": "#420022", "input_fg": "#ffffff", "input_border": "#800040", "btn_bg": "#420022", "btn_fg": "#ff99cc", "accent": "#ff99cc", "type": "dark"},
    "Storm Blue": {"bg": "#151e24", "fg": "#d4e6f1", "input_bg": "#212f38", "input_fg": "#ffffff", "input_border": "#34495e", "btn_bg": "#212f38", "btn_fg": "#d4e6f1", "accent": "#3498db", "type": "dark"},
    # --- ULTRA COLLECTION ---
    "Neon City (Ultra)": {"bg": "#050505", "fg": "#00f3ff", "input_bg": "#0a0a0a", "input_fg": "#ff0099", "input_border": "#00f3ff", "btn_bg": "#111111", "btn_fg": "#00f3ff", "accent": "#ff0099", "type": "dark"},
    "Radioactive (Ultra)": {"bg": "#0a0f00", "fg": "#ccff00", "input_bg": "#141f00", "input_fg": "#ffffff", "input_border": "#66ff00", "btn_bg": "#1f3300", "btn_fg": "#ccff00", "accent": "#66ff00", "type": "dark"},
    "Vaporwave 80s (Ultra)": {"bg": "#240046", "fg": "#ff9e00", "input_bg": "#3c096c", "input_fg": "#ff9e00", "input_border": "#9d4edd", "btn_bg": "#5a189a", "btn_fg": "#e0aaff", "accent": "#9d4edd", "type": "dark"},
    "Obsidian Glass (Ultra)": {"bg": "#000000", "fg": "#e0e0e0", "input_bg": "#1a1a1a", "input_fg": "#ffffff", "input_border": "#333333", "btn_bg": "#1a1a1a", "btn_fg": "#ffffff", "accent": "#e0e0e0", "type": "dark"},
    "Crimson Fury (Ultra)": {"bg": "#1a0000", "fg": "#ff4d4d", "input_bg": "#330000", "input_fg": "#ffffff", "input_border": "#ff0000", "btn_bg": "#4d0000", "btn_fg": "#ffcccc", "accent": "#ff4d4d", "type": "dark"},
    "Deep Space (Ultra)": {"bg": "#020c1b", "fg": "#64ffda", "input_bg": "#112240", "input_fg": "#e6f1ff", "input_border": "#233554", "btn_bg": "#0a192f", "btn_fg": "#64ffda", "accent": "#64ffda", "type": "dark"},
    "Golden Luxury (Ultra)": {"bg": "#121212", "fg": "#ffd700", "input_bg": "#1c1c1c", "input_fg": "#ffffff", "input_border": "#cfb53b", "btn_bg": "#262626", "btn_fg": "#ffd700", "accent": "#cfb53b", "type": "dark"},
    "Hacker Green (Ultra)": {"bg": "#000000", "fg": "#00ff00", "input_bg": "#001100", "input_fg": "#00ff00", "input_border": "#003300", "btn_bg": "#002200", "btn_fg": "#00ff00", "accent": "#00ff00", "type": "dark"},
    "Oceanic Zen (Ultra)": {"bg": "#001e26", "fg": "#00d4ff", "input_bg": "#003542", "input_fg": "#ffffff", "input_border": "#005f73", "btn_bg": "#0a9396", "btn_fg": "#ffffff", "accent": "#00d4ff", "type": "dark"},
    "Ghost White (Ultra)": {"bg": "#f0f2f5", "fg": "#1c1e21", "input_bg": "#ffffff", "input_fg": "#000000", "input_border": "#1877f2", "btn_bg": "#e4e6eb", "btn_fg": "#050505", "accent": "#1877f2", "type": "light"}
}

# --- OUTPUT FORMATS ---
OUTPUT_FORMATS = {
    "PNG": {"ext": ".png", "format": "PNG", "supports_alpha": True},
    "JPEG": {"ext": ".jpg", "format": "JPEG", "supports_alpha": False},
    "WebP": {"ext": ".webp", "format": "WEBP", "supports_alpha": True},
    "BMP": {"ext": ".bmp", "format": "BMP", "supports_alpha": False},
    "GIF": {"ext": ".gif", "format": "GIF", "supports_alpha": True},
    "TIFF": {"ext": ".tiff", "format": "TIFF", "supports_alpha": True},
    "ICO": {"ext": ".ico", "format": "ICO", "supports_alpha": True},
}

class CenteredDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter
        super().paint(painter, option, index)

class DropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu) # Removed
        # self.customContextMenuRequested.connect(self.show_context_menu) # Removed
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and self.main_window:
            paths = [url.toLocalFile() for url in urls]
            self.main_window.add_paths(paths)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            item = self.itemAt(event.pos())
            if item:
                # Immediate delete
                # We need to handle this carefully.
                # If we just remove the item, we need to make sure we also unselect it or handle selection?
                # Actually, simpler: just identify the path and call remove.
                path = item.toolTip()
                if self.main_window:
                    self.main_window.remove_paths([path])
        else:
            super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.remove_selected_items()
        else:
            super().keyPressEvent(event)

    # def show_context_menu(self, pos): ... # Removed
            
    def remove_selected_items(self):
        items = self.selectedItems()
        if not items: return
        
        paths_to_remove = []
        for item in items:
            paths_to_remove.append(item.toolTip())
            
        if self.main_window:
            self.main_window.remove_paths(paths_to_remove)

# --- THREADS ---
class UpdateCheckerThread(QThread):
    update_found = pyqtSignal(str, str, str) # version, url, body
    update_not_found = pyqtSignal()
    
    def run(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                tag = data.get("tag_name", "").replace("v", "")
                body = data.get("body", "")
                
                try:
                    remote = [int(x) for x in tag.split('.') if x.isdigit()]
                    local = [int(x) for x in CURRENT_VERSION.split('-')[0].split('.') if x.isdigit()]
                    
                    if remote > local:
                        assets = data.get("assets", [])
                        exe_url = ""
                        for asset in assets:
                            if asset["name"].endswith(".exe"):
                                exe_url = asset["browser_download_url"]
                                break
                        if not exe_url and assets: exe_url = data["html_url"]
                        
                        if exe_url:
                            self.update_found.emit(tag, exe_url, body)
                            return
                except: pass
            self.update_not_found.emit()
        except: self.update_not_found.emit()

class UpdateDownloaderThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    
    def __init__(self, url, dest_path):
        super().__init__()
        self.url = url
        self.dest_path = dest_path
        
    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            with open(self.dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            prog = int((downloaded / total_size) * 100)
                            self.progress.emit(prog)
            self.finished.emit(self.dest_path)
        except: self.finished.emit("")

class UpdateDialog(QDialog):
    def __init__(self, parent, new_ver, url, body, lang):
        super().__init__(parent)
        self.lang = lang
        self.url = url
        self.setWindowTitle(LOCALE[lang]["upd_title"])
        self.setFixedWidth(450)
        self.setStyleSheet(parent.styleSheet())
        
        layout = QVBoxLayout(self)
        
        lbl = QLabel(LOCALE[lang]["upd_msg"].format(new_ver))
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        
        changes = QTextEdit()
        changes.setReadOnly(True)
        changes.setPlainText(body)
        changes.setStyleSheet("background-color: rgba(0,0,0,0.2); border: 1px solid #555;")
        layout.addWidget(changes)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar { text-align: center; } QProgressBar::chunk { background-color: #27ae60; }")
        layout.addWidget(self.progress)
        
        btns = QHBoxLayout()
        self.btn_update = QPushButton(LOCALE[lang]["upd_btn"])
        self.btn_update.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 6px;")
        self.btn_update.clicked.connect(self.start_update)
        
        btn_cancel = QPushButton(LOCALE[lang]["upd_skip"])
        btn_cancel.clicked.connect(self.reject)
        
        btns.addWidget(self.btn_update)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)
        
    def start_update(self):
        self.btn_update.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        new_exe = os.path.join(os.path.dirname(sys.executable), "update_temp.exe")
        self.downloader = UpdateDownloaderThread(self.url, new_exe)
        self.downloader.progress.connect(self.progress.setValue)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.start()
        
    def on_download_finished(self, path):
        if path:
            self.install_update(path)
        else:
            QMessageBox.critical(self, "Error", LOCALE[self.lang]["upd_err"])
            self.reject()
            
    def install_update(self, new_path):
        current_exe = sys.executable
        folder = os.path.dirname(current_exe)
        bat_path = os.path.join(folder, "updater.bat")
        pid = os.getpid()
        
        cmds = f"""@echo off
timeout /t 2 /nobreak > NUL
:loop
tasklist /FI "PID eq {pid}" 2>NUL | find /I /N "{pid}" >NUL
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 >NUL
    goto loop
)
timeout /t 1 /nobreak >NUL
move /y "{new_path}" "{current_exe}" > NUL
start "" "{current_exe}"
del "%~f0"
"""
        try:
            with open(bat_path, "w") as f:
                f.write(cmds)
            subprocess.Popen([bat_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE, close_fds=True)
            QApplication.quit()
            sys.exit(0)
        except Exception as e:
            QMessageBox.critical(self, "Update Error", str(e))
            self.reject()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        hide_console()
        
        self.settings = QSettings("StormApp", "STORM_MultiIco_v200")
        self.current_lang = self.settings.value("language", "ru")
        self.current_theme = self.settings.value("theme", "Dark (Default)")
        self.file_list = []
        self.output_folder = ""
        
        self.setWindowTitle(LOCALE[self.current_lang]["window_title"])
        self.setMinimumSize(540, 500)
        self.resize(540, 500)
        
        try:
            icon_path = resource_path("stormmultiicoconverter.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass
        
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        
        self.init_ui()
        self.apply_theme(self.current_theme)
        self.update_texts()
        
        if self.chk_auto_update.isChecked():
            self.check_updates(silent=True)
    
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)
        
        # --- TOP BAR ---
        top_bar = QHBoxLayout()
        
        self.lbl_lang = QLabel("Язык:")
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["🇷🇺 Русский", "🇺🇸 English"])
        self.combo_lang.setCurrentText("🇷🇺 Русский" if self.current_lang == "ru" else "🇺🇸 English")
        self.combo_lang.currentTextChanged.connect(self.change_language)
        self.combo_lang.setFixedWidth(130)
        self.combo_lang.setFixedHeight(30)
        self.combo_lang.setEditable(True)
        self.combo_lang.lineEdit().setReadOnly(True)
        self.combo_lang.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combo_lang.setItemDelegate(CenteredDelegate())
        
        top_bar.addWidget(self.lbl_lang)
        top_bar.addWidget(self.combo_lang)
        top_bar.addStretch()
        
        self.lbl_theme = QLabel("Тема:")
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(list(THEMES.keys()))
        self.combo_theme.setCurrentText(self.current_theme)
        self.combo_theme.currentTextChanged.connect(self.apply_theme)
        self.combo_theme.setFixedWidth(160)
        self.combo_theme.setFixedHeight(30)
        self.combo_theme.setEditable(True)
        self.combo_theme.lineEdit().setReadOnly(True)
        self.combo_theme.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combo_theme.setItemDelegate(CenteredDelegate())
        
        top_bar.addWidget(self.lbl_theme)
        top_bar.addWidget(self.combo_theme)
        main_layout.addLayout(top_bar)
        
        # --- TITLE ---
        self.lbl_title = QLabel("STORM MULTI-ICO CONVERTER")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #3B8ED0;")
        main_layout.addWidget(self.lbl_title)
        
        self.lbl_subtitle = QLabel()
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_subtitle.setStyleSheet("font-size: 11px; color: gray;")
        main_layout.addWidget(self.lbl_subtitle)
        
        # --- INPUT GROUP ---
        self.grp_input = QGroupBox()
        input_layout = QVBoxLayout(self.grp_input)
        input_layout.setSpacing(8)
        
        btn_row = QHBoxLayout()
        
        self.btn_select = QPushButton()
        self.btn_select.setMinimumHeight(40)
        self.btn_select.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select.clicked.connect(self.select_files)
        
        self.btn_select_folder = QPushButton()
        self.btn_select_folder.setMinimumHeight(40)
        self.btn_select_folder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_select_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_folder.clicked.connect(self.select_folder)
        
        self.btn_clear = QPushButton()
        self.btn_clear.setMinimumHeight(40)
        self.btn_clear.setFixedWidth(50) # Smaller clear button
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_files)
        
        btn_row.addWidget(self.btn_select)
        btn_row.addWidget(self.btn_select_folder)
        btn_row.addWidget(self.btn_clear)
        input_layout.addLayout(btn_row)
        
        self.list_files = DropListWidget(self)
        self.list_files.setMinimumHeight(100)
        self.list_files.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        input_layout.addWidget(self.list_files)
        
        self.lbl_drop = QLabel()
        self.lbl_drop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_drop.setStyleSheet("color: gray; font-size: 11px;")
        input_layout.addWidget(self.lbl_drop)
        
        main_layout.addWidget(self.grp_input, 1) # Stretch factor 1
        
        # --- OUTPUT GROUP ---
        self.grp_output = QGroupBox()
        output_layout = QGridLayout(self.grp_output)
        output_layout.setSpacing(10)
        
        # Format & Size in one row
        self.lbl_format = QLabel()
        self.lbl_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.combo_format = QComboBox()
        self.combo_format.addItems(list(OUTPUT_FORMATS.keys()))
        self.combo_format.setCurrentText("PNG")
        self.combo_format.setFixedHeight(34)
        self.combo_format.setEditable(True)
        self.combo_format.lineEdit().setReadOnly(True)
        self.combo_format.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combo_format.setItemDelegate(CenteredDelegate())
        
        self.lbl_size = QLabel()
        self.lbl_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.combo_size = QComboBox()
        self.combo_size.setEditable(True)
        self.combo_size.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_size.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setup_size_presets()
        self.combo_size.currentTextChanged.connect(self.on_size_changed)
        self.combo_size.setFixedHeight(34)
        
        output_layout.addWidget(self.lbl_format, 0, 0)
        output_layout.addWidget(self.combo_format, 0, 1)
        output_layout.addWidget(self.lbl_size, 0, 2)
        output_layout.addWidget(self.combo_size, 0, 3)
        
        output_layout.setColumnStretch(1, 1)
        output_layout.setColumnStretch(3, 1)
        
        # Width & Height
        self.lbl_width = QLabel()
        self.lbl_width.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_width = QSpinBox()
        self.spin_width.setRange(0, 8192)
        self.spin_width.setValue(0) # Logic handled as 0 = "Empty"
        self.spin_width.setSpecialValueText(" ") # Display empty if 0
        self.spin_width.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_width.setFixedHeight(34)
        self.spin_width.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        self.spin_width.setKeyboardTracking(True)
        
        self.lbl_height = QLabel()
        self.lbl_height.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_height = QSpinBox()
        self.spin_height.setRange(0, 8192)
        self.spin_height.setValue(0)
        self.spin_height.setSpecialValueText(" ")
        self.spin_height.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_height.setFixedHeight(34)
        self.spin_height.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        self.spin_height.setKeyboardTracking(True)
        
        output_layout.addWidget(self.lbl_width, 1, 0)
        output_layout.addWidget(self.spin_width, 1, 1)
        output_layout.addWidget(self.lbl_height, 1, 2)
        output_layout.addWidget(self.spin_height, 1, 3)
        
        main_layout.addWidget(self.grp_output)
        
        # --- TRANSPARENCY GROUP ---
        self.grp_transparency = QGroupBox()
        trans_layout = QHBoxLayout(self.grp_transparency)
        
        self.lbl_opacity = QLabel()
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(0, 100)
        self.slider_opacity.setValue(100)
        self.slider_opacity.valueChanged.connect(self.on_slider_changed)
        
        self.spin_opacity = QSpinBox()
        self.spin_opacity.setRange(0, 100)
        self.spin_opacity.setValue(100)
        self.spin_opacity.setSuffix("%")
        self.spin_opacity.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_opacity.valueChanged.connect(self.on_spin_changed)
        self.spin_opacity.setFixedWidth(80)
        self.spin_opacity.setFixedHeight(34)
        self.spin_opacity.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        
        trans_layout.addWidget(self.lbl_opacity)
        trans_layout.addWidget(self.slider_opacity, 1)
        trans_layout.addWidget(self.spin_opacity)
        
        main_layout.addWidget(self.grp_transparency)
        
        # --- BUTTONS ---
        buttons_layout = QHBoxLayout()
        self.btn_multi_ico = QPushButton()
        self.btn_multi_ico.setMinimumHeight(45)
        self.btn_multi_ico.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_multi_ico.setEnabled(False)
        self.btn_multi_ico.clicked.connect(self.create_multi_ico)
        
        self.btn_convert = QPushButton()
        self.btn_convert.setMinimumHeight(45)
        self.btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self.convert_images)
        
        buttons_layout.addWidget(self.btn_multi_ico)
        buttons_layout.addWidget(self.btn_convert)
        main_layout.addLayout(buttons_layout)
        
        self.btn_open = QPushButton()
        self.btn_open.setMinimumHeight(35)
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.setVisible(False)
        self.btn_open.clicked.connect(self.open_folder)
        main_layout.addWidget(self.btn_open)
        
        # --- FOOTER & AUTO-UPDATE ---
        footer_layout = QHBoxLayout()
        self.chk_auto_update = QCheckBox()
        self.chk_auto_update.setChecked(self.settings.value("auto_update", True, type=bool))
        self.chk_auto_update.stateChanged.connect(lambda: self.settings.setValue("auto_update", self.chk_auto_update.isChecked()))
        
        self.lbl_status = QLabel()
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        footer_layout.addWidget(self.chk_auto_update)
        footer_layout.addWidget(self.lbl_status, 1)
        main_layout.addLayout(footer_layout)
        
    def setup_size_presets(self):
        model = QStandardItemModel()
        all_values = []
        
        empty_item = QStandardItem("")
        model.appendRow(empty_item)
        
        for group, items in SIZE_GROUPS.items():
            header = QStandardItem(f"—— {group} ——")
            header.setEnabled(False) 
            header.setData(QColor(150, 150, 150), Qt.ItemDataRole.ForegroundRole) # Grey color
            font = header.font()
            font.setBold(True)
            header.setFont(font)
            header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.appendRow(header)
            
            for item_text in items:
                item = QStandardItem(item_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                model.appendRow(item)
                all_values.append(item_text)

        self.combo_size.setModel(model)
        
        # Completer
        completer = QCompleter(all_values)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.combo_size.setCompleter(completer)
    
    def update_texts(self):
        t = LOCALE[self.current_lang]
        self.setWindowTitle(t["window_title"])
        self.lbl_subtitle.setText(t["subtitle"])
        self.lbl_lang.setText(t["lang"])
        self.lbl_theme.setText(t["theme"])
        self.btn_select.setText(t["btn_select"])
        self.btn_select_folder.setText(t["btn_select_folder"])
        self.btn_clear.setText(t["btn_clear"])
        self.lbl_drop.setText(t["drop_hint"])
        self.grp_input.setTitle(t["grp_input"])
        self.grp_output.setTitle(t["grp_output"])
        self.grp_transparency.setTitle(t["grp_transparency"])
        self.lbl_format.setText(t["lbl_format"])
        self.lbl_size.setText(t["lbl_size"])
        self.lbl_width.setText(t["lbl_width"])
        self.lbl_height.setText(t["lbl_height"])
        self.lbl_opacity.setText(t["lbl_opacity"])
        self.btn_convert.setText(t["btn_convert"])
        self.btn_multi_ico.setText(t["btn_multi_ico"])
        self.btn_open.setText(t["btn_open"])
        self.chk_auto_update.setText(t["auto_update"])
        self.update_status()
    
    def update_status(self):
        t = LOCALE[self.current_lang]
        if not self.file_list:
            self.lbl_status.setText(t["status_wait"])
            self.lbl_status.setStyleSheet("color: gray;")
        else:
            self.lbl_status.setText(t["status_ready"].format(count=len(self.file_list)))
            self.lbl_status.setStyleSheet(f"color: {THEMES[self.current_theme]['accent']};")
    
    def change_language(self, text):
        self.current_lang = "ru" if "Русский" in text else "en"
        self.settings.setValue("language", self.current_lang)
        self.update_texts()
    
    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        theme = THEMES.get(theme_name, THEMES["Dark (Default)"])
        
        self.setStyleSheet(f"""
            QMainWindow, QWidget, QDialog {{
                background-color: {theme['bg']};
                color: {theme['fg']};
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 13px;
            }}
            QGroupBox {{
                border: 1px solid {theme['input_border']};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 14px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
            QPushButton {{
                background-color: {theme['btn_bg']};
                color: {theme['btn_fg']};
                border: 1px solid {theme['input_border']};
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['accent']};
                border-color: {theme['accent']};
            }}
            QPushButton:disabled {{
                background-color: {theme['input_bg']};
                color: #666;
            }}
            QComboBox, QSpinBox, QLineEdit {{
                background-color: {theme['input_bg']};
                color: {theme['input_fg']};
                border: 1px solid {theme['input_border']};
                border-radius: 4px;
                padding: 4px;
            }}
            QComboBox:hover, QSpinBox:hover, QLineEdit:hover {{
                border-color: {theme['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
             QComboBox::down-arrow {{
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {theme['fg']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['input_bg']};
                color: {theme['input_fg']};
                selection-background-color: {theme['accent']};
                outline: 0;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: {theme['btn_bg']};
                border: none;
                width: 18px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: {theme['accent']};
            }}
            QSpinBox::up-arrow {{ width: 0; height: 0; border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 5px solid {theme['fg']}; }}
            QSpinBox::down-arrow {{ width: 0; height: 0; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid {theme['fg']}; }}
            QSlider::groove:horizontal {{
                background: {theme['input_bg']};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {theme['accent']};
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {theme['accent']};
                border-radius: 4px;
            }}
            QCheckBox {{ color: {theme['fg']}; spacing: 5px; }}
            QCheckBox::indicator {{ 
                width: 16px; height: 16px; 
                border: 1px solid {theme['input_border']}; 
                border-radius: 3px; 
            }}
            QCheckBox::indicator:unchecked {{ background-color: {theme['input_bg']}; }}
            QCheckBox::indicator:checked {{ background-color: #27ae60; border: 1px solid #27ae60; }}
            QListWidget {{
                background-color: {theme['input_bg']};
                color: {theme['input_fg']};
                border: 1px solid {theme['input_border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 4px 8px;
                border-radius: 3px;
            }}
            QListWidget::item:selected {{
                background-color: {theme['accent']};
            }}
        """)
        
        self.btn_multi_ico.setStyleSheet(f"background-color: #FF6B35; color: white; border-radius: 6px;")
        self.btn_convert.setStyleSheet(f"background-color: {theme['accent']}; color: white; border-radius: 6px;")
        self.btn_open.setStyleSheet(f"background-color: #2CC985; color: white; border-radius: 6px;")
        self.lbl_title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {theme['accent']};")
        self.update_status()

    def on_size_changed(self, text):
        pass # Allow empty

    def on_slider_changed(self, value):
        self.spin_opacity.blockSignals(True)
        self.spin_opacity.setValue(value)
        self.spin_opacity.blockSignals(False)
    
    def on_spin_changed(self, value):
        self.slider_opacity.blockSignals(True)
        self.slider_opacity.setValue(value)
        self.slider_opacity.blockSignals(False)
    
    def select_files(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tiff *.ico);;All Files (*)")
        if filepaths: self.add_paths(filepaths)
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder: self.add_paths([folder])
    
    def add_paths(self, paths):
        # Create a set of normalized existing paths for fast lookup
        existing_norm = {os.path.normpath(p).lower() for p in self.file_list}
        
        for path in paths:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS:
                            p = os.path.join(root, f)
                            p_norm = os.path.normpath(p).lower()
                            if p_norm not in existing_norm:
                                self.file_list.append(p)
                                existing_norm.add(p_norm)
            elif os.path.isfile(path):
                if os.path.splitext(path)[1].lower() in IMAGE_EXTENSIONS:
                    p_norm = os.path.normpath(path).lower()
                    if p_norm not in existing_norm:
                        self.file_list.append(path)
                        existing_norm.add(p_norm)
        self.refresh_file_list()

    def remove_paths(self, paths_to_remove):
        # Normalize removal list
        remove_norm = {os.path.normpath(p).lower() for p in paths_to_remove}
        # Rebuild file_list keeping only those NOT in removal list
        self.file_list = [
            f for f in self.file_list 
            if os.path.normpath(f).lower() not in remove_norm
        ]
        self.refresh_file_list()

    
    def refresh_file_list(self):
        self.list_files.clear()
        for filepath in self.file_list:
            item = QListWidgetItem(os.path.basename(filepath))
            item.setToolTip(filepath)
            self.list_files.addItem(item)
        has_files = len(self.file_list) > 0
        self.btn_convert.setEnabled(has_files)
        self.btn_multi_ico.setEnabled(has_files)
        self.btn_open.setVisible(False)
        if has_files: self.output_folder = os.path.dirname(self.file_list[0])
        self.update_status()
    
    def clear_files(self):
        self.file_list.clear()
        self.refresh_file_list()
    
    def check_updates(self, silent=False):
        self.checker = UpdateCheckerThread()
        self.checker.update_found.connect(self.show_update_dialog)
        self.checker.start()

    def show_update_dialog(self, ver, url, body):
        dlg = UpdateDialog(self, ver, url, body, self.current_lang)
        dlg.exec()

    def get_unique_filename(self, filepath):
        if not os.path.exists(filepath):
            return filepath
        base, ext = os.path.splitext(filepath)
        n = 1
        while True:
            new_path = f"{base}_{n}{ext}"
            if not os.path.exists(new_path):
                return new_path
            n += 1

    def create_multi_ico(self):
        if not self.file_list: return
        t = LOCALE[self.current_lang]
        total = len(self.file_list)
        success = 0
        errors = []
        # Descending Order (256 -> 16) with base = 256.
        # Using 256 as the base image ensures all layers are saved correctly by Pillow.
        ico_sizes = [(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)]
        
        for i, filepath in enumerate(self.file_list):
            self.lbl_status.setText(t["status_proc"].format(current=i+1, total=total))
            QApplication.processEvents()
            try:
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                output_dir = os.path.dirname(filepath)
                # Output filename for Multi-ICO
                out_path = os.path.join(output_dir, f"{base_name}.ico")
                out_path = self.get_unique_filename(out_path)

                with Image.open(filepath) as img:
                    img = img.convert("RGBA")
                    op = self.spin_opacity.value()
                    if op < 100:
                        # Process alpha
                        r, g, b, a = img.split()
                        a = a.point(lambda p: int(p * op / 100))
                        img = Image.merge("RGBA", (r, g, b, a))
                    
                    # We create each frame directly from the source for maximum sharpness.
                    # Order is critical: 64x64 first (user request), then 256 (desktop), 
                    # then smaller sizes (for taskbar and list views).
                    s64 = img.resize((64, 64), Image.Resampling.LANCZOS)
                    s256 = img.resize((256, 256), Image.Resampling.LANCZOS)
                    s128 = img.resize((128, 128), Image.Resampling.LANCZOS)
                    s48 = img.resize((48, 48), Image.Resampling.LANCZOS)
                    s32 = img.resize((32, 32), Image.Resampling.LANCZOS)
                    s16 = img.resize((16, 16), Image.Resampling.LANCZOS)

                    # Save: 64 is the primary frame (index 0).
                    # 'append_images' handles the rest of the multi-size structure.
                    s64.save(out_path, format='ICO', append_images=[s256, s128, s48, s32, s16])
                    
                success += 1
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {str(e)}")
            
        if errors:
             QMessageBox.warning(self, t["error_gen"], "\n".join(errors))

        self.lbl_status.setText(t["status_done"].format(count=success))
        self.lbl_status.setStyleSheet("color: #2CC985;")
        self.btn_open.setVisible(True)

    def convert_images(self):
        if not self.file_list: return
        t = LOCALE[self.current_lang]
        total = len(self.file_list)
        success = 0
        errors = []
        
        fmt_name = self.combo_format.currentText()
        if fmt_name not in OUTPUT_FORMATS:
            QMessageBox.critical(self, "Error", f"Invalid format: {fmt_name}")
            return
            
        fmt = OUTPUT_FORMATS[fmt_name]
        
        # Logic: Width/Height > Preset > Skip/Error
        w = self.spin_width.value()
        h = self.spin_height.value()
        
        if w == 0 or h == 0:
            # Try parse from combo
            txt = self.combo_size.currentText()
            if "×" in txt:
                try:
                    parts = txt.split("×")
                    w = int(parts[0].strip())
                    h = int(parts[1].strip())
                except: w, h = 0, 0
        
        for i, filepath in enumerate(self.file_list):
            self.lbl_status.setText(t["status_proc"].format(current=i+1, total=total))
            QApplication.processEvents()
            try:
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                output_dir = os.path.dirname(filepath)
                
                with Image.open(filepath) as img:
                    img = img.convert("RGBA")
                    op = self.spin_opacity.value()
                    if op < 100:
                        r, g, b, a = img.split()
                        a = a.point(lambda p: int(p * op / 100))
                        img = Image.merge("RGBA", (r, g, b, a))
                    
                    target_w, target_h = w, h
                    if target_w == 0 or target_h == 0:
                        target_w, target_h = img.size # Keep original
                    
                    # Resize
                    img_resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    
                    # Generate Output Path
                    if fmt_name == "ICO (Single size)":
                        suffix = f"_{target_w}x{target_h}"
                    else:
                        suffix = f"_{target_w}x{target_h}"
                    
                    out_path = os.path.join(output_dir, f"{base_name}{suffix}{fmt['ext']}")
                    out_path = self.get_unique_filename(out_path)
                    
                    if fmt_name == "ICO (Single size)":
                         img_resized.save(out_path, format='ICO', sizes=[(target_w, target_h)])
                    else:
                        if not fmt["supports_alpha"]:
                            bg = Image.new("RGB", img_resized.size, (255, 255, 255))
                            bg.paste(img_resized, mask=img_resized.split()[3])
                            img_resized = bg
                        
                        if fmt["format"] == "JPEG": 
                            img_resized.save(out_path, format=fmt["format"], quality=95)
                        else: 
                            img_resized.save(out_path, format=fmt["format"])
                
                success += 1
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {str(e)}")
        
        if errors:
            QMessageBox.warning(self, t["error_gen"], "\n".join(errors))
            
        self.lbl_status.setText(t["status_done"].format(count=success))
        self.lbl_status.setStyleSheet("color: #2CC985;")
        self.btn_open.setVisible(True)


    def open_folder(self):
        if self.output_folder and os.path.exists(self.output_folder):
            if platform.system() == "Windows":
                os.startfile(self.output_folder)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.output_folder])
            else:
                subprocess.Popen(["xdg-open", self.output_folder])

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())