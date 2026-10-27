#!/usr/bin/env python
"""Group-root sweep (D-20261028-04).

WHY
---
The 2026-10-28 decision named the failure mode: a resident script that finds the
group tree by climbing `..\\..` or by pasting a mirror path keeps "working" while
reading a week-old ledger. `Tools/group_root.py` is the one resolver; this tool
answers the question the decision actually asks -- *is any resident script still
doing it the old way?* -- instead of relying on somebody grepping by hand once.

WHY NOT A PLAIN GREP
--------------------
A raw scan of this repo finds several hundred dotted-paths and drive letters.
Almost none of them are the defect:

  * one-off round scripts (`Tools/_r1219bmc_closeout.py`) -- they ran once, they
    are history, and rewriting them would be churn without a reader;
  * this repo's OWN root (`...\\quant\\bigmoney`) pasted in -- a portability wart,
    not the D-19 failure (it cannot resolve to a stale *group* tree);
  * `Tools/group_root.py` itself, whose whole job is to name the banned shapes.

So the census classifies every hit and only the `resident-group-root` bucket is a
gate failure. Advisory buckets are published so the next sweep sees drift early.

Usage:
    python scripts/group_root_sweep.py run         # census -> results JSON
    python scripts/group_root_sweep.py selftest    # offline, hermetic

Exit: 0 = no resident group-root defects, 1 = at least one (gate red),
      2 = mechanism failure (repo root unreadable).
"""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCAN_DIRS = ("scripts", "Tools", "firm", "live", "monitor")
SUFFIXES = (".py", ".ps1")

# A drive-lettered path that stops at the group tree (mode: group root) or that
# walks into quant/bigmoney (mode: this repo's own root).
DRIVE_PATH = re.compile(r"[A-Za-z]:[\\/]{1,2}(?P<rest>[^\"'\s)]+)", re.IGNORECASE)
CLIMB = re.compile(r"""["'](?:\.\.[\\/]){2,}(?P<rest>[^"']*)["']"""
                   r"""|["']\.\.["']\s*[,)]\s*["']\.\.["']""")
RESOLVER_IMPORT = re.compile(r"\bfrom\s+group_root\s+import|import\s+group_root\b")

# Round-scoped scratch scripts. They are history; the sweep names them, it does
# not rewrite them.
ONE_OFF = re.compile(r"(^_|^_?r\d{3,}|^run_.*_bm[abc]|^register_.*r?\d{3,})", re.IGNORECASE)

# The resolver has to NAME the banned shapes to reject them; holding it to the
# rule it implements would be a tautology. Every other resident file is in scope.
EXEMPT = {"scripts/group_root_sweep.py", "Tools/group_root.py"}

# A script that cannot import the Python resolver (a .ps1, a one-shot .py) may
# still walk up -- but only if it VALIDATES each candidate, and only if it says
# so in the file. The marker is the audit trail; without it the climb stays a
# defect. Accepted shape: `# group-root-sweep: validated-walk - <why>`.
VALIDATED_WALK = re.compile(r"group-root-sweep:\s*validated-walk", re.IGNORECASE)


def _mode_of(rest):
    """Classify a drive-lettered path by where it stops.

    `K:\\Fluxgroup` is a per-host DEPLOYMENT root (task backups, machine-state
    flags); `K:\\Fluxgroup\\FluxGroup` is the group TREE. Only the latter can be
    served stale by a mirror, so only the latter is a D-19 concern.
    """
    parts = [p for p in re.split(r"[\\/]+", rest) if p]
    low = [p.lower() for p in parts]
    if not low or "fluxgroup" not in low[0]:
        return None
    tail = low[1:]
    if not tail:
        # `D:\FluxGroup` alone is ambiguous: the group tree on some host, or a
        # per-host deployment root named after it. Kept advisory, never a gate.
        return "bare-root"
    if tail[0].startswith("."):
        # K:\Fluxgroup\.codely-cli\... -- per-host deployment, outside any repo
        return "deployment-root"
    if tail[0] in ("minigame", "bigstream", "bighouse", "fluxverse"):
        return "sibling-repo"
    if "quant" in tail and "bigmoney" in tail:
        return "repo-root"
    # nested FluxGroup/, or straight into the tree (D:\FluxGroup\cph4, cph4/, docs/)
    return "group-root"


