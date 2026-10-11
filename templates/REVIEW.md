# Review instructions

## Passes
Run four passes and tag each finding with its pass:
- **Bugs:** logic errors, broken edge cases, regressions in neighbouring flows, state that isn't shared between windows, and resource leaks (listeners, file handles, timers) in long-running sessions.
- **Desktop security:**
  - **Web-tech stacks:** IPC or commands exposed without input validation; a renderer that gains Node or filesystem access (Electron `contextIsolation`, `sandbox` or `nodeIntegration` changed, Tauri capabilities widened); `shell.openExternal` or open-URL calls on untrusted input; navigation or new windows not denied by default; CSP loosened.
  - **Files:** path traversal in file open, save or import; unsafe deserialization of user files.
  - **Updates:** update artifacts not signature-checked.
  - **Secrets:** secrets or tokens in the source, the bundle or the logs; personal data in logs or crash reports.
  - **A backend:** permissions enforced only in the UI.
- **Platform:** a hard-coded Ctrl or Cmd instead of the platform's modifier; hard-coded paths or separators instead of the platform APIs; case-sensitive file-name assumptions; locale-dependent parsing; HiDPI or scaling issues; a menu item in the wrong place for the OS's conventions; an OS-specific branch without a test on that OS.
- **Compliance:**
  - the diff matches the work item's `spec.md` (every `AC-n` and its platform tag) and its `plan.md`, and departures from the plan are explained;
  - every schema change has a migration and a test from the last released schema;
  - the prototype's `data-testid`s and command ids are kept;
  - no file listed in `work/*/locks.txt` or `product/locks.txt` changed;
  - no CI OS was removed or made non-blocking.

## What Important means here
Reserve Important for findings that would break behaviour, lose user data, weaken the app's sandbox or signing, leak data, or contradict the spec. Style and naming are nits.

## Cap the nits
Report at most five nits; summarize the rest as a count.

## Do not report
Generated files, lockfiles, the `prototype/` design files, the CI screenshot artifacts, and anything CI already enforces.
