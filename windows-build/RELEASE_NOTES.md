# NYX Browser 1.0.0-dev.3.9 — Windows x64 preview

## Native Windows window behavior
- Restored native resizing on all four edges and corners for NYX's frameless custom window.
- Uses QWindow.startSystemResize so Windows handles interactive resizing, snapping and tiling instead of simulated geometry changes.
- Keeps native title-bar move handling, so dragging NYX to screen edges can use Windows 11 Snap behavior.

## YouBusta quick access
- Added a dedicated YouBusta toolbar shortcut that opens the extension manager directly.
- The official YouBusta installer remains in the extension manager and requires explicit user approval for its requested permissions.
- YouBusta depends on Qt WebEngine's Manifest V3 extension support. The extension uses advanced APIs including proxy and webRequest; Qt WebEngine does not guarantee full Chrome API parity, so the extension must be tested in the actual NYX build before claiming all features work.

## Preserved
- dev.3.8 address bar direct URL routing and proxy credential fixes.
- dev.3.7 YouTube fullscreen and popup-tab fixes.
