# NYX Mobile PWA companion (0.2.5)

This folder contains the responsive web companion for phone testing. It is not the native NYX desktop browser.

## Local Wi-Fi preview

Run `run_mobile_preview.bat` from the project root on Windows. Keep the terminal open. Find the PC IPv4 address with `ipconfig`, connect the phone to the same Wi-Fi and open `http://PC-IP:8000/`.

## Install and offline mode

For Add to Home Screen and service-worker caching, host this folder over HTTPS. Then open the HTTPS URL in a compatible mobile browser and use its Add to Home Screen / Install command.

A PWA does not control the host browser's system tabs, system proxy or native extension APIs. Older browser engines may not support every PWA feature.
