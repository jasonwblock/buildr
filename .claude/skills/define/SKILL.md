---
name: define
description: Stage 0 (Define) of the desktop SDLC. Runs an interactive interview that turns an app idea, a target app to clone, or a clone with modifications ("a clone of Microsoft Planner, but…") into an approved product/definition.md for a Windows and macOS desktop app. Use when starting a new desktop app.
argument-hint: "[app idea in words | \"a clone of <app>\" | \"a clone of <app>, but <changes>\"]"
disable-model-invocation: true
---

# /define: decide what app we're building

You write `product/definition.md`, the app-level definition that every later stage traces back to. The user answers questions, corrects drafts and approves; they never write it themselves.

Input: $ARGUMENTS

## 0. Pick the mode
Read the input and choose one of three modes. Say which one in a line.

| Mode | Recognise it by | What happens |
|---|---|---|
| **Interview** | An idea, a problem, or nothing at all | You propose and the user picks, round by round (step 3) |
| **Clone** | "a clone of X", "like X", "a desktop X", "rebuild X" | `/clone`'s teardown runs first; the interview then only fills the gaps it leaves |
| **Clone + changes** | A target app plus changes: "X, but…", "X without…", "X with…", "X for <a different audience>" | As for Clone, and every change becomes a modification `M-n` mapped onto the teardown |

- **A named target app and no teardown:** if there's no `product/reference/<target-slug>/teardown.md` yet, read `.claude/skills/clone/SKILL.md` and follow its steps 1–6, passing it the whole input, modifications included. Then come back here at step 1.
- **The input is ambiguous** (for example "something like Trello"): ask with AskUserQuestion whether "Like X" means "Clone X's features (Recommended)" or "Just inspiration".
- **`product/definition.md` already exists:**
  - If it's approved, stop. A new feature goes through `/intent`. Reopening the definition means the user deletes its line from `product/locks.txt` themselves.
  - If it's a draft, offer to continue it.

## 1. Read before asking
- **The teardown,** if there is one: `product/reference/<slug>/teardown.md`, with its parity choices and modifications.
- **`CLAUDE.md`,** and any code already in the repo. If an app already exists, this is a re-definition, so read its windows, its data model and its packaging. Don't ask about anything the code answers.
- **`.claude/skills/scaffold/stacks.md`,** for the stack decision in round 6.
- **The questions:** `interview.md` (next to this file) holds the question bank and the recommended defaults for each round.

## 2. Seed a draft
Before you ask anything, write the best guess for every section of the template into `product/definition.md`, with `Status: draft`.
- **A clone:** the seed comes from the teardown.
  - Each `T-n` the user kept becomes a feature `D-n`, with `Source: T-n`.
  - Each `M-n` becomes a new `D-n`, or a change to one, with `Source: M-n`.
  - A dropped `T-n` goes under *Out of scope*.
- **Interview mode:** the seed is your proposal, built from the idea and the defaults in `interview.md`.

The seed is what makes the interview fast: every question offers the seeded answer as its recommended option.

## 3. Interview, round by round
The rounds, in order, with the questions themselves in `interview.md`:

1. **Purpose:** who it's for, the problem it solves, why it's a desktop app, and what success looks like.
2. **Shape:** the app's archetype, the main window's layout, and the MVP feature list (a multi-select of the seeded `D-n`).
3. **Data:** where data lives, accounts and sync, sharing, import and export, and how data is kept safe.
4. **Desktop integration:** tray or menu bar, notifications, launch at login, file types and links, global shortcuts.
5. **Platforms and distribution:** OS versions and CPU architectures, the distribution channel, updates, signing, licensing.
6. **Stack:** recommend one from `stacks.md`'s decision table, given the answers so far, and give two alternatives.
7. **Quality bars:** accessibility, localization, performance budgets, telemetry and privacy.

How to run them:
- **One AskUserQuestion call per round,** with at most 4 questions. The seeded answer is the first option, labelled "(Recommended)".
- **Skip what you already know.** Drop any question the input, the teardown or the code already answers. Skip a whole round if nothing in it is still open. For a clone, rounds 1 and 2 are usually mostly answered.
- **After the round 2 answers, offer a fast path.** Add one question to the round 3 call: "Accept recommended defaults for the rest (Recommended)" or "Go through every round". If the user accepts, fill rounds 3–7 with the seeded defaults and go straight to step 4.
- **After each round,** update the draft and show the user a compact diff of what changed (a few lines, not the whole file).
- **Follow up only on real gaps.** An answer typed under Other gets one follow-up question, and only if it opens a gap.
- **Never ask the user to design tables, IPC channels or APIs.** The spec derives those later.

## 4. Write the definition
Fill `product/definition.md` from the template below.
- **Features:** each feature gets one row in the table, with an id `D-n`, a tier (`MVP`, `Later` or `Out`) and a source (`T-n`, `M-n`, `interview` or `input`).
- **For a clone,** check the coverage mechanically. This must print nothing:
  ```bash
  comm -23 <(grep -E '^\| T-[0-9]+ .*\| (MVP|Change) \|\s*$' product/reference/<slug>/teardown.md | grep -oE '^\| T-[0-9]+' | tr -d '| ' | sort -u) <(grep -oE 'T-[0-9]+' product/definition.md | sort -u)
  comm -23 <(grep -oE '^\| M-[0-9]+' product/reference/<slug>/teardown.md | tr -d '| ' | sort -u) <(grep -oE 'M-[0-9]+' product/definition.md | sort -u)
  ```
  The first command covers every `T-n` whose parity is MVP or Change. The second covers every modification `M-n`. If either prints an id, fix the definition.
