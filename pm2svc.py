# -*- coding: utf-8 -*-
"""PM2 interaction layer for pm2-app.

Everything PM2 related goes through this module so the UI never touches the
terminal directly. All commands are executed with the *user's* environment
(HOME, PATH) so the app works with the same daemon the user runs in a shell.
"""

import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import time

APP_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"
CONFIG_DIR = os.path.join(HOME, ".config", "PM2-App")
ECOSYSTEM_DIR = os.path.join(CONFIG_DIR, "ecosystems")

SUPPORTED_EXT = {".js", ".mjs", ".cjs", ".py", ".sh"}
_NODE_CANDIDATES = ("index.js", "main.js", "app.js", "bot.js", "index.mjs", "main.mjs")
_PY_CANDIDATES = ("main.py", "bot.py", "app.py", "run.py", "index.py")
_JS_SINGLE = ("index.js", "main.js", "bot.js", "app.js")
_PY_SINGLE = ("main.py", "bot.py", "app.py", "run.py")


class PM2Error(Exception):
    def __init__(self, message, output=""):
        super().__init__(message)
        self.output = output


def _safe_name(name):
    """Filesystem-safe slug used only for config/log file names (PM2 name keeps original)."""
    cleaned = re.sub(r"[^A-Za-z0-9._\-]+", "-", name).strip("-._")
    return (cleaned or "app")[:40]


def ensure_dirs():
    os.makedirs(ECOSYSTEM_DIR, exist_ok=True)


