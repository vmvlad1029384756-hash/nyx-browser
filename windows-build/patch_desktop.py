from __future__ import annotations

import os
import re
import shutil
import struct
import sys
from pathlib import Path

DATA_PATHS = r'''from __future__ import annotations
import os
import shutil
import sys
from pathlib import Path

DATA_LOCATION_WARNING = ""
APP_NAME = "NYX Browser"

def _copy_data(source: Path, destination: Path) -> bool:
    global DATA_LOCATION_WARNING
    if not source.is_dir():
        return True
    if destination.exists() and any(destination.iterdir()):
        return True
    staging = destination.with_name(destination.name + ".migration-temp")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if staging.exists():
            shutil.rmtree(staging)
        shutil.copytree(source, staging, dirs_exist_ok=False)
        if destination.exists():
            destination.rmdir()
        staging.replace(destination)
        return True
    except OSError as exc:
        shutil.rmtree(staging, ignore_errors=True)
        DATA_LOCATION_WARNING = (
            "Не удалось перенести старые данные NYX на выбранный диск. "
            "Чтобы сохранить профиль, браузер временно продолжит использовать "
            f"прежнюю папку. Подробности: {exc}"
        )
        return False

def resolve_app_dir(executable_dir=None, environ=None, is_windows=None) -> Path:
    global DATA_LOCATION_WARNING
    env = os.environ if environ is None else environ
    windows = (os.name == "nt") if is_windows is None else bool(is_windows)
    legacy = Path(env.get("LOCALAPPDATA") or Path.home()) / APP_NAME
    if not windows or executable_dir is None:
        return legacy
    marker = Path(executable_dir) / "nyx-user-data-path.txt"
    try:
        text = marker.read_text(encoding="utf-8").strip()
        selected = Path(text).expanduser()
        if not text or not selected.is_absolute():
            return legacy
    except (OSError, ValueError):
        return legacy
    try:
        if selected.resolve() != legacy.resolve():
            if not _copy_data(legacy, selected):
                return legacy
            _copy_data(Path.home() / "Downloads" / APP_NAME, selected / "Downloads")
    except OSError as exc:
        DATA_LOCATION_WARNING = f"Не удалось подготовить папку данных NYX: {exc}"
        return legacy
    return selected

_EXE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else None
APP_DIR = resolve_app_dir(_EXE_DIR)
APP_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR = APP_DIR / "Downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
'''

DEFAULT_BROWSER = r'''from __future__ import annotations
import sys
from pathlib import Path
from urllib.parse import quote

APP_NAME = "NYX Browser"
APP_KEY = r"Software\Clients\StartMenuInternet\NYX Browser"
CAPABILITIES = APP_KEY + r"\Capabilities"

def register_default_browser(executable=None) -> bool:
    """Register NYX as a candidate handler; never modify protected UserChoice keys."""
    if sys.platform != "win32":
        return False
    import winreg
    exe = str(Path(executable or sys.executable).resolve())
    quoted = f'"{exe}"'
    open_command = f'{quoted} "%1"'
    icon = f'{quoted},0'

    def write(key_path, name, value):
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

    write(APP_KEY, "", APP_NAME)
    write(APP_KEY + r"\DefaultIcon", "", icon)
    write(APP_KEY + r"\shell\open\command", "", quoted)
    write(CAPABILITIES, "ApplicationName", APP_NAME)
    write(CAPABILITIES, "ApplicationDescription", "NYX Browser — тёмный браузер для Windows")
    write(CAPABILITIES, "ApplicationIcon", icon)
    for ext in (".htm", ".html"):
        write(CAPABILITIES + r"\FileAssociations", ext, "NYXBrowserHTML")
    for scheme in ("http", "https"):
        write(CAPABILITIES + r"\URLAssociations", scheme, "NYXBrowserURL")
    write(r"Software\Classes\NYXBrowserHTML", "", "NYX Browser HTML Document")
    write(r"Software\Classes\NYXBrowserHTML\DefaultIcon", "", icon)
    write(r"Software\Classes\NYXBrowserHTML\shell\open\command", "", open_command)
    write(r"Software\Classes\NYXBrowserURL", "", "NYX Browser URL")
    write(r"Software\Classes\NYXBrowserURL", "URL Protocol", "")
    write(r"Software\Classes\NYXBrowserURL\DefaultIcon", "", icon)
    write(r"Software\Classes\NYXBrowserURL\shell\open\command", "", open_command)
    write(r"Software\RegisteredApplications", APP_NAME, CAPABILITIES)
    return True

def open_default_apps_settings() -> bool:
    if sys.platform != "win32":
        return False
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QDesktopServices
    direct = QUrl("ms-settings:defaultapps?registeredAppUser=" + quote(APP_NAME, safe=""))
    return QDesktopServices.openUrl(direct) or QDesktopServices.openUrl(QUrl("ms-settings:defaultapps"))
'''

