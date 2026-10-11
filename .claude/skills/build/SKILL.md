---
name: build
description: Stage 3 (Build) of the desktop SDLC. Plans in plan mode, commits plan.md, implements against the approved spec with its own feedback loop on the local OS, records which platform-tagged ACs only CI can prove, then runs the fresh verifier. Use after /spec is approved.
argument-hint: "[work item slug or issue id]"
disable-model-invocation: true
---

# /build: plan, implement, verify

Work item: $ARGUMENTS. It's a slug, a work folder, or an issue id (`R-4`, `ENG-123`, `#45`), which matches the `work/*` folder whose name contains it, lowercased, with `#` written as `gh-`. If it's empty, use the most recently modified `work/*/` folder whose spec is approved and which has no `verify.md`. Name it in one line.

## 1. Read everything first
- `intent.md` and `spec.md`. The spec must be approved.
- If there's UI: `prototype-notes.md`, the snapshot in `prototype/`, and `screens/*.png`.
- `CLAUDE.md`: the Commands, the Platforms (which OSes run locally and which only in CI), and the verification section.
- `.claude/skills/scaffold/stacks.md`, the section for this stack: its security defaults and its test layers.

## 2. Plan (no code yet)
1. Enter plan mode if you can (EnterPlanMode). Otherwise, plan without editing any files.
2. Draft a plan with these sections:
   - **Files:** the files that change and what each gets.
   - **Order of work.** Data and migrations first, then the core/IPC layer, then the UI, menus and shortcuts, then OS integration.
   - **Risks:** what this could break (other windows, older data, the other OS, packaging), and the riskiest step.
   - **Coverage:** a table mapping **every** `AC-n`, every changed screen and every menu command to the files and the test that proves it. The table also has a column for where it's proven: `local` or `CI <os>`.
   - **Alternatives:** the options you didn't take, and why.
3. Check the coverage mechanically. All three commands must print nothing:
   ```bash
   comm -23 <(grep -oE 'AC-[0-9]+' work/<folder>/spec.md | sort -u) <(grep -oE 'AC-[0-9]+' work/<folder>/plan.md 2>/dev/null | sort -u)
   comm -23 <(grep -oE '^- #[a-z0-9-]+' work/<folder>/prototype-notes.md 2>/dev/null | cut -c3- | sort -u) <(grep -oE '#[a-z0-9-]+' work/<folder>/plan.md 2>/dev/null | sort -u)
   comm -23 <(grep -oE '^- cmd:[a-z0-9.-]+' work/<folder>/prototype-notes.md 2>/dev/null | cut -c3- | sort -u) <(grep -oE 'cmd:[a-z0-9.-]+' work/<folder>/plan.md 2>/dev/null | sort -u)
   ```
   Run them after writing `plan.md`. The second checks the screen ids (`- #tasks` lines in the notes). The third checks the menu command ids (`- cmd:file.new-task` lines). In `plan.md`, write screen and command ids exactly that way (`#tasks`, `cmd:file.new-task`). If any check prints ids, fix the plan.
4. Get the user's approval:
   - **In plan mode,** exiting plan mode is the approval prompt.
   - **Otherwise,** use AskUserQuestion: "Approve the plan (Recommended)" or "Request changes".

   Once they accept it:
   - write `work/<folder>/plan.md`;
   - run the coverage checks;
   - commit with the message `plan(<slug>): <title>`.

## 3. Implement, with your own loop
- **Work in the order the plan gives,** in small commits.
- **Loop until the targets pass,** typically 2–3 rounds:
  - write the code and tests for the next AC;
  - run the test, lint and build commands from `CLAUDE.md`;
  - fix the code, never the test or the target.
- **Data:**
  - every schema change ships with a migration, and a test that opens a fixture database from the last released schema;
  - add the fixture if it's missing, by generating it from the previous release's schema;
  - never edit an old migration.
- **The UI:**
  - start the app on a local OS, and use the **Screenshot** command for each changed screen, in the same state, platform and theme as `screens/*.png`;
  - compare layout, elements, hierarchy, menus and copy, not pixels;
  - adjust;
  - check the minimum window size and the dark theme.
- **Menus and shortcuts:** register them through the stack's menu and accelerator API, with the platform's modifier (Ctrl or Cmd). Test that each command is reachable from its menu and its shortcut.
- **Security:** keep the stack's security defaults from `stacks.md`. New IPC commands validate their input, and expose only what the spec lists.
- **Keep the prototype's `data-testid`s and command ids** in the app, or their accessibility-id equivalents on non-web stacks.
- **ACs tagged for an OS you can't run locally:**
  - write their tests so they run in CI on that OS;
  - list them in `plan.md` as `CI <os>`;
  - never mark them passed from a local run on a different OS.
- **If you depart from the plan,** update `plan.md` in the same commit and say why.

## 4. Verify with fresh context
1. Spawn the `verifier` subagent. Give it the work folder path and the command that starts the app. Nothing else: it must form its own view.
2. Fix every finding marked **blocking**. Then run the verifier **once** more on the result.
3. Write `work/<folder>/verify.md`. It holds:
   - the verifier's final report;
   - the commands run and their pasted output;
   - a **platform table:** each `AC-n` with `pass`, `fail`, `CI-pending <os>` or `not checked`, and its evidence;
   - the findings left open, with a reason for each.
4. Commit it. `/ship` resolves the `CI-pending` rows from the CI run on the PR.

## 5. Report
Tell the user:
- which ACs passed locally;
- which are CI-pending, and on which OS;
- what's left open;
- where the screenshots are;
- the next step: `/ship <slug>`.

## Asking the user
Use the **AskUserQuestion** tool for every question and every approval, not a question in prose.
- **Batching:** up to 4 questions per call, with 2–4 options each.
- **The default** is the first option, labelled "(Recommended)".
- **Wording:** labels are short (1–5 words) and the reasoning goes in each option's description. Headers are at most 12 characters.
- **Free text:** the tool always adds "Other" for a typed answer, so never add an "Other" option yourself.
- **An approval is a question too:** "Approve (Recommended)" or "Request changes". Apply whatever the user types under Other, then ask again.
- **Without AskUserQuestion** (a headless run, or another agent harness), ask in one numbered message instead, with the default after each question.

## Rules
- **Never edit** anything listed in `work/*/locks.txt` or `product/locks.txt`, the living prototype, or tests that existed before this build, unless the spec says to change them. If a locked artifact is wrong, stop and ask with AskUserQuestion: "Stop so I can reopen it (Recommended)", or "Build it as specified". Say what's wrong in the question.
- **Never skip, delete or weaken a failing test** to get green. That includes adding a platform skip to a test that fails on one OS.
- **Show the output of every command you rely on.** Don't summarize it.
