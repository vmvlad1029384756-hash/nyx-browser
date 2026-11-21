# NYX Browser — official project website

The static website for NYX Browser, deployed with Cloudflare Pages.

## Files
- `index.html` — project homepage and mobile installation instructions (Russian / English).
- `style.css` — main visual system and responsive layout.
- `mobile.css` — touch and small-screen finishing styles.
- `script.js` — language switcher, mobile navigation, FAQ and site interactions.
- `mobile-site.js` — PWA install prompt and service-worker registration.
- `manifest.webmanifest` — installable website metadata.
- `service-worker.js` — offline cache for the website shell only.
- `support.html` — project support page.
- `favicon.svg` — NYX site icon.

## Mobile website installation
The website can be added to a phone's home screen:
- **Android:** open the HTTPS website in Chrome, then use the browser menu's Install app / Add to Home screen option. Where supported, the page also shows an install button.
- **iPhone:** open the HTTPS website in Safari, tap Share, then Add to Home Screen.

This installs the **website as a web app**, not the native NYX browser. Android APK and iOS native app releases are not published yet. Never download unofficial NYX APKs from third-party sites.

The service worker caches the NYX website shell for basic offline reopening. It does not make external websites or online browser features work offline.

## Local preview
Open `index.html` in a browser, or run a local static server from this directory. Service workers and PWA installation require HTTPS in deployment (localhost is suitable for local testing).

## Publishing
The site is connected to Cloudflare Pages through this GitHub repository. A push to the configured production branch may trigger a deployment.

## Accuracy note
The Windows download button remains disabled until a real installer URL is published. The website is installable on supported phones, but native mobile browser builds must not be described as released until they are built and tested.