TRANSPARENT_SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="tile" x1="0" y1="0" x2="0.9" y2="1">
      <stop offset="0" stop-color="#24202e"/><stop offset="0.55" stop-color="#100d1d"/><stop offset="1" stop-color="#080611"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#d7a5ff"/><stop offset="0.5" stop-color="#8e4be9"/><stop offset="1" stop-color="#452080"/>
    </linearGradient>
    <linearGradient id="front" x1="0" y1="0" x2="0.85" y2="1">
      <stop offset="0" stop-color="#eadcff"/><stop offset="0.28" stop-color="#b58af5"/><stop offset="0.62" stop-color="#8b42ef"/><stop offset="1" stop-color="#5420a8"/>
    </linearGradient>
    <linearGradient id="side" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#5e2a9e"/><stop offset="0.45" stop-color="#a75aff"/><stop offset="1" stop-color="#34135f"/>
    </linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="#9a42ff" stop-opacity=".34"/><stop offset="1" stop-color="#9a42ff" stop-opacity="0"/></radialGradient>
    <filter id="soft"><feGaussianBlur stdDeviation="9"/></filter>
  </defs>
  <ellipse cx="128" cy="130" rx="116" ry="116" fill="url(#glow)" filter="url(#soft)"/>
  <rect x="25" y="25" width="206" height="206" rx="27" fill="url(#tile)" stroke="url(#edge)" stroke-width="2.2"/>
  <!-- Faceted, beveled N redrawn from the supplied NYX avatar reference. -->
  <path d="M70 70H104V186H70Z" fill="url(#side)" stroke="#b978ff" stroke-width="1.5"/>
  <path d="M152 70H186V186H152Z" fill="url(#side)" stroke="#b978ff" stroke-width="1.5"/>
  <path d="M70 70H104L186 186H152Z" fill="url(#front)" stroke="#e2c5ff" stroke-width="1.5"/>
  <path d="M70 70L104 70L186 186L152 186Z" fill="none" stroke="#f2e3ff" stroke-opacity=".65" stroke-width="1.7"/>
  <path d="M70 70H104L152 118V151Z" fill="#eadcff" opacity=".20"/>
  <path d="M152 70H186L152 105Z" fill="#f0e3ff" opacity=".58"/>
  <path d="M70 151L104 118V186H70Z" fill="#54218f" opacity=".55"/>
  <path d="M152 186H186V151Z" fill="#35135f" opacity=".52"/>
  <path d="M70 70H104L186 186H152" fill="none" stroke="#f0dfff" stroke-width="1.7" opacity=".9"/>
