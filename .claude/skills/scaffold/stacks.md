# Desktop stacks: decision table and per-stack notes

Tooling changes quickly. These notes say **what to set up and why**. Before running any scaffolding command, check the exact commands, package names and versions against the official docs (WebFetch), and pin what you install. If the docs disagree with this file, the docs win; mention the difference to the user.

## Decision table
Read the definition's answers, then recommend the first row that fits.

| If… | Recommend | Why | Watch out for |
|---|---|---|---|
| Web skills, Windows + macOS, and automated UI verification of the real app on **both** OSes matters most (the default for this kit) | **Electron** (Electron Forge, Vite, TypeScript) | The HTML prototype carries over directly. Playwright drives the real packaged app and takes screenshots on Windows and macOS. Mature signing, notarization and updates. | Downloads of 100 MB+ and idle memory of 150 MB+. Security defaults must be kept on. |
| Web skills, and download size or memory matters (utilities, tray apps) | **Tauri 2** (Rust core, system WebView) | Installers of a few MB and a small memory footprint. HTML/CSS carries over. A permission (capability) model per window. | Real-app WebDriver E2E works on Windows (and Linux) but **not macOS**, so there you test the UI in a browser with mocked IPC, plus a manual smoke check. WebView2 and WKWebView render slightly differently. You'll need some Rust. |
| C#/.NET skills, Windows + macOS | **Avalonia UI** | One XAML codebase. Headless UI tests can render screenshots on any OS. | The prototype's HTML has to be rebuilt in XAML. Mac `.app` bundling is extra setup. |
| C#/.NET, **Windows only** | **WinUI 3** (Windows App SDK) or WPF | The most native Windows look; MSIX. | No macOS. UI automation needs FlaUI or Appium on Windows. |
| Dart/Flutter skills, or a mobile app later | **Flutter** | One codebase across desktop and mobile. Golden (screenshot) tests. | Doesn't feel native on desktop by default. Windows builds must happen on Windows, macOS builds on a Mac. |
| Heavy native work, C++ or Python | **Qt 6** (QML; PySide6 for Python) | Native performance and a mature desktop toolkit. | Licensing (LGPL or commercial). Heavier tooling. |

Native-per-platform (SwiftUI on macOS plus WinUI on Windows) means two codebases. Recommend it only when the definition puts native feel above everything and there's capacity for two apps.

## What every stack must end up with (the walking skeleton)
- **The app runs:** it launches into the main window with the definition's app menu and its default and minimum window sizes.
- **Window state:** it remembers the window's size and position, and stays on screen if a monitor is removed.
- **One instance:** a second launch focuses the running window, unless the definition allows several instances.
- **Logs and crashes:** logs are written to the platform log folder (Windows `%LOCALAPPDATA%\<App>\logs`, macOS `~/Library/Logs/<App>`), and a crash handler is stubbed in.
- **Data:** the data folder is resolved through the platform API (Windows `%APPDATA%\<App>`, macOS `~/Library/Application Support/<App>`), never hard-coded. There's a schema-version table, and the migrations run at startup.
- **Theme:** light and dark follow the OS.
- **Commands** for test, lint, start, e2e, screenshot and package, recorded in `CLAUDE.md`.
- **CI:** one workflow with a `windows-latest` and `macos-latest` matrix that lints, tests, runs the e2e and screenshot suite, uploads the screenshots as artifacts, and builds unsigned packages.

## Verification layers (all stacks)
1. **Unit:** domain logic and storage, including the migrations.
2. **UI component:** screens rendered in isolation, with the platform bridge mocked. Fast, and runs on every OS.
3. **End-to-end:** the real app (a built or packaged binary) launched and driven by automation, taking screenshots per screen id. This is the layer the verifier relies on. If a stack can't do it on some OS, `CLAUDE.md` says so, and those checks become manual smoke steps in the release checklist.

**The screenshot command** in `CLAUDE.md` takes a screen id, an optional theme and an optional window size, and writes a PNG. `/build` and the verifier call it the same way on every stack.

## Electron
- **Create:** `npm create electron-app@latest <name> -- --template=vite-typescript` (Electron Forge). Add the UI framework the prototype suggests, or plain TypeScript.
- **Security:** keep these defaults, and check them in review:
  - `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`;
  - a preload that exposes a small, typed API through `contextBridge`;
  - the main process validates every IPC message's arguments and sender;
  - a strict CSP;
  - `setWindowOpenHandler` denies by default, and `will-navigate` is blocked;
  - `shell.openExternal` only for `https:` URLs on an allowlist.
- **Tests:** Vitest for units and components. For e2e, Playwright's `_electron.launch()` against the built app; `page.screenshot()` handles screenshots. It works on Windows and macOS.
- **Package:** Forge makers:
  - Windows: Squirrel (the default), or WiX MSI, or MSIX;
  - macOS: DMG and ZIP.

  (electron-builder with NSIS and DMG is the common alternative.)
- **Sign:**
  - macOS: `osxSign` and `osxNotarize` in the Forge config, with an App Store Connect API key or an app-specific password from CI secrets;
  - Windows: signtool with a certificate, or a cloud signing service, configured in the maker.
- **Update:** `update-electron-app` (with update.electronjs.org, for public GitHub repos) or `electron-updater`.

## Tauri 2
- **Prerequisites:**
  - Rust (rustup);
  - on Windows, the MSVC build tools and WebView2 (preinstalled on Windows 11);
  - on macOS, the Xcode command-line tools.
