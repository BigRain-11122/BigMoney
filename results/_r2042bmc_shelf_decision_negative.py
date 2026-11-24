#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Negative control for scripts/cash_leg_shelf_decision.py (r2042, bm-c).

Every leg mutates a COPY of the published face and asks the real check() to catch it.
A check that cannot fail on a poisoned copy is not a check.  The last leg asserts that the
published files were not touched by this whole exercise (byte-for-byte).

Usage:  python results/_r2042bmc_shelf_decision_negative.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cash_leg_shelf_decision as M  # noqa: E402

errs = []
legs = [0]


def leg(cond, msg):
    legs[0] += 1
    if not cond:
        errs.append(msg)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


def capture(fn):
    """Run fn, return (rc, stdout text)."""
    old = sys.stdout
    sys.stdout = io.StringIO()
    try:
        rc = fn()
        out = sys.stdout.getvalue()
    finally:
        sys.stdout = old
    return rc, out


def main():
    before = {p: sha(p) for p in (M.OUT_JSON, M.OUT_MD, M.SHELF_JSON, M.BAKEOFF_JSON)}
    tmp = tempfile.mkdtemp(prefix="r2042neg_")

    def fresh_case():
        """A pristine copy of the two published files, rewritten into tmp each time."""
        j = os.path.join(tmp, "case.json")
        m = os.path.join(tmp, "case.md")
        shutil.copyfile(M.OUT_JSON, j)
        shutil.copyfile(M.OUT_MD, m)
        return j, m

    def load(p):
        return json.load(io.open(p, encoding="utf-8"))

    def dump(p, obj):
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

    # L1 -- a healthy copy must be green (otherwise every red below is meaningless)
    j, m = fresh_case()
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 0 and "CHECK OK" in out, "a pristine copy must pass, got rc=%s %s" % (rc, out[:200]))

    # L2 -- one shelf's yuan number moved -> arithmetic leg names it, and it is not a staleness
    j, m = fresh_case()
    d = load(j)
    d["shelves"][0]["extra_cny_per_year"] += 50.0
    dump(j, d)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and "yuan" in out and "STALE" not in out,
        "a moved yuan number must be CHECK FAILED without the STALE word, got: %s" % out[:300])

    # L3 -- the winner's capacity class is downgraded but the decision string is left alone
    j, m = fresh_case()
    d = load(j)
    for s in d["shelves"]:
        if s["code"] == d["winner"]["code"]:
            s["capacity_class"] = "BLOCKED"
    dump(j, d)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and ("gates do not follow" in out or "decision" in out),
        "a class change must break the gates leg, got: %s" % out[:300])

    # L4 -- a defence mean flips sign; the frozen decision string now contradicts its own gates
    j, m = fresh_case()
    d = load(j)
    for s in d["shelves"]:
        if s["defence_mean_pct"] < 0:
            s["defence_mean_pct"] = abs(s["defence_mean_pct"])
            break
    dump(j, d)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and ("gates do not follow" in out or "decision" in out),
        "a flipped defence mean must break the gates leg, got: %s" % out[:300])

    # L5 -- a parent moves by one byte -> STALE, and never a "CHECK FAILED" (two different words)
    j, m = fresh_case()
    patched = os.path.join(tmp, "shelf_moved.json")
    shutil.copyfile(M.SHELF_JSON, patched)
    with io.open(patched, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n")
    old = M.SHELF_JSON
    M.SHELF_JSON = patched
    try:
        rc, out = capture(lambda: M.check(j, m))
    finally:
        M.SHELF_JSON = old
    leg(rc == 3 and "STALE" in out and "CHECK FAILED" not in out,
        "a moved parent must be STALE only, got: %s" % out[:300])

    # L6 -- the page drops one verdict token
    j, m = fresh_case()
    d = load(j)
    text = io.open(m, encoding="utf-8").read().replace(d["verdict"][0], "REMOVED")
    with io.open(m, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and "page missing verdict token" in out,
        "a dropped token must be named, got: %s" % out[:300])

    # L7 -- two numbers swapped inside the winner sentence (the E-20261122 family)
    j, m = fresh_case()
    d = load(j)
    w = d["winner"]
    good = M.winner_sentence(d)
    swapped = good.replace("%.0f" % w["extra_cny_per_year"], "%.0f" % abs(w["defence_day_cny"]), 1)
    text = io.open(m, encoding="utf-8").read().replace(good, swapped)
    with io.open(m, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and "winner sentence" in out,
        "a swapped winner sentence must be named, got: %s" % out[:300])

    # L8 -- a number written as a string must be named, not traceback
    j, m = fresh_case()
    d = load(j)
    d["shelves"][0]["extra_pp"] = "0.2"
    dump(j, d)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and "non-numeric" in out and "Traceback" not in out,
        "a stringified number must be a named failure, got: %s" % out[:300])

    # L9 -- the ticket cash written as a string must also be named, not crash
    j, m = fresh_case()
    d = load(j)
    d["ruler"]["ticket_cash_cny"] = "565245.9"
    dump(j, d)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and "not a number" in out and "Traceback" not in out,
        "a stringified ticket must be a named failure, got: %s" % out[:300])

    # L10 -- content hash no longer describes the face
    j, m = fresh_case()
    d = load(j)
    d["content_sha256"] = "0" * 64
    dump(j, d)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and "content_sha256" in out,
        "a stale content hash must be named, got: %s" % out[:300])

    # L11 -- a shelf that the parent does not have must not be silently accepted
    j, m = fresh_case()
    d = load(j)
    ghost = json.loads(json.dumps(d["shelves"][0]))
    ghost["code"] = "999999"
    d["shelves"].append(ghost)
    dump(j, d)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and "not in the parent face" in out,
        "an invented shelf must be named, got: %s" % out[:300])

    # L12 -- a missing published file is STALE with a name, not a crash
    rc, out = capture(lambda: M.check(os.path.join(tmp, "nope.json"), m))
    leg(rc == 3 and "STALE" in out and "Traceback" not in out,
        "a missing face must be STALE, got: %s" % out[:300])

    # L13 -- a doubled percent left in the page (a %-format string that never ran)
    j, m = fresh_case()
    text = io.open(m, encoding="utf-8").read() + "\n直方图 100%% 完\n"
    with io.open(m, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    rc, out = capture(lambda: M.check(j, m))
    leg(rc == 3 and "literal %%" in out,
        "a literal %% in the page must be named, got: %s" % out[:300])

    # L14 -- this whole exercise must not have touched the published bytes
    after = {p: sha(p) for p in before}
    leg(before == after, "the published faces were modified by the negative control")

    shutil.rmtree(tmp, ignore_errors=True)

    if errs:
        for e in errs:
            print("NEGATIVE FAIL:", e)
        print("NEGATIVE %d/%d PASSED" % (legs[0] - len(errs), legs[0]))
        return 1
    print("NEGATIVE OK %d/%d PASS" % (legs[0], legs[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