</svg>
'''

def write_ico(svg_path: Path, ico_path: Path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QByteArray, QBuffer, QIODevice, Qt
    from PySide6.QtGui import QGuiApplication, QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer
    _app = QGuiApplication.instance() or QGuiApplication([])
    renderer = QSvgRenderer(str(svg_path))
    if not renderer.isValid():
        raise RuntimeError("NYX SVG icon is invalid")
    frames = []
    for size in (16, 24, 32, 48, 64, 128, 256):
        image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        raw = QByteArray()
        buffer = QBuffer(raw)
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly) or not image.save(buffer, "PNG"):
            raise RuntimeError("Could not render NYX icon PNG")
        frames.append((size, bytes(raw)))
        buffer.close()
    header = struct.pack("<HHH", 0, 1, len(frames))
    offset = 6 + 16 * len(frames)
    entries = bytearray()
    payload = bytearray()
    for size, png in frames:
        dim = 0 if size == 256 else size
        entries.extend(struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset))
        payload.extend(png)
        offset += len(png)
    ico_path.write_bytes(header + entries + payload)

def patch(root: Path):
    core, ui, assets, tests = (root / "nyx" / "core", root / "nyx" / "ui",
                               root / "nyx" / "assets", root / "tests")
    (core / "data_paths.py").write_text(DATA_PATHS, encoding="utf-8")
    (core / "default_browser.py").write_text(DEFAULT_BROWSER, encoding="utf-8")
    svg_path = assets / "nyx.svg"
    svg_path.write_text(TRANSPARENT_SVG, encoding="utf-8")
    write_ico(svg_path, assets / "nyx.ico")

    storage_path = core / "storage.py"
    storage = storage_path.read_text(encoding="utf-8")
    old = """APP_DIR = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'NYX Browser'
APP_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = APP_DIR / 'settings.json'
DB_FILE = APP_DIR / 'nyx.db'
DOWNLOADS_DIR = Path.home() / 'Downloads' / 'NYX Browser'
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
"""
    new = """# APP_DIR remains NYX Browser data; source-run fallback is %LOCALAPPDATA%\\NYX Browser.
from nyx.core.data_paths import APP_DIR, DOWNLOADS_DIR
CONFIG_FILE = APP_DIR / 'settings.json'
DB_FILE = APP_DIR / 'nyx.db'
"""
    if old not in storage:
        raise RuntimeError("Original storage data path block not found")
    storage = storage.replace(old, new, 1)
    old_return = """    except (OSError, json.JSONDecodeError):
        pass
    return data
"""
    new_return = """    except (OSError, json.JSONDecodeError):
        pass
    legacy_downloads = str(Path.home() / 'Downloads' / 'NYX Browser')
    if data.get('download_dir') == legacy_downloads:
        data['download_dir'] = str(DOWNLOADS_DIR)
    return data
"""
    if old_return not in storage:
        raise RuntimeError("Settings return block not found")
    storage_path.write_text(storage.replace(old_return, new_return, 1), encoding="utf-8")

    main_path = root / "nyx" / "main.py"
    main = main_path.read_text(encoding="utf-8")
    main = main.replace("from PySide6.QtWidgets import QApplication\n",
                        "from PySide6.QtWidgets import QApplication, QMessageBox\nfrom PySide6.QtCore import QTimer, QUrl\n", 1)
    main = main.replace("from nyx.core.storage import load_settings, init_db\n",
                        "from nyx.core.storage import load_settings, init_db\nfrom nyx.core.data_paths import DATA_LOCATION_WARNING\nfrom nyx.core.default_browser import register_default_browser\n", 1)
    main = re.sub(r"1\.0\.0-dev\.3\.\d+", "1.0.0-dev.3.9", main)
    old_start = """    window=MainWindow();window.show()
    sys.exit(app.exec())
"""
    new_start = """    window=MainWindow();window.show()
    try:
        register_default_browser()
    except Exception:
        pass
    if DATA_LOCATION_WARNING:
        QMessageBox.warning(window, 'Папка данных NYX', DATA_LOCATION_WARNING)
    launch_target = next((arg for arg in sys.argv[1:] if arg.startswith(('http://', 'https://', 'file://'))), None)
    if launch_target is None:
        from pathlib import Path
        launch_target = next((Path(arg).resolve().as_uri() for arg in sys.argv[1:] if Path(arg).exists()), None)
    if launch_target:
        QTimer.singleShot(0, lambda: window.current_tab().active_view.setUrl(QUrl.fromUserInput(launch_target)))
    sys.exit(app.exec())
"""
    if old_start not in main:
        raise RuntimeError("App startup block not found")
    main_path.write_text(main.replace(old_start, new_start, 1), encoding="utf-8")

    window_path = ui / "main_window.py"
    window = window_path.read_text(encoding="utf-8")
    window = window.replace(
        "from PySide6.QtCore import Qt, QUrl, QUrlQuery, Signal, QEvent, QTimer, QStringListModel, QPropertyAnimation, QEasingCurve, QSize\\n",
        "from PySide6.QtCore import Qt, QUrl, QUrlQuery, Signal, QObject, QEvent, QTimer, QStringListModel, QPropertyAnimation, QEasingCurve, QSize\\n",
        1,
    )
    window = window.replace("from nyx.core.password_vault import list_credentials, get_password\n",
                            "from nyx.core.password_vault import list_credentials, get_password\nfrom nyx.core.default_browser import register_default_browser, open_default_apps_settings\n", 1)
    window = re.sub(r"1\.0\.0-dev\.3\.\d+", "1.0.0-dev.3.9", window)
    old_toolbar = """        self.incognito_btn=self._button('◉','Новое окно инкогнито · Ctrl+Shift+N',self.open_incognito_window); self.incognito_btn.setObjectName('toolbarActionButton'); self.toolbar.addWidget(self.incognito_btn)
        self.downloads_btn.setFixedSize(40,40); self.extensions_btn.setFixedSize(40,40); self.incognito_btn.setFixedSize(40,40)
"""
    new_toolbar = """        self.incognito_btn=self._button('◉','Новое окно инкогнито · Ctrl+Shift+N',self.open_incognito_window); self.incognito_btn.setObjectName('toolbarActionButton'); self.toolbar.addWidget(self.incognito_btn)
        self.default_browser_btn=self._button('◎','Сделать NYX браузером по умолчанию',self.set_as_default_browser); self.default_browser_btn.setObjectName('toolbarActionButton'); self.toolbar.addWidget(self.default_browser_btn)
        self.downloads_btn.setFixedSize(40,40); self.extensions_btn.setFixedSize(40,40); self.incognito_btn.setFixedSize(40,40); self.default_browser_btn.setFixedSize(40,40)
"""
    if old_toolbar not in window:
        raise RuntimeError("Browser toolbar button block not found")
    window = window.replace(old_toolbar, new_toolbar, 1)
    anchor = "    def open_settings(self, initial_page=0):\n"
    method = """    def set_as_default_browser(self):
        if sys.platform != 'win32':
            QMessageBox.information(self, 'Браузер по умолчанию', 'Эта настройка доступна в Windows.')
            return
        try:
            register_default_browser()
            if open_default_apps_settings():
                QMessageBox.information(self, 'Браузер по умолчанию',
                    'Открыты параметры Windows. Найди NYX Browser и нажми «Использовать по умолчанию». Windows попросит подтвердить выбор — это обязательный системный шаг.')
            else:
                QMessageBox.warning(self, 'Браузер по умолчанию',
                    'Не удалось открыть параметры Windows. Открой Параметры → Приложения → Приложения по умолчанию и выбери NYX Browser.')
        except Exception as exc:
            QMessageBox.warning(self, 'Браузер по умолчанию', f'Не удалось зарегистрировать NYX в Windows: {exc}')

"""
    if anchor not in window:
        raise RuntimeError("MainWindow settings method not found")
    window = window.replace(anchor, method + anchor, 1)
    needle = "('⚙ Настройки',self.open_settings),('▦ Spaces',self.open_spaces)"
    repl = "('🌐 Браузер по умолчанию',self.set_as_default_browser),('⚙ Настройки',self.open_settings),('▦ Spaces',self.open_spaces)"
    if needle not in window:
        raise RuntimeError("Tools menu list not found")
    window_path.write_text(window.replace(needle, repl, 1), encoding="utf-8")

    # Qt WebEngine enables the Fullscreen API at profile level, but a page must
    # also accept fullScreenRequested and the browser chrome must get out of the way.
    browser_tab_path = ui / "browser_tab.py"
    browser_tab = browser_tab_path.read_text(encoding="utf-8")
    old_class = "class BrowserTab(QWidget):"
    new_class = """class NYXWebEnginePage(QWebEnginePage):
    def __init__(self, profile, view, browser_tab):
        super().__init__(profile, view)
        self.browser_tab = browser_tab

    def createWindow(self, window_type):
        # Chromium calls this for target=_blank and window.open().
        return self.browser_tab.create_popup_page()


class BrowserTab(QWidget):
    fullScreenRequested = Signal(object, object)"""
    if old_class not in browser_tab:
        raise RuntimeError("BrowserTab class declaration not found")
    browser_tab = browser_tab.replace(old_class, new_class, 1)
    browser_tab = browser_tab.replace(
        "    def __init__(self, profile=None, parent=None, private_mode: bool = False):",
        "    def __init__(self, profile=None, parent=None, private_mode: bool = False, load_home: bool = True):",
        1,
    )
    browser_tab = browser_tab.replace(
        "        self.load_home()\n",
        "        if load_home:\n            self.load_home()\n",
        1,
    )
    browser_tab = browser_tab.replace(
        "            page = QWebEnginePage(self.profile, view)",
        "            page = NYXWebEnginePage(self.profile, view, self)",
        1,
    )
    old_popup_anchor = "    def _new_view(self):\n"
    popup_method = """    def create_popup_page(self):
        main_window = self.window()
        if hasattr(main_window, "create_popup_tab"):
            return main_window.create_popup_tab()
        return None

"""
    if old_popup_anchor not in browser_tab:
        raise RuntimeError("BrowserTab view factory anchor not found")
    browser_tab = browser_tab.replace(old_popup_anchor, popup_method + old_popup_anchor, 1)
    old_page = "        page=view.page()\n"
    new_page = """        page=view.page()
        if hasattr(page, 'fullScreenRequested'):
            page.fullScreenRequested.connect(
                lambda request, v=view: self.fullScreenRequested.emit(v, request)
            )
"""
    if old_page not in browser_tab:
        raise RuntimeError("BrowserTab page initialization not found")
    browser_tab_path.write_text(browser_tab.replace(old_page, new_page, 1), encoding="utf-8")

    old_tab_start = "        tab=BrowserTab(profile=self.profile, private_mode=self.private_mode)\n"
    new_tab_start = """        tab=BrowserTab(profile=self.profile, private_mode=self.private_mode, load_home=load_home)
        tab.fullScreenRequested.connect(self.handle_web_fullscreen_request)
"""
    if old_tab_start not in window:
        raise RuntimeError("MainWindow new-tab initialization not found")
    window = window.replace(old_tab_start, new_tab_start, 1)

    fullscreen_methods = '''    def handle_web_fullscreen_request(self, view, request):
        """Honor HTML5 fullscreen requests (YouTube, video players and web apps)."""
        try:
            entering = bool(request.toggleOn())
            request.accept()
        except Exception:
            try:
                request.reject()
            except Exception:
                pass
            return

        if entering:
            if getattr(self, "_web_fullscreen_active", False):
                return
            self._web_fullscreen_active = True
            self._web_fullscreen_was_maximized = self.isMaximized()
            widgets = {
                "title_bar": self.title_bar,
                "tab_row": self.tabs.tab_row,
                "toolbar": self.toolbar,
                "sidebar": self.sidebar,
                "status": self.status,
            }
            self._web_fullscreen_visibility = {
                name: widget.isVisible() for name, widget in widgets.items()
            }
            for widget in widgets.values():
                widget.hide()
            self.showFullScreen()
            view.setFocus()
            return

        if not getattr(self, "_web_fullscreen_active", False):
            return
        self._web_fullscreen_active = False
        if getattr(self, "_web_fullscreen_was_maximized", False):
            self.showMaximized()
        else:
            self.showNormal()
        visibility = getattr(self, "_web_fullscreen_visibility", {})
        widgets = {
            "title_bar": self.title_bar,
            "tab_row": self.tabs.tab_row,
            "toolbar": self.toolbar,
            "sidebar": self.sidebar,
            "status": self.status,
        }
        for name, widget in widgets.items():
            widget.setVisible(visibility.get(name, True))
        self._position_sidebar()

