# Desktop prototype conventions

The prototype simulates a desktop app in a browser. It has to show what the build must reproduce (layout, menus, shortcuts, states, platform differences) without pretending to be pixel-exact OS chrome.

## Structure
```html
<body data-platform="win" data-theme="light">
  <div class="desktop">                      <!-- a neutral backdrop standing in for the OS desktop -->
    <div class="mac-menubar">…</div>          <!-- macOS only: the global menu bar, rendered from menus -->
    <div class="window" data-window="main" style="--w:1200px; --h:800px">
      <div class="titlebar">…</div>           <!-- Windows: title, caption buttons on the right. macOS: traffic lights on the left -->
      <nav class="win-menubar">…</nav>         <!-- Windows only: the in-window menu bar, rendered from menus -->
      <section data-screen="tasks" data-window="main">…</section>
      <section data-screen="tasks-empty" data-window="main">…</section>
    </div>
    <div class="window dialog" data-window="settings">
      <section data-screen="settings-general" data-window="settings">…</section>
    </div>
  </div>
  <aside class="proto-toolbar">platform · theme · size · role · screen list</aside>
</body>
```
- **Routing:** `#<screen-id>` shows that screen and its window. Query parameters set the toolbar: `?platform=win|mac&theme=light|dark&size=default|min&role=<role>`. Every combination has a stable URL, so screenshots can be reproduced.
- **The toolbar** sits outside the simulated desktop, and it's hidden when the URL has `&shot=1`, for screenshots.

## Menus as data
```js
const menus = [
  { id: "file", label: "File", items: [
    { command: "file.new-task", label: "New Task", shortcut: { win: "Ctrl+N", mac: "⌘N" }, testid: "menu-file-new-task" },
    { separator: true },
    { command: "app.quit", label: { win: "Exit", mac: null }, shortcut: { win: "Alt+F4", mac: null } } // on macOS, Quit lives in the app menu
  ]},
];
```
- **One source** renders both the macOS global menu bar and the Windows in-window menu bar, and the shortcuts on the screens.
- **The macOS app menu** (About, Settings… ⌘,, Hide, Quit ⌘Q) is generated on macOS only. On Windows, Settings and Exit go wherever the definition says.
- **Wiring:** each command is wired to the mock behaviour where it matters, so clicking a menu item, or pressing its shortcut in the browser, does what the app will do.
- **Context menus** use the same item shape, in a `contextMenus` object keyed by the target element's testid.

## Platform chrome
- **Keep the chrome schematic:** recognisable, but simple. Caption buttons on Windows, traffic lights on macOS, the system font stack (`Segoe UI Variable`/`Segoe UI` on Windows, `-apple-system`/`SF Pro` on macOS), and native-feeling control sizes.
- **Platform differences** are written as `[data-platform="mac"] …` CSS rules, or as small branches in the render code. Only differences the definition or the intent asks for.

## Stubs for what the OS draws
Use a dashed box labelled with what the OS will show:
- the open and save file dialogs;
- OS notifications (in the screen corner);
- permission prompts;
- the Windows tray area and the macOS menu-bar extra;
- the about box, where the stack provides a native one.

These record intent ("Save dialog: default name `<plan>.json`, filter JSON"), not visuals.

## States
Each state that matters is its own screen id:
- empty, loading and error;
- long content and many items;
- the minimum window size;
- dark theme.

The minimum size is the definition's minimum window size. The layout must not break at it.

## Fixtures and testids
- **`fixtures`:** one object, shaped like the definition's core concepts, with realistic names and a few edge cases (long titles, empty lists, overdue dates).
- **Testids:** `data-testid` on every interactive element, named the way the app should name it, in kebab-case.
- **Commands:** `data-command` on anything that triggers a menu command.

## For a clone
- **Use our identity:** our app name in the title bar and about box, our icon placeholder, and our palette. A recognisable layout is fine; the target's colours, icons, illustrations and copy aren't.
- **Shortcuts:** where the teardown lists the target's shortcuts and the definition keeps them, use the same keys. That's interoperability, not copying.
