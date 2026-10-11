---
name: roadmap
description: Stage 0b (Plan) of the desktop SDLC. Splits the approved product/definition.md into milestones and a backlog of shippable work items (R-n), starting with a walking skeleton, and checks that every MVP feature is covered. Use after /define (and optionally /prototype app).
argument-hint: "[optional: milestone count or focus]"
disable-model-invocation: true
---

# /roadmap: from a definition to a backlog

A whole app is too big for one work item. You write:
- `product/roadmap.md`: the milestones, and why they're in that order;
- `product/backlog.md`: one heading per work item `R-n`, in a format `/intent R-n` can read.

Input: $ARGUMENTS

## Steps

1. **Read:**
   - `product/definition.md`, which must be approved;
   - the teardown, if there is one;
   - `product/prototype-shell/` and its notes, if `/prototype app` ran;
   - `CLAUDE.md`;
   - `.claude/skills/scaffold/stacks.md`.

   If a `product/roadmap.md` already exists, update it: keep the existing `R-n` ids, mark done items, and add new ones at the end of the numbering.

2. **Shape the milestones.**
   - **M0, the walking skeleton.** It's always `R-1`, built by `/scaffold`: the stack, the main window, the app menu, the data folder and migrations, the commands, a CI matrix on every target OS, and an unsigned package per OS. No features.
   - **M1 onwards, vertical slices.** Each milestone leaves the app usable for something real.
     - Core objects come first, and each is built end to end: storage, UI, menus and shortcuts.
     - Then come the features that depend on them, in dependency order.
     - For a clone, follow the target's key flows, so the first slices let the user complete its most common flow.
   - **The last MVP milestone, release readiness:**
     - signed installers on each OS;
     - automatic updates, per the definition;
     - first-run and empty states;
     - an accessibility pass;
     - an upgrade test from the previous version;
     - a crash-reporting opt-in, if the definition asks for one.
   - **Later-tier features** go into a final "After MVP" milestone, unordered.

3. **Size the work items.**
   - Each `R-n` is one `/intent → /build → /ship` cycle, a few days of work at most. Split anything larger.
   - **Cross-cutting definition rules** get their own items where they need groundwork, for example "Undo/redo infrastructure" before the features that use it, or "Sync-ready IDs and timestamps" if sync is Later.
   - **Each item records:**
     - the `D-n`s it covers;
     - what it depends on (`R-n`);
     - whether it has UI;
     - its platform risk, if any (e.g. "macOS menu-bar extra behaves differently");
     - its size: S, M or L.

4. **Write the files** from the templates below. Then check the coverage mechanically. This must print nothing:
   ```bash
   comm -23 <(grep -E '^\| D-[0-9]+ \|[^|]*\| MVP \|' product/definition.md | grep -oE '^\| D-[0-9]+' | tr -d '| ' | sort -u) <(grep -oE 'D-[0-9]+' product/backlog.md | sort -u)
   ```
   If it prints any ids, add work items for them.

5. **Approve.** Show the milestone list, with each milestone's items as one line apiece. Then ask in one AskUserQuestion call:
   - **The approval:** "Approve (Recommended)" or "Request changes".
   - **Where the backlog lives:**
     - "`product/backlog.md` (Recommended)": the default when `Tracker:` in `CLAUDE.md` is `none` or a file;
     - "Also create tracker issues": offer this only if a tracker is configured:
       - GitHub: create the issues with `gh issue create`, one per `R-n`, labelled with the milestone;
       - Linear or Jira: create them through a connected MCP server.

       Write each new issue's key into its backlog heading (`## R-4: … (ENG-57)`). If no MCP server is connected for that tracker, say so and keep the file.
6. **On approval:**
   - **The tracker line:** if `Tracker:` is `none`, set it to `file:product/backlog.md` in `CLAUDE.md`, so `/intent R-4` resolves.
   - **Commit** with the message `roadmap(<app-slug>): <n> milestones, <m> work items`.
   - **Don't lock the roadmap.** It's a plan that changes as work lands. `/ship` marks items done.
7. **Next step:** `/scaffold`. It builds `R-1`, then the features follow with `/intent R-2`.

## Asking the user
Use the **AskUserQuestion** tool for every question and every approval, not a question in prose.
- **Batching:** up to 4 questions per call, with 2–4 options each.
- **The default** is the first option, labelled "(Recommended)".
- **Wording:** labels are short (1–5 words) and the reasoning goes in each option's description. Headers are at most 12 characters.
- **Free text:** the tool always adds "Other" for a typed answer, so never add an "Other" option yourself.
- **An approval is a question too:** "Approve (Recommended)" or "Request changes". Apply whatever the user types under Other, then ask again.
- **Without AskUserQuestion** (a headless run, or another agent harness), ask in one numbered message instead, with the default after each question.

## Templates

`product/roadmap.md`:
```markdown
# Roadmap: <App name>
Definition: product/definition.md · Backlog: product/backlog.md · Updated: <YYYY-MM-DD>

## M0: Walking skeleton
Goal: … · Items: R-1
## M1: <name>
Goal: what a user can do when this milestone ships · Items: R-2, R-3, …
## Release readiness
## After MVP

## Order and reasoning
Why this order: dependencies, the riskiest assumptions first, and the target's key flows (for a clone).
```

`product/backlog.md`: `/intent`, `/triage` and `issue.py` read this file.
- Each item is a level-2 heading that starts with its id, followed by a `Status:` line.
- Never write `- [ ]` checklist lines that contain an id: the parser reads those as issues too.

```markdown
# Backlog: <App name>

## R-1: Walking skeleton
Status: todo
Milestone: M0 · Size: M · UI: yes · Depends on: none
Covers: (none; infrastructure)
What: launches into the main window with the app menu; data folder and migrations; CI on Windows and macOS; unsigned packages.
Platform risk: …

## R-2: <title>
Status: todo
Milestone: M1 · Size: S · UI: yes · Depends on: R-1
Covers: D-1, D-4
What: one or two sentences in the user's terms.
```
`Status:` is one of `todo`, `in progress`, `in review` or `done`.

## Rules
- Don't invent features. Every item traces to a `D-n`, or is infrastructure that a `D-n` or a definition rule needs. Say which.
- Keep the definition's names for things.
