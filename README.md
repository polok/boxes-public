# boxes-public

The public site of Boxes / Kartony (served at https://haker.dev/boxes-public/): a landing page, the privacy policy, the terms of use and the support page in 8 languages: `pl/`, `en/`, `de/`, `it/`, `es/`, `fr/`, `zh/` (Simplified Chinese), `ja/`. The pages at the root only send the browser to its language (and list all of them).

Everything is generated; do not edit the HTML by hand.

```bash
python3 -m pip install Pillow            # one-time, only for the screenshots
python3 tools/build.py                   # pages and stylesheet
python3 tools/build.py --shots ../boxes-ios/fastlane/screenshots   # also refresh the store posters on the landing pages
```

- Texts: `tools/content_*.py` (one dict per language, the same structure in all of them: nav labels, `index`, `privacy`, `terms`, `support`). Edit all eight when the meaning changes, and bump the "updated" date of the policy, the terms and the support page.
- Layout and styles: `tools/build.py`. Fonts and the icon: `assets/`.
- The privacy policy must stay in step with what the app does (Firebase Analytics and Crashlytics, optional iCloud sync, on-device dictation) and with the App Privacy answers in App Store Connect.
- The App Store listing links to `<lang>/index.html`, `<lang>/privacy.html` and `<lang>/support.html` (`fastlane/metadata` in boxes-ios); the app links to `<lang>/privacy.html` and `<lang>/terms.html` (`AppLinks`).