'''
    fullscreen_methods += """    def create_popup_tab(self):
        # Called by QWebEnginePage.createWindow for target=_blank / window.open.
        self.new_tab(load_home=False)
        tab = self.current_tab()
        return tab.view.page() if tab else None

"""
    window = window.replace(
        "    def new_tab(self,url:QUrl|None=None):",
        "    def new_tab(self,url:QUrl|None=None, load_home: bool = True):",
        1,
    )
    anchor_method = "    def new_tab(self,url:QUrl|None=None, load_home: bool = True):\n"
    if anchor_method not in window:
        raise RuntimeError("MainWindow new_tab method anchor not found")
    window = window.replace(anchor_method, fullscreen_methods + anchor_method, 1)
    resize_helper = r'''

class NativeWindowEdgeResizer(QObject):
    """Restore native Windows resize borders for NYX's frameless window."""
    def __init__(self, window):
        super().__init__(window)
        self.window = window

    def _edges_at(self, point):
        rect = self.window.frameGeometry()
        x = point.x() - rect.left()
        y = point.y() - rect.top()
        margin = 9
        edges = Qt.Edge(0)
        if x <= margin: edges |= Qt.Edge.LeftEdge
        elif x >= rect.width() - margin: edges |= Qt.Edge.RightEdge
        if y <= margin: edges |= Qt.Edge.TopEdge
        elif y >= rect.height() - margin: edges |= Qt.Edge.BottomEdge
        return edges

    def eventFilter(self, watched, event):
        try:
            if not hasattr(watched, "window") or watched.window() is not self.window:
                return False
            if self.window.isMaximized() or self.window.isFullScreen():
                return False
            kind = event.type()
            if kind not in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseMove):
                return False
            point = event.globalPosition().toPoint()
            edges = self._edges_at(point)
            if kind == QEvent.Type.MouseMove:
                if edges == (Qt.Edge.LeftEdge | Qt.Edge.TopEdge) or edges == (Qt.Edge.RightEdge | Qt.Edge.BottomEdge):
                    self.window.setCursor(Qt.CursorShape.SizeFDiagCursor)
                elif edges == (Qt.Edge.RightEdge | Qt.Edge.TopEdge) or edges == (Qt.Edge.LeftEdge | Qt.Edge.BottomEdge):
                    self.window.setCursor(Qt.CursorShape.SizeBDiagCursor)
                elif edges & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
                    self.window.setCursor(Qt.CursorShape.SizeHorCursor)
                elif edges & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
                    self.window.setCursor(Qt.CursorShape.SizeVerCursor)
                else:
                    self.window.unsetCursor()
                return False
            if event.button() == Qt.MouseButton.LeftButton and edges:
                handle = self.window.windowHandle()
                if handle and handle.startSystemResize(edges):
                    event.accept()
                    return True
        except Exception:
            return False
        return False

