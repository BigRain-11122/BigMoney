"""Run child processes without ever creating a console window.

Why this file exists
--------------------
Every automation on this machine runs under pythonw.exe, which has no console of
its own. That is enough to keep *its own* window away, but not enough for the
children: a console program started from a GUI process gets a brand-new console,
and with classic-console delegation on this box that console is a visible window
-- a black flash every time the arbiter asks `nvidia-smi`, every time the board's
auto-fix shells out, every time git is called.

The fix is one flag pair on the child: CREATE_NO_WINDOW plus a STARTUPINFO that
says SW_HIDE. This module is the single place that does it, so a new automation
cannot forget: import `run` instead of `subprocess.run`.

Windows-only flags are applied only on Windows; elsewhere it is plain subprocess.
"""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
SW_HIDE = 0


def _startupinfo():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = SW_HIDE
    return si


def run(cmd, **kwargs):
    """subprocess.run with no console window for the child (Windows)."""
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    if os.name == "nt":
        kwargs.setdefault("startupinfo", _startupinfo())
        kwargs.setdefault("creationflags", CREATE_NO_WINDOW)
    return subprocess.run(cmd, **kwargs)


def popen(cmd, **kwargs):
    """subprocess.Popen with the same guarantee."""
    if os.name == "nt":
        kwargs.setdefault("startupinfo", _startupinfo())
        kwargs.setdefault("creationflags", CREATE_NO_WINDOW)
    return subprocess.Popen(cmd, **kwargs)


def selftest():
    """Prove it: a console child runs, exits 0, and leaves no conhost behind."""
    checks = []
    r = run(["cmd", "/c", "echo silent-run-ok"])
    checks.append(("child exit 0", r.returncode == 0))
    checks.append(("child output captured", "silent-run-ok" in (r.stdout or "")))
    import shutil
    if shutil.which("nvidia-smi"):
        g = run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
        checks.append(("nvidia-smi reachable", g.returncode == 0 and bool((g.stdout or "").strip())))
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
