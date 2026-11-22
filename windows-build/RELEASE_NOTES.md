# NYX Browser 1.0.0-dev.3.10 — Windows x64 preview

## Startup crash
- Fixed a missing QObject import in the native Windows window-edge resize handler that caused dev.3.9 to fail on launch.

## Updating and profile retention
- Installer now remembers the previous installation directory instead of defaulting to a new directory on each update.
- This keeps the existing UserData folder beside the application and avoids creating a fresh empty profile when updating in place.
- The installer does not intentionally delete browser profile data during an in-place update.

## Still under investigation
- Search suggestions/history dropdown behavior.
- Proxy profile selection persistence and full Simple Proxy Switcher compatibility.
- In-app update download and safe replacement flow.

These remaining items are not marked as fixed until the source behavior and upgrade path have been verified.