'''
    if "class NativeWindowEdgeResizer(QObject):" not in window:
        class_anchor = "class MainWindow(QMainWindow):"
        if class_anchor not in window:
            raise RuntimeError("MainWindow class anchor not found for native resizing")
        window = window.replace(class_anchor, resize_helper + "\n" + class_anchor, 1)
    init_anchor = "        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)\n"
    init_patch = """        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        # QApplication-level filtering catches mouse presses on every child widget at the true outer edge.
        self._native_edge_resizer = NativeWindowEdgeResizer(self)
        app_instance = QApplication.instance()
        if app_instance is not None:
            app_instance.installEventFilter(self._native_edge_resizer)
"""
    if init_anchor not in window:
        raise RuntimeError("Frameless window setup anchor not found")
    window = window.replace(init_anchor, init_patch, 1)

    toolbar_anchor = """        self.extensions_btn=self._button('◈','Расширения',self.open_extensions); self.extensions_btn.setObjectName('toolbarActionButton'); self.toolbar.addWidget(self.extensions_btn)
"""
    toolbar_patch = toolbar_anchor + """        self.youbusta_toolbar_btn=self._button('Ю','ЮБуст для YouTube · установка и настройки',self.open_extensions); self.youbusta_toolbar_btn.setObjectName('toolbarActionButton'); self.toolbar.addWidget(self.youbusta_toolbar_btn)
"""
    if toolbar_anchor not in window:
        raise RuntimeError("Extensions toolbar button anchor not found")
    window = window.replace(toolbar_anchor, toolbar_patch, 1)
    window = window.replace(
        "self.downloads_btn.setFixedSize(40,40); self.extensions_btn.setFixedSize(40,40); self.incognito_btn.setFixedSize(40,40)",
        "self.downloads_btn.setFixedSize(40,40); self.extensions_btn.setFixedSize(40,40); self.youbusta_toolbar_btn.setFixedSize(40,40); self.incognito_btn.setFixedSize(40,40)",
        1,
    )
    window_path.write_text(window, encoding="utf-8")

    # Reliable URL detection, persistent proxy credentials, and modern-site compatibility.
    (core / "navigation.py").write_text(r'''"""Address-bar URL detection and search routing."""
from __future__ import annotations
import re
from urllib.parse import quote
from PySide6.QtCore import QUrl

_SCHEME = re.compile(r"^(?:https?|ftp|file|about):", re.IGNORECASE)
_DOMAIN = re.compile(r"^(?:localhost|(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|\[[0-9a-fA-F:]+\]|(?:\d{1,3}\.){3}\d{1,3})(?::\d{1,5})?$")
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
    "Bing": "https://www.bing.com/search?q=",
    "Brave Search": "https://search.brave.com/search?q=",
}
def looks_like_url(value: str) -> bool:
    text = (value or "").strip()
    if not text:
        return False
    if _SCHEME.match(text):
        return True
    if any(ch.isspace() for ch in text):
        return False
    authority = re.split(r"[/\?#]", text, maxsplit=1)[0]
    return bool(_DOMAIN.fullmatch(authority))
def resolve_address_input(value: str, engine: str = "Google") -> tuple[QUrl, bool]:
    """Return (destination, is_search); URL input is never sent to search."""
    text = (value or "").strip()
    if looks_like_url(text):
        target = text if _SCHEME.match(text) else "https://" + text
        return QUrl.fromUserInput(target), False
    base = SEARCH_ENGINES.get(engine, SEARCH_ENGINES["Google"])
    return QUrl(base + quote(text, safe="")), True
''', encoding="utf-8")

    (core / "proxy.py").write_text(r'''from __future__ import annotations
from PySide6.QtNetwork import QNetworkProxy
try:
    import keyring
except Exception:
    keyring = None

KEYRING_SERVICE = "NYX Browser Proxy"
def proxy_credential_key(settings: dict) -> str:
    kind = settings.get("proxy_type", settings.get("type", "HTTP"))
    return "|".join((str(kind).upper(), str(settings.get("proxy_host", settings.get("host", ""))).strip().lower(), str(int(settings.get("proxy_port", settings.get("port", 0)) or 0))))
def save_proxy_password(settings: dict, password: str) -> bool:
    if not password or keyring is None or not (settings.get("proxy_host") or settings.get("host")):
        return False
    try:
        keyring.set_password(KEYRING_SERVICE, proxy_credential_key(settings), password)
        return True
    except Exception:
        return False
def get_proxy_password(settings: dict) -> str:
    direct = str(settings.get("proxy_password", ""))
    if direct:
        return direct
    if keyring is None or not (settings.get("proxy_host") or settings.get("host")):
        return ""
    try:
        return keyring.get_password(KEYRING_SERVICE, proxy_credential_key(settings)) or ""
    except Exception:
        return ""
def configure_proxy(settings: dict) -> None:
    """Configure Qt WebEngine's Chromium network stack before profiles are created."""
    if not settings.get("proxy_enabled"):
        QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
        return
    host = str(settings.get("proxy_host", "")).strip()
    try:
        port = int(settings.get("proxy_port") or 0)
    except (TypeError, ValueError):
        port = 0
    if not host or not (1 <= port <= 65535):
        QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
        return
    proxy_type = str(settings.get("proxy_type", "HTTP")).upper()
    kind = QNetworkProxy.ProxyType.Socks5Proxy if proxy_type == "SOCKS5" else QNetworkProxy.ProxyType.HttpProxy
    proxy = QNetworkProxy(kind, host, port)
    username = str(settings.get("proxy_username", "")).strip()
    password = get_proxy_password(settings)
    if username:
        proxy.setUser(username)
    if password:
        proxy.setPassword(password)
    QNetworkProxy.setApplicationProxy(proxy)
