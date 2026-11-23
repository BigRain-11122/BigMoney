#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for scripts/idx_fut_carry_hedge_beta_lots.py

Every leg writes its own bytes to a scratch path and calls the face's REAL check().
No leg inherits the previous leg's file (r1999 lesson: a mutation that survives between
legs makes the harness green for the wrong reason).

Two families are proved here:
  * the drift/defect split -- a moved cutoff or a moved input digest must say STALE,
    a number that contradicts its own inputs must NOT say STALE;
  * the two arithmetic rules the page leans on -- whole lots are never zero, and a
    widened estimation window cannot be read as "no effect" when the lots disagree.
"""

import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_carry_hedge_beta_lots as F  # noqa: E402

LEGS = []


def ok(name, cond, why=""):
    LEGS.append((name, bool(cond), why))


def with_face(mutate):
    """Copy the real face to a scratch path, mutate it, run the real check()."""
    real = F.OUT_PATH
    if not os.path.exists(real):
        return 2, "STALE face missing (no face to mutate)"
    tmpdir = tempfile.mkdtemp(prefix="beta_lots_neg_")
    try:
        scratch = os.path.join(tmpdir, "face.json")
        shutil.copy2(real, scratch)
        obj = json.load(io.open(scratch, "r", encoding="utf-8"))
        mutate(obj)
        with io.open(scratch, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        saved = F.OUT_PATH
        F.OUT_PATH = scratch
        try:
            buf = io.StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                rc = F.check()
            finally:
                sys.stdout = old
            return rc, buf.getvalue().strip()
        finally:
            F.OUT_PATH = saved
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    # ---- rule 1: a lot is never zero, however small beta gets
    ok("ceil of a tiny beta is one lot", F.whole_lots(0.02, "ceil") == 1)
    ok("round of a tiny beta is one lot", F.whole_lots(0.02, "round") == 1)
    ok("beta None is not a lot count", F.whole_lots(None, "ceil") is None)

    # ---- rule 2: the verdict must react to a real spread, and stay quiet otherwise
    stable = F.rolling_row([1.2, 1.3, 1.4], 2)
    ok("a tight window set names exactly one lot count", stable["ceil_lots_seen"] == [2])
    wide = F.rolling_row([0.9, 1.6], 2)
    ok("a wide window set names both boundaries", wide["ceil_lots_seen"] == [1, 2])
    fake = {"X_vs_Y": {"state": "ok", "rolling": {"242": wide},
                       "cost_of_indivisibility": {"pnl_difference_cny_vs_exact": -6000.0}}}
    ok("the verdict is not STABLE when the rows disagree",
       F.verdict_of(fake) != "INTEGER_HEDGE_IS_STABLE_ACROSS_ESTIMATION_WINDOWS")
    fake2 = {"X_vs_Y": {"state": "ok", "rolling": {"242": stable},
                        "cost_of_indivisibility": {"pnl_difference_cny_vs_exact": 0.0}}}
    ok("the verdict IS STABLE when the rows agree",
       F.verdict_of(fake2) == "INTEGER_HEDGE_IS_STABLE_ACROSS_ESTIMATION_WINDOWS")

    # ---- the page must carry the sign warning, otherwise a reader reads +47k as a saving
    face = json.load(io.open(F.OUT_PATH, "r", encoding="utf-8"))
    any_cost = None
    for key, body in (face.get("arms") or {}).items():
        if isinstance(body, dict) and body.get("cost_of_indivisibility"):
            any_cost = body["cost_of_indivisibility"]
            break
    ok("the cost block explains its own sign",
       bool(any_cost) and "bet, not a saving" in (any_cost.get("why_the_sign_is_what_it_is") or ""))
    doc = io.open(F.DOC_PATH, "r", encoding="utf-8").read()
    ok("the page repeats the sign warning in prose", "Read the sign before the number" in doc)
    ok("the page prints its own generation stamp", "generated 20" in doc)
    ok("the page names its evidence cutoff", "evidence_cutoff" in doc)

    # ---- drift vs defect: five mutations, each asserted on the wording as well as the rc
    rc, _ = with_face(lambda o: None)
    ok("an untouched face passes", rc == 0, "rc=%s" % rc)

    def move_cutoff(o):
        o["evidence_cutoff"] = "1990-01-01"
    rc, out = with_face(move_cutoff)
    ok("a moved cutoff is STALE", rc == 3 and "STALE" in out, "rc=%s %s" % (rc, out[:60]))

    def move_inputs(o):
        o["inputs"] = {"fake": "digest"}
    rc, out = with_face(move_inputs)
    ok("a moved input digest is STALE", rc == 3 and "STALE" in out, "rc=%s" % rc)

    def flip_verdict(o):
        o["verdict"] = "EVERYTHING_IS_FINE"
    rc, out = with_face(flip_verdict)
    ok("a hand-flipped verdict fails and does not say STALE",
       rc == 3 and "STALE" not in out, "rc=%s %s" % (rc, out[:60]))

    def break_beta(o):
        key = sorted((o.get("arms") or {}).keys())[0]
        o["arms"][key]["beta_full_sample"] = 99.0
    rc, out = with_face(break_beta)
    ok("a number that contradicts its inputs fails and does not say STALE",
       rc == 3 and "STALE" not in out, "rc=%s %s" % (rc, out[:60]))

    def drop_face(o):
        o.pop("arms", None)
    rc, out = with_face(drop_face)
    ok("a face missing its own table fails", rc == 3, "rc=%s" % rc)

    failed = [leg for leg in LEGS if not leg[1]]
    for name, good, why in LEGS:
        print("%-68s %s %s" % (name, "PASS" if good else "FAIL", why))
    print("negative control: %d/%d" % (len(LEGS) - len(failed), len(LEGS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
