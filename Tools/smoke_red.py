#!/usr/bin/env python
# smoke_red.py -- "what did the last full suite fail on?", read off the suite's
# own record (r1748 bm-c tech chore, driven by the r1747 closeout).
#
# The problem this retires: r1747 closed with "Summary: 600/601 PASS, 1 FAIL"
# and no [FAIL] line anywhere in results/_smoke_r1747.out. The transcript is a
# shared file handle, so a spliced write can overwrite exactly the one line an
# auditor needs -- that run carries a lone "[" at line 581, a leg name chopped
# in half ("product: alloc cell checkpoin"), and one leg name printed twice.
# Counting says something is wrong; it cannot say WHAT. smoke_test now writes
# logs/smoke_legs.json on every run (smoke_test._verdict_record), including the
# failing names and their details.
#
# This reader is what a round open should use instead of grepping an 80KB
# transcript: one line, exit code, names.
#
# Exit codes (priority order):
#   0 = last recorded run has zero failing legs
#   3 = last recorded run has failing legs (names on stdout, one per line)
#   2 = no record on disk / unreadable record -- NOT a pass. A missing file
#       means no run has finished since the recorder landed, and reading that
#       as green is the same defect one level up.
#
# Usage:
#   python Tools/smoke_red.py
#   python Tools/smoke_red.py --selftest
import json
import os
import sys
import tempfile

DEFAULT_RECORD = os.path.join("logs", "smoke_legs.json")


def load(path=None):
    """The record as a dict, or None when there is nothing readable there."""
    path = path or DEFAULT_RECORD
    try:
        with open(path, encoding="utf-8") as fh:
            rec = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(rec, dict) or "fail" not in rec:
        return None
    return rec


def verdict(rec):
    """(exit code, lines to print) for one record."""
    failed = rec.get("failed") or []
    n_fail = int(rec.get("fail") or 0)
    head = ("%s: %s/%s PASS, %d FAIL"
            % (rec.get("ts") or "?", int(rec.get("pass") or 0),
               int(rec.get("legs") or 0), n_fail))
    if not failed:
        # A count without names would be the same blind spot the record fixes.
        if n_fail:
            return 2, [head + " -- the record counts reds but names none (unreadable record)"]
        return 0, [head + " (green)"]
    lines = [head]
    for row in failed:
        name = str((row or {}).get("name") or "?")
        detail = str((row or {}).get("detail") or "")
        lines.append("RED: " + name + ((" | " + detail[:200]) if detail else ""))
    return 3, lines


def main(argv) -> int:
    if "--selftest" in argv:
        return _selftest()
    path = (argv[0] if argv and not argv[0].startswith("-") else None)
    rec = load(path)
    if rec is None:
        print("UNKNOWN: no readable suite record at %s -- nothing has finished since the "
              "recorder landed, which is not a pass" % (path or DEFAULT_RECORD))
        return 2
    rc, lines = verdict(rec)
    for line in lines:
        print(line)
    return rc


def _selftest() -> int:
    """Four states a reader must tell apart, plus a record that counts reds and
    names none (that one is a broken record, not a pass)."""
    ok = 0
    bad = []

    def want(label, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append(label)

    d = tempfile.mkdtemp(prefix="smoke-red-selftest-")
    red = os.path.join(d, "red.json")
    with open(red, "w", encoding="utf-8") as fh:
        json.dump({"ts": "2026-11-16T02:01:00", "legs": 601, "pass": 600, "fail": 1,
                   "failed": [{"name": "product: some leg", "detail": "boom"}]}, fh)
    rc, lines = verdict(load(red))
    want("a red run exits 3", rc == 3)
    want("a red run names the leg", any("product: some leg" in ln for ln in lines))
    want("a red run carries the count", any("600/601" in ln for ln in lines))

    green = os.path.join(d, "green.json")
    with open(green, "w", encoding="utf-8") as fh:
        json.dump({"ts": "2026-11-16T03:01:00", "legs": 601, "pass": 601,
                   "fail": 0, "failed": []}, fh)
    rc, lines = verdict(load(green))
    want("a green run exits 0", rc == 0)
    want("a green run says green", any("green" in ln for ln in lines))

    want("a missing record is None, never an empty pass", load(os.path.join(d, "nope.json")) is None)
    junk = os.path.join(d, "junk.json")
    with open(junk, "w", encoding="utf-8") as fh:
        fh.write("{not json")
    want("an unreadable record is None", load(junk) is None)

    counted = {"ts": "x", "legs": 10, "pass": 9, "fail": 1, "failed": []}
    rc, lines = verdict(counted)
    want("a record that counts reds but names none exits 2, not 0", rc == 2)

    print("smoke_red selftest: %d PASS, %d FAIL" % (ok, len(bad)))
    for b in bad:
        print("  FAILED", b)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