- **The name:** propose the app's own name, which for a clone must not be the target's name or a confusable variant of it. Then the slug, the bundle identifier (`com.<org>.<app>`), and the data folder name.

## 5. Review and approve
Show the user the definition: the summary, the feature table, and the platform and stack decisions. Then, in one AskUserQuestion call, ask:
- **Each open question still in the draft,** one question each, with its default first. Answered ones move into the right section.
- **The approval:** "Approve (Recommended)" or "Request changes".

Apply any changes, then ask again.

## 6. On approval
1. If the folder isn't a git repository yet, ask "Initialize git here (Recommended)" or "Not now". Commit only if there is a repository.
2. Set `Status: approved`.
3. Lock it: `echo "product/definition.md" >> product/locks.txt`.
4. In `CLAUDE.md`, inside the kit's section, set the `App:`, `Stack:` and `Targets:` lines. If there's no kit section, add those three lines under a `## Product` heading.
5. Commit with the message `define(<app-slug>): <App name> definition`.

## 7. Next step
Tell the user the next two steps:
- **`/prototype app`** (recommended): a clickable shell of the main window, its navigation and its menus, so they can see the app before it's split up;
- **`/roadmap`:** splits the definition into milestones and a backlog.

## Asking the user
Use the **AskUserQuestion** tool for every question and every approval, not a question in prose.
- **Batching:** up to 4 questions per call, with 2–4 options each. Use `multiSelect` for "which of these are in the MVP".
- **The default** is the first option, labelled "(Recommended)".
- **Wording:** labels are short (1–5 words) and the reasoning goes in each option's description. Headers are at most 12 characters.
- **Free text:** the tool always adds "Other" for a typed answer, so never add an "Other" option yourself.
- **An approval is a question too:** "Approve (Recommended)" or "Request changes". Apply whatever the user types under Other, then ask again.
- **Without AskUserQuestion** (a headless run, or another agent harness), ask in one numbered message instead, with the default after each question.

## Template

```markdown
# <App name>: product definition
Status: draft
Origin: interview | clone of <Target> | clone of <Target> with modifications
Teardown: product/reference/<slug>/teardown.md (clone modes only)
Date: <YYYY-MM-DD>

## Summary
One paragraph: what it is, who it's for, and why it's a desktop app.

## Identity
- Name: · Slug: · Bundle id: com.<org>.<app> · Data folder: <AppName>
- For a clone, what makes it distinct: its own name, icon, palette and copy; no trademarks of <Target>.

## Users and problems
Each user type, their main jobs, and what better looks like for them.

## Core concepts
The things users create and manage, in their own words (e.g. Plan, Bucket, Task), and how they relate.

## Features
| ID | Feature | Tier | Source | Notes |
|---|---|---|---|---|
| D-1 | … | MVP | T-3 | … |
Tier is MVP, Later or Out. Source is T-n, M-n, interview or input.

## App shape
- Archetype: document-based | workspace/library | utility/tray | editor/tool | other
- Main window: layout (e.g. sidebar + content + inspector), default size, minimum size
- Other windows and dialogs: settings, about, secondary windows, multi-window rules
- Menus: the top-level menus and the commands that must be in them
- Shortcut conventions: Ctrl on Windows, Cmd on macOS; any app-specific shortcuts
- Presence: dock/taskbar only | plus tray/menu bar | tray/menu bar only; close-vs-quit behaviour on each OS

## Data
- Where data lives: local database | user-owned files | cloud with local cache
- Accounts and sync: none | optional | required; conflict rule
- Sharing and collaboration:
- Import and export: formats, including interop with <Target>'s exports where that's lawful
- Safety: autosave, undo depth, trash and restore, backups
- Upgrades: data from older versions must always open (migrations)

## Desktop integration
Notifications · launch at login · file associations · URL scheme (deep links) · global shortcuts · drag and drop · clipboard · printing · share

## Platforms and distribution
- Windows: minimum version, architectures (x64, ARM64)
- macOS: minimum version, architectures (Apple Silicon, Intel, or universal)
- Linux: no | later | yes (formats)
- Channel: direct download | Microsoft Store | Mac App Store | winget/Homebrew
- Updates: automatic in-app | store-managed | manual
- Signing: Windows code-signing method; Apple Developer ID and notarization
- Licensing and price:

## Stack
- Decision: <stack> — why, in two or three sentences, tied to the answers above
- Alternatives considered: <stack> — why not; <stack> — why not
- Verification approach on each OS (from stacks.md)

## Quality bars
- Accessibility: keyboard-only use; screen readers (Narrator, NVDA, VoiceOver); contrast; high-contrast mode
- Localization: languages at launch; right-to-left?
- Performance: cold start under <n> s; idle memory under <n> MB; large-data target (e.g. 10k tasks)
- Privacy and telemetry: none | opt-in | opt-out; crash reporting
- Display: HiDPI, light and dark themes following the OS

## Out of scope
## Open questions
Only what the user chose to leave open, each with the default that applies if nobody answers.
```

## Rules
- Write in the user's terms. Implementation detail belongs in the spec, except for the stack decision.
- Leave a section out if it doesn't apply; never pad.
- **For a clone,** replicate function, not identity:
  - never reuse the target's name, logo, icons, illustrations, help text or marketing copy;
  - never decompile it, scrape behind a login, or bypass its licensing.
- Once `product/definition.md` is in `product/locks.txt`, a hook refuses edits to it. If the user wants to reopen it, tell them to delete its line from `product/locks.txt` themselves.
