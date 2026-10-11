---
name: ship
description: Stage 5 (Deploy) of the desktop SDLC. Opens the PR for a verified work item, resolves CI-pending acceptance criteria from the Windows/macOS CI matrix and its screenshot artifacts, then works review comments and failing checks until it is green and waiting only on the user. Never merges and never publishes a release. Use after /build, /fix or /scaffold.
argument-hint: "[work item slug or issue id]"
disable-model-invocation: true
---

# /ship: a green PR on every OS, waiting only on you

Work item: $ARGUMENTS. It's a slug, a work folder, or an issue id (`R-4`, `ENG-123`, `#45`), which matches the `work/*` folder whose name contains it, lowercased, with `#` written as `gh-`. If it's empty, use the most recently modified `work/*/` folder that has a `verify.md`. Name it in one line.

## Steps

1. **Check before opening the PR.**
   - `verify.md` exists, and it lists no open blocking findings. If it does, ask with AskUserQuestion, listing the findings in the question: "Stop and fix them first (Recommended)" or "Ship anyway".
   - The branch isn't `main` or `master`.
   - The working tree is clean.
2. **Release the test locks.**
   - Remove from `locks.txt` every line that isn't under `work/`, so later work can change those tests and fixtures again:
     ```bash
     grep '^work/' work/<folder>/locks.txt > work/<folder>/locks.tmp; mv work/<folder>/locks.tmp work/<folder>/locks.txt
     ```
   - If the work came from `product/backlog.md`, set the item's `Status: done` in this branch. The backlog then reads done exactly when the PR merges.
   - Commit, if anything changed.
3. **Push the branch and open the PR** with `gh pr create`. Target the default branch unless `CLAUDE.md` names another.
   - **The title:** if the work came from an issue, start with its id: `R-4: <title>` or `ENG-123: <title>`.
   - **The body:**
     - **What and why:** two or three sentences from the intent.
     - **The issue link,** taken from the `Source:` line of `intent.md` or `bug.md`:

       | Source | Line |
       |---|---|
       | Linear | `Closes ENG-123` |
       | GitHub | `Closes #45` (or `Closes owner/repo#45` for another repo) |
       | Jira | the key in the title is enough; add the issue's URL |
       | Backlog or local file | `Source: product/backlog.md#R-4` |
     - **Links:** `intent.md`, `spec.md`, `plan.md`, `verify.md`.
     - **Acceptance:** a table of each `AC-n` with its platform tag and its result per OS.
     - **Departures from the plan,** and the findings left open.
     - **Screenshots:** links to the `screens/` files, and to the build's screenshots.
     - **Packaging impact,** if the spec has any: new entitlements, file associations, URL schemes.
   - **Report back to the issue,** if it came from a tracker:
     - **A comment** with the PR URL: `python3 .claude/scripts/issue.py comment "<ref>" "PR: <url>"`.
     - **The status:** only if `CLAUDE.md` says `Status updates: on`, run `python3 .claude/scripts/issue.py status "<ref>" "<In review state>"`.
     - **If the script exits with 3,** skip the step.
4. **Resolve the CI-pending ACs** from the PR's CI run.
   1. Watch the checks: `gh pr checks <n> --watch`.
   2. Download the screenshot artifacts: `gh run download <run-id> --dir work/<folder>/ci-screens/`.
   3. Read the per-OS test results in the run's logs.
   4. **For each `CI-pending <os>` row in `verify.md`,** set it to `pass` or `fail`, with the evidence (the run link and the test name or screenshot path). Compare the CI screenshots against `screens/*-<os>-*.png`: layout, elements, hierarchy and copy, not pixels.
   5. A `fail` here is a blocking finding. Fix it in a new commit, push, and repeat.
   6. Commit the updated `verify.md` and the CI screenshots.
5. **Babysit the PR,** for at most 3 rounds:
   1. `gh pr checks <n> --watch`, and read the result **per OS**. A job that fails only on one OS is still a failure.
   2. Read the unresolved review comments: `gh pr view <n> --comments`, plus `gh api repos/{owner}/{repo}/pulls/<n>/comments` for comments on lines.
   3. **For a failing check:** find the cause, fix it, and push a new commit.
   4. **For a review comment:**
      - fix it if it's right and within the spec;
      - reply with your reasoning if you disagree;
      - list it for the user if it changes the spec.
   5. If the same mistake was flagged twice, propose a one-line addition to `CLAUDE.md` in the PR.
6. **Report:**
   - the PR URL;
   - whether the checks are green on each OS;
   - the ACs per OS;
   - what's waiting on the user: approval, the comments you didn't act on, and any `not checked` rows;
   - the next step after the merge: `/intent <next R-n>`, or `/release` when the milestone is complete.

## Asking the user
Use the **AskUserQuestion** tool for every question and every approval, not a question in prose.
- **Batching:** up to 4 questions per call, with 2–4 options each.
- **The default** is the first option, labelled "(Recommended)".
- **Wording:** labels are short (1–5 words) and the reasoning goes in each option's description. Headers are at most 12 characters.
- **Free text:** the tool always adds "Other" for a typed answer, so never add an "Other" option yourself.
- **An approval is a question too:** "Approve (Recommended)" or "Request changes". Apply whatever the user types under Other, then ask again.
- **Without AskUserQuestion** (a headless run, or another agent harness), ask in one numbered message instead, with the default after each question.

## Rules
- **Never merge,** never push to `main` or `master`, never force-push, never skip hooks (`--no-verify`).
- **Never weaken a test or a check to get green.** That includes removing an OS from the CI matrix, or marking a job `continue-on-error`.
- **Never tag or publish a release here.** That's `/release`.
