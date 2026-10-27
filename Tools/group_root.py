#!/usr/bin/env python
"""Group-root resolution (D-20261028-04).

WHY
---
A resident script that reads the group ledger has to find the group repo. Two
shortcuts are banned by the 2026-10-28 decision, because both silently serve an
OLD tree:

  * `..\\..` climbs -- they land wherever the layout happens to put them, and on
    a machine with a mirrored checkout they land on the mirror;
  * hardcoded paths (`K:\\Fluxgroup\\FluxGroup`, `D:\\FluxGroup`, ...) -- same
    problem, written down instead of computed.

FluxVerse's live damage: `D:\\FluxGroup\\cph4` was nine days stale (235 vs 373
rows) while every script "worked", so gates fired on week-old decisions.

RULE
----
A candidate is only usable when ALL THREE hold:
  1. `git -C <cand> rev-parse --show-toplevel` == <cand>  (a subdirectory of some
     other repo cannot masquerade as the group tree);
  2. its origin URL is the group repo;
  3. among the survivors, the one with the NEWEST cph4/evolution-ledger.md (or
     docs/decisions.md) mtime wins -- the live tree beats a mirror.

Candidates are still allowed to come from a climb or a literal path; they are a
HINT. The three checks above are what actually decide.

Usage:
    from Tools.group_root import pick
    root, rejected = pick()                 # -> (path|None, [(cand, reason)])
    root = pick_or_default("K:\\Fluxgroup\\FluxGroup")
"""
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
LEDGERS = ("cph4/evolution-ledger.md", "docs/decisions.md")


def _git_out(args, cwd):
    try:
        r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                           creationflags=CREATE_NO_WINDOW)
    except Exception as exc:                     # git absent / not spawnable
        return 1, "spawn-failed: %s" % exc
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace").strip()


def ledger_mtime(cand):
    """Newest mtime of the two ledger faces; 0.0 when the candidate has neither."""
    newest = 0.0
    for rel in LEDGERS:
        try:
            newest = max(newest, os.path.getmtime(os.path.join(cand, *rel.split("/"))))
        except OSError:
            continue
    return newest


def candidates(extra=()):
    """Default hint list for this repo layout, plus anything the caller passes."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = []
    env = os.environ.get("FLUXGROUP_ROOT")
    if env:
        out.append(env)
    out.extend(extra)
    out.append(os.path.normpath(os.path.join(here, "..", "..")))
    out.append(r"K:\Fluxgroup\FluxGroup")
    out.append(r"C:\Fluxgroup\FluxGroup")
    out.append(r"C:\Users\Administrator\FluxGroup")
    seen, uniq = set(), []
    for c in out:
        if not c:
            continue
        k = os.path.normcase(os.path.normpath(c))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(os.path.normpath(c))
    return uniq


def pick(cands=None):
    """-> (live_group_root|None, [(candidate, reason_why_rejected)])."""
    cands = candidates() if cands is None else list(cands)
    viable, rejected = [], []
    for cand in cands:
        if not os.path.isdir(cand):
            rejected.append((cand, "absent"))
            continue
        rc, top = _git_out(["rev-parse", "--show-toplevel"], cand)
        if rc != 0:
            rejected.append((cand, "not-a-worktree"))
            continue
        if os.path.normcase(os.path.normpath(top)) != os.path.normcase(os.path.normpath(cand)):
            rejected.append((cand, "toplevel-is-%s" % top))
            continue
        rc, url = _git_out(["remote", "get-url", "origin"], cand)
        if rc != 0 or "fluxgroup" not in (url or "").lower():
            rejected.append((cand, "origin-is-%s" % (url or "none")))
            continue
        viable.append((ledger_mtime(cand), cand))
    if not viable:
        return None, rejected
    viable.sort(reverse=True)
    return viable[0][1], rejected


def pick_or_default(default=None, cands=None):
    """Convenience for callers that used to hardcode a path: never raises, and
    prints the reason on stderr instead of failing silently."""
    root, rejected = pick(cands if cands is not None else candidates(
        extra=[default] if default else []))
    if root is None:
        sys.stderr.write("group_root: no viable group tree; rejected=%s\n" % (rejected,))
        return default
    return root


def _selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    root, rejected = pick()
    leg("resolves a live group tree on this host", root is not None, str(root))

    here = os.path.dirname(os.path.abspath(__file__))
    sub, rej2 = pick([here])
    leg("a repo subdirectory is rejected, not returned as the group root",
        sub is None and any("toplevel-is" in why for _c, why in rej2),
        "picked=%s rejected=%s" % (sub, rej2))

    fake = os.path.join(os.path.dirname(here), "results", "no_such_tree_r1315")
    none_ok, rej3 = pick([fake])
    leg("a missing candidate is reported, not guessed",
        none_ok is None and rej3 == [(os.path.normpath(fake), "absent")], str(rej3))

    if root:
        m1 = ledger_mtime(root)
        leg("ledger mtime is readable on the live tree", m1 > 0.0, "%.0f" % m1)

    passed = sum(1 for _n, c, _d in legs if c)
    for name, c, detail in legs:
        print("[%s] %s%s" % ("PASS" if c else "FAIL", name, ("  " + detail) if detail else ""))
    print("group_root selftest: %d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    r, rej = pick()
    print("group_root: %s" % (r or "NONE"))
    for c, why in rej:
        print("  rejected %s (%s)" % (c, why))
    sys.exit(0 if r else 2)