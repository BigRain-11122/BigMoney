#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for scripts/idx_fut_carry_ladder_years.py

Every control breaks one published number in a copy of the face and asserts that
`check` notices -- and, just as important, that the notice is the RIGHT WORD: a broken
number is CHECK FAILED (which must never contain the word STALE), while upstream drift
is STALE.  A face whose check cannot tell those apart teaches the chain to ignore it
(r1850/r1934: the run_leg hook only pays for a rewrite when the text says STALE).

    python results/_r2107bmc_ladder_years_negative.py
"""
import copy
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_carry_ladder_years as M  # noqa: E402

FACE = M.OUT
TMP = os.path.join(HERE, "_r2107bmc_negative_face.json")


def load():
    with io.open(FACE, encoding="utf-8") as f:
        return json.load(f)


def run_check(face, probe_upstream=False, patch=None):
    if patch:
        face = copy.deepcopy(face)
        patch(face)
    with io.open(TMP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    rc, lines = M.check(TMP, probe_upstream=probe_upstream)
    return rc, "\n".join(lines)


def main():
    if not os.path.exists(FACE):
        print("CONTROL FAILED: face missing, cannot arm the controls")
        return 1
    base = load()
    engine = base["engine_rung"]
    results = []

    def record(name, cond, detail=""):
        results.append((name, bool(cond), detail))

    # 0 the untampered face must pass
    rc, txt = run_check(base)
    record("real face passes", rc == 0 and M.V_OK in txt, "rc=%d" % rc)

    # 1 one published year return moved
    def p1(f):
        f["measured"]["rungs"][engine]["years"]["2025"]["return_pct"] += 1.0
    rc, txt = run_check(base, patch=p1)
    record("year return tampered", rc == M.RC_FAIL and "STALE" not in txt.split(":")[0], txt[:90])

    # 2 a year row deleted (its bars are then missing from the day count)
    def p2(f):
        del f["measured"]["rungs"][engine]["years"]["2024"]
    rc, txt = run_check(base, patch=p2)
    record("year row deleted", rc == M.RC_FAIL and "STALE" not in txt.split(":")[0], txt[:90])

    # 3 the judgment token flipped
    def p3(f):
        f["judgment"]["year_concentration"] = M.V_ONE
    rc, txt = run_check(base, patch=p3)
    record("judgment flipped", rc == M.RC_FAIL and "STALE" not in txt.split(":")[0], txt[:90])

    # 4 money column moved by more than the published precision
    def p4(f):
        f["measured"]["rungs"][engine]["years"]["2026"]["money_cny"] += 5000.0
    rc, txt = run_check(base, patch=p4)
    record("money tampered", rc == M.RC_FAIL and "STALE" not in txt.split(":")[0], txt[:90])

    # 5 the stored loss-year list disagrees with the year table
    def p5(f):
        f["measured"]["rungs"][engine]["concentration"]["negative_years"] = ["2023"]
    rc, txt = run_check(base, patch=p5)
    record("loss list tampered", rc == M.RC_FAIL and "STALE" not in txt.split(":")[0], txt[:90])

    # 6 upstream drift is STALE, and that word is present
    def p6(f):
        f["inputs"]["lattice"]["sha256"] = "0" * 64
    rc, txt = run_check(base, probe_upstream=True, patch=p6)
    record("upstream digest moved -> STALE", rc == M.RC_STALE and "STALE" in txt, txt[:90])

    # 7 the concentration reading is not vacuous on the real face
    c = base["measured"]["rungs"][engine]["concentration"]
    record("ex-best cost is positive", c["best_year_cost_pp"] > 0.0,
           "%.3f pp" % c["best_year_cost_pp"])
    record("ex-best CAGR below full", c["cagr_ex_best_pct"] < c["cagr_pct"],
           "%.3f < %.3f" % (c["cagr_ex_best_pct"], c["cagr_pct"]))

    # 8 the sibling face's published number is not silently reproduced here
    cf = base.get("cross_face") or {}
    record("cross-face gap is disclosed", cf.get("published_ann_pct") is not None
           and cf.get("gap_pp") is not None, json.dumps(cf.get("gap_pp")))

    bad = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(("  ok   %-32s %s" if ok else "  FAIL %-32s %s") % (name, detail))
    try:
        os.remove(TMP)
    except OSError:
        pass
    if bad:
        print("CONTROLS FAILED %d/%d" % (len(bad), len(results)))
        return 1
    print("ALL_CONTROLS_PASS %d/%d" % (len(results), len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
