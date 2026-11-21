# NYX Browser for Android — early MVP

This is a separate native Android client. It uses Android System WebView; it is not the Windows PySide6 executable repackaged for phones.

## Current MVP scope

- Android 8.0 (API 26) and newer, subject to device testing
- Local NYX start page, URL/address search and normal HTTPS navigation
- Multiple tabs and basic session restoration
- Back, forward, reload and home controls
- Downloads through Android DownloadManager
- File-picker support for website upload forms
- JavaScript and DOM storage for modern sites
- Safe Browsing enabled, mixed HTTP/HTTPS content blocked
- Camera, microphone and geolocation requests are denied until a dedicated permission/settings flow is implemented

This is a development build, not a public release. Password sync, extensions, proxy profiles, private browsing, translation UI and full desktop feature parity are not implemented yet. Some websites may behave differently in Android System WebView than in desktop Chromium.

## Build

Open this folder in a recent Android Studio, or use Gradle 9.6 with JDK 17 and Android SDK Platform 37.

    gradle :app:assembleDebug

The debug APK is written to app/build/outputs/apk/debug/app-debug.apk. The GitHub Actions workflow also builds and uploads this APK for device testing.

The CI debug APK is signed with the standard debug key. It is for testing only; a separate protected release-signing setup is required before public distribution.

## iPhone

The Windows executable and Android APK do not run on iPhone. The website will be kept responsive, and an installable web companion can be used from Safari Share → Add to Home Screen. A full native iOS browser is a separate Swift/WKWebView project and requires its own build, device testing and Apple distribution setup.
