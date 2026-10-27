#!/usr/bin/env python
"""Worktree poison probe -- catch a stale-snapshot revert BEFORE it is staged.

Why this exists (r1188): an autostash rebase re-materialised another machine's
pre-r1310 changeset into this working tree -- 62 files, 1,986 deleted lines,
including `scripts/etf_book_spanning_pre2020.py`, 133 lines of
`scripts/etf_book_production.py` and `scripts/marks_coverage.py`. Nothing about
the tree looked wrong (every file was a plain `M`/`D`), and the only thing that
stopped it was the pre-push ownership claw, i.e. after the commit existed. The
shape to assert is simple and mechanical: a working tree that DELETES content
HEAD already has, in bulk, is not an edit -- it is a revert.

Verdicts
  CLEAN    nothing that looks like a revert
  SUSPECT  >=200 lines deleted anywhere, or >=3 files gone from the tree with no
           line signal to read (a big rewrite can look like this, so it is
           reported, not blocked)
  POISON   >=2 files HEAD carries are gone with >=200 deleted lines, OR >=2 faces
           owned by another machine are deleted/emptied in the same tree

Usage
  python Tools/tree_poison_probe.py            # probe the live tree
  python Tools/tree_poison_probe.py --json     # + machine-readable face
  python Tools/tree_poison_probe.py --selftest # offline, 12 legs

Exit codes: 0 clean/suspect, 3 poison (caller must not `git add -A`), 2 tool
failure.  Read-only: it never touches the index or the worktree.
"""
import json
import os
import re
import subprocess
import sys

NO_WIN = 0x08000000
MACHINES = ("bm-a", "bm-b", "bm-c")
# Faces a machine signs as its own: the probe treats losing THESE as poison,
# because the machine they belong to will rewrite them and the loss is silent.
OWNED = (
    re.compile(r"(?:^|/)state-(bm-[abc])\.json$"),
    re.compile(r"(?:^|/)round_reports-(bm-[abc])\.md$"),
    re.compile(r"(?:^|/)machines/(bm-[abc])\.json$"),
    re.compile(r"\.(bm-[abc])\.(?:json|jsonl)$"),
)

REVERT_FILES_FLOOR = 2
REVERT_LINES_FLOOR = 200
FOREIGN_FACES_FLOOR = 2


def owner_of(path):
    for rx in OWNED:
        m = rx.search(path)
        if m:
            return m.group(1)
    return None


def classify(rows, self_machine=None):
    """rows: [{"path", "added", "deleted", "exists"}] -> (verdict, reasons, stats)."""
    gone = [r for r in rows if not r["exists"]]
    gone_lines = sum(r["deleted"] or 0 for r in gone)
    all_deleted = sum(r["deleted"] or 0 for r in rows)
    foreign = []
    for r in rows:
        who = owner_of(r["path"])
        if who and who != self_machine and (not r["exists"] or (r["deleted"] or 0) > (r["added"] or 0)):
            foreign.append(r["path"])
    reasons = []
    if len(gone) >= REVERT_FILES_FLOOR and gone_lines >= REVERT_LINES_FLOOR:
        reasons.append("%d files HEAD carries are missing from the tree (%d deleted lines)"
                       % (len(gone), gone_lines))
    if len(foreign) >= FOREIGN_FACES_FLOOR:
        reasons.append("%d faces owned by another machine are being deleted/emptied: %s"
                       % (len(foreign), ", ".join(sorted(foreign)[:4])))
    if reasons:
        verdict = "POISON"
    elif all_deleted >= REVERT_LINES_FLOOR:
        verdict = "SUSPECT"
        reasons.append("%d deleted lines across %d file(s) -- large rewrite or partial revert, look before staging"
                       % (all_deleted, len([r for r in rows if (r["deleted"] or 0) > 0])))
    elif len(gone) >= REVERT_FILES_FLOOR + 1:
        verdict = "SUSPECT"
        reasons.append("%d files gone from the tree with no line counts to read" % len(gone))
    else:
        verdict = "CLEAN"
    stats = {"rows": len(rows), "deleted_files": len(gone),
             "deleted_lines": gone_lines, "all_deleted_lines": all_deleted,
             "foreign_faces": len(foreign)}
    return verdict, reasons, stats


def git(*args):
    p = subprocess.run(["git", "-c", "core.quotepath=false"] + list(args),
                       capture_output=True, creationflags=NO_WIN)
    if p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace")


def parse_numstat(text):
    """`git diff --numstat -z` -> rows. NUL-separated so CJK paths stay intact."""
    rows = []
    for tok in text.split("\0"):
        tok = tok.strip("\n")
        if not tok or tok.count("\t") < 2:
            continue
        add, dele, path = tok.split("\t", 2)
        if " => " in path:  # rename summary is not a deletion signal
            continue
        rows.append({
            "path": path,
            "added": 0 if add == "-" else int(add),
            "deleted": 0 if dele == "-" else int(dele),
        })
    return rows


