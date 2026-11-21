# NYX Browser for Android — development build

This is the first native Android browser client. It is a separate Kotlin + Android WebView application; it is not the website PWA.

## Current MVP
- Native Android app shell with NYX dark/purple styling.
- Embedded Android WebView for normal HTTPS/HTTP browsing.
- Up to 12 independent tabs with switching and closing.
- Address bar with URL-or-search handling.
- Back, forward, reload and home controls.
- Local bookmarks and browsing history.
- Downloads through Android DownloadManager.
- Website file-picker support for uploads.
- Share current page through Android share sheet.
- Safe Browsing enabled where supported by the platform.
- Mixed insecure content blocked; SSL certificate errors are cancelled.

## Intentionally not included yet
- Incognito/private tabs and automatic private-data clearing.
- Password manager and autofill.
- Extension support.
- Built-in page translation.
- Proxy/VPN management.
- Per-site camera, microphone and geolocation permissions. These are denied by this first MVP until a safe native consent flow is implemented.
- iOS build.
- Signed release APK or Google Play release.

There is no advertising SDK, ad injection, affiliate redirect or analytics SDK in this app.

## Build
The GitHub Actions workflow `.github/workflows/android-debug.yml` builds a debug APK using JDK 17, Gradle 9.5.0, Android Gradle Plugin 9.3.1, Kotlin 2.4.21 and Android API 36.

To build locally, open this repository in a recent Android Studio installation with Android SDK Platform 36 and JDK 17, or run:
```bash
gradle :app:assembleDebug
```

The build artifact is named `app-debug.apk`. Debug builds are for testing only and are not a final public release.

## Security notes
- JavaScript is enabled because modern websites require it; no JavaScript bridge is exposed to web pages.
- File-system access from websites is disabled.
- Mixed content is blocked.
- SSL errors are cancelled, never bypassed.
- Safe Browsing remains enabled on supported devices.
- Web permission requests are denied until a native permission UX exists.

## Platform notes
- Minimum Android version: Android 8.0 (API 26) for the first test build.
- Target Android version: Android 16 (API 36).
- This is a WebView-based browser MVP, not a Chromium fork. Website compatibility and media support depend partly on the Android System WebView installed on the device.
- Test on multiple physical devices before publishing a public APK.
