---
name: prototype
description: Stage 2a (Design) of the desktop SDLC. Keeps one living HTML prototype of the desktop app (windows, menus, shortcuts, dialogs, tray) with a Windows/macOS and light/dark switcher. `/prototype app` designs the whole-app shell from the definition; `/prototype <item>` changes it for one feature and snapshots it into the work item on approval.
argument-hint: "[app | work item slug or issue id]"
disable-model-invocation: true
---

# /prototype: design it in the project's desktop prototype

The project keeps **one living HTML prototype** that simulates the desktop app, and every feature changes it. When the user approves, you copy a snapshot. Later stages read that snapshot, never the living prototype.

Input: $ARGUMENTS
- **`app`: the shell.** Design the app shell from `product/definition.md`: the main window, the navigation, the menus, settings, about, empty states for each MVP area, and the tray if there is one. The snapshot goes to `product/prototype-shell/`.
- **Anything else: one feature.** A slug, a work folder, or an issue id (`R-4`, `ENG-123`, `#45`) matches the `work/*` folder whose name contains it, lowercased, with `#` written as `gh-`.
- **Empty:** use the most recently modified `work/*/` whose `intent.md` is approved and which has no `prototype/` yet. If there's none, but the definition is approved and there's no shell yet, use `app`. Name the choice in one line.

## Steps

1. **Read:**
   - `product/definition.md`: its App shape, Identity, Platforms and Quality bars;
   - for a feature, the work item's `intent.md`, which must be approved;
   - `CLAUDE.md`;
   - for a clone, the teardown's *Views* and *Not ours to copy*.
2. **Find the prototype.**
   - **Look for it:** the `Prototype:` line in `CLAUDE.md`; otherwise a `prototype/` folder; otherwise an HTML file with `data-screen` markers.
   - **If you find several,** ask which with AskUserQuestion.
   - **If `CLAUDE.md` doesn't record the path,** confirm it in the same call, then add the `Prototype:` line.
3. **Choose the starting point:**
   - **A prototype exists:** modify it in place. Change only the screens, menus and windows this feature needs.
     - If the real app has visibly moved on from the prototype on those screens, ask: "Sync those screens from the app first (Recommended)", as a separate commit, or "Keep the prototype as it is".
   - **No prototype, but an app exists:** create `prototype/index.html`, seeded from the app's theme, its components and its neighbouring screens.
   - **No prototype and no app:** create `prototype/index.html` from the definition.
4. **Follow the desktop conventions** in `conventions.md` (next to this file). In short:
   - **One self-contained HTML file:**
     - a **window frame** per screen, with platform chrome that switches between Windows and macOS;
     - a **menu bar** rendered from one `menus` object;
     - **shortcuts** shown as Ctrl on Windows and ⌘ on macOS;
     - a **light/dark** switch, and a window-size preset (default and minimum);
     - **context menus** on right-click.
   - **Native pieces are labelled stubs:** open and save dialogs, OS notifications and permission prompts. Don't design what the OS draws.
   - **Screens:** `<section data-screen="<id>" data-window="<window-id>">`, routed by `#<id>`, with `?platform=win|mac&theme=light|dark`. Each state that matters has its own screen id, such as `#tasks-empty`.
   - **Testids:** a stable `data-testid` on every interactive element. Every menu command has a `data-command` id like `file.new-task`.
   - **Data:** mock data in one `fixtures` object, shaped like the definition's core concepts. No network, except pinned CDN assets.
   - **Our own look.** For a clone, use our name, icon placeholder, palette and copy, never the target's.
5. **Iterate.**
   - **Show it after each change.** Give the user the file path to open, or `npx serve prototype`. List the changed `#screen` links, for both `?platform=win` and `?platform=mac`.
   - **Look at your own result first,** if a browser tool is available (Playwright MCP, or `npx playwright screenshot`). Look at both platforms and both themes.
   - **After each round,** ask with AskUserQuestion: "Approve (Recommended)" or "More changes". Repeat until the user approves.
6. **On approval:**
   1. **Write the notes:** `prototype-notes.md` in the work folder, or `product/prototype-shell/notes.md` for `app`. They list:
      - **the screens and windows added and changed,** one per line, as `- #<screen-id>: <what>`;
      - **the menu commands added or changed,** one per line, as `- cmd:<command-id>: <label>, <Windows shortcut> / <macOS shortcut>`.

        `/build` greps these two line formats to check its plan's coverage, so keep them exactly.
      - the testids that matter;
      - the platform differences the user chose;
      - the design decisions made during the iteration;
      - mock data that implies a rule.
   2. **Take the snapshot.** Copy the living prototype into `work/<folder>/prototype/`, or `product/prototype-shell/prototype/`.
   3. **Take the screenshots.** Save one of each added or changed screen to `screens/<screen-id>-<win|mac>-<light|dark>.png`. Light is required on both platforms; dark is required for the main screens. Also take one per role where the screen differs. If no browser tool works, say so plainly. Never claim screenshots you didn't take.
   4. **Lock the approved files.**
      - For a feature: append `work/<folder>/prototype/`, `work/<folder>/screens/` and `work/<folder>/prototype-notes.md` to `work/<folder>/locks.txt`.
      - For `app`: append `product/prototype-shell/` to `product/locks.txt`.
   5. **Commit** the living prototype, the snapshot and the notes with the message `prototype(<slug>): <summary>`.
7. **Next step:**
   - for a feature, `/spec <slug>`;
   - for `app`, `/roadmap`.

## Asking the user
Use the **AskUserQuestion** tool for every question and every approval, not a question in prose.
- **Batching:** up to 4 questions per call, with 2–4 options each.
- **The default** is the first option, labelled "(Recommended)".
- **Wording:** labels are short (1–5 words) and the reasoning goes in each option's description. Headers are at most 12 characters.
- **Free text:** the tool always adds "Other" for a typed answer, so never add an "Other" option yourself.
- **An approval is a question too:** "Approve (Recommended)" or "Request changes". Apply whatever the user types under Other, then ask again.
- **Without AskUserQuestion** (a headless run, or another agent harness), ask in one numbered message instead, with the default after each question.

## Rules
- Never delete or restyle screens outside this feature's scope without asking.
- The prototype is a design artifact, not app code. Even on a web-tech stack (Electron, Tauri), never copy it into the app's source. The build reimplements it in the app's own components.
- Follow each OS's conventions where the definition says to, and don't invent platform differences the user didn't ask for.
