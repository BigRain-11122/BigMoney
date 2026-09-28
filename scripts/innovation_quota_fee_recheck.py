"""T-2026-09-28-112 fee-after recheck -- REPO-CALENDAR-P1 eligible cells.

Frozen condition (research/INNOVATION_QUOTA_W1_PREREG.md s3, frozen @dd62920e):
"若判正入册前补费后复核" -- before any STRATEGY_LIBRARY intake, the 3
G2-eligible calendar-switch cells must clear the cost face. This recheck
imports the frozen W1 engine (zero re-implementation) and applies a
uniform per-placement fee haircut at episode starts, sweeping conservative
stress bounds.

Fee model (declared pre-run, zero fee-table fact-face dependency):
  * one placement = one swing_engine episode (a repo placement decision);
    fee = b x principal, haircut applied to the episode's first accrual
    day (ser[lo] -= b). Passive daily roll = one episode per trading day
    (same mechanism, disclosed informational only).
  * sweep bounds (bp of principal per placement): 0.5 / 1.0 / 2.0 / 5.0.
  * flip bound b* = the highest swept bound a cell clears, refined one
    grid step below the first failure.
  * FROZEN PASS LINE: intake PASS iff b* >= 1.0 bp uniform per placement.
    1bp is deliberately conservative vs the exchange repo fee band for
    GC001-GC028 (order 0.036-0.84 bp per placement per 10-wan-yuan lot,
    prereg s3 froze the claim "按标准费率极低"); the verdict NEVER depends
    on the exact schedule -- the decision-relevant number is b* itself:
    any actual fee below b* passes.
  * Verdict criterion = cell sharpe_after_fee >= frozen skill_line_v2
    25.006 (read programmatically from the P1 receipt gates face -- zero
    hand-copy). DSR/PBO/nulls/D6 are NOT re-derived: the judged verdict
    stands; this is the cost-face recheck only (ledger +0, attrition +0).
  * passive-after-fee pickup face is informational and churn-biased at
    uniform b (daily roll pays ~37x more placements/year than calendar
    switch) -- disclosed in-receipt; the frozen skill_line passive_term
    was pre-fee and does not move.

Products: results/innovation_quota/FEE-RECHECK-P1.json (top-level
evidence_cutoff + cutoff_meta per C2 law).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed refusal)
"""
import argparse
import json
import os
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # cutoff_meta (C2 law)
from innovation_quota_w1 import (CELLS, EVIDENCE_CUTOFF, _cell_stats,
                                 cell_window, load_repo_panel, passive_roll,
                                 run_cell, sharpe_of)

OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
P1_RECEIPT = os.path.join(OUT_DIR, "REPO-CALENDAR-P1.json")
OUT_JSON = os.path.join(OUT_DIR, "FEE-RECHECK-P1.json")

ELIGIBLE = ["CAL-SWITCH-GC014", "QW5-SWITCH-GC014", "CAL-SWITCH-GC028"]
GC007_EXCLUDED = ("CAL-SWITCH-GC007 judged-negative (19.3526 < mu_null "
                  "22.3153); closed per RANDOM_LARGE_SAMPLE_LAW s5 -- "
                  "not part of this intake")
SWEEP_BP = [0.5, 1.0, 2.0, 5.0]
PASS_LINE_BP = 1.0                              # frozen pre-run


def _refuse(msg):
    print("[fee-recheck] FAIL-CLOSED: %s" % msg)
    return 2


def apply_fee(ser, episodes, b):
    """Per-placement fee haircut: episode start day return -= b (fraction
    of principal). Exactly one haircut per episode, deterministic."""
    out = np.array(ser, dtype=float, copy=True)
    for lo, _hi, _rate in episodes:
        out[lo] -= b
    return out


def cell_flip_bound(ser, episodes, line, sweep=SWEEP_BP):
    """b* = highest swept bound with sharpe_after_fee >= line; refine one
    grid step below first failure. Returns (b_star_bp, per_bound)."""
    per_bound = {}
    b_star = 0.0
    prev = 0.0
    for bp in sweep:
        b = bp / 10000.0
        s = sharpe_of(apply_fee(ser, episodes, b))
        ok = bool(s >= line)
        per_bound["%gbp" % bp] = {"sharpe_after_fee": round(s, 4),
                                  "clears_line": ok}
        if ok:
            b_star = float(bp)
            prev = float(bp)
        else:
            if b_star > 0.0:
                # refine: midpoint of the passing/failing bracket
                b_star = round((prev + bp) / 2.0, 2)
            break
    else:
        b_star = float(sweep[-1])                # cleared everything
    return b_star, per_bound


