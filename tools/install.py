#!/usr/bin/env python3
"""Install the desktop SDLC kit into a project and configure it. Run it through install.sh.

  install.sh [project-dir] [--yes]

project-dir is asked for when omitted (default: the current directory). --yes accepts every default without asking
(also the behaviour when stdin isn't a terminal); --ask forces the questions even then.
Re-running it updates the kit's files and can reconfigure the CLAUDE.md block. It never
writes credentials: it only checks whether the environment has them.
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = ("skills", "agents", "hooks", "scripts")
START = "<!-- desktop-sdlc-kit:start"
END = "<!-- desktop-sdlc-kit:end -->"
WEB_KIT_START = "<!-- agentic-sdlc-kit:start"
HOOK_CMD = 'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/protect.py" || exit 2'
TBD = "TBD"
TARGET_CHOICES = [
    ("windows-x64, macos-universal", "Windows and macOS"),
    ("windows-x64", "Windows only"),
    ("macos-universal", "macOS only"),
    ("windows-x64, macos-universal, linux-x64", "Windows, macOS and Linux"),
]


# ---------------------------------------------------------------- terminal UI

class UI:
    def __init__(self, interactive):
        self.interactive = interactive
        tty = sys.stdout.isatty()
        self.b = (lambda s: f"\033[1m{s}\033[0m") if tty else (lambda s: s)
        self.dim = (lambda s: f"\033[2m{s}\033[0m") if tty else (lambda s: s)

    def section(self, title):
        print("\n" + self.b(title))

    def note(self, text):
        print("  " + self.dim(text))

    def ask(self, question, default=""):
        shown = f" [{default}]" if default else ""
        if not self.interactive:
            print(f"  {question}{shown}: {default or '-'}")
            return default
        try:
            answer = input(f"  {question}{shown}: ").strip()
        except EOFError:
            answer = ""
        return answer or default

    def yes(self, question, default=True):
        hint = "Y/n" if default else "y/N"
        while True:
            answer = self.ask(f"{question} ({hint})", "").lower()
            if not answer:
                return default
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no"):
                return False
            print("  Please answer y or n.")

    def choose(self, question, options, default):
        """options: list of (value, label). Returns a value."""
        print(f"  {question}")
        for i, (value, label) in enumerate(options, 1):
            mark = "*" if value == default else " "
            print(f"   {mark}{i}) {label}")
        values = [v for v, _ in options]
        while True:
            answer = self.ask("Choose", str(values.index(default) + 1))
            if answer.isdigit() and 1 <= int(answer) <= len(options):
                return values[int(answer) - 1]
            if answer in values:
                return answer
            print(f"  Enter a number from 1 to {len(options)}.")


# ---------------------------------------------------------------- detection

def run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def is_wsl():
    try:
        with open("/proc/version", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


def dev_os():
    """-> (label, the local target OS names that can run the desktop app here)."""
    system = platform.system()
    if system == "Windows":
        return "windows", ["windows"]
    if system == "Darwin":
        return "macos", ["macos"]
    if is_wsl():
        win = ["windows (via scripts/win-run.sh)"] if shutil.which("powershell.exe") else []
        return "windows (WSL2)", win + ["linux (WSLg)"]
    return "linux", ["linux"]


def platform_matrix(targets, local):
    """-> (local targets, CI-only targets) as display strings, for the chosen targets."""
    wanted = {t.split("-")[0] for t in (s.strip() for s in targets.split(",")) if t}
    here = [l for l in local if l.split(" ")[0] in wanted]
    ci = sorted(w for w in wanted if not any(l.split(" ")[0] == w for l in here))
    return (", ".join(here) or "none (CI only)"), (", ".join(ci) or "none")


def package_scripts(target):
    pkg = os.path.join(target, "package.json")
    if not os.path.isfile(pkg):
        return None, {}, {}
    try:
        data = json.load(open(pkg, encoding="utf-8"))
    except ValueError:
        return None, {}, {}
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    pm = next((m for f, m in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun"), ("bun.lock", "bun"))
               if os.path.exists(os.path.join(target, f))), "npm")
    return pm, data.get("scripts", {}), deps


def detect(target):
    """-> dict stack/test/build/lint/start/e2e/screenshot/package with '' where nothing was found."""
    found = dict.fromkeys(("stack", "test", "build", "lint", "start", "e2e", "screenshot", "package"), "")
    pm, scripts, deps = package_scripts(target)
    runner = (lambda s: f"{pm} test" if s == "test" else f"{pm} run {s}") if pm else None
    if pm:
        if "test" in scripts and "no test specified" not in scripts["test"]:
            found["test"] = runner("test")
        for key, names in (("build", ("build",)), ("lint", ("lint",)), ("start", ("start", "dev")),
                           ("e2e", ("e2e", "test:e2e")), ("screenshot", ("screenshot", "screens")),
                           ("package", ("package", "make", "dist"))):
            found[key] = next((runner(n) for n in names if n in scripts), "")
    if os.path.isdir(os.path.join(target, "src-tauri")) or "@tauri-apps/cli" in deps:
        found["stack"] = "Tauri 2"
        if pm:
            found["start"] = found["start"] or f"{pm} run tauri dev"
            found["package"] = found["package"] or f"{pm} run tauri build"
        found["test"] = found["test"] or "cargo test --manifest-path src-tauri/Cargo.toml"
        found["lint"] = found["lint"] or "cargo clippy --manifest-path src-tauri/Cargo.toml"
    elif "electron" in deps:
        found["stack"] = "Electron"
    sln = [f for f in os.listdir(target) if f.endswith((".sln", ".slnx", ".csproj"))] if os.path.isdir(target) else []
    if sln and not found["stack"]:
        text = ""
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in ("bin", "obj", "node_modules", ".git")]
            for f in files:
                if f.endswith(".csproj"):
                    text += open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
        found["stack"] = ("Avalonia UI" if "Avalonia" in text else "WinUI 3" if "WindowsAppSDK" in text
                          else "WPF" if "UseWPF" in text else ".NET")
        found.update({k: found[k] or v for k, v in (("test", "dotnet test"), ("build", "dotnet build"),
                                                     ("lint", "dotnet format --verify-no-changes"))})
    if os.path.isfile(os.path.join(target, "pubspec.yaml")) and not found["stack"]:
        found["stack"] = "Flutter"
        found.update({k: found[k] or v for k, v in (("test", "flutter test"), ("lint", "flutter analyze"),
                                                     ("e2e", "flutter test integration_test"))})
    if os.path.isfile(os.path.join(target, "Cargo.toml")) and not found["stack"]:
        found.update({k: found[k] or v for k, v in (("test", "cargo test"), ("build", "cargo build"), ("lint", "cargo clippy"))})
    return found


def detect_prototype(target):
    for rel in ("prototype/index.html", "prototype.html"):
        if os.path.isfile(os.path.join(target, rel)):
            return rel
    proto_dir = os.path.join(target, "prototype")
    if os.path.isdir(proto_dir):
        htmls = sorted(f for f in os.listdir(proto_dir) if f.endswith(".html"))
        if htmls:
            return "prototype/" + htmls[0]
    return ""


def github_remote(target):
    code, url = run(["git", "remote", "get-url", "origin"], cwd=target)
    return code == 0 and "github.com" in url


def linear_teams():
    sys.path.insert(0, os.path.join(KIT, ".claude", "scripts"))
    try:
        import issue  # the kit's own client
        return [t["key"] for t in issue.linear_gql("{ teams(first:50){ nodes{ key } } }")["teams"]["nodes"]]
    except (SystemExit, Exception):
        return []


# ---------------------------------------------------------------- steps

def copy_kit(target, ui):
    dest = os.path.join(target, ".claude")
    existing = [p for p in PARTS if os.path.isdir(os.path.join(dest, p))]
    if existing:
        ui.note("Kit files are already installed here; they can be updated to this version.")
        ui.note("Any edits you made to the kit's own skills, agent, hook or script are overwritten.")
        if not ui.yes("Update the kit's files", True):
            return "kept"
    for part in PARTS:
        src = os.path.join(KIT, ".claude", part)
        for root, dirs, files in os.walk(src):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            rel = os.path.relpath(root, src)
            out = os.path.join(dest, part, rel)
            os.makedirs(out, exist_ok=True)
            for f in files:
                if not f.endswith(".pyc"):
                    shutil.copy2(os.path.join(root, f), os.path.join(out, f))
    return "updated" if existing else "installed"


def merge_settings(target):
    path = os.path.join(target, ".claude", "settings.json")
    entry = {"matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash", "hooks": [{"type": "command", "command": HOOK_CMD}]}
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"hooks": {"PreToolUse": [entry]}}, f, indent=2)
            f.write("\n")
        return "created"
    try:
        settings = json.load(open(path, encoding="utf-8"))
    except ValueError:
        return "invalid"
    pre = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
    if any(h.get("command") == HOOK_CMD for e in pre for h in e.get("hooks", [])):
        return "unchanged"
    shutil.copy2(path, path + ".bak")
    pre.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    return "merged"


def render_block(cfg):
    with open(os.path.join(KIT, "templates", "CLAUDE.md.snippet"), encoding="utf-8") as f:
        text = f.read()
    values = {
        "APP_NAME": cfg["app"] or "TBD (set by /define)", "STACK": cfg["stack"] or "TBD (chosen by /define)",
        "TARGETS": cfg["targets"], "DEV_OS": cfg["dev_os"], "LOCAL_TARGETS": cfg["local"], "CI_TARGETS": cfg["ci"],
        "TEST_CMD": cfg["test"] or TBD, "BUILD_CMD": cfg["build"] or TBD, "LINT_CMD": cfg["lint"] or TBD,
        "START_CMD": cfg["start"] or TBD, "E2E_CMD": cfg["e2e"] or TBD, "SCREENSHOT_CMD": cfg["screenshot"] or TBD,
        "PACKAGE_CMD": cfg["package"] or TBD, "PROTOTYPE": cfg["prototype"],
        "TRACKER": cfg["tracker"], "STATUS_UPDATES": cfg["status"], "TRIAGE": cfg["triage"],
    }
    text = re.sub(r"\{\{(\w+)\}\}", lambda m: values.get(m.group(1), m.group(0)), text)  # function replacer: values are data
    start, end = text.index(START), text.index(END) + len(END)
    return text[start:end], text[end:].strip()


def write_claude_md(target, cfg):
    path = os.path.join(target, "CLAUDE.md")
    block, tail = render_block(cfg)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(block + "\n\n" + tail + "\n")
        return "created"
    current = open(path, encoding="utf-8").read()
    if START in current and END in current:
        shutil.copy2(path, path + ".bak")
        new = current[:current.index(START)] + block + current[current.index(END) + len(END):]
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        return "updated (previous version in CLAUDE.md.bak)"
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\n" + block + ("\n\n" + tail if "## Things Claude gets wrong" not in current else "") + "\n")
    return "appended the kit's section"


# ---------------------------------------------------------------- main

def configure(target, ui):
    cfg = {}
    found = detect(target)

    ui.section("App")
    ui.note("/define sets the name and the stack; leave them as TBD for a new app.")
    cfg["app"] = ui.ask("App name", TBD)
    cfg["stack"] = ui.ask("Stack", found["stack"] or TBD)

    ui.section("Platforms")
    cfg["targets"] = ui.choose("Which platforms will the app ship on?", TARGET_CHOICES, TARGET_CHOICES[0][0])
    cfg["dev_os"], local = dev_os()
    cfg["local"], cfg["ci"] = platform_matrix(cfg["targets"], local)
    ui.note(f"This machine: {cfg['dev_os']}. Run locally on: {cfg['local']}. Verified only in CI on: {cfg['ci']}.")
    if cfg["dev_os"].startswith("windows (WSL") and "windows" not in cfg["local"]:
        ui.note("powershell.exe isn't reachable from WSL, so Windows runs fall back to CI. /scaffold explains the options.")

    ui.section("Commands")
    ui.note("One command each; leave TBD for a new app (/scaffold fills them in).")
    for key, label in (("test", "Test"), ("lint", "Lint"), ("build", "Build"), ("start", "Start the app (dev)"),
                       ("e2e", "E2E (real app)"), ("screenshot", "Screenshot"), ("package", "Package (unsigned)")):
        cfg[key] = ui.ask(label, found[key] or TBD)
    cfg = {k: ("" if v == TBD else v) for k, v in cfg.items()}

    ui.section("Prototype")
    proto = detect_prototype(target)
    if proto:
        ui.note(f"Found {proto}; /prototype will modify it.")
    else:
        ui.note("No prototype yet; /prototype app creates one at this path.")
    path = ui.ask("Prototype path", proto or "prototype/index.html")
    cfg["prototype"] = path if os.path.isfile(os.path.join(target, path)) else f"{path} (created by /prototype app)"

    ui.section("Issues")
    ui.note("For a new app, choose None: /roadmap writes product/backlog.md and points the tracker at it.")
    new_app = not [f for f in os.listdir(target) if f not in (".git", ".claude", "CLAUDE.md", "REVIEW.md")]
    env_default = ("none" if new_app else "linear" if os.environ.get("LINEAR_API_KEY")
                   else "jira" if os.environ.get("JIRA_BASE_URL") else "github" if github_remote(target) else "none")
    tracker = ui.choose("Where do issues come from?", [
        ("none", "None yet (the backlog file /roadmap writes)"), ("linear", "Linear"), ("jira", "Jira"),
        ("github", "GitHub issues"), ("file", "A local file (JSON, Markdown, CSV, SQLite)")], env_default)
    triage, status = "none", "off"
    if tracker == "linear":
        if not os.environ.get("LINEAR_API_KEY"):
            ui.note("LINEAR_API_KEY isn't set in this shell. Export it before using Linear issues.")
        teams = linear_teams()
        team = ui.ask("Linear team key" + (f" ({', '.join(teams)})" if teams else ""), teams[0] if len(teams) == 1 else "")
        triage = f"linear --team {team.upper() or '<KEY>'} --state Triage"
    elif tracker == "jira":
        missing = [v for v in ("JIRA_BASE_URL",) if not os.environ.get(v)]
        if not (os.environ.get("JIRA_PAT") or (os.environ.get("JIRA_EMAIL") and os.environ.get("JIRA_API_TOKEN"))):
            missing.append("JIRA_EMAIL + JIRA_API_TOKEN (or JIRA_PAT)")
        if missing:
            ui.note("Not set in this shell: " + ", ".join(missing) + ". Export them before using Jira issues.")
        project = ui.ask("Jira project key", "")
        triage = f"jira --project {project.upper() or '<KEY>'} --label triage"
    elif tracker == "github":
        if run(["gh", "auth", "status"])[0] != 0:
            ui.note("The gh CLI isn't signed in. Run: gh auth login")
        triage = "github --label " + ui.ask("Label that marks issues for /triage", "triage")
    elif tracker == "file":
        f = ui.ask("Issues file, relative to the project", "product/backlog.md")
        if not os.path.isfile(os.path.join(target, f)):
            ui.note(f"{f} doesn't exist yet; /roadmap creates product/backlog.md, or create the file yourself.")
        tracker = f"file:{f}"
        triage = f"file:{f}"
    if tracker != "none" and not tracker.startswith("file:"):
        status = "on" if ui.yes("Let the skills change issue status (In Progress, In Review)", False) else "off"
    cfg.update(tracker=tracker, triage=triage, status=status)
    return cfg


def main():
    ap = argparse.ArgumentParser(description="Install the desktop SDLC kit into a project.")
    ap.add_argument("project", nargs="?", help="the project's folder (asked for when omitted)")
    ap.add_argument("-y", "--yes", action="store_true", help="accept every default without asking")
    ap.add_argument("--ask", action="store_true", help="ask even when stdin isn't a terminal (scripted answers)")
    args = ap.parse_args()
    ui = UI(interactive=(args.ask or sys.stdin.isatty()) and not args.yes)
    print(ui.b("Desktop SDLC kit"))

    ui.section("Project")
    project = args.project or ui.ask("Project directory", os.getcwd())
    target = os.path.abspath(os.path.expanduser(project))
    if os.path.realpath(target) == os.path.realpath(KIT):
        sys.exit("That's the kit itself. Choose the project's folder.")
    if os.path.exists(target) and not os.path.isdir(target):
        sys.exit(f"{target} is a file, not a folder.")
    if not os.path.isdir(target):
        if not ui.yes(f"{target} doesn't exist. Create it", True):
            sys.exit("Nothing installed.")
        os.makedirs(target)
        print(f"  created {target}")
    claude_md = os.path.join(target, "CLAUDE.md")
    claude_text = open(claude_md, encoding="utf-8").read() if os.path.exists(claude_md) else ""
    if WEB_KIT_START in claude_text:
        ui.note("This project has the web agentic SDLC kit installed. Both kits use the same skill names")
        ui.note("(/intent, /build, …), so installing this one replaces those skills with the desktop versions.")
        if not ui.yes("Replace them with the desktop kit", False):
            sys.exit("Nothing installed.")
    if shutil.which("git") is None:
        sys.exit("git is required: the skills work in branches and commits.")
    code, top = run(["git", "rev-parse", "--show-toplevel"], cwd=target)
    if code == 0 and os.path.realpath(top) == os.path.realpath(target):
        ui.note("Already a git repository.")
    elif code == 0 and not ui.yes(f"This folder is inside the git repository at {top}. Create a separate one here", False):
        ui.note(f"Using the repository at {top}.")
    elif code == 0 or ui.yes("Create a git repository here (git init)", True):
        run(["git", "init", "-q", "-b", "main"], cwd=target)
        print("  created a git repository (branch main)")
    else:
        ui.note("Skipped. The skills need one before /define commits anything.")

    ui.section("Checks")
    checks = [("gh", "/ship, /release and /triage"), ("npx", "prototype screenshots via npx playwright (or the Playwright MCP)"),
              ("node", "Electron or Tauri front ends"), ("cargo", "Tauri"), ("dotnet", "Avalonia, WinUI, WPF"),
              ("flutter", "Flutter")]
    if is_wsl():
        checks.append(("powershell.exe", "running Windows builds from WSL (scripts/win-run.sh)"))
    for tool, why in checks:
        print(f"  {'ok     ' if shutil.which(tool) else 'missing'} {tool}: {why}")
    ui.note("Only the toolchain for your stack is needed; /scaffold checks it again.")

    has_block = START in claude_text
    reconfigure = True
    if has_block:
        ui.section("CLAUDE.md")
        ui.note("This project already has the kit's CLAUDE.md section. Reconfiguring replaces it (a backup is kept).")
        reconfigure = ui.yes("Reconfigure it", False)
    cfg = configure(target, ui) if reconfigure else None

    workflow = False
    if cfg and cfg["tracker"] != "none":
        ui.section("Triage")
        workflow = ui.yes("Add the nightly /triage GitHub workflow", False)

    ui.section("Installing")
    os.makedirs(os.path.join(target, ".claude"), exist_ok=True)
    print(f"  kit files: {copy_kit(target, ui)}")
    print(f"  .claude/settings.json: {merge_settings(target)}")
    if cfg:
        print(f"  CLAUDE.md: {write_claude_md(target, cfg)}")
    review = os.path.join(target, "REVIEW.md")
    if os.path.exists(review):
        print("  REVIEW.md: kept the existing one")
    else:
        shutil.copy2(os.path.join(KIT, "templates", "REVIEW.md"), review)
        print("  REVIEW.md: created")
    if workflow:
        wf = os.path.join(target, ".github", "workflows", "triage.yml")
        if os.path.exists(wf):
            print("  .github/workflows/triage.yml: kept the existing one")
        else:
            os.makedirs(os.path.dirname(wf), exist_ok=True)
            shutil.copy2(os.path.join(KIT, "templates", "triage.yml"), wf)
            print("  .github/workflows/triage.yml: created (add the CLAUDE_CODE_OAUTH_TOKEN secret and your tracker's)")

    ui.section("Next")
    print("  1. Start a new Claude Code session in the project (skills load at session start).")
    print("  2. Type one of:")
    print("       /define <your app idea>")
    print("       /clone <an existing app>")
    print("       /clone <an existing app>, but <what you'd change>")
    if not github_remote(target):
        print("  3. Before /scaffold runs CI: add a GitHub remote (gh repo create).")
    print("  Guide: " + os.path.join(KIT, "GUIDE.md"))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelled; nothing after the last step shown was changed.")
