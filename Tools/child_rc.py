"""Tell a child process that rendered a verdict apart from one that was killed first.

Why this exists (r1943 bm-c, live-fire): the unattended smoke suite closed one leg
red -- "fleet: a partial-index commit cannot silently shrink the tree | guard
selftest rc=3221225786" -- while that very guard's selftest passed 17/17 on the
same box minutes earlier. rc=3221225786 is 0xC000013A = STATUS_CONTROL_C_EXIT:
the child did not fail, it was killed by a console control event (the launcher
that started the suite was torn down and the event reached the child). A process
that dies that way never rendered a verdict, so reading its exit code as "the
guard is broken" spends a whole round proving nothing -- and, worse, it teaches
the reader that this leg is noise, which is how real defects get ignored later
(r1789 family, inverted).

The rule this module implements: only "this program ran and said no" is a red.
"Something outside killed it" is a third state that must be counted apart from
green (a silent pass would read as clean) and apart from red.

Usage
  from Tools.child_rc import classify, is_interrupted, describe
  state = classify(tp.returncode)        # {'state': 'ok'|'failed'|'interrupted', ...}
  python Tools/child_rc.py selftest
  python Tools/child_rc.py <exit-code>   # human reading of one code

Exit codes: 0 = selftest green / code read, 1 = selftest red, 2 = bad usage.
"""
from __future__ import annotations

import os
import subprocess
import sys

# Windows NTSTATUS values that mean "a control event or a debugger ended me",
# not "I ran to completion and returned this number".
#   0xC000013A STATUS_CONTROL_C_EXIT -- Ctrl-C, Ctrl-Break, or the console closed.
#   0x40010004 DBG_TERMINATE_PROCESS -- the process was terminated through a debugger.
# POSIX reports a signal death as a negative return code instead: -2 SIGINT,
# -9 SIGKILL, -15 SIGTERM. They are here so a Linux box reads the same table.
CONTROL_EXIT = {
    0xC000013A: "STATUS_CONTROL_C_EXIT (Ctrl-C / Ctrl-Break / the console was closed)",
    0x40010004: "DBG_TERMINATE_PROCESS (terminated through a debugger)",
    -2: "SIGINT (interrupted)",
    -9: "SIGKILL (killed)",
    -15: "SIGTERM (terminated)",
}


def _unsigned(rc: int) -> int:
    """The DWORD a Windows exit code actually is (subprocess may hand back either sign)."""
    return rc & 0xFFFFFFFF


def classify(rc) -> dict:
    """Say what an exit code means: ran-and-said-no, ran-and-said-yes, or was killed.

    Never returns state='ok' for a code it cannot read, and never returns
    'interrupted' for an ordinary non-zero code -- an ordinary failure has to stay
    red, otherwise this helper becomes a way to silence legs.
    """
    if rc is None:
        return {"state": "failed", "code": None, "hex": None,
                "name": "NO EXIT CODE", "detail": "the child never produced an exit code"}
    try:
        code = int(rc)
    except (TypeError, ValueError):
        return {"state": "failed", "code": rc, "hex": None,
                "name": "UNREADABLE EXIT CODE", "detail": "exit code was not an integer"}
    if code == 0:
        return {"state": "ok", "code": 0, "hex": "0x00000000",
                "name": "SUCCESS", "detail": "the child ran and returned 0"}
    # subprocess hands the code back unsigned (3221225786) while a PowerShell reader
    # prints the same event signed (-1073741510); both spellings must classify alike.
    for key in (code, _unsigned(code)):
        if key in CONTROL_EXIT:
            return {"state": "interrupted", "code": code, "hex": "0x%08X" % _unsigned(code),
                    "name": CONTROL_EXIT[key],
                    "detail": "the child was killed before it rendered a verdict"}
    return {"state": "failed", "code": code, "hex": "0x%08X" % _unsigned(code),
            "name": "NON-ZERO EXIT", "detail": "the child ran and returned %d" % code}


def is_interrupted(rc) -> bool:
    return classify(rc)["state"] == "interrupted"


def describe(rc) -> str:
    s = classify(rc)
    if s["hex"] is None:
        return "rc=%s %s" % (s["code"], s["name"])
    return "rc=%d (%s %s)" % (s["code"], s["hex"], s["name"])


# ---------------------------------------------------------------------------
# selftest: the interesting leg spawns a real child that really dies of the
# control-event code. A table lookup alone would pass even if subprocess handed
# the code back in a different sign (r1935: a self-check that only re-computes
# itself can never say "I am wrong").
# ---------------------------------------------------------------------------

def _legs():
    out = []

    def leg(name, ok, detail=""):
        out.append((name, bool(ok), detail))
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" " + detail) if detail else ""))

    leg("L1 a clean child is ok", classify(0)["state"] == "ok", "rc=0")
    leg("L2 an ordinary failure stays red", classify(1)["state"] == "failed")
    c = classify(3221225786)
    leg("L3 the control-event code reads as interrupted, with a name",
        c["state"] == "interrupted" and "STATUS_CONTROL_C_EXIT" in c["name"], c["hex"])
    leg("L4 the same code read as a signed integer reads the same",
        classify(-1073741510)["state"] == "interrupted", "-1073741510")
    leg("L5 a missing exit code is never green or forgiven",
        classify(None)["state"] == "failed", classify(None)["name"])
    leg("L6 describe() prints the hex and the meaning, not a verdict",
        "0xC000013A" in describe(3221225786) and "STATUS_CONTROL_C_EXIT" in describe(3221225786))

    # Real child, real control-event code: proves the OS round-trip, not a constant.
    # os._exit cannot ask for it (OverflowError on the way to C int, which returns rc=1 --
    # the first version of this leg asserted exactly that and went red, which is the
    # whole point of driving the code path instead of the table), so the child asks
    # the kernel directly. POSIX has the same shape through a real signal.
    if os.name == "nt":
        _runner = [sys.executable, "-c",
                   "import ctypes; ctypes.windll.kernel32.ExitProcess(3221225786)"]
    else:
        _runner = [sys.executable, "-c",
                   "import os, signal; os.kill(os.getpid(), signal.SIGTERM)"]
    try:
        kill = subprocess.run(_runner, capture_output=True, text=True, timeout=120)
        got = classify(kill.returncode)
        leg("L7 a child that really dies of a control event classifies as interrupted",
            got["state"] == "interrupted", "rc=%s" % kill.returncode)
    except Exception as e:  # pragma: no cover - only on a broken interpreter
        leg("L7 a child that really dies of a control event classifies as interrupted", False, str(e))

    # Real child, ordinary failure: the same code path must still say red.
    try:
        bad = subprocess.run([sys.executable, "-c", "import sys; sys.exit(3)"],
                             capture_output=True, text=True, timeout=120)
        leg("L8 a child that really exits 3 stays red",
            classify(bad.returncode)["state"] == "failed", "rc=%s" % bad.returncode)
    except Exception as e:  # pragma: no cover
        leg("L8 a child that really exits 3 stays red", False, str(e))
    return out


def main(argv) -> int:
    if len(argv) > 1 and argv[1] == "selftest":
        legs = _legs()
        n = sum(1 for _, ok, _ in legs if ok)
        print("\nselftest: %d/%d PASS" % (n, len(legs)))
        return 0 if n == len(legs) else 1
    if len(argv) > 1:
        try:
            print(describe(int(argv[1], 0)))
            return 0
        except ValueError:
            print("usage: child_rc.py selftest | child_rc.py <exit-code>", file=sys.stderr)
            return 2
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
