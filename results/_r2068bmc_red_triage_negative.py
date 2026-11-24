# -*- coding: utf-8 -*-
"""Negative control for scripts/block_red_triage.py (r2068, bm-c).

The face claims three reds are not what they say.  A classifier that can only
ever say "not real" is worth nothing, so this control makes each branch fire
on an input where the *right* answer is the opposite of the live one:

  1. an empty bank (only blocked items)          -> REAL, not a reader false red
  2. a nine-day cash gap                         -> REAL, not uninformative
  3. a current cash panel under a red row        -> DRIFT, not uninformative
  4. a two-machine diff                          -> trusted, not flagged
  5. the live face's own inputs                 -> the live classes
  6. behavioural: poison the face's bar and the
     published read must go rc3 with STALE       -> the check cannot be a
                                                    re-computation of itself

Run: python results/_r2068bmc_red_triage_negative.py
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import block_red_triage as T  # noqa: E402

CASES = []


def leg(name, fn):
    try:
        fn()
        CASES.append((name, True, ""))
    except AssertionError as e:
        CASES.append((name, False, str(e) or "assert"))


def _ctx(bank=None, pend=0, diff=None, cash=None):
    return {"bank": bank or {"items": []}, "queue_pending": pend,
            "diff": diff or {}, "cash": cash or {}}


def _cash(**kw):
    base = {"modal_bar": "2026-11-20", "files": 11, "hist": {}, "allowance_days": 4,
            "printed_lag": 5, "honest_lag": 4, "horizon": "2026-11-24", "sessions": 2}
    base.update(kw)
    return base


ROW_SUPPLY = {"id": "W1_supply", "status": "RED", "detail": "no open question left"}
ROW_CASH = {"id": "D6_cash_rate", "status": "RED", "detail": "5d behind"}
ROW_INGEST = {"id": "G6_ingest", "status": "RED", "detail": "self-diff"}


# 1. an empty bank must stay RED and be called REAL ---------------------------------------
def c_empty_bank_is_real():
    r = T.triage_row(ROW_SUPPLY, {}, _ctx(bank={"items": [{"status": "blocked"}] * 2}))
    assert r["class"] == "REAL", r["class"]
    assert r["true_state"]["row_would_be"] == "RED", r["true_state"]


# 2. a genuinely late panel must not hide behind "uninformative" --------------------------
def c_nine_day_gap_is_real():
    r = T.triage_row(ROW_CASH, {}, _ctx(cash=_cash(modal_bar="2026-11-13", printed_lag=12,
                                                   honest_lag=11, sessions=7)))
    assert r["class"] == "REAL", r["class"]


# 3. a current panel under a red row is drift, not a data problem -------------------------
def c_current_panel_is_drift():
    r = T.triage_row(ROW_CASH, {}, _ctx(cash=_cash(modal_bar="2026-11-24", printed_lag=1,
                                                   honest_lag=0, sessions=0)))
    assert r["class"] == "DRIFT", r["class"]


# 4. a real two-machine handover must be trusted -----------------------------------------
def c_two_machine_diff_trusted():
    lanes = {"l%d" % i: {"file_delta": 0, "byte_delta": 0,
                         "theirs": {"modified": "T"}, "ours": {"modified": "T"}} for i in range(3)}
    lanes["l0"] = {"file_delta": 1, "byte_delta": 4,
                   "theirs": {"modified": "T"}, "ours": {"modified": "U"}}
    d = {"theirs": {"machine": "bm-a", "generated": "G1"},
         "ours": {"machine": "bm-c", "generated": "G2"}, "lanes": lanes, "verdict": "GAPS"}
    r = T.triage_row(ROW_INGEST, {}, _ctx(diff=T.ingest_sides_distinct(d)))
    assert r["class"] in ("REAL", "UNCLASSIFIED") or r["true_state"]["handover_measured"] is True
    assert T.ingest_sides_distinct(d)["trustworthy"] is True


# 5. the live inputs must reproduce the live classes ------------------------------------
def c_live_classes():
    p = json.load(io.open(T.OUT, encoding="utf-8")) if os.path.exists(T.OUT) else None
    if p is None:
        raise AssertionError("face missing -- run the script first")
    got = {r["id"]: r["class"] for r in p["reds"]}
    want = {"D6_cash_rate": "UNINFORMATIVE", "W1_supply": "FALSE_RED_READER",
            "G6_ingest": "FALSE_GREEN_PRODUCER"}
    assert got == want, (got, want)
    assert p["real_gaps"] == ["D6_cash_rate"], p["real_gaps"]
    assert p["false_reds"] == ["W1_supply"], p["false_reds"]
    assert p["board"]["line_state_honest"] == "BUSY", p["board"]


# 6. behavioural: the published read must go STALE when its inputs move ------------------
def c_check_goes_stale():
    path = T.OUT
    if not os.path.exists(path):
        raise AssertionError("face missing -- run the script first")
    raw = open(path, "rb").read()
    try:
        p = json.loads(raw.decode("utf-8"))
        p["cash_panel"]["modal_bar"] = "2020-01-01"     # the panel moved under the face
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
        rc = T.check_only()
        assert rc == 3, "check must refuse a moved input, rc=%s" % rc
    finally:
        with open(path, "wb") as f:
            f.write(raw)
    # and the honest read is clean again byte-for-byte
    assert open(path, "rb").read() == raw
    assert T.check_only() == 0


def c_check_clean_after_restore():
    assert T.check_only() == 0


for n, f in [
    ("an empty bank stays a real red", c_empty_bank_is_real),
    ("a nine-day cash gap stays real", c_nine_day_gap_is_real),
    ("a current panel under a red row is drift", c_current_panel_is_drift),
    ("a real two-machine handover is trusted", c_two_machine_diff_trusted),
    ("the live face reproduces the live classes", c_live_classes),
    ("poisoning the face makes the check STALE", c_check_goes_stale),
    ("the restored face checks clean", c_check_clean_after_restore),
]:
    leg(n, f)

bad = [c for c in CASES if not c[1]]
for n, ok, why in CASES:
    print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", n, "" if ok else " | " + why))
print("%d/%d negative legs pass" % (len(CASES) - len(bad), len(CASES)))
sys.exit(0 if not bad else 1)
