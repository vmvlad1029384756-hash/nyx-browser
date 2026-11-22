# NYX Browser 1.0.0-dev.3.7 — Windows x64 preview

## YouTube and video playback
- Added a handler for Qt WebEngine HTML5 fullscreen requests.
- Entering video fullscreen hides browser chrome and expands the video to the full display.
- Exiting fullscreen restores the previous window state and browser controls.
- This addresses the missing fullscreen-request handling that prevented YouTube's fullscreen button from taking effect.

## Installer and profile
- Keeps the tested dev.3.6 installer behavior: C: default, user-selectable install location, UAC elevation for setup, and writable user data for a standard user.
- Russian / English installer language selection.
- NYX avatar icon and default-browser registration.

The first-link YouTube navigation issue still requires the exact failing URL or a reproduction path to identify whether the site opens a new window, redirects, or fails to load. This preview is not code-signed; SmartScreen may show an unknown-publisher warning.