def scan_file(path):
    """-> list of raw hits {kind, line, text} plus whether the resolver is used."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], {"resolver": False, "validated_walk": False}
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in DRIVE_PATH.finditer(line):
            mode = _mode_of(m.group("rest"))
            if mode:
                hits.append({"kind": "literal", "mode": mode, "line": i,
                             "text": line.strip()[:200]})
        if CLIMB.search(line) and not DRIVE_PATH.search(line):
            hits.append({"kind": "climb", "mode": "group-root", "line": i,
                         "text": line.strip()[:200]})
    return hits, {"resolver": bool(RESOLVER_IMPORT.search(text)),
                  "validated_walk": bool(VALIDATED_WALK.search(text))}


def _inside(path):
    try:
        path.relative_to(ROOT)
        return True
    except ValueError:                     # selftest fixtures live outside the repo
        return False


def classify(path, hits, flags):
    """Attach a bucket to every hit for one file.

    flags is {"resolver": bool, "validated_walk": bool} -- a bool is still
    accepted so the selftest can pass one directly.
    """
    if not isinstance(flags, dict):
        flags = {"resolver": bool(flags), "validated_walk": False}
    uses_resolver = flags["resolver"]
    rel = str(path.relative_to(ROOT)).replace(os.sep, "/") if _inside(path) else path.name
    one_off = bool(ONE_OFF.search(path.stem))
    out = []
    for h in hits:
        if rel in EXEMPT:
            bucket = "exempt-resolver"
        elif h["mode"] == "deployment-root":
            bucket = "deployment-root-literal"
        elif h["mode"] == "bare-root":
            bucket = "bare-root-literal"
        elif h["mode"] == "repo-root":
            bucket = "repo-root-literal"
        elif h["mode"] == "sibling-repo":
            bucket = "sibling-repo-literal"
        elif uses_resolver:
            bucket = "group-root-hint"          # literal is only a hint to the resolver
        elif one_off:
            bucket = "one-off"
        elif h["kind"] == "climb" and flags["validated_walk"]:
            bucket = "validated-walk"           # declared and validated, not blind
        else:
            bucket = "resident-group-root"      # the D-19 defect
        row = dict(h)
        row.update({"file": rel, "bucket": bucket, "uses_resolver": uses_resolver})
        out.append(row)
    return out


def census():
    rows, by_file = [], {}
    files = 0
    resolver_users = []
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.suffix.lower() not in SUFFIXES or "__pycache__" in p.parts:
                continue
            files += 1
            hits, uses = scan_file(p)
            if uses["resolver"]:
                resolver_users.append(str(p.relative_to(ROOT)).replace(os.sep, "/"))
            if not hits:
                continue
            classified = classify(p, hits, uses)
            rows.extend(classified)
            by_file[str(p.relative_to(ROOT)).replace(os.sep, "/")] = [
                {"bucket": c["bucket"], "mode": c["mode"], "line": c["line"]}
                for c in classified]

    buckets = {}
    for r in rows:
        buckets.setdefault(r["bucket"], []).append(r)
    defects = buckets.get("resident-group-root", [])
    return {
        "schema": "group-root-sweep/2",
        "decision": "D-20261028-04",
        "scan_dirs": list(SCAN_DIRS),
        "files_scanned": files,
        "n_hits": len(rows),
        "counts": {k: len(v) for k, v in sorted(buckets.items())},
        "verdict": "PASS" if not defects else "FAIL",
        "defects": defects,
        "advisory": {k: v[:40] for k, v in buckets.items() if k != "resident-group-root"},
        "files_using_resolver": sorted(resolver_users),
        "by_file": by_file,
        "law": "a resident script must resolve the group root via Tools/group_root"
               " (validated toplevel + origin + newest ledger mtime); a literal is a"
               " hint, a climb is never the decision",
    }


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def _selftest():
    import tempfile
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    # 1. classification of a foreign-mirror literal as the defect it is
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        bad = tmp / "resident_thing.py"
        bad.write_text("GRP = r'D:\\FluxGroup\\cph4'\n", encoding="utf-8")
        hits, uses = scan_file(bad)
        rows = [{"file": "x", **h} for h in hits]
        modes = {r["mode"] for r in rows}
        leg("a bare mirror literal is classified group-root", modes == {"group-root"},
            str(modes))
        leg("the defect survives one_off=False",
            not ONE_OFF.search("resident_thing") and len(hits) == 1)

        # 2. a one-off round script is named but not a gate failure
        oneoff = tmp / "_r1219bmc_closeout.py"
        oneoff.write_text("GROUP = r'K:\\Fluxgroup\\FluxGroup'\n", encoding="utf-8")
        o_rows = classify(oneoff, scan_file(oneoff)[0], False)
        leg("one-off round scripts land in the advisory bucket",
            o_rows and o_rows[0]["bucket"] == "one-off", str([r["bucket"] for r in o_rows]))

        # 3. the same literal is only a hint when the resolver is imported
        hint = tmp / "resident_ok.py"
        hint.write_text("from group_root import pick_or_default\n"
                        "GRP = pick_or_default(r'K:\\Fluxgroup\\FluxGroup')\n",
                        encoding="utf-8")
        h_hits, h_uses = scan_file(hint)
        h_rows = classify(hint, h_hits, h_uses)
        leg("a literal feeding the resolver is a hint, not a defect",
            h_uses and h_rows and h_rows[0]["bucket"] == "group-root-hint",
            str([r["bucket"] for r in h_rows]))

        # 4. this repo's own root is a different (advisory) bucket
        own = tmp / "resident_own.py"
        own.write_text("ROOT = r'K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney'\n",
                       encoding="utf-8")
        a_rows = classify(own, scan_file(own)[0], False)
        leg("this repo's own root is not confused with the group root",
            a_rows and a_rows[0]["bucket"] == "repo-root-literal",
            str([r["bucket"] for r in a_rows]))

        # 5. a climb with no resolver is the defect (the r1315 shape)
        climb = tmp / "resident_climb.py"
        climb.write_text("p = os.path.join('..', '..', 'docs', 'decisions.md')\n",
                         encoding="utf-8")
        c_hits, c_uses = scan_file(climb)
        leg("a bare '..\\..' climb is caught", bool(c_hits), str(c_hits))
        leg("a bare climb with no declaration is still a defect",
            classify(climb, c_hits, c_uses)[0]["bucket"] == "resident-group-root",
            str([r["bucket"] for r in classify(climb, c_hits, c_uses)]))

        # 5b. a validated walk that SAYS SO is advisory, not a defect
        walk = tmp / "resident_walk.py"
        walk.write_text("# group-root-sweep: validated-walk - candidates checked for"
                        " origin before use\n"
                        "c = os.path.join('..', '..')\n", encoding="utf-8")
        w_hits, w_flags = scan_file(walk)
        w_rows = classify(walk, w_hits, w_flags)
        leg("a declared, validated walk lands in the advisory bucket",
            w_flags["validated_walk"] and w_rows and w_rows[0]["bucket"] == "validated-walk",
            str([r["bucket"] for r in w_rows]))

        # 6. clean file produces nothing
        clean = tmp / "resident_clean.py"
        clean.write_text("from group_root import pick\nroot, rej = pick()\n",
                         encoding="utf-8")
        leg("a clean file yields zero hits", scan_file(clean)[0] == [])

        # 7. the per-host deployment root is NOT the group tree (K:\Fluxgroup\.codely-cli)
        dep = tmp / "resident_dep.py"
        dep.write_text('VALVE = r"K:\\Fluxgroup\\.codely-cli\\machine-state.flag"\n',
                       encoding="utf-8")
        d_rows = classify(dep, scan_file(dep)[0], False)
        leg("a deployment-root path is advisory, not a group-tree defect",
            d_rows and d_rows[0]["bucket"] == "deployment-root-literal",
            str([r["bucket"] for r in d_rows]))

    # 7. the live census runs and its verdict is internally consistent
    try:
        live = census()
    except Exception as exc:                       # pragma: no cover
        leg("live census runs", False, repr(exc))
        live = None
    if live:
        leg("live census scanned files", live["files_scanned"] > 100,
            "files=%d" % live["files_scanned"])
        leg("live census verdict matches its defect count",
            (live["verdict"] == "PASS") == (live["counts"].get("resident-group-root", 0) == 0),
            "verdict=%s counts=%s" % (live["verdict"], live["counts"]))
        leg("the resolver itself is in the scanned set",
            any("group_root" in f for f in live["files_using_resolver"]),
            str(live["files_using_resolver"]))

    passed = sum(1 for _n, c, _d in legs if c)
    for name, c, detail in legs:
        print("[%s] %s%s" % ("PASS" if c else "FAIL", name, ("  " + detail) if detail else ""))
    print("group_root_sweep selftest: %d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return _selftest()
    if cmd != "run":
        sys.stderr.write("usage: group_root_sweep.py [run|selftest]\n")
        return 2
    if not (ROOT / "scripts").is_dir():
        sys.stderr.write("group_root_sweep: repo root unreadable: %s\n" % ROOT)
        return 2
    payload = census()
    out = ROOT / "results" / "group_root_sweep.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print("group_root_sweep: %s files=%d hits=%d counts=%s"
          % (payload["verdict"], payload["files_scanned"], payload["n_hits"],
             payload["counts"]))
    for r in payload["defects"][:20]:
        print("  DEFECT %s:%d %s" % (r["file"], r["line"], r["text"]))
    print("  resolver users: %s" % ", ".join(payload["files_using_resolver"]))
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))