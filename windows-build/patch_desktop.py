from __future__ import annotations

import os
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
    main = main.replace("1.0.0-dev.3.2", "1.0.0-dev.3.3")
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
    window = window.replace("from nyx.core.password_vault import list_credentials, get_password\n",
                            "from nyx.core.password_vault import list_credentials, get_password\nfrom nyx.core.default_browser import register_default_browser, open_default_apps_settings\n", 1)
    window = window.replace("1.0.0-dev.3.2", "1.0.0-dev.3.3")
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

    (root / "VERSION.txt").write_text("1.0.0-dev.3.3\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_desktop.py <extracted source root>")
    patch(Path(sys.argv[1]).resolve())
