# NYX Browser 1.0.0-dev.3.6 — Windows x64 preview

## Installer redesign
- Default installation path is on C: under Program Files.
- The user can select another drive and exact destination folder.
- Setup requests Windows administrator approval (UAC) so it can create the selected installation directory.
- Browser profile, cookies, history, cache and downloads remain in the selected installation tree, under UserData.
- The UserData directories grant the interactive Users group Modify access so NYX can write its profile while running as a normal, non-elevated user.
- Removed the custom folder-creation preflight code that incorrectly rejected valid destinations.

## Included from previous builds
- Russian / English installer language selection.
- Supplied NYX avatar icon.
- Default-browser registration; Windows still requires the user to confirm the default app in Settings.

This is a development preview for Windows 10/11 x64. It is not code-signed; SmartScreen may show an unknown-publisher warning. Physical Windows testing is still required.
