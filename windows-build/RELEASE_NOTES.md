## NYX Browser 1.0.0-dev.3.3 — Windows x64 preview

This preview adds a language chooser, destination-folder selection and per-user default-browser registration.

### Installer
- Select Russian or English before the wizard starts.
- The initial destination is D:\Programs\NYX Browser when drive D: exists.
- Use the folder field or Browse button to select another drive and folder.
- Installation is per-user and does not require administrator privileges.
- The browser profile, cookies, history, WebEngine cache and default downloads folder are placed under the selected install folder\UserData\NYX Browser, on the same drive.
- When an existing profile is found in %LOCALAPPDATA%\NYX Browser, NYX copies it to the selected data folder and keeps the original as a safety copy.

### Default browser
NYX registers support for HTTP, HTTPS, HTM and HTML. Windows controls the final choice: use the new globe button in NYX to open Windows Default Apps, select NYX Browser and confirm. The installer does not silently change protected Windows defaults.

### Icon
The application and installer icons use a transparent NYX vector mark without a black square background.

### Important
- Windows 10/11 x64.
- This is a development preview, not a stable release.
- The installer is not code-signed. Windows SmartScreen may show an unknown-publisher warning.
- User data is intentionally retained when the application is uninstalled.
- Password secrets remain in Windows Credential Manager, managed by Windows.
- NYX does not claim to bypass network, regional, DNS, TLS or site-side restrictions.
- Physical Windows testing is still required before calling this a stable release.
