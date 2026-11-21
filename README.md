# NYX Browser — official website

The static website for NYX Browser, deployed with Cloudflare Pages.

## Files
- `index.html` — page structure and content (Russian / English).
- `style.css` — responsive visual system and layout.
- `script.js` — language switcher, mobile navigation, FAQ and subtle reveal effects.
- `favicon.svg` — site icon.

## Local preview
Open `index.html` in a browser, or run a local static server from this directory.

## Publishing
The site is connected to Cloudflare Pages through this GitHub repository. A push to the configured production branch may trigger a deployment.

## Accuracy note
The download button remains disabled until a real installer URL is published. The site intentionally does not claim that planned browser capabilities are already released.


## Mobile application work

The Android client lives in `android/` and is an early native WebView-based MVP. It is not included in the Windows ZIP. Android CI builds a debug APK for testing; it is not a public signed release. The informational website is responsive, but a separate installable iPhone PWA companion and a full native iOS browser are still planned work.

## Automated Windows packaging

The Windows workflow extracts the desktop source ZIP, runs its 18 regression tests, packages the app with PyInstaller, compiles the Inno Setup installer and uploads both the installer and portable bundle as temporary CI artifacts. Python is bundled in the packaged application, so end users do not need to install Python. The artifact is unsigned and is not a public release until clean-machine testing is complete.
