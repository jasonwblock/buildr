---
name: spec
description: Stage 2b (Design) of the desktop SDLC. Writes work/<slug>/spec.md from the approved intent, the prototype snapshot, the product definition and the codebase, with platform-tagged acceptance criteria (AC-n [win|mac|both]) and flagged concerns with defaults. Use after /intent (and /prototype if there is UI).
argument-hint: "[work item slug or issue id]"
disable-model-invocation: true
---

# /spec: what to build, written for the builder

You write `spec.md` for an engineer, or a build session, who has never seen the conversation. The user approves the **flags** you raise; they don't read the spec line by line.

Work item: $ARGUMENTS. It's a slug, a work folder, or an issue id (`R-4`, `ENG-123`, `#45`), which matches the `work/*` folder whose name contains it, lowercased, with `#` written as `gh-`. If it's empty, use the most recently modified `work/*/` with an approved intent and no `spec.md`. Name it in one line.

## Steps

1. **Read:**
   - `intent.md`;
   - `prototype-notes.md` and the snapshot in `prototype/`, if there's UI;
   - `product/definition.md`;
   - `CLAUDE.md`, especially its Platforms section;
   - the code this touches:
     - the data model and the migrations;
     - the IPC or core/UI boundary;
     - the menu definitions;
     - the settings;
     - the OS-integration code;
     - the existing tests;
     - any backend.
2. **Cross-check four sources and turn each mismatch into a flag:**
   - **the intent's** *Data and behaviour*, *Desktop integration* and *Platform differences*;
   - **the prototype's** screens, menus, shortcuts and mock data;
   - **the definition:** its platforms, data rules and quality bars;
   - **the existing code and schema.**

   Examples:
   - the intent keeps history, but the prototype's delete removes the item;
   - the prototype's shortcut clashes with an existing command, or with a reserved OS shortcut (Ctrl+Alt+Del, ⌘Tab, ⌘H, Alt+F4);
   - a field shown in the prototype that the schema doesn't have, and **existing user databases would need a migration**;
   - the prototype shows a tray menu, but the definition has no tray presence;
   - the intent says "same on both platforms", but the prototype's notes chose different placements.
3. **Write `spec.md`** from the template below. *What changes* is relative to the current app.
4. **Number the acceptance criteria** `AC-1`, `AC-2`, … and tag each with the platforms it applies to: `[both]`, `[win]` or `[mac]`. Each must be checkable without asking anyone. Examples:
   - a test assertion;
   - "`[both]` the IPC command `tasks:delete` with an unknown id returns `NotFound` and changes nothing";
   - "`[win]` Ctrl+Shift+N opens the New Plan dialog; `[mac]` ⌘⇧N does";
   - "`[both]` the `#tasks` screen matches `screens/tasks-<platform>-light.png`";
   - "`[both]` a database at schema v3, copied from `test/fixtures/db-v3.sqlite`, opens and migrates with no data loss";
   - "`[both]` after quitting and relaunching, the open plan and the window's size and position are restored".

   Cover:
   - every screen, window and menu command in `prototype-notes.md`;
   - every rule in the intent;
   - each platform difference;
   - existing data (the migration from the last released schema);
   - the definition's quality bars that this change touches: keyboard access, screen-reader labels, dark theme, the minimum window size, and the performance budget if it touches large data.
5. **Present only the flags, using AskUserQuestion:**
   - **One question per flag.** It states the conflict. Your recommended resolution comes first, then 1–3 real alternatives.
   - **Up to 4 flags:** ask them all in one call.
   - **More than 4:** first ask "Accept all <n> recommended resolutions (Recommended)" or "Review them one by one". Ask in batches of 4 only if the user wants to review.
   - **No flags:** ask just for the approval: "Approve (Recommended)" or "Request changes".

   The user's answers to the flags are the approval.
6. **On approval:**
   1. write each flag's resolution into the spec;
   2. set `Status: approved`;
   3. append `work/<folder>/spec.md` to `locks.txt`;
   4. commit with the message `spec(<slug>): <title>`.
7. **Next step:** `/build <slug>`.

## Asking the user
Use the **AskUserQuestion** tool for every question and every approval, not a question in prose.
- **Batching:** up to 4 questions per call, with 2–4 options each.
- **The default** is the first option, labelled "(Recommended)".
- **Wording:** labels are short (1–5 words) and the reasoning goes in each option's description. Headers are at most 12 characters.
- **Free text:** the tool always adds "Other" for a typed answer, so never add an "Other" option yourself.
- **An approval is a question too:** "Approve (Recommended)" or "Request changes". Apply whatever the user types under Other, then ask again.
- **Without AskUserQuestion** (a headless run, or another agent harness), ask in one numbered message instead, with the default after each question.

## Template

```markdown
# Spec: <title>
Status: draft
Intent: work/<folder>/intent.md · Prototype: work/<folder>/prototype/ · Covers: D-n, …

## Summary
## What changes
### Data (entities, fields, storage location, migration from the last released schema, existing user data)
### Core/UI boundary (IPC commands or service calls: name, arguments, result, errors, input validation)
### Windows and screens (by prototype #id: new or changed; sizes; state restore)
### Menus, shortcuts and context menus
| Command id | Menu (Windows) | Menu (macOS) | Shortcut (Windows) | Shortcut (macOS) | Enabled when |
|---|---|---|---|---|---|
### OS integration (notifications, file types, deep links, tray, drag and drop, clipboard, launch at login)
### Permissions and security (OS prompts and entitlements; IPC allowlist and capabilities; server-side rules if there's a backend)
### Packaging impact (new entitlements, file associations or URL schemes that the installer and manifest must declare)
### Platform differences
## Rules
## Acceptance criteria
- AC-1 [both] …
## Flags
- F-1 … Default: … Resolution: …
## Not in this change
```

## Rules
- Don't invent requirements. Anything not traceable to the intent, the prototype, the definition or the code goes in as a flag.
- Keep the user's and the prototype's names for things (testids, screen ids, command ids, terms) unchanged.
- Every new or changed field on disk gets a migration AC. Data on users' machines is never thrown away silently.