''', encoding="utf-8")

    window = window.replace(
        "from nyx.core.proxy import configure_proxy\n",
        "from nyx.core.proxy import configure_proxy, get_proxy_password, save_proxy_password\n"
        "from nyx.core.navigation import resolve_address_input\n",
        1,
    )
    profile_anchor = "        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)"
    profile_patch = """        # Remove the QtWebEngine product token while preserving the actual Chromium version.
        try:
            ua = re.sub(r"\\s+QtWebEngine/[^\\s]+", "", self.profile.httpUserAgent()).strip()
            self.profile.setHttpUserAgent(ua)
        except Exception:
            pass
        self.profile.setProperty('nyxProxyUsername', str(self.settings.get('proxy_username', '')).strip())
        self.profile.setProperty('nyxProxyPassword', get_proxy_password(self.settings))
        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)"""
    if profile_anchor not in window:
        raise RuntimeError("WebEngine profile settings anchor not found")
    window = window.replace(profile_anchor, profile_patch, 1)

    old_address = """        part=raw.split('/')[0]; is_url='.' in part and ' ' not in raw
        if is_url:
            url=QUrl.fromUserInput(raw if '://' in raw else 'https://'+raw)
        else:
            engine=self.settings.get('search_engine','Google')
            engines={'Google':'https://www.google.com/search?q=','DuckDuckGo':'https://duckduckgo.com/?q=','Bing':'https://www.bing.com/search?q=','Brave Search':'https://search.brave.com/search?q='}
            base=engines.get(engine,engines['Google'])
            url=QUrl(base+QUrl.toPercentEncoding(raw).data().decode('ascii'))
            record_search(raw, engine, private=self.private_mode)"""
    new_address = """        engine=self.settings.get('search_engine','Google')
        url,is_search=resolve_address_input(raw, engine)
        if is_search:
            record_search(raw, engine, private=self.private_mode)"""
    if old_address not in window:
        raise RuntimeError("Address bar routing block not found")
    window = window.replace(old_address, new_address, 1)

    save_anchor = """            persisted=dict(self.settings); persisted.pop('proxy_password',None)
            save_settings(persisted); self.refresh_addons(); self.apply_theme()"""
    save_patch = """            if self.settings.get('proxy_password'):
                save_proxy_password(self.settings, self.settings.get('proxy_password', ''))
            self.profile.setProperty('nyxProxyUsername', str(self.settings.get('proxy_username', '')).strip())
            self.profile.setProperty('nyxProxyPassword', get_proxy_password(self.settings))
            persisted=dict(self.settings); persisted.pop('proxy_password',None)
            save_settings(persisted); self.refresh_addons(); self.apply_theme()"""
    if save_anchor not in window:
        raise RuntimeError("Settings save anchor not found")
    window = window.replace(save_anchor, save_patch, 1)
    window = window.replace(
        "Настройки сохранены. Поиск и оформление обновлены; прокси применится после перезапуска.",
        "Настройки сохранены. Поиск и оформление обновлены; для смены прокси перезапусти NYX."
    )
    window_path.write_text(window, encoding="utf-8")

    browser_tab_path = ui / "browser_tab.py"
    browser_tab = browser_tab_path.read_text(encoding="utf-8")
    old_auth = """    def _proxy_authentication(self,url,authenticator,proxy_host=''):
        username,ok=QInputDialog.getText(self,'Авторизация прокси',f'Логин для прокси {proxy_host or url.host()}:')
        if not ok: return
        password,ok=QInputDialog.getText(self,'Авторизация прокси','Пароль:',QLineEdit.EchoMode.Password)
        if ok:
            authenticator.setUser(username); authenticator.setPassword(password)"""
    new_auth = """    def _proxy_authentication(self,url,authenticator,proxy_host=''):
        username = str(self.profile.property('nyxProxyUsername') or '') if self.profile else ''
        password = str(self.profile.property('nyxProxyPassword') or '') if self.profile else ''
        if username and password:
            authenticator.setUser(username); authenticator.setPassword(password)
            return
        username,ok=QInputDialog.getText(self,'Авторизация прокси',f'Логин для прокси {proxy_host or url.host()}:',text=username)
        if not ok: return
        password,ok=QInputDialog.getText(self,'Авторизация прокси','Пароль:',QLineEdit.EchoMode.Password)
        if ok:
            authenticator.setUser(username); authenticator.setPassword(password)"""
    if old_auth not in browser_tab:
        raise RuntimeError("Proxy authentication handler not found")
    browser_tab_path.write_text(browser_tab.replace(old_auth, new_auth, 1), encoding="utf-8")

    dialogs_path = ui / "dialogs.py"
    dialogs = dialogs_path.read_text(encoding="utf-8")
    dialogs = dialogs.replace(
        "from nyx.core.proxy_profiles import parse_proxy_line",
        "from nyx.core.proxy_profiles import parse_proxy_line\nfrom nyx.core.proxy import save_proxy_password, get_proxy_password",
        1,
    )
    dialogs = dialogs.replace(
        "self.proxy_user.setText(profile.get('username', '')); self.proxy_password.clear()",
        "self.proxy_user.setText(profile.get('username', '')); self.proxy_password.setText(get_proxy_password({'proxy_type': profile.get('type', 'HTTP'), 'proxy_host': profile.get('host', ''), 'proxy_port': profile.get('port', 8080)}))",
        1,
    )
    dialogs = dialogs.replace(
        "self.proxy_profiles.append(profile); self.refresh_proxy_presets(); self.proxy_presets.setCurrentIndex(self.proxy_presets.count() - 1)",
        "self.proxy_profiles.append(profile); save_proxy_password(profile, self.proxy_password.text()); self.refresh_proxy_presets(); self.proxy_presets.setCurrentIndex(self.proxy_presets.count() - 1)",
        1,
    )
    dialogs = dialogs.replace(
        "self.proxy_profiles.append(profile); added += 1\n            last_password = parsed.get('password', '')",
        "self.proxy_profiles.append(profile); save_proxy_password(profile, parsed.get('password', '')); added += 1\n            last_password = parsed.get('password', '')",
        1,
    )
    dialogs = dialogs.replace("Пароль на время текущего запуска", "Пароль (сохранится в хранилище Windows)")
    dialogs = dialogs.replace(
        "Пароли намеренно не включены в экспорт.",
        "Пароли сохраняются отдельно в системном хранилище учётных данных, а не в открытом файле настроек."
    )
    dialogs_path.write_text(dialogs, encoding="utf-8")

    main_path = root / "nyx" / "main.py"
    main = main_path.read_text(encoding="utf-8")
    main = re.sub(r"1\.0\.0-dev\.3\.\d+", "1.0.0-dev.3.9", main)
    main_path.write_text(main, encoding="utf-8")

    (tests / "test_navigation.py").write_text(r'''import unittest
from nyx.core.navigation import looks_like_url, resolve_address_input

