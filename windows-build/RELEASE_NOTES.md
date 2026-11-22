# NYX Browser 1.0.0-dev.3.8 — Windows x64 preview

## Address bar
- Fixed URL detection for complete https:// URLs, domains with paths and query strings, localhost and host:port inputs.
- URL input now opens the destination directly; plain words continue to use the selected search engine.

## Proxy Switcher
- Proxy credentials are saved in the operating system credential store through Python keyring instead of plaintext settings.
- Imported Simple Proxy Switcher entries keep their own credentials per proxy endpoint.
- Selected saved profiles restore their password automatically.
- Proxy username and password are supplied automatically when Chromium requests proxy authentication.
- Proxy changes still require restarting NYX because the proxy must be configured before the first WebEngine profile is created.

## ChatGPT and modern websites
- Removed the QtWebEngine product token from the browser user-agent while preserving the actual Chromium version.
- Enabled JavaScript-created windows/popups used by authentication flows.
- Retains the dev.3.7 fullscreen and popup-tab fixes.

The build and automated tests do not replace a live test with your specific proxy provider or ChatGPT account. If ChatGPT still fails, capture the exact page/error so the next fix can target the actual failure rather than guessing.
