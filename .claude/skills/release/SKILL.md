---
name: release
description: Stage 6 (Release) of the desktop SDLC. Prepares a versioned release of the desktop app — version bump, changelog, readiness checks against the definition — as a PR; after the user merges it, tags (with approval) to run the signing/notarizing release workflow, checks the signed Windows and macOS installers, and leaves a DRAFT GitHub Release plus a manual smoke checklist. Never publishes.
argument-hint: "[version (e.g. 1.2.0) | patch | minor | major | tag <version>]"
disable-model-invocation: true
---

# /release: signed installers, waiting only on you to publish

Input: $ARGUMENTS

A release has two phases, and each one runs as its own invocation:
- **Prepare:** a release PR with the version bump and the changelog. This is the default.
- **Tag:** after the user has merged that PR, tag it, run the release workflow, and check its output. Run as `tag <version>`. If the input is empty, it's chosen automatically when the version on the default branch has no tag yet.

## Prepare

1. **Read:**
   - `product/definition.md`: Platforms and distribution, and the Quality bars;
   - `product/roadmap.md` and `product/backlog.md`;
   - `CLAUDE.md`;
   - `CHANGELOG.md`, if it exists;
   - the version source for the stack (`package.json`, `src-tauri/tauri.conf.json` and `Cargo.toml`, `*.csproj` `<Version>`, `pubspec.yaml`);
   - the last tag: `git describe --tags --abbrev=0`;
   - the release workflow (`.github/workflows/release.yml`), if it exists.
2. **Collect what's in the release:**
   - `git log <last-tag>..origin/<default>`;
   - the merged work items (`work/*/` with `verify.md`, whose commits are in that range);
   - the backlog items that are now done.
3. **Propose the version.**
   - Semver: `major` for breaking data or file-format changes, or a dropped platform; `minor` for features; `patch` for fixes only. Before 1.0, use `minor` for anything user-facing.
   - Ask with AskUserQuestion: the computed version (Recommended), and the next alternative.
4. **Check readiness.** Each check gets ✅, ❌ or ⚠️, with its evidence:
   - **CI:** green on the default branch for every target OS (`gh run list --branch <default> --limit 5`).
   - **Release workflow:** it exists, and it builds, signs, notarizes (macOS) and creates a **draft** release for each target and architecture in the definition.
     - If it's missing, offer to add it to this PR, from the stack's notes in `.claude/skills/scaffold/stacks.md`.
   - **Signing secrets:** check that they exist **by name only**, with `gh secret list`. Never read, print or ask for their values. If any are missing, list the names and what each is for.
   - **Updates:** the updater configuration points at the right feed or release channel, and the update artifacts are signed, where the stack signs them.
   - **Data safety:** the migration tests from the last released schema pass. The release's fixture database is added for the next one (`test/fixtures/db-v<n>.sqlite`).
   - **Quality bars** from the definition that this release touches: accessibility, performance and privacy. Record them as checked or not checked; don't fail on a bar nothing changed.
   - **Identity, for a clone:** no target trademarks in the app name, the icons, the installer text or the store metadata.
5. **Write the release PR** on the branch `release/v<version>`:
   - the version bump in every version source;
   - a `CHANGELOG.md` entry in the user's language, from the intents' Outcomes and the bugs' Observed lines, grouped as Added, Changed and Fixed;
   - `releases/v<version>.md`: the readiness table, the included work items, and the **manual smoke checklist** (below).

   Commit, push, and open the PR with `gh pr create`, titled `Release v<version>`. Report it, and stop. **The user merges it.**

## Tag (after the user has merged the release PR)

1. **Confirm** that the release PR is merged, and that the default branch's version equals `<version>`.
2. **Ask** with AskUserQuestion, before anything outward-facing: "Push tag v<version> to start the release workflow (Recommended)" or "Not yet". The question says that the workflow will sign with the production certificates and create a draft release.
3. **Tag and run.** Create the tag with `git tag -a v<version> -m "v<version>"` on the merge commit, and push only that tag with `git push origin v<version>`. Then watch the run with `gh run watch`.
4. **Check the output.**
   - **The draft release:** `gh release view v<version>`. It has an asset for each target and architecture in the definition, plus the update artifacts.
   - **The signatures,** checked in CI. Add these steps to the workflow if they're missing, and read their output:
     - **Windows:** `Get-AuthenticodeSignature <file>` reports `Valid` on the installer and the main executable.
     - **macOS:** `codesign --verify --deep --strict` and `spctl -a -vv -t install` pass, and `xcrun stapler validate` passes on the DMG or app.
   - **The checksums:** SHA-256 for each asset, added to the release notes.
5. **Write the draft's notes** from the changelog entry, with `gh release edit v<version> --notes-file …`. Keep it a **draft**.
6. **Report:**
   - the draft release URL;
   - the per-OS signature results;
   - the manual smoke checklist the user must run before publishing.

## Manual smoke checklist (goes in `releases/v<version>.md`)
For each target OS, on a clean machine or VM where possible:
- [ ] Download and install from the draft release. There's no SmartScreen or Gatekeeper warning, beyond what's expected for the signing method.
- [ ] First launch: the onboarding and empty states, and the theme follows the OS.
- [ ] **Upgrade from the previous release** with real data in place: the data is intact, and settings and window state are kept.
- [ ] Auto-update from the previous release to this one, where updates are automatic.
- [ ] The file associations and URL scheme open the app, if there are any.
- [ ] Uninstall: the app is removed, and user data is kept or removed per the definition.
- [ ] Anything the verifier marked `NOT CHECKED` for this OS in the included work items.

## Asking the user
Use the **AskUserQuestion** tool for every question and every approval, not a question in prose.
- **Batching:** up to 4 questions per call, with 2–4 options each.
- **The default** is the first option, labelled "(Recommended)".
- **Wording:** labels are short (1–5 words) and the reasoning goes in each option's description. Headers are at most 12 characters.
- **Free text:** the tool always adds "Other" for a typed answer, so never add an "Other" option yourself.
- **An approval is a question too:** "Approve (Recommended)" or "Request changes". Apply whatever the user types under Other, then ask again.
- **Without AskUserQuestion** (a headless run, or another agent harness), ask in one numbered message instead, with the default after each question.

## Rules
- **Never publish** a release, submit to a store, or move a draft to published. The user does that after the smoke checklist.
- **Never push a tag without the user's explicit approval in this run.** Never move or delete an existing tag.
- **Never handle secret values.** Never weaken signing or notarization, or skip them, to get a green run.
- **Never merge** the release PR.
