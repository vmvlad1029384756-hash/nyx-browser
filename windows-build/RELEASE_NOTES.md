# NYX Browser 1.0.0-dev.3.4 — Windows x64 preview

## Installer directory fix
- Selecting a custom folder now uses that exact folder; Setup no longer appends another "NYX Browser" directory automatically.
- Before installation, Setup checks that the selected folder can be created and written to.
- If Windows blocks access, Setup shows a clear message before copying browser files.

## Included from dev.3.3
- Russian / English language selection.
- Custom installation drive and folder; D: is preferred when available.
- Browser profile, cookies, history, cache and downloads stored on the selected drive.
- Registration as a Windows default-browser candidate (Windows still requires the user to confirm).
- Supplied NYX avatar artwork in the application and installer icon.

This is a development preview for Windows 10/11 x64. It is not code-signed; SmartScreen may show an unknown-publisher warning. Physical Windows testing is still required.
