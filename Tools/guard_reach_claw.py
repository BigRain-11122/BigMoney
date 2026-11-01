"""guard_reach_claw -- refuse a commit that changes a gate's reach without saying what it reaches.

E342 measured the guard population in ``smoke_test.py`` and ``Tools/s6_chain_bmb.py`` and found the
answer to "what did the rewrite leave behind?" is almost always *nothing a machine can read*: 0 of 5
in-place rewrites left the new acceptance set in a published face, one left a commit message, one
left nothing at all (c169c702), and 3 more checks vanished and came back.  That is what makes the
c169c702 shape invisible: the diff is small, the file grows, every counting face stays green.

This is the cheapest mechanism that would have caught it.  It needs no history and no build: it
compares the *staged* version of the two guarded files with HEAD, and for every check whose
condition changed or disappeared under the same name it demands one of

    (a) some staged path under ``results/``  -- the reach change is priced by a published face, or
    (b) a staged line carrying ``GUARD-REACH: <what the gate now accepts>`` -- an explicit record.

Both are things a careful author was going to write anyway; neither needs a new file format.  A
commit that changes a check and neither of those fails closed (rc=3), which is exactly the state
c169c702 was in.

Usage:
    python Tools/guard_reach_claw.py check        # judge the index (rc 0 clean / 3 violation / 2 error)
    python Tools/guard_reach_claw.py selftest     # judge fixtures, no repo state involved
"""

import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from e342_guard_rewrite_records import (  # noqa: E402  (single source of truth for the parsing)
    CHAIN, GUARDED, SMOKE, check_conditions, check_events)

MARK = "GUARD-REACH:"


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def judge(old_maps, new_maps, staged_paths, staged_text):
    """-> list of violations.  Pure: every input is a plain value, so the selftest can drive it."""
    priced = any(p.replace("\\", "/").startswith("results/") for p in staged_paths)
    lines = [l for l in (staged_text or "").splitlines() if MARK in l]
    violations = []
    for path in GUARDED:
        old_map = old_maps.get(path) or {}
        new_map = new_maps.get(path) or {}
        events, _detail = check_events(old_map, new_map, path)
        for ev in events:
            if ev["kind"] == "rewritten":
                what = "%s (%s)" % (ev["name"], ev["widen"])
            else:
                what = "%s (removed)" % ev["name"]
            if priced:
                continue
            if any(ev["name"] in line for line in lines):
                continue
            violations.append({"file": path, "check": ev["name"], "kind": ev["kind"],
                               "widen": ev["widen"], "what": what})
    return violations


# ---------------------------------------------------------------------------------------------- git

def _git(*args):
    proc = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def staged_text(path):
    rc, out, _err = _git("diff", "--cached", "--unified=0", "--", path)
    return out if rc == 0 else ""


def staged_paths():
    rc, out, _err = _git("diff", "--cached", "--name-only")
    return [p.strip() for p in out.splitlines() if p.strip()] if rc == 0 else []


def version(path, rev=None):
    rc, out, _err = _git("show", "%s:%s" % (rev, path) if rev else ":" + path)
    return out if rc == 0 else None


def cmd_check():
    paths = staged_paths()
    old_maps, new_maps = {}, {}
    for path in GUARDED:
        after = version(path)                      # the index
        before = version(path, "HEAD")
        if after is None or before is None:
            continue                               # a new or deleted file has no rewrite to judge
        try:
            old_maps[path] = check_conditions(before, path)
            new_maps[path] = check_conditions(after, path)
        except SyntaxError as exc:
            say("guard_reach_claw: cannot parse staged %s: %s" % (path, exc))
            return 2
    bad = judge(old_maps, new_maps, paths, "\n".join(staged_text(p) for p in GUARDED))
    if not bad:
        say("guard_reach_claw: no gate changed its reach without a record (%s files staged)"
            % len(paths))
        return 0
    for v in bad:
        say("GUARD-REACH MISSING  %s :: %s" % (v["file"], v["what"]))
    say("guard_reach_claw: %d gate change(s) with no staged results/ face and no '%s' line"
        % (len(bad), MARK))
    return 3


# ----------------------------------------------------------------------------------------- selftest

def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    old = {SMOKE: {"leg a": ["n >= 3"], "leg b": ["ok is True"]},
           CHAIN: {"dualrun": ["['python', 'x.py']"]}}
    new = {SMOKE: {"leg a": ["n >= 1"], "leg b": ["ok is True"]},
           CHAIN: {"dualrun": ["['python', 'x.py']"]}}

    v = judge(old, new, ["results/x.json"], "")
    check("L1 a widened gate with a staged results face passes", v == [], str(v))
    v = judge(old, new, ["smoke_test.py"], "GUARD-REACH: leg a now accepts n >= 1")
    check("L2 a widened gate with an explicit GUARD-REACH line passes", v == [], str(v))
    v = judge(old, new, ["smoke_test.py"], "")
    check("L3 the c169c702 shape fails closed with the check named", 
          len(v) == 1 and v[0]["check"] == "leg a", str(v))
    v = judge(old, new, ["smoke_test.py"], "GUARD-REACH: leg b unchanged")
    check("L4 a GUARD-REACH line about another check does not excuse this one",
          len(v) == 1 and v[0]["check"] == "leg a", str(v))
    v = judge(old, {SMOKE: {"leg b": ["ok is True"]}, CHAIN: old[CHAIN]}, ["x.py"], "")
    check("L5 a vanished check is a violation too", len(v) == 1 and v[0]["kind"] == "removed", str(v))
    v = judge(old, old, [], "")
    check("L6 an untouched gate is not a violation", v == [], str(v))
    v = judge({SMOKE: {"leg a": ["n >= 3"]}, CHAIN: {}},
              {SMOKE: {"leg a": ["n >= 3"]}, CHAIN: {"new": ["['python', 'y.py']"]}}, [], "")
    check("L7 a brand-new leg is not a rewrite of anything", v == [], str(v))
    v = judge({SMOKE: {"leg a": ["n >= 3"]}, CHAIN: old[CHAIN]},
              {SMOKE: {"leg a": ["n >= 3"]}, CHAIN: {"dualrun": ["['python', 'x.py', 'go']"]}},
              [], "")
    kinds = sorted(x["kind"] for x in v)
    check("L8 a chain leg whose command changed counts as a reach change",
          kinds == ["rewritten"] and v[0]["file"] == CHAIN, str(v))

    for name, ok, detail in checks:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " | " + str(detail)))
    failed = [n for n, ok, _d in checks if not ok]
    say("selftest %d/%d" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "check":
        return cmd_check()
    if cmd == "selftest":
        return cmd_selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))