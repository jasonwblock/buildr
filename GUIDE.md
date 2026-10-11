# Using the desktop SDLC skills

## One-time setup per project
Run `<kit>/install.sh <project>` and answer its questions about platforms, commands (leave them `TBD` for a new app) and issues. Then start a new Claude Code session in the project.

## A new app, start to finish
| Step | You type | You do |
|---|---|---|
| 1 | `/define <idea>`, or `/clone <app>`, or `/clone <app>, but <changes>` | Answer the rounds (or accept the defaults), pick parity for a clone, approve |
| 2 | `/prototype app` *(recommended)* | Click through the app shell in both platform modes, ask for changes, approve |
| 3 | `/roadmap` | Approve the milestones and the backlog |
| 4 | `/scaffold` | Approve the plan and the push to CI; the empty app now runs and packages on every OS |
| 5 | `/ship r-1` | Review the skeleton's PR, and merge it |

**Examples of step 1:**
- `/define a markdown journal that works offline and syncs later`
- `/clone Microsoft Planner`
- `/clone Microsoft Planner, but I want it offline-first, with time tracking per task, a weekly review view, and no Teams dependency`

## A feature, start to finish
| Step | You type | You do |
|---|---|---|
| 1 | `/intent R-4` (or an idea, or an issue) | Answer up to 4 questions, approve; you're warned if it departs from the definition |
| 2 | `/prototype R-4` *(UI only: screens, menus, dialogs, tray)* | Look at both platforms and both themes, approve |
| 3 | `/spec R-4` | Resolve each flag, or accept them all |
| 4 | `/build R-4` | Approve the plan, then wait. It builds, tests on the local OS and runs a fresh verifier |
| 5 | `/ship R-4` | It resolves the macOS/Windows CI-pending checks from CI. Review the PR and merge it |

## A release
1. `/release`: checks readiness and opens a release PR with the version bump and the changelog. **You merge it.**
2. `/release tag <version>`: asks before pushing the tag. Then CI signs, notarizes and creates a **draft** release, and the skill checks the signatures.
3. **You** run the smoke checklist in `releases/v<version>.md` (install, upgrade with real data, auto-update, uninstall) on each OS, then publish the draft.

## A bug or a crash
`/fix <description, crash report or issue>`, then `/ship <id>`.
- It writes a failing test first, on the OS where the bug happens. If you can't run that OS locally, the test fails in CI.
- It locks the test, then fixes the code without touching it.

## Incoming work
- **`/triage`** turns new issues and crash groups into drafts, all in one PR.
- **To act on a draft:**
  - `/intent <id>` for a feature;
  - `/fix <id>` for a bug;
  - `/roadmap` to schedule it.

## Where things live
| Path | What it is |
|---|---|
| `product/definition.md` | The approved app definition, with features `D-n` (locked) |
| `product/reference/<target>/teardown.md` | The clone teardown, with `T-n` features, `M-n` modifications and sources (locked) |
| `product/prototype-shell/` | The approved app-shell prototype (locked) |
| `product/roadmap.md`, `product/backlog.md` | Milestones, and the `R-n` work items |
| `work/<date>-<id>-<name>/` | One work item: `intent.md`, `prototype/`, `screens/`, `spec.md`, `plan.md`, `verify.md`, `ci-screens/` |
| `releases/v<version>.md` | The readiness table and the smoke checklist |

## Good to know
- **Approved files are locked.** To reopen one, delete its line from `work/<item>/locks.txt` or `product/locks.txt` yourself.
- **Platform honesty.** `CLAUDE.md` says which OSes run locally. Anything else is `CI-pending` until the CI matrix proves it. From WSL, Windows runs on the Windows host through `scripts/win-run.sh`, and macOS through CI.
- **Nothing reaches users without you.** Claude never merges, never publishes a release, and asks before pushing a release tag.
- **Signing secrets** live only in CI secrets. The skills check them by name and never see their values.
- **Teach it once.** When Claude makes the same mistake twice, add a line under *Things Claude gets wrong* in `CLAUDE.md`.