class AddressNavigationTests(unittest.TestCase):
    def test_full_https_url_with_path_is_direct_navigation(self):
        url, is_search = resolve_address_input("https://example.com/path?q=nyx", "Google")
        self.assertFalse(is_search)
        self.assertEqual(url.toString(), "https://example.com/path?q=nyx")
    def test_domain_with_path_is_direct_navigation(self):
        self.assertTrue(looks_like_url("example.com/docs/page"))
        self.assertFalse(resolve_address_input("example.com/docs/page")[1])
    def test_domain_with_port_is_direct_navigation(self):
        self.assertTrue(looks_like_url("localhost:8080/status"))
        self.assertFalse(resolve_address_input("localhost:8080/status")[1])
        self.assertTrue(looks_like_url("192.168.1.10:8080"))
    def test_plain_words_use_search_engine(self):
        url, is_search = resolve_address_input("NYX Browser help", "DuckDuckGo")
        self.assertTrue(is_search)
        self.assertTrue(url.toString().startswith("https://duckduckgo.com/?q="))

if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")
    (tests / "test_proxy_profiles_secure.py").write_text(r'''import unittest
from nyx.core.proxy import proxy_credential_key
from nyx.core.proxy_profiles import parse_proxy_line

class ProxyProfileTests(unittest.TestCase):
    def test_simple_proxy_switcher_format(self):
        parsed = parse_proxy_line("127.0.0.1:8080:alice:secret")
        self.assertEqual((parsed["host"], parsed["port"], parsed["username"], parsed["password"]),
                         ("127.0.0.1", 8080, "alice", "secret"))
    def test_uri_proxy_format(self):
        parsed = parse_proxy_line("socks5://alice:secret@127.0.0.1:1080")
        self.assertEqual(parsed["type"], "SOCKS5")
        self.assertEqual(parsed["username"], "alice")
        self.assertEqual(parsed["password"], "secret")
    def test_credentials_are_keyed_by_endpoint_and_type(self):
        self.assertEqual(proxy_credential_key({"type":"SOCKS5","host":"127.0.0.1","port":1080}),
                         "SOCKS5|127.0.0.1|1080")

if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

    (tests / "test_native_window_resize.py").write_text(r'''from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class NativeWindowResizeTests(unittest.TestCase):
    def test_frameless_window_has_native_edge_resize_filter(self):
        source = (ROOT / "nyx" / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn("class NativeWindowEdgeResizer(QObject):", source)
        self.assertIn("handle.startSystemResize(edges)", source)
        self.assertIn("app_instance.installEventFilter(self._native_edge_resizer)", source)
        self.assertIn("self.window.isMaximized() or self.window.isFullScreen()", source)

    def test_youbusta_has_quick_access_from_toolbar(self):
        source = (ROOT / "nyx" / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn("self.youbusta_toolbar_btn", source)
        self.assertIn("self.open_extensions", source)

if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

    (tests / "test_fullscreen_support.py").write_text(r'''from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class FullscreenSupportTests(unittest.TestCase):
    def test_webengine_fullscreen_request_is_wired(self):
        browser_tab = (ROOT / "nyx" / "ui" / "browser_tab.py").read_text(encoding="utf-8")
        main_window = (ROOT / "nyx" / "ui" / "main_window.py").read_text(encoding="utf-8")
        self.assertIn("fullScreenRequested = Signal(object, object)", browser_tab)
        self.assertIn("page.fullScreenRequested.connect", browser_tab)
        self.assertIn("request.toggleOn()", main_window)
        self.assertIn("request.accept()", main_window)
        self.assertIn("self.showFullScreen()", main_window)
        self.assertIn("self._position_sidebar()", main_window)
        self.assertIn("def createWindow(self, window_type)", browser_tab)
        self.assertIn("return self.browser_tab.create_popup_page()", browser_tab)
        self.assertIn("def create_popup_tab(self)", main_window)

if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

    (tests / "test_windows_install_options.py").write_text(r'''from pathlib import Path
import tempfile
import unittest
from nyx.core.data_paths import resolve_app_dir

class WindowsInstallOptionsTests(unittest.TestCase):
    def test_no_marker_uses_legacy_localappdata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            local, exe = root / "local", root / "app"
            local.mkdir()
            exe.mkdir()
            self.assertEqual(resolve_app_dir(exe, {"LOCALAPPDATA": str(local)}, True),
                             local / "NYX Browser")

    def test_marker_uses_chosen_folder_and_keeps_legacy_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            local = root / "old-local"
            exe = root / "D" / "Programs" / "NYX Browser"
            selected = exe / "UserData" / "NYX Browser"
            old = local / "NYX Browser"
            exe.mkdir(parents=True)
            old.mkdir(parents=True)
            (old / "settings.json").write_text('{"theme":"NYX Violet"}', encoding="utf-8")
            (exe / "nyx-user-data-path.txt").write_text(str(selected), encoding="utf-8")
            result = resolve_app_dir(exe, {"LOCALAPPDATA": str(local)}, True)
            self.assertEqual(result, selected)
            self.assertTrue((selected / "settings.json").exists())
            self.assertTrue((old / "settings.json").exists())

if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

    (root / "VERSION.txt").write_text("1.0.0-dev.3.9\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_desktop.py <extracted source root>")
    patch(Path(sys.argv[1]).resolve())