def run_cmd(cmd, cwd=None, timeout=40):
    """Run a command with the user's own env. Returns trimmed stdout."""
    env = os.environ.copy()
    env.setdefault("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise PM2Error(f"Command not found: {cmd[0]}", str(exc))
    except subprocess.TimeoutExpired:
        raise PM2Error("Command timed out", " ".join(cmd))
    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    if proc.returncode != 0:
        raise PM2Error(out.strip() or f"Command failed: {' '.join(cmd)}", out)
    return out.strip()


# --------------------------------------------------------------------------
# Detection / availability
# --------------------------------------------------------------------------
def _extra_candidates(*names):
    """Extra well-known install locations for an executable across OSes."""
    out = []
    if IS_WINDOWS:
        base_dirs = [
            os.environ.get("APPDATA", ""),
            os.environ.get("LOCALAPPDATA", ""),
            os.path.join(HOME, "AppData", "Roaming"),
            os.path.join(HOME, "AppData", "Local"),
            os.path.join(HOME, "scoop", "apps"),
        ]
        for base in base_dirs:
            for name in names:
                out.append(os.path.join(base, "npm", name))
                out.append(os.path.join(base, "nodejs", name))
    else:
        for n in names:
            out.append(os.path.join(HOME, ".npm-global", "bin", n))
            out.append(os.path.join(HOME, ".local", "bin", n))
            out.append("/usr/local/bin/" + n)
            out.append("/usr/bin/" + n)
            out.append("/opt/homebrew/bin/" + n)
            out.append("/usr/local/sbin/" + n)
    return out


def _which_or_candidates(name, extra):
    found = shutil.which(name)
    if found:
        return found
    for candidate in extra:
        if os.path.isfile(candidate):
            return candidate
    return None


def pm2_path():
    return _which_or_candidates("pm2", _extra_candidates("pm2", "pm2.cmd", "pm2.exe"))


def node_path():
    return _which_or_candidates("node", _extra_candidates("node", "node.exe"))


def npm_path():
    return _which_or_candidates("npm", _extra_candidates("npm", "npm.cmd", "npm.exe"))


def python_interpreter():
    """Name of the Python executable PM2 should use for .py scripts."""
    return "python" if IS_WINDOWS else "python3"


def _run_streaming(cmd, cwd, progress=None):
    """Run a command, forwarding each output line to `progress`. Returns (rc, tail)."""
    env = os.environ.copy()
    env.setdefault("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
    tail = []
    try:
        proc = subprocess.Popen(
            cmd, cwd=cwd, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
    except (OSError, ValueError) as exc:
        raise PM2Error("Could not run: " + " ".join(cmd), str(exc))
    assert proc.stdout is not None
    for raw in proc.stdout:
        line = raw.rstrip("\n")
        tail.append(line)
        if len(tail) > 200:
            tail.pop(0)
        if progress:
            try:
                progress(line)
            except Exception:
                pass
    proc.wait()
    return proc.returncode, "\n".join(tail)


def install_pm2_auto(progress=None, prefix_dir=None):
    """Install PM2 automatically (best effort).

    Returns (ok: bool, detail: str). Tries `npm -g` first; if that is not
    allowed (no admin rights) it falls back to a user-local prefix at
    ~/.npm-global (or `prefix_dir` for testing).
    """
    if prefix_dir is None and pm2_path():
        return True, "pm2 already installed"
    npm = npm_path()
    if not npm:
        raise PM2Error("node_missing", "Node.js / npm not found")

    attempts = []

    def attempt(cmd):
        rc, tail = _run_streaming(cmd, HOME, progress=progress)
        attempts.append(tail)
        return rc == 0

    if prefix_dir is None:
        # 1) try a normal global install (works when the user may write the dir)
        if attempt([npm, "install", "-g", "pm2"]):
            if pm2_path():
                return True, attempts[-1]
        # 2) fall back to a user-local prefix (no sudo needed)
        prefix_dir = os.path.join(HOME, ".npm-global")

    os.makedirs(prefix_dir, exist_ok=True)
    attempt([npm, "install", "-g", "--prefix", prefix_dir, "pm2"])

    if pm2_path():
        return True, attempts[-1] if attempts else ""
    detail = "\n\n".join(attempts[-2:])
    return False, detail


def is_pm2_ready():
    path = pm2_path()
    if not path:
        return False
    try:
        run_cmd([path, "-v"], timeout=15)
        return True
    except PM2Error:
        return False


# --------------------------------------------------------------------------
# Process listing
# --------------------------------------------------------------------------
def list_apps():
    """Return parsed `pm2 jlist` entries enriched for the UI."""
    path = pm2_path()
    if not path:
        return []
    try:
        raw = run_cmd([path, "jlist"], timeout=30)
    except PM2Error:
        return []
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return []
    apps = []
    now = time.time() * 1000
    for item in data or []:
        env = item.get("pm2_env") or {}
        monit = item.get("monit") or {}
        status = env.get("status", "unknown")
        uptime_ms = env.get("pm_uptime")
        uptime_sec = None
        if isinstance(uptime_ms, (int, float)) and uptime_ms and status == "online":
            uptime_sec = max(0, (now - uptime_ms) / 1000.0)
        apps.append({
            "id": item.get("pm_id"),
            "name": env.get("name") or item.get("name") or "?",
            "status": status,
            "pid": item.get("pid"),
            "cpu": monit.get("cpu"),
            "memory": monit.get("memory"),
            "restarts": env.get("restart_time") or 0,
            "unstable": env.get("unstable_restarts") or 0,
            "uptime_sec": uptime_sec,
            "cwd": env.get("pm_cwd") or "",
            "script": env.get("pm_exec_path") or "",
            "interpreter": env.get("exec_interpreter") or "",
            "out_log": env.get("pm_out_log_path") or "",
            "err_log": env.get("pm_err_log_path") or "",
            "created": env.get("pm_created_at") or 0,
        })
    return apps


def name_taken(name, exclude_id=None):
    for app in list_apps():
        if app["name"] == name and app["id"] != exclude_id:
            return True
    return False


def unique_name(base):
    name = base
    counter = 2
    while name_taken(name):
        name = f"{base}-{counter}"
        counter += 1
    return name


# --------------------------------------------------------------------------
# Ecosystem config generation
# --------------------------------------------------------------------------
def _entry_for_folder(folder):
    """Decide how to run a dropped folder. Returns (script_path, kind) or raises."""
    pkg_json = os.path.join(folder, "package.json")
    if os.path.isfile(pkg_json):
        try:
            with open(pkg_json, "r", encoding="utf-8") as fh:
                pkg = json.load(fh)
        except (ValueError, OSError):
            pkg = {}
        main = pkg.get("main")
        if isinstance(main, str) and main:
            candidate = os.path.join(folder, main)
            if os.path.isfile(candidate):
                return candidate, "node"
        # No usable "main": look for a classic entry file.
        for name in _NODE_CANDIDATES:
            candidate = os.path.join(folder, name)
            if os.path.isfile(candidate):
                return candidate, "node"
        return None, "node"  # package.json exists but no entry found
    for name in _NODE_CANDIDATES:
        candidate = os.path.join(folder, name)
        if os.path.isfile(candidate):
            return candidate, "node"
    for name in _PY_CANDIDATES:
        candidate = os.path.join(folder, name)
        if os.path.isfile(candidate):
            return candidate, "python"
    return None, None


def prepare_entry(path):
    """Turn a dropped file/folder into (script, kind, cwd, label_key).

    kind: 'node' | 'python' | 'bash' | 'unsupported'
    Raises PM2Error with a user-friendly message when nothing usable is found.
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise PM2Error("not_found", path)
    if os.path.isdir(path):
        script, kind = _entry_for_folder(path)
        if not script:
            if os.path.isfile(os.path.join(path, "package.json")):
                raise PM2Error("no_entry", path)
            raise PM2Error("no_entry", path)
        label = "nodeProject" if kind == "node" and os.path.isfile(os.path.join(path, "package.json")) else (
            "python" if kind == "python" else "other")
        return script, kind, path, label
    # Plain file
    ext = os.path.splitext(path)[1].lower()
    folder = os.path.dirname(path)
    base = os.path.basename(path)
    if ext in (".js", ".mjs", ".cjs"):
        return path, "node", folder, "nodeFile"
    if ext == ".py":
        return path, "python", folder, "python"
    if ext == ".sh":
        return path, "bash", folder, "bash"
    if ext == ".jsx" or ext == ".ts":
        raise PM2Error("unsupported", base)
    raise PM2Error("unsupported", base)


def _ecosystem_content(name, script, cwd, kind):
    payload = {
        "name": name,
        "script": script,
        "cwd": cwd,
        "autorestart": True,
        "merge_logs": True,
        "time": True,
        "kill_timeout": 3000,
        "max_memory_restart": "2G",
        "env": {"NODE_ENV": "production"},
    }
    if kind == "python":
        payload["interpreter"] = python_interpreter()
    elif kind == "bash":
        payload["interpreter"] = "bash"
    # "time": True adds timestamps to the log lines — very useful for beginners.
    # Logs go to the user's own ~/.pm2/logs directory (default location).
    return "module.exports = " + json.dumps({"apps": [payload]}, indent=2, ensure_ascii=False) + ";\n"


def start_app(script, cwd, kind, base_name):
    """Start an app through a generated ecosystem config. Returns chosen name."""
    path = pm2_path()
    if not path:
        raise PM2Error("pm2_missing", "")
    ensure_dirs()
    name = unique_name(base_name)
    filename = f"{_safe_name(name)}-{int(time.time())}.config.cjs"
    eco_path = os.path.join(ECOSYSTEM_DIR, filename)
    with open(eco_path, "w", encoding="utf-8") as fh:
        fh.write(_ecosystem_content(name, script, cwd, kind))
    try:
        run_cmd([path, "start", eco_path], cwd=cwd, timeout=60)
        # Keep the boot dump in sync so "auto-start" always reflects the list.
        try:
            run_cmd([path, "save"], timeout=30)
        except PM2Error:
            pass
    finally:
        try:
            os.remove(eco_path)
        except OSError:
            pass
    return name


def stop_app(name):
    run_cmd([pm2_path(), "stop", name], timeout=40)


def restart_app(name):
    run_cmd([pm2_path(), "restart", name], timeout=40)


def delete_app(name):
    run_cmd([pm2_path(), "delete", name], timeout=40)
    try:
        run_cmd([pm2_path(), "save"], timeout=30)
    except PM2Error:
        pass


def describe_app(name):
    """pm2 describe — returns raw output text."""
    return run_cmd([pm2_path(), "describe", name], timeout=30)


# --------------------------------------------------------------------------
# Logs
# --------------------------------------------------------------------------
def read_tail(path, max_bytes=32768, max_lines=400):
    """Read the last lines of a log file quickly."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        if size > max_bytes:
            fh.seek(size - max_bytes)
            fh.readline()  # drop a possibly cut line
        data = fh.read()
    lines = data.splitlines()
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Auto-start on boot
# --------------------------------------------------------------------------
def username():
    return getpass.getuser()


def boot_enabled():
    """True when PM2 is registered to start on boot for this user.

    Linux: checks the pm2 systemd unit. Windows/macOS: PM2 keeps no registry
    entry we can read without extra tooling, so we report the last known state
    the user confirmed in the app instead.
    """
    if pm2_path() is None or IS_WINDOWS or IS_MAC:
        return False
    try:
        proc = subprocess.run(
            ["systemctl", "is-enabled", f"pm2-{username()}"],
            capture_output=True, text=True, timeout=15,
        )
        return "enabled" in (proc.stdout or "").lower()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _extract_sudo_line(output):
    """PM2 prints the exact command to run with admin rights; grab it."""
    for ln in (x.strip() for x in output.splitlines()):
        if ln.startswith("sudo") and "pm2 startup" in ln:
            return ln
        if ln.startswith("env ") and "pm2 startup" in ln:
            return "sudo " + ln
        if ln.startswith("pm2 startup") or ln.startswith("pm2-startup"):
            return ln
    return ""


def startup_sudo_command():
    """Return the exact admin command PM2 recommends for enabling boot start."""
    path = pm2_path()
    if not path:
        return ""
    if IS_WINDOWS:
        candidates = ([path, "startup"],)
    else:
        init = "launchd" if IS_MAC else "systemd"
        candidates = ([path, "startup", init, "-u", username(), "--hp", HOME],)
    # Ask PM2 itself what it needs; when the user lacks rights it prints the
    # exact command without running it.
    for try_cmd in candidates:
        try:
            out = run_cmd(try_cmd, timeout=30)
        except PM2Error as exc:
            out = exc.output or str(exc)
        line = _extract_sudo_line(out)
        if line:
            return line
    if IS_WINDOWS:
        return "npm install -g pm2-windows-startup && pm2-startup install"
    if IS_MAC:
        return f"sudo env PATH=$PATH:{os.path.dirname(path)} pm2 startup launchd -u {username()} --hp {HOME}"
    return f"sudo env PATH=$PATH:{os.path.dirname(path)} pm2 startup systemd -u {username()} --hp {HOME}"


def save_list():
    run_cmd([pm2_path(), "save"], timeout=30)
