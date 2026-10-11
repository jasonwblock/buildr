# Desktop SDLC kit

The desktop-app version of the [agentic SDLC kit](https://github.com/jasonwblock/agentic-sdlc-kit), for a solo developer building a **Windows and macOS desktop app** with Claude Code.

It adds an app-level front end to the original per-feature loop. You say what to build in one of three ways:

| You type | What happens |
|---|---|
| `/define a habit tracker that lives in the tray` | **Interactive definition.** Up to 7 short multiple-choice rounds: purpose, shape, data, desktop integration, platforms, stack, and quality bars. Every question comes with a recommended default, and after round 2 you can accept the defaults for the rest. |
| `/clone Microsoft Planner` | **Target app clone.** Claude researches the app from public sources (and your screenshots, if you add them) into a feature teardown `T-n`. You pick parity per area: MVP, Core only, Later or Drop. The interview then fills only the gaps. |
| `/clone Microsoft Planner, but offline-first, with time tracking and no Teams dependency` | **Clone with changes.** As above, plus each change becomes a modification `M-n` mapped onto the teardown. Conflicts (for example offline-first versus real-time co-editing) come back to you as questions. |

All three produce the same approved `product/definition.md`. Everything after that is shared.

## The flow

```
/define ─┐
         ├──► product/definition.md ──► /prototype app ──► /roadmap ──► /scaffold (R-1)
/clone  ─┘        (D-n features)          (app shell)      (R-n backlog)   (walking skeleton, CI on Win + Mac)

per backlog item:  /intent R-n ──► /prototype ──► /spec ──► /build ──► /ship        ──► /release
                                   (if UI)                  │ verifier                   (signed installers,
bugs and crashes:  /triage ──► /fix ──► /ship              ▼                             draft release)
```

| Skill | Stage | Writes | Your part |
|---|---|---|---|
| `/define` | Define | `product/definition.md` with `D-n` features, platforms and the stack decision | Answer up to 7 rounds of ≤4 questions (or accept the defaults), approve |
| `/clone` | Define | `product/reference/<target>/teardown.md` (`T-n`, `M-n`), then continues into `/define` | Pick parity per area, resolve conflicts, approve |
| `/roadmap` | Plan | `product/roadmap.md`, and `product/backlog.md` (`R-n` items `/intent` can read) | Approve the milestones |
| `/scaffold` | Build | The walking skeleton: stack, main window, menus, data folder and migrations, commands, CI matrix | Approve the plan; push for CI |
| `/intent` | Plan | `work/<date>-<slug>/intent.md`, checked against the definition | Answer ≤4 questions, approve |
| `/prototype` | Design | The **living desktop prototype** (window chrome, menus, shortcuts, Win/Mac and light/dark switchers); a snapshot and screenshots per platform | Iterate, approve |
| `/spec` | Design | `spec.md` with platform-tagged `AC-n [win\|mac\|both]` and `F-n` flags | Resolve the flags |
| `/build` | Build + Test | `plan.md`, the code and tests, and `verify.md` with a per-OS table | Approve the plan |
| `/fix` | Bug | `bug.md`, a locked failing test (on the affected OS, or in CI), the fix | Rarely anything |
| `/ship` | Deploy | The PR, with CI-pending ACs resolved from the Windows/macOS matrix and its screenshots | Review and merge |
| `/release` | Release | A release PR, then (with your approval) a tag, signed and notarized installers, and a **draft** GitHub Release | Merge, approve the tag, run the smoke checklist, publish |
| `/triage` | Maintain | Draft intents and bugs from issues and crash reports, in one PR | Pick what to pursue |

## What's different from the web kit

- **An app-level definition before features.** The web kit assumes the app exists and starts at `/intent`. Here, `/define` or `/clone` decides the whole app first, `/roadmap` turns it into a backlog, and `/scaffold` builds a skeleton that runs on every target OS. `/intent` flags any feature that departs from the definition.
- **The platform is part of every criterion.** Acceptance criteria are tagged `[both]`, `[win]` or `[mac]`.
  - `CLAUDE.md` records which OSes run locally and which only in CI.
  - A local run never proves another OS's criterion: it stays `CI-pending` until `/ship` reads the CI matrix and its screenshot artifacts.
- **Desktop concerns are first-class:**
  - windows, menus and shortcuts (Ctrl versus ⌘), and close-versus-quit;
  - single instance and window-state restore;
  - the platform data folder, and **migrations from older installed versions** (every schema change needs a test from the last released schema);
  - OS integration: notifications, tray, file types, deep links;
  - accessibility through Narrator, NVDA and VoiceOver;
  - the stack's security defaults (Electron's context isolation, Tauri's capabilities).
- **The prototype simulates a desktop.** Menus are data, rendered as the macOS global menu bar or the Windows in-window menu bar. Native dialogs and notifications are labelled stubs, and screenshots are taken per platform and theme.
- **Releases are a stage.** `/release` handles versioning, the changelog, a readiness check (CI on every OS, signing secrets present **by name only**, the updater, migrations), and signature checks on the outputs. It never publishes; you do, after the smoke checklist.
- **Stack-agnostic, with a recommendation.** `.claude/skills/scaffold/stacks.md` has a decision table and per-stack notes:
  - Electron is the default, because Playwright can drive the real app on both OSes;
  - then Tauri 2, Avalonia, WinUI/WPF and Flutter;
  - plus notes on working from **WSL** (Windows runs mirrored to the Windows host via `scripts/win-run.sh`, and macOS through CI).

## Clones: function, not identity
`/clone` rebuilds what an app **does**, under your own name, icon, colours and words.
- It researches public sources only: docs, help centers, shortcut pages, release notes and reviews. It never logs in as you, scrapes behind authentication, or decompiles anything.
- The teardown cites a source for every feature and marks each one `documented`, `observed` or `inferred`.
- Importing the target's documented export formats and matching its shortcuts is allowed. Anything relying on undocumented formats becomes an open question for you.
- `/release` checks the installer and the app for the target's trademarks.

This is engineering hygiene, not legal advice. For a commercial clone, have someone qualified look at the name and branding.

## Shared with the web kit
`issue.py` (Linear, Jira, GitHub and local-file issues) is unchanged, the locks hook is the same, and so are the "Asking the user" conventions and the never-merge rule. Read the web kit's README for those details.
- **What's new in the hook:** it also honours `product/locks.txt`, so an approved definition, teardown and app shell are protected.
- **The backlog:** `product/backlog.md` uses the Markdown format `issue.py` already reads (`## R-4: …` plus a `Status:` line). A new app works without any tracker.

## Install into a project

```bash
<this kit>/install.sh ~/code/my-desktop-app      # or run it with no argument and it asks
```

The installer copies the kit into the project's `.claude/` and merges the hook into `settings.json`. It then writes a `CLAUDE.md` section that covers the product, the platform matrix (detecting Windows, macOS, Linux and WSL) and the commands, and adds `REVIEW.md`. For a new app, leave the commands as `TBD`: `/scaffold` fills them in. `--yes` accepts every default.

**Don't install both kits into one project.** They share skill names (`/intent`, `/build`, …), and the installer warns if the web kit is there.

**Requirements:**
- `python3`, for the hook;
- `gh`, signed in;
- the toolchain for your stack;
- for prototype screenshots, the Playwright MCP server or `npx playwright`;
- macOS builds, signing and notarization need a Mac or the `macos-latest` CI runners, plus an Apple Developer Program membership to sign;
- Windows signing needs a certificate or a cloud signing service.

## Limits
- **Skills are advisory.** The hard guarantees are the locks hook, the coverage checks (`T-n` → `D-n` → `R-n` → `AC-n`, screens and commands), and the verifier running with fresh context.
- **Some UI can't be automated everywhere.** Tauri has no real-app WebDriver on macOS, and native stacks need UI Automation or Appium. Where e2e isn't possible, it's recorded as `NOT CHECKED` and becomes a manual smoke step at release time, rather than a pretend pass.
- **Not yet run with a real session.** These skills are adapted from the web kit, whose own skills hadn't been run end to end yet either. The tooling notes in `stacks.md` must be checked against current docs at scaffold time; the skill says to do this.

## License
MIT. See `LICENSE`.
