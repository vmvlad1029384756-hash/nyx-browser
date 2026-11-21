# NYX Browser 1.0.0-dev.3.5 — Windows x64 preview

## Installer reliability fix
- Removed the custom directory preflight that incorrectly rejected valid paths such as D:\programms.
- Removed explicit ACL modification on installation directories. Per-user installation now relies on the current Windows user's normal inherited permissions instead of attempting to rewrite directory permissions.
- The installer uses the exact selected destination and creates the required folders itself.

## Included from dev.3.4
- Russian / English installer language selection.
- D: preferred by default when available; otherwise LocalAppData.
- User data stored alongside the selected installation drive.
- NYX application icon and default-browser registration.

This is a development preview for Windows 10/11 x64. The installer is not code-signed. Please test installation on Windows before wider promotion.
