---
name: scaffold
description: Builds work item R-1, the walking skeleton of the desktop app. Sets up the chosen stack, main window, app menu, data folder and migrations, test/e2e/screenshot/package commands, and a Windows + macOS CI matrix, then verifies the empty app launches. Use after /roadmap, once per app.
argument-hint: "[optional: R-1 or a different skeleton item id]"
disable-model-invocation: true
---

# /scaffold: a walking skeleton on every target OS

You build the app's skeleton: it launches, shows the main window and the menu, stores data in the right place, and builds, tests and packages on each target OS in CI. It has no features yet. Every later `/build` relies on the commands you set up here.

Input: $ARGUMENTS. It defaults to `R-1` from `product/backlog.md`.

## 1. Read
- `product/definition.md`, which must be approved. You need its Stack, App shape, Data, and Platforms and distribution sections, and its Identity.
- `product/backlog.md`, for the skeleton item.
- `product/prototype-shell/`, if it exists: its `menus` object and its main window layout seed the menu and the window.
- `.claude/skills/scaffold/stacks.md`, the section for the chosen stack. Then **check the stack's current official docs** (WebFetch) for the create command, the test tooling and the packaging. Note any difference from `stacks.md`.
- `CLAUDE.md`.

**Stop if the repo already has app code.** Offer instead to fill in only what's missing from the skeleton checklist in `stacks.md`, as a normal `/intent` work item.

## 2. Probe the environment
Run these, and paste the results:
- **The OS:** `uname -a`. In WSL, `grep -qi microsoft /proc/version && echo WSL`.
- **The toolchains:** whichever of `node -v`, `npm -v`, `cargo -V`, `dotnet --version`, `flutter --version` and `gh --version` apply.
- **From WSL:** `powershell.exe -NoProfile -Command '$PSVersionTable.PSVersion; node -v; dotnet --version'`. This checks the Windows host's toolchain.
- **On a Mac:** `xcode-select -p`.

Then work out the **platform matrix**:
- **Run locally:** the target OSes you can actually build, launch and screenshot here. From WSL, Windows is local only through the Windows host, with `scripts/win-run.sh`.
- **CI only:** every other target, typically macOS.

If a toolchain is missing, list what to install, and ask with AskUserQuestion: "I'll install it now" (the user runs it themselves; suggest `! <command>`), or "Scaffold with CI-only verification for that OS".

## 3. Plan (no code yet)
Enter plan mode if you can. The plan covers:
- **The create command,** with its flags, from the docs you checked. Also the folder layout.
- **Identity:**
  - the app name;
  - the bundle id;
  - the Windows AppUserModelID (the same as the bundle id);
  - the data folder name;
  - the icon placeholder: our own, never a clone target's.
- **The skeleton checklist** from `stacks.md`, item by item. For each item, say which file holds it and the test that proves it.
- **The commands** that go in `CLAUDE.md`:
  - **Test** (unit and component);
  - **Lint;**
  - **Build;**
  - **Start** (dev);
  - **E2E** (the real app);
  - **Screenshot:** `<command> <screen-id> [--theme light|dark] [--size WxH] --out <path>`;
  - **Package** (unsigned, for the local OS).

  For Windows from WSL, wrap the commands in `scripts/win-run.sh`.
- **CI:** `.github/workflows/ci.yml`, from the skeleton in `stacks.md`, with the stack's setup steps and the screenshot artifact upload.
- **Security defaults** for the stack (`stacks.md`).
- **What can't be verified where,** for example "Tauri: no real-app e2e on macOS; mocked-IPC screenshots plus a manual smoke list".

Get the user's approval:
- **In plan mode,** exiting plan mode is the approval prompt.
- **Otherwise,** use AskUserQuestion: "Approve the plan (Recommended)" or "Request changes".

## 4. Create the work item and build
1. **The work item.** Create `work/<YYYY-MM-DD>-r-1-walking-skeleton/`. If you're on `main` or `master`, create and switch to the branch `work/R-1-walking-skeleton`. Write `plan.md` from the approved plan, and commit it with the message `plan(r-1-walking-skeleton): walking skeleton`.
2. **The stack.** Run the create command, then build the checklist in small commits.
3. **The menu.** Build it from the definition's App shape, or from the shell prototype's `menus`, with each OS's conventions:
   - **macOS:** an app menu with About, Settings… (Cmd+,), Hide and Quit (Cmd+Q). Edit and Window menus with the standard roles.
   - **Windows:** a File menu that ends with Exit, Settings under Tools or File, and Help ▸ About.

   Commands not built yet stay out of the menu. Never ship dead items.
4. **Smoke tests,** which the skeleton gets now:
   - the app launches and the main window has the expected title;
   - the data folder resolves to the platform path, and the migrations run from empty;
   - window state is restored across a relaunch;
   - a second launch focuses the first instance;
   - the screenshot command produces `main` in light and dark.
5. **The commands in `CLAUDE.md`.** Write them into the kit section (replacing `TBD`). Also fill in the `## Platforms` lines: Targets, Dev machine, Run locally on, and Verified only in CI on.
6. **Run everything you can locally,** and paste the output:
   - test;
   - lint;
   - build;
   - e2e;
   - the screenshot of `main` in light and dark, saved to `work/<folder>/verify-screens/`;
   - package.

   Look at the screenshots yourself.
7. **Push the branch and run CI on every target OS.**
   - First ask with AskUserQuestion: "Push the branch and run CI (Recommended)" or "Not yet". If there's no GitHub remote, say so, and suggest `gh repo create`.
   - Watch the run: `gh run watch`.
   - Then download the screenshot artifacts into `work/<folder>/ci-screens/<os>/` with `gh run download <id> --dir …`, and look at them.

## 5. Verify
1. Spawn the `verifier` subagent. Give it the work folder and the start command.
2. Fix the blocking findings, and verify once more.
3. Write `verify.md`. It holds:
   - the verifier's report;
   - the command output;
   - the CI run's link, with its result per OS;
   - the platform matrix;
   - what was checked only in CI, or not at all.
4. Commit it.
5. Mark `R-1` `Status: in review` in `product/backlog.md`.

## 6. Next step
`/ship r-1`, then the first feature: `/intent R-2`.

## Asking the user
Use the **AskUserQuestion** tool for every question and every approval, not a question in prose.
- **Batching:** up to 4 questions per call, with 2–4 options each.
- **The default** is the first option, labelled "(Recommended)".
- **Wording:** labels are short (1–5 words) and the reasoning goes in each option's description. Headers are at most 12 characters.
- **Free text:** the tool always adds "Other" for a typed answer, so never add an "Other" option yourself.
- **An approval is a question too:** "Approve (Recommended)" or "Request changes". Apply whatever the user types under Other, then ask again.
- **Without AskUserQuestion** (a headless run, or another agent harness), ask in one numbered message instead, with the default after each question.

## Rules
- **Never** commit certificates, signing passwords, API keys or updater private keys. Never weaken the stack's security defaults to make something work.
- **Never claim a platform was verified** if it wasn't run there. CI evidence counts; an assumption doesn't.
- **Pin your dependencies** (lockfiles committed). Don't use tooling the docs mark as deprecated.
- **Install system-wide tools only with the user's consent.** That includes SDKs, Xcode and Visual Studio components.
