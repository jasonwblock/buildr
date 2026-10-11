# /define question bank

Each round is one AskUserQuestion call with at most 4 questions. Use only the questions still open, and reword them for the app at hand. The first option is the seeded default, labelled "(Recommended)". The options below are typical; replace them with ones that fit this app, keeping 2–4 per question. The tool always adds Other.

For a clone, the teardown usually answers rounds 1 and 2. Ask only about the places where the user's modifications or audience differ from the target's.

## Round 1: Purpose
| Header | Question | Typical options (default first) |
|---|---|---|
| Users | Who is this for, first? | The seeded persona · Individuals · Small teams · A specific profession |
| Problem | Which problem matters most at launch? | 2–3 seeded problem statements |
| Why desktop | Why a desktop app rather than a web app? | Works offline · Fast, native feel · Deep OS integration (files, tray, shortcuts) · Data stays on the machine |
| Success | What tells you it's working? | Daily use by the first user · Replaces <tool> for <job> · N paying users |

## Round 2: Shape
| Header | Question | Typical options |
|---|---|---|
| Archetype | What kind of desktop app is it? | Workspace/library (one window over a collection: Planner, Notion, Mail) · Document-based (open and save files: Word, Figma) · Utility/tray (lives in the tray or menu bar) · Editor/tool (one focused canvas) |
| Layout | The main window's layout? | Sidebar + content (+ inspector) · Tabs · Single canvas · Master-detail list |
| MVP | Which features are in the first release? *(multiSelect)* | The seeded `D-n`s, the 4 most important first; the rest move to Later unless the user types them under Other |
| Windows | One window or several? | One main window, with dialogs · Several of the same kind (one per document or project) · A main window plus tool windows |

## Round 3: Data
| Header | Question | Typical options |
|---|---|---|
| Storage | Where does the user's data live? | Local database (SQLite) in the app's data folder · Files the user picks and owns · Cloud account, with a local cache |
| Sync | Do accounts or sync exist at launch? | None: local only · Optional sync later (keep the data model ready) · Required account |
| Sharing | Can several people work on the same data? | No, single user · Share by exporting files · Real-time collaboration (needs a backend) |
| Safety | How is data protected from mistakes? | Autosave, undo and a trash · Autosave plus automatic backups · Explicit save (document apps) |

**The fast-path question,** added to this call: "Accept recommended defaults for the rest (Recommended)" or "Go through every round".

## Round 4: Desktop integration
| Header | Question | Typical options |
|---|---|---|
| Presence | Where does the app live while it runs? | Taskbar/Dock only, and it quits when closed (Windows) or stays in the Dock (macOS) · Plus a tray/menu-bar icon · Tray/menu bar only |
| Notify | Does it send OS notifications? | Yes, for reminders and due dates · No |
| Files | Does it open its own files or links? | No · Its own file type (double-click to open) · A URL scheme for deep links · Both |
| Extras | Which OS features matter at launch? *(multiSelect)* | Drag and drop · Launch at login · Global shortcut · Printing |

## Round 5: Platforms and distribution
| Header | Question | Typical options |
|---|---|---|
| Platforms | Which platforms at launch? | Windows and macOS · Windows first, macOS later · Windows, macOS and Linux |
| Versions | Minimum OS versions? | Windows 10 22H2+ and 11; macOS 13+ (Apple Silicon and Intel, universal) · Windows 11 only; macOS 14+ Apple Silicon only |
| Channel | How do users get it and its updates? | Direct download with automatic updates · Microsoft Store and Mac App Store · winget and Homebrew, with updates by package manager |
| Signing | Code signing at launch? | Sign both (Apple Developer Program, about $99 a year; a Windows signing service or certificate) · Unsigned beta first (SmartScreen and Gatekeeper warnings) |

Put the cost and the warnings in the option descriptions. Unsigned macOS apps are hard for users to open, so recommend signing for any release beyond friends and family.

## Round 6: Stack
Use the decision table in `.claude/skills/scaffold/stacks.md`. Ask one question: "Which stack?" Offer:
- the stack the table recommends for these answers, first;
- two real alternatives.

Each option's description gives the trade-off in one line: binary size, how verifiable the UI is on each OS, the team's language, and how native it feels. If the repo already has a stack, confirm it rather than asking.

## Round 7: Quality bars
| Header | Question | Typical options |
|---|---|---|
| Access | Accessibility target? | Full keyboard use plus screen-reader labels (Narrator, NVDA, VoiceOver) · Keyboard only for now |
| Languages | Languages at launch? | English, with strings externalized · English only, hard-coded · Several: list them |
| Speed | Performance budget? | Cold start < 2 s, idle memory < 300 MB, smooth with 10k items · Not a concern yet |
| Telemetry | Crash reports and usage data? | Opt-in crash reports only · None · Opt-out usage analytics |

## Seeding defaults
Use these when nothing in the input says otherwise:
- **Data and platforms:** local-first SQLite storage, no account, Windows and macOS, direct download with automatic updates, and signed builds.
- **The app's shape:** light and dark themes that follow the OS, full keyboard use, English with strings externalized, and opt-in crash reports.
- **Closing the window:** on Windows, closing the last window quits the app unless it has a tray icon. On macOS, the app stays in the Dock until the user quits it with Cmd+Q.