def _read_frozen_line():
    """Frozen skill_line_v2 from the P1 receipt gates face (no hand-copy)."""
    with open(P1_RECEIPT, encoding="utf-8") as fh:
        r = json.load(fh)
    g = r["gates"][ELIGIBLE[0]]["g1_prime_v2"]
    return float(g["skill_line"]["line"]), int(g["skill_line"]["n_eff"]), g


def cmd_run():
    P, err = load_repo_panel()
    if P is None:
        return _refuse("panel gates refused: %s" % err)
    try:
        line, n_eff, sl_face = _read_frozen_line()
    except (OSError, KeyError, ValueError) as e:
        return _refuse("frozen line unreadable from P1 receipt: %s" % e)

    pas_ser, pas_eps = passive_roll(P)
    cells_face = {}
    for c in CELLS:
        name = c["name"]
        ser, eps, _win = run_cell(P, c)
        face = {"sharpe_pre_fee": round(sharpe_of(ser), 4),
                "n_episodes": len(eps),
                "ann_ret_pre_fee": _cell_stats(ser)["ann_ret_natural_day"]}
        if name not in ELIGIBLE:
            face["in_this_recheck"] = False
            face["note"] = GC007_EXCLUDED if name == "CAL-SWITCH-GC007" else ""
            cells_face[name] = face
            continue
        b_star, per_bound = cell_flip_bound(ser, eps, line)
        b1 = 1.0 / 10000.0
        s_after_1bp = sharpe_of(apply_fee(ser, eps, b1))
        face.update({"in_this_recheck": True,
                     "sweep": per_bound,
                     "flip_bound_bp": b_star,
                     "sharpe_after_fee_1bp": round(s_after_1bp, 4),
                     "ann_ret_after_fee_1bp":
                         _cell_stats(apply_fee(ser, eps, b1))
                         ["ann_ret_natural_day"],
                     "fee_recheck_pass": bool(b_star >= PASS_LINE_BP)})
        cells_face[name] = face

    # informational passive face (churn-biased at uniform b, disclosed)
    pas_after = sharpe_of(apply_fee(pas_ser, pas_eps, 1.0 / 10000.0))
    passive_face = {"sharpe_pre_fee": round(sharpe_of(pas_ser), 4),
                    "n_episodes": len(pas_eps),
                    "sharpe_after_fee_1bp": round(pas_after, 4),
                    "churn_bias_note": "uniform-b passive face is "
                    "informational only: daily roll pays one placement per "
                    "trading day (~37x the calendar-switch placement "
                    "count/year), so uniform b over-penalizes passive; the "
                    "frozen skill_line passive_term is pre-fee and does "
                    "not move"}

    overall = all(cells_face[n]["fee_recheck_pass"] for n in ELIGIBLE)
    product = {
        "batch": "REPO_CALENDAR_P1_FEE_RECHECK",
        "kind": "intake-fee-recheck (T-2026-09-28-112 step 1; NOT a judged "
                "batch: ledger +0, gate_attrition +0, DSR/PBO/nulls/D6 "
                "stand as judged in REPO-CALENDAR-P1.json)",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "ticket": "T-2026-09-28-112 (claimed bm-c r183)",
        "prereg": "research/INNOVATION_QUOTA_W1_PREREG.md s3 frozen "
                  "cost clause + s7 receipt (@dd62920e freeze)",
        "skill_line_frozen": {"line": line, "n_eff": n_eff,
                              "source": "REPO-CALENDAR-P1.json gates face "
                                        "(programmatic read, zero hand-copy)",
                              "passive_term": sl_face["skill_line"]
                              ["passive_term"] if isinstance(
                                  sl_face, dict) and "passive_term" in
                                  sl_face.get("skill_line", {}) else None},
        "fee_model": {"unit": "per-placement fraction of principal, "
                              "haircut at episode start day",
                      "sweep_bp": SWEEP_BP,
                      "pass_line_bp": PASS_LINE_BP,
                      "pass_line_note": "frozen pre-run: intake PASS iff "
                                        "flip bound b* >= 1.0bp uniform per "
                                        "placement; verdict independent of "
                                        "the exact exchange fee schedule "
                                        "(any actual fee below b* passes)",
                      "schedule_band_disclosure":
                          "exchange repo fee band for GC001-GC028 believed "
                          "order 0.036-0.84bp per placement per 10-wan lot "
                          "(prereg s3 froze '按标准费率极低'); if CEO face "
                          "supplies a sharper table the b* recheck reruns "
                          "trivially -- no fact-face dependency"},
        "passive_face_informational": passive_face,
        "cells": cells_face,
        "intake_verdict": {"fee_recheck_pass_all": bool(overall),
                           "eligible_cells": ELIGIBLE,
                           "next": "STRATEGY_LIBRARY cash-leg sleeve "
                                   "CANDIDATE intake (this ticket step 2); "
                                   "CE admission face is a separate walk "
                                   "(intake != activation)"},
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    print("[fee-recheck] cells: " + ", ".join(
        "%s b*=%gbp pass=%s" % (n, cells_face[n]["flip_bound_bp"],
                                cells_face[n]["fee_recheck_pass"])
        for n in ELIGIBLE))
    print("[fee-recheck] overall intake fee-recheck PASS = %s" % overall)
    print("[fee-recheck] receipt: %s" % os.path.relpath(OUT_JSON, ROOT))
    return 0


def _synth_P(n_days=60):
    """Hermetic synthetic panel-shaped dict for the real swing_engine."""
    t0 = np.datetime64("2024-01-01")
    cal = np.arange(t0, t0 + np.timedelta64(n_days * 2, "D"),
                    dtype="datetime64[D]")
    # drop weekends to mimic trading calendar
    wd = np.array([d.astype("datetime64[D]").astype(int) % 7 < 5
                   for d in cal.astype("datetime64[D]")], dtype=bool)
    cal = cal[wd]
    m = len(cal)
    rates = {"GC001": np.full(m, 2.0), "GC007": np.full(m, 3.0),
             "GC014": np.full(m, 3.2), "GC028": np.full(m, 3.4)}
    win = np.zeros(m, dtype=bool)
    win[-2:] = True                          # month-end-ish window tail
    return {"cal": cal, "rates": rates, "w_me": win, "w_qe": win,
            "w_ph": np.zeros(m, dtype=bool)}


def cmd_selftest():
    ok = [0, 0]

    def chk(name, cond):
        ok[0] += 1
        ok[1] += bool(cond)
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))

    P = _synth_P()
    cell = CELLS[1]                          # CAL-SWITCH-GC014
    ser, eps, _win = run_cell(P, cell)
    # 1. fee once per episode, exact haircut value
    b = 5.0 / 10000.0
    fed = apply_fee(ser, eps, b)
    hits = sum(1 for lo, _h, _r in eps if abs((ser[lo] - fed[lo]) - b) < 1e-15)
    chk("fee once per episode, exact value", hits == len(eps) and
        len(eps) > 0)
    # 2. sharpe non-increasing in fee over the sweep grid
    ss = [sharpe_of(apply_fee(ser, eps, bp / 10000.0)) for bp in SWEEP_BP]
    chk("sharpe monotone non-increasing across sweep",
        all(ss[i] >= ss[i + 1] - 1e-12 for i in range(len(ss) - 1)))
    # 3. passive episode count == placements with in-window accrual
    _ps, peps = passive_roll(P)
    dayn = P["cal"][-1].astype("datetime64[D]").astype(int)
    day0 = P["cal"][0].astype("datetime64[D]").astype(int) + 1
    expected = sum(1 for d in P["cal"]
                   if d.astype("datetime64[D]").astype(int) + 1 <= dayn
                   and d.astype("datetime64[D]").astype(int) >= day0 - 1)
    chk("passive placements == trading days with next-day accrual",
        len(peps) == expected)
    # 4. flip-bound + verdict logic on a constructed line
    s0 = sharpe_of(ser)
    mid = s0 * 0.97                          # a line the cell clears pre-fee
    b_star, per_bound = cell_flip_bound(ser, eps, mid)
    passing = [bp for bp in SWEEP_BP
               if per_bound["%gbp" % bp]["clears_line"]]
    chk("flip bound within swept bracket and consistent",
        (b_star >= max(passing) if passing else b_star == 0.0) and
        all(bp <= b_star + 1e-9 for bp in passing))
    # 5. frozen-line read refuses on malformed receipt
    bad = os.path.join(tempfile.mkdtemp(), "bad.json")
    with open(bad, "w", encoding="utf-8") as fh:
        json.dump({"gates": {}}, fh)
    global P1_RECEIPT
    keep = P1_RECEIPT
    P1_RECEIPT = bad
    try:
        _read_frozen_line()
        refused = False
    except (OSError, KeyError, ValueError):
        refused = True
    finally:
        P1_RECEIPT = keep
    chk("frozen-line read fail-closed on malformed receipt", refused)

    print("[fee-recheck] selftest %d/%d" % (ok[1], ok[0]))
    return 0 if ok[0] == ok[1] else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    return cmd_selftest() if a.cmd == "selftest" else cmd_run()


if __name__ == "__main__":
    sys.exit(main())