- **Create:** `npm create tauri-app@latest` (choose TypeScript plus the framework). Check its `--help` for the non-interactive flags.
- **Security:** in `src-tauri/capabilities/`, grant each window only the commands it uses. Set a CSP in `tauri.conf.json`. Validate the arguments of every `#[tauri::command]`.
- **Tests:**
  - `cargo test` for the core;
  - Vitest with `@tauri-apps/api/mocks` (`mockIPC`) for the UI;
  - Playwright against the Vite dev server with IPC mocked, for screenshots on every OS;
  - real-app e2e through `tauri-driver` (WebDriver) on Windows. It isn't available on macOS: record that in `CLAUDE.md` and add a manual macOS smoke list.
- **Package:** `tauri build`:
  - Windows: an NSIS `-setup.exe` and/or an MSI (WiX);
  - macOS: `.app` and `.dmg`.

  Cross-building macOS from another OS isn't supported; use CI.
- **Sign:**
  - Windows: `bundle.windows.certificateThumbprint`, or a `signCommand` for cloud signing;
  - macOS: `APPLE_SIGNING_IDENTITY`, plus the notarization variables (`APPLE_API_KEY`… or `APPLE_ID`/`APPLE_PASSWORD`/`APPLE_TEAM_ID`).

  Use `tauri-apps/tauri-action` in CI.
- **Update:** `tauri-plugin-updater`. Updates are signed with the app's own key pair (`tauri signer generate`), whose private key lives only in CI secrets.

## Avalonia UI (.NET)
- **Create:** `dotnet new install Avalonia.Templates`, then `dotnet new avalonia.mvvm -o <Name>`.
- **Tests:** xUnit or NUnit, with Avalonia's headless test packages. Rendered frames can be captured to PNG for screenshots on any OS. Real-app e2e (optional): Appium, with a Windows driver and the Mac2 driver.
- **Package:** `dotnet publish -c Release -r win-x64|win-arm64|osx-arm64|osx-x64 --self-contained`. Then Velopack (`vpk pack`) for installers and delta updates on Windows and macOS, or MSIX on Windows. macOS needs an `.app` bundle with an `Info.plist`.
- **Sign:**
  - Windows: signtool, or cloud signing (Velopack can call either);
  - macOS: `codesign` with hardened runtime, then `xcrun notarytool submit --wait` and `xcrun stapler staple`.
- **Update:** Velopack.

## WinUI 3 / WPF (Windows only)
- **Create:** the Windows App SDK templates (`dotnet new winui` once the templates are installed), or `dotnet new wpf`.
- **Tests:** xUnit for view models. FlaUI (UI Automation) for e2e and screenshots on Windows.
- **Package, sign and update:** MSIX with App Installer updates, or the Microsoft Store; or Velopack.

## Flutter
- **Create:** `flutter create --platforms=windows,macos <name>`.
- **Tests:**
  - `flutter test`: widget tests, plus golden tests (`matchesGoldenFile`) as screenshots. Goldens are font- and OS-sensitive, so keep them per OS;
  - `flutter test integration_test -d windows|macos` for the real app.
- **Package:** `flutter build windows|macos`. Then, on Windows, MSIX (the `msix` package) or Inno Setup; on macOS, a DMG from the `.app`. Build each OS on that OS.
- **Update:** a Sparkle/WinSparkle wrapper (e.g. `auto_updater`), or the stores.

## Signing and secrets (all stacks)
- **Windows:** sign the executables and the installer with an OV or EV certificate, or with Microsoft's cloud signing service. Unsigned builds trigger SmartScreen warnings.
- **macOS:** you need an Apple Developer Program membership, a Developer ID Application certificate, hardened runtime, notarization, and stapling. Unsigned apps are blocked by Gatekeeper.
- **Secrets:** certificates, passwords, API keys and updater private keys go only in CI secrets. They never go in the repo, `CLAUDE.md`, logs or work files. Skills check secrets by name (`gh secret list`), never by value.

## CI skeleton (GitHub Actions)
```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        os: [windows-latest, macos-latest]   # add ubuntu-latest if Linux is a target
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      # setup steps for the stack: actions/setup-node, dtolnay/rust-toolchain, actions/setup-dotnet, subosito/flutter-action
      # install, lint, unit tests
      # e2e and screenshots (writes to e2e-screens/)
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: screens-${{ matrix.os }}
          path: e2e-screens/
      # unsigned package build (proves packaging still works)
```
The release workflow is separate and triggered by a version tag. It signs, notarizes and creates a **draft** GitHub Release (see `/release`).

## Working from WSL on Windows
WSL builds and runs **Linux** binaries. The Windows target needs the Windows toolchain, and macOS needs a Mac or CI.
- **Edit and run unit tests in WSL,** as usual.
- **For Windows e2e, screenshots and packaging,** mirror the working tree to a Windows-side folder and run the commands with PowerShell. `/scaffold` writes `scripts/win-run.sh` for this:
  ```bash
  #!/usr/bin/env bash
  # Run a command on the Windows host against a mirror of this working tree.
  set -euo pipefail
  MIRROR_WIN='C:\dev\<app>'; MIRROR=/mnt/c/dev/<app>
  mkdir -p "$MIRROR"
  rsync -a --delete --exclude node_modules --exclude target --exclude bin --exclude obj --exclude .git ./ "$MIRROR/"
  powershell.exe -NoProfile -Command "Set-Location '$MIRROR_WIN'; $*"
  ```
  The mirror is a build folder, not a second checkout. Never edit it.
- **WSLg** can show the Linux build for quick looks. That isn't the Windows target, so it never counts as Windows verification.
- **Alternatively,** run Claude Code natively on Windows for this project, and skip the mirror.
- **macOS** is verified in CI (the matrix and the screenshot artifacts) unless a Mac is available. The verifier marks macOS-only checks it couldn't run as `CI` or `NOT CHECKED`; it never passes them on assumption.
