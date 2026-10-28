#!/usr/bin/env python
r"""group_root.py -- single resolver for the FluxGroup tree, plus a hazard audit (D-20261028-04).

WHY THIS EXISTS
---------------
D-20261028-04: a resident lane script that finds the group repo by climbing
two levels of parent directories, or by a hardcoded mirror path, reads whatever
happens to sit there. The observed damage was silent: `D:\FluxGroup\cph4` was 11
days stale while the live tree kept moving, so lanes read an old world and fired
on it without any error.

The law this file implements: resolve the group root ONLY from
  (a) `git -C <repo> rev-parse --show-toplevel` on THIS repo, then walking up its
      own ancestry -- every step validated as a group worktree; or
  (b) among the worktrees that pass (a), the one with the newest
      `cph4/evolution-ledger.md`.
plus one explicit, validated override (`BIGMONEY_GROUP_ROOT`). No `..\..` blind
climb, no hardcoded mirror path, and an unreadable answer is UNKNOWN (rc 2), never
an older tree read as current.

USAGE
-----
    python Tools/group_root.py check              # resolve + evidence, rc0/rc2
    python Tools/group_root.py audit [--json F]   # scan resident scripts for hazards
    python Tools/group_root.py selftest           # hermetic fixtures only

IMPORT
------
    from Tools.group_root import resolve
    root = resolve()          # str or None -- caller must treat None as UNKNOWN

Exit codes: 0 ok, 1 hazard found (audit), 2 cannot resolve (check).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000
LEDGER = os.path.join("cph4", "evolution-ledger.md")
DECISIONS = os.path.join("docs", "decisions.md")

# Hazards a resolver must not contain. Deliberately narrow: this file itself
# mentions these strings in its own audit table, so the auditor skips itself.
HAZARD_PATTERNS = (
    # os.path.join(ROOT, "..", "..") -- two or more parent args in one call
    ("blind-climb", re.compile(r'"\.\."\s*,\s*"\.\."')),
    # "../.." / '..\\..' written as one literal
    ("blind-climb", re.compile(r'["\']\.\.(?:[\\/]\.\.)+["\']')),
    ("hardcoded-mirror", re.compile(r'["\'](?:[A-Za-z]:[\\/](?:Fluxgroup|FluxGroup)[^"\']*)["\']')),
    ("shell-climb", re.compile(r'cd\s+\.\.[\\/]\.\.')),
)
LEDGER_READ = re.compile(r"decisions\.md|orders\.md|evolution-ledger", re.I)


def _run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          creationflags=CREATE_NO_WINDOW)


def _is_worktree(path):
    if not os.path.isdir(path):
        return False
    r = _run(["git", "-C", path, "rev-parse", "--is-inside-work-tree"])
    return r.returncode == 0 and r.stdout.strip() == "true"


def toplevel(path=ROOT):
    """git-reported root of this repo, or None."""
    r = _run(["git", "-C", path, "rev-parse", "--show-toplevel"])
    if r.returncode != 0:
        return None
    out = r.stdout.strip()
    return os.path.normpath(out) if out else None


def _is_group_tree(path):
    return bool(path) and _is_worktree(path) and os.path.isfile(
        os.path.join(path, DECISIONS))


def _ledger_mtime(path):
    p = os.path.join(path, LEDGER)
    try:
        return os.path.getmtime(p)
    except OSError:
        return 0.0


def candidates(start=ROOT):
    """Anchored candidates only: ancestors of THIS repo's git toplevel.

    Returns [(path, rule)] where rule says why that path is in the list.
    """
    out = []
    env = os.environ.get("BIGMONEY_GROUP_ROOT")
    if env:
        out.append((os.path.normpath(env), "env:BIGMONEY_GROUP_ROOT"))
    top = toplevel(start)
    if not top:
        return out
    cur = top
    for _ in range(4):
        cur = os.path.dirname(cur)
        if not cur or cur == os.path.dirname(cur):
            break
        out.append((cur, "ancestor-of-toplevel"))
    return out


def resolve(start=ROOT):
    """Return dict {root, rule, evidence}; root is None when UNKNOWN."""
    seen = []
    valid = []
    for path, rule in candidates(start):
        ok = rule.startswith("env:") or _is_group_tree(path)
        if rule.startswith("env:") and not _is_group_tree(path):
            # an override is a claim, not an authority: validate it like any other
            seen.append({"path": path, "rule": rule, "accepted": False,
                         "why": "env override is not a group worktree (no %s)" % DECISIONS})
            continue
        if not ok:
            continue
        valid.append({"path": path, "rule": rule,
                      "ledger_mtime": _ledger_mtime(path)})
        seen.append({"path": path, "rule": rule, "accepted": True})
    if not valid:
        return {"root": None, "rule": "none", "evidence": [],
                "tried": seen, "verdict": "UNKNOWN"}
    valid.sort(key=lambda e: e["ledger_mtime"], reverse=True)
    best = valid[0]
    return {
        "root": best["path"],
        "rule": ("newest-%s" % LEDGER) if len(valid) > 1 else best["rule"],
        "evidence": [{"path": v["path"], "rule": v["rule"],
                      "ledger_mtime": time.strftime(
                          "%Y-%m-%d %H:%M", time.localtime(v["ledger_mtime"]))}
                     for v in valid],
        "tried": seen,
        "verdict": "OK",
    }


# ---------------------------------------------------------------- audit ----
# Resident scripts only: one-off windows (`_r1234...`) and scratch files are
# historical evidence, not lanes that wake up every five minutes.
RESIDENT_DIRS = ("Tools", "scripts")
SKIP_NAME = re.compile(r"^(_r\d|_tmp|_w\d|_r_)", re.I)
AUDIT_SELF = "group_root.py"


def _iter_scripts(start=ROOT):
    for sub in RESIDENT_DIRS:
        d = os.path.join(start, sub)
        for dirpath, dirnames, files in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in ("__pycache__", "_tmp")]
            for fn in files:
                if not fn.endswith((".py", ".ps1")):
                    continue
                if SKIP_NAME.match(fn) or fn == AUDIT_SELF:
                    continue
                yield os.path.join(dirpath, fn)


def audit(start=ROOT):
    rows = []
    for p in sorted(_iter_scripts(start)):
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        hits = []
        for kind, pat in HAZARD_PATTERNS:
            for m in pat.finditer(txt):
                line = txt.count("\n", 0, m.start()) + 1
                hits.append({"kind": kind, "line": line,
                             "text": m.group(0)[:90]})
        uses_resolver = "group_root" in txt
        reads_ledger = bool(LEDGER_READ.search(txt))
        if hits and reads_ledger:
            verdict = "HAZARD"
        elif hits:
            # a cross-machine launcher may legitimately name another box's tree;
            # that is a note, not a stale-ledger read (D-20261028-04 scope).
            verdict = "mirror-note"
        elif uses_resolver:
            verdict = "resolver"
        elif reads_ledger:
            # mentions a group ledger but resolves nothing -- informational, and
            # the ones that DO locate the group tree are the hazards above.
            verdict = "ledger-mention"
        else:
            verdict = "clear"
        rows.append({"path": os.path.relpath(p, start).replace(os.sep, "/"),
                     "verdict": verdict,
                     "hits": hits, "uses_resolver": uses_resolver})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["check", "audit", "selftest"])
    ap.add_argument("--json", default=None, help="write the report here")
    a = ap.parse_args(argv)

    if a.cmd == "check":
        r = resolve()
        if r["root"]:
            print("group-root: OK %s (rule=%s)" % (r["root"], r["rule"]))
            for e in r["evidence"]:
                print("  candidate %s [%s] ledger=%s"
                      % (e["path"], e["rule"], e["ledger_mtime"]))
            rc = 0
        else:
            print("group-root: UNKNOWN -- no validated group worktree in this repo's ancestry.")
            print("  a reader must say UNKNOWN, not read an older tree as current")
            for e in r["tried"]:
                print("  rejected: %s [%s]" % (e["path"], e["rule"]))
            rc = 2
        if a.json:
            open(a.json, "w", encoding="utf-8").write(json.dumps(r, indent=1))
        return rc

    if a.cmd == "audit":
        rows = audit()
        hz = [r for r in rows if r["verdict"] == "HAZARD"]
        un = [r for r in rows if r["verdict"] == "ledger-mention"]
        for r in rows:
            if r["verdict"] in ("HAZARD", "ledger-mention", "resolver", "mirror-note"):
                print("%-16s %s" % (r["verdict"], r["path"]))
                for h in r["hits"]:
                    print("    L%-5d %-17s %s" % (h["line"], h["kind"], h["text"]))
        print("group-root audit: %d scripts, hazards=%d ledger-mentions=%d resolver-backed=%d "
              "mirror-notes=%d clear=%d"
              % (len(rows), len(hz), len(un),
                 sum(1 for r in rows if r["verdict"] == "resolver"),
                 sum(1 for r in rows if r["verdict"] == "mirror-note"),
                 sum(1 for r in rows if r["verdict"] == "clear")))
        if a.json:
            open(a.json, "w", encoding="utf-8").write(json.dumps(rows, indent=1))
        return 1 if hz else 0

    return selftest()


# ------------------------------------------------------------- selftest ----
def _mk_repo(path):
    os.makedirs(path, exist_ok=True)
    _run(["git", "init", "-q", path])
    return path


def _mk_group(path, ledger_age=0):
    _mk_repo(path)
    os.makedirs(os.path.join(path, "docs"), exist_ok=True)
    os.makedirs(os.path.join(path, "cph4"), exist_ok=True)
    open(os.path.join(path, DECISIONS), "w", encoding="utf-8").write("| date | x |\n")
    led = os.path.join(path, LEDGER)
    open(led, "w", encoding="utf-8").write("- x\n")
    t = time.time() - ledger_age
    os.utime(led, (t, t))
    return path


def selftest():
    passed = failed = 0

    def leg(ok, name, detail=""):
        nonlocal passed, failed
        if ok:
            passed += 1
            print("[PASS] %s %s" % (name, detail))
        else:
            failed += 1
            print("[FAIL] %s %s" % (name, detail))

    tmp = tempfile.mkdtemp(prefix="grp_")
    # layout: <tmp>/FluxGroup/{docs,cph4} + <tmp>/FluxGroup/quant/bigmoney(repo)
    grp = _mk_group(os.path.join(tmp, "FluxGroup"), ledger_age=3600)
    repo = _mk_repo(os.path.join(grp, "quant", "bigmoney"))

    r = resolve(repo)
    leg(r["root"] == grp and r["verdict"] == "OK",
        "ancestry of the git toplevel finds the group tree", r["rule"])

    # a sibling stale mirror two levels up from a DIFFERENT repo must not win
    other = os.path.join(tmp, "elsewhere")
    _mk_repo(other)
    r2 = resolve(other)
    leg(r2["root"] is None and r2["verdict"] == "UNKNOWN",
        "no group worktree in ancestry -> UNKNOWN, not a guess",
        str(r2["root"]))

    # env override is validated, not trusted
    fake = os.path.join(tmp, "not-a-group")
    os.makedirs(fake, exist_ok=True)
    os.environ["BIGMONEY_GROUP_ROOT"] = fake
    r3 = resolve(repo)
    leg(r3["root"] == grp, "an invalid env override is rejected, the real tree still wins",
        r3["rule"])
    # and a valid override is honoured
    grp2 = _mk_group(os.path.join(tmp, "FluxGroup-alt"), ledger_age=0)
    os.environ["BIGMONEY_GROUP_ROOT"] = grp2
    r4 = resolve(repo)
    leg(r4["root"] == grp2, "a valid env override is honoured", r4["root"])
    del os.environ["BIGMONEY_GROUP_ROOT"]

    # two valid trees in ancestry -> newest ledger wins (law 2)
    inner = _mk_group(os.path.join(grp, "quant"), ledger_age=0)
    r5 = resolve(repo)
    leg(r5["root"] == inner and r5["rule"].startswith("newest"),
        "two valid trees -> newest evolution-ledger wins", r5["rule"])
    r6 = resolve(repo)
    leg(r6["evidence"][0]["path"] == inner, "the winner is the first evidence row")

    # auditor catches both hazard shapes and spares one-off windows
    fd = os.path.join(tmp, "audit")
    os.makedirs(os.path.join(fd, "Tools"), exist_ok=True)
    open(os.path.join(fd, "Tools", "bad_climb.py"), "w", encoding="utf-8").write(
        'import os\nROOT = os.path.dirname(os.path.abspath(__file__))\n'
        'G = os.path.normpath(os.path.join(ROOT, "..", ".."))\n'
        'open(os.path.join(G, "docs", "decisions.md")).read()\n')
    open(os.path.join(fd, "Tools", "bad_hard.py"), "w", encoding="utf-8").write(
        'GRP = r"C:\\Fluxgroup\\FluxGroup"\nprint(open(os.path.join(GRP, "docs", "decisions.md")).read())\n')
    open(os.path.join(fd, "Tools", "good.py"), "w", encoding="utf-8").write(
        'from Tools.group_root import resolve\np = resolve()\n')
    open(os.path.join(fd, "Tools", "_r1234bmc_s0.py"), "w", encoding="utf-8").write(
        'G = os.path.normpath(os.path.join(ROOT, "..", ".."))\n')
    rows = {r["path"]: r for r in audit(fd)}
    leg(rows["Tools/bad_climb.py"]["verdict"] == "HAZARD", "blind climb is a hazard")
    leg(rows["Tools/bad_hard.py"]["verdict"] == "HAZARD", "hardcoded mirror is a hazard")
    leg(rows["Tools/good.py"]["verdict"] == "resolver", "resolver use is recognised")
    leg("Tools/_r1234bmc_s0.py" not in rows, "one-off windows are not audited")

    # the live repo must resolve to a tree that is newer than any mirror we can see
    live = resolve(ROOT)
    if live["root"]:
        dec = os.path.join(live["root"], DECISIONS)
        bytes_now = os.path.getsize(dec) if os.path.isfile(dec) else -1
        leg(bytes_now > 0, "live tree resolves with a readable decisions.md",
            "%s %dB" % (live["root"], bytes_now))
    else:
        leg(False, "live tree resolves", "UNKNOWN -- fix the layout before trusting lanes")

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("selftest: %d/%d PASS" % (passed, passed + failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())