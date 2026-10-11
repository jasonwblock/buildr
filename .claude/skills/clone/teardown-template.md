# Teardown template

Copy this into `product/reference/<target-slug>/teardown.md`, and keep the table layouts exactly as they are: `/define` and `/roadmap` check them with grep.
- Each inventory row starts with `| T-n |`, and its **last** column is the parity: `MVP`, `Later`, `Drop` or `Change`, left empty until step 4.
- Each modification row starts with `| M-n |`.

```markdown
# Teardown: <Target> (<vendor>, <edition/surface>, as of <YYYY-MM-DD>)
Status: draft
Requested: <the user's request, verbatim>

## What it is
Two or three sentences: who it's for, its core job, and where it runs today (web, Teams, mobile, desktop).

## Core objects
The things users create and manage, and how they relate (e.g. Plan 1─* Bucket 1─* Task; Task *─* Label; Task 1─* Checklist item).
Note the limits, where documented (e.g. "up to 20 checklist items per task" [3]).

## Views and windows
| View | What it shows | Main actions | Desktop translation |
|---|---|---|---|
| Board | Tasks as cards in bucket columns | Drag between buckets; quick add | Main window content area; drag and drop |

## Feature inventory
| ID | Area | Feature | Evidence | Confidence | Parity |
|---|---|---|---|---|---|
| T-1 | Tasks | Create a task with title, due date and assignee | [2] | documented | |
| T-2 | Views | Board view grouped by bucket, progress or priority | [2], user-evidence/board.png | observed | |

## Key flows
Numbered steps for the 3–6 flows users do most (e.g. "Create a plan → add buckets → add tasks → assign → track progress").

## Keyboard shortcuts
| Action | Target's shortcut | Ours (Windows / macOS) |
|---|---|---|

## Integrations and platform behaviour
Sign-in and accounts, notifications (email, push), calendar sync, import and export formats, offline behaviour, sharing and permission levels.

## Pain points and gaps
From reviews and forums: what users ask for or complain about. These are often good modifications. Cite each one.

## Modifications
| ID | Requested change (user's words) | Kind | Maps to | Resolution |
|---|---|---|---|---|
| M-1 | Works fully offline | cross-cutting | T-14 (Change), T-15 (Drop) | Local SQLite; sync is Later |

Kind is adds, changes T-n, removes T-n, or cross-cutting.

## Unknowns
Behaviour we couldn't observe or confirm, each with the assumption /define will offer as a default.

## Not ours to copy
The target's name, logo, icons, illustrations, colour palette, and any UI copy or help text that's distinctive. Note anything specific here (e.g. its signature colour or mascot).

## Sources
1. <title>: <url> (retrieved <date>)
```