def read_tree(self_machine):
    head = set(p for p in git("ls-tree", "-r", "--name-only", "-z", "HEAD").split("\0") if p)
    rows = parse_numstat(git("diff", "HEAD", "--numstat", "-z"))
    for r in rows:
        r["exists"] = os.path.exists(r["path"])
    seen = set(r["path"] for r in rows)
    for p in head - seen:
        if not os.path.exists(p):  # gone, and git printed no row for it
            rows.append({"path": p, "added": 0, "deleted": 0, "exists": False})
    return rows


def probe(self_machine="bm-b"):
    rows = read_tree(self_machine)
    verdict, reasons, stats = classify(rows, self_machine=self_machine)
    gone_raw = [r for r in rows if not r["exists"]]
    face = {"machine": self_machine, "verdict": verdict, "reasons": reasons, "stats": stats,
            "worst": sorted(gone_raw, key=lambda r: -(r["deleted"] or 0))[:8]}
    print("tree poison: %s | rows=%d deletes=%d lines=%d foreign=%d"
          % (verdict, stats["rows"], stats["deleted_files"], stats["deleted_lines"],
             stats["foreign_faces"]))
    for r in reasons:
        print("  - " + r)
    return verdict, face


def _rows(*items):
    return [{"path": p, "added": a, "deleted": d, "exists": e} for p, a, d, e in items]


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    big = _rows(*[("scripts/f%d.py" % i, 0, 120, False) for i in range(6)])
    v, r, s = classify(big, "bm-b")
    leg("6 deleted files / 720 lines -> POISON", v == "POISON")
    leg("poison names the file count", "6 files" in " ".join(r))

    one = _rows(("_tmp_scratch.py", 0, 5, False))
    v, _, _ = classify(one, "bm-b")
    leg("one small scratch deletion -> CLEAN", v == "CLEAN")

    two = _rows(("fleet/machines/bm-a.json", 1, 33, True),
                ("round_reports-bm-a.md", 0, 3, False))
    v, r, _ = classify(two, "bm-b")
    leg("two foreign faces emptied -> POISON", v == "POISON")
    leg("foreign reason quotes the owner", "another machine" in " ".join(r))

    own = _rows(("state-bm-b.json", 1, 33, True), ("results/x.bm-b.json", 0, 9, False))
    v, _, _ = classify(own, "bm-b")
    leg("own faces are not foreign", v == "CLEAN")

    mods = _rows(*[("results/regen%d.json" % i, 40, 30, True) for i in range(3)])
    v, _, _ = classify(mods, "bm-b")
    leg("three regenerated faces -> CLEAN", v == "CLEAN")

    mid = _rows(("scripts/big.py", 5, 400, True))
    v, r, _ = classify(mid, "bm-b")
    leg("one 400-line rewrite -> SUSPECT not POISON", v == "SUSPECT")
    leg("suspect says look before staging", "look before staging" in " ".join(r))

    bins = _rows(*[("data/p%d.parquet" % i, 0, 0, False) for i in range(4)])
    v, _, _ = classify(bins, "bm-b")
    leg("binary deletions carry no line signal (>=3 files, 0 lines) -> SUSPECT floor only",
        v == "SUSPECT")

    mixed = _rows(("scripts/marks_coverage.py", 0, 267, False),
                  ("state-bm-c.json", 44, 44, True),
                  ("results/marks_coverage.json", 0, 141, False))
    v, _, s = classify(mixed, "bm-b")
    leg("the r1188 tree would have been caught (POISON)", v == "POISON")
    leg("r1188 shape counted 2 real deletions", s["deleted_files"] == 2)

    ok = sum(1 for _, c in legs if c)

    # The live tree had 10 phantom "missing" files because git quoted CJK paths;
    # the parser must keep those names intact and read their line counts.
    parsed = parse_numstat("0\t267\tscripts/marks_coverage.py\0"
                           "44\t44\tstate-bm-c.json\0"
                           "12\t0\tcontent/drama/\u5267\u672c.md\0")
    by = {r["path"]: r for r in parsed}
    leg("parse_numstat keeps a CJK path byte-intact", "content/drama/\u5267\u672c.md" in by)
    leg("parse_numstat reads its line counts", by.get("content/drama/\u5267\u672c.md", {}).get("added") == 12)
    leg("parse_numstat keeps a deletion", by.get("scripts/marks_coverage.py", {}).get("deleted") == 267)
    ok = sum(1 for _, c in legs if c)
    for name, cond in legs:
        if not cond:
            print("FAIL: " + name)
    print("selftest: %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    verdict, face = probe()
    if "--json" in argv:
        path = "results/tree_poison_probe.bm-b.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        print("face: " + path)
    return 3 if verdict == "POISON" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))