# r450 bm-b W8 freeze-window D6 cells probe (COV-SHRINK-AB-P1).
#
# Adjudicates the D6 same-family correlation admission faces BEFORE the
# burn, on the x1 net convention, using the runner's own accrual
# machinery (scripts/innovation_quota_w8.py derive_anchors/arm_series --
# single implementation, zero drift; the runner later carries the
# frozen d6 block verbatim, no re-computation at burn, W6 precedent).
#
# Faces (prereg sec.1 protocol, W7 mirror):
#   A  batch-internal  A vs B arms -- expected ~1 (variant face of the
#                      same pipeline, both cells burn; non-rejectable by
#                      design, disclosed)
#   B  vs T33 four in-book rotation cells (merge clause at |corr|>=0.7)
#   C  vs registered six (structural containment: the arms are blends OF
#                      the corps members; disclose-only, t27 blend
#                      precedent)
#   D  vs B_MAXDIV production static-assembly face (re-derived from the
#                      same t27 machinery, IS-segment weights on the
#                      same matrix) -- the UPGRADE-TARGET confirmation
#                      face: the family hypothesis IS the production
#                      assembly's cov-face upgrade (zoo #89 route:
#                      "same pipeline"), so the reject line does not
#                      apply to this face; pre-declared at freeze
#                      BEFORE the number (structural same-assembly
#                      relationship), disclosed.
#
# No performance metric of the batch cells is persisted (D6 admission
# protocol only). Writes results/_r450bmb_w8_d6_probe_facts.json.
import io
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "results"))

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ce_transfer import COST_X1_RATE            # x1 = 13.041bp/side
from iv6_portfolio import _init_worker, member_run_iv6
from parallel_runner import run_cells_parallel, worker_cap
from t27_blend_tournament import (FROZEN_ROSTER, daily_ret_matrix,
                                  mdp_weights)
import innovation_quota_w8 as W8                # the runner (single source)
from live.paper import OOS_START

OUT = os.path.join(ROOT, "results", "_r450bmb_w8_d6_probe_facts.json")
D6_REJECT = 0.7
T33_CELLS_PATH = os.path.join(ROOT, "results", "t33_attack_wave_cells.jsonl")
T33_GATES_PATH = os.path.join(ROOT, "results", "t33_attack_wave_gates.json")
T33_ROT_CELLS = ["slope_r2_rotation_25_top3_r8",
                 "dual_momentum_etf_20_60_top3",
                 "rs_rotation_20", "composite_top5"]


def _pearson(a: pd.Series, b: pd.Series) -> float:
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < 20:
        return float("nan")
    c = np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]
    return float(c) if np.isfinite(c) else float("nan")


def _panel_calendar_union(cutoff: str) -> pd.DatetimeIndex:
    from live.paper import load_core
    ps = pd.Timestamp(cutoff)
    all_idx = set()
    for df in load_core().values():
        all_idx.update(df.index[df.index <= ps])
    return pd.DatetimeIndex(sorted(all_idx))


def run() -> int:
    t0 = time.time()
    # ---- x1 sleeves only (D6 = x1 net convention), t27 verbatim shape
    jobs = [(f"{tid}|None", member_run_iv6, (tid, None))
            for tid in FROZEN_ROSTER]
    res = run_cells_parallel(jobs, workers=min(worker_cap(), 12),
                             desc="w8-d6-sleeves", initializer=_init_worker)
    res.pop("__workers__", None)
    sleeves = {}
    for tid in FROZEN_ROSTER:
        r1 = res[f"{tid}|None"]
        r1["eq_s"] = pd.Series(r1["eq"], index=pd.to_datetime(r1["dates"]))
        sleeves[tid] = {"x1": r1}
    cutoff = max(sleeves[t]["x1"]["cutoff"] for t in FROZEN_ROSTER)
    R1 = daily_ret_matrix(sleeves, "x1")
    print(f"matrix {R1.shape} {R1.index[0].date()}..{R1.index[-1].date()} "
          f"cutoff {cutoff} ({time.time() - t0:.0f}s)", flush=True)

    # ---- arm accrual via the runner machinery (single source)
    rows = W8.derive_anchors(R1)
    netA, faceA = W8.arm_series(R1, rows, "A", COST_X1_RATE)
    netB, faceB = W8.arm_series(R1, rows, "B", COST_X1_RATE)
    lo = pd.Timestamp(faceA["lo_date"])
    print(f"accrual lo {faceA['lo_date']} singular_carried_A="
          f"{faceA['n_singular_carried']} "
          f"({time.time() - t0:.0f}s)", flush=True)

    d6 = {"batch_internal_A_vs_B": round(abs(_pearson(netA, netB)), 4),
          "batch_internal_note": "variant face of the same frozen "
                                 "pipeline (sample vs LW-shrunk cov) -- "
                                 "expected near 1, both cells burn, "
                                 "non-rejectable by design (W7 "
                                 "bottom-vs-dual precedent)",
          "vs_t33_cells": {}, "merge_clause_applied": [],
          "vs_registered_six": {"max_abs_corr": None, "argmax": None},
          "vs_b_maxdiv_production_face": None,
          "production_face_note":
              "B_MAXDIV production static assembly re-derived from the "
              "same t27 machinery (IS-segment weights on the same x1 "
              "matrix, t27 evaluation-frame caliber); the family IS the "
              "production assembly's cov-face upgrade per zoo #89 "
              "adoption route -- upgrade-target confirmation face, "
              "reject line structurally non-applicable (pre-declared at "
              "freeze), disclosed"}

    # B face: vs T33 in-book rotation cells (merge clause at 0.7)
    t33_idx = _panel_calendar_union("2026-09-24")     # T33 own cutoff face
    t33_rows = {}
    with open(T33_CELLS_PATH, encoding="utf-8") as fh:
        for ln in fh.read().splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("status") == "ok" and r.get("face") == "base" \
                    and r.get("cand") in T33_ROT_CELLS and "rets" in r:
                t33_rows[r["cand"]] = pd.Series(
                    r["rets"], index=t33_idx[1:len(r["rets"]) + 1])
    for cid in T33_ROT_CELLS:
        if cid not in t33_rows:
            d6["vs_t33_cells"][cid] = None
            continue
        ca = round(abs(_pearson(netA, t33_rows[cid])), 4)
        cb = round(abs(_pearson(netB, t33_rows[cid])), 4)
        d6["vs_t33_cells"][cid] = {"A": ca, "B": cb}
        if max(ca, cb) >= D6_REJECT:
            d6["merge_clause_applied"].append(cid)

    # C face: vs registered six (structural containment, disclose-only)
    try:
        gates = json.load(open(T33_GATES_PATH, encoding="utf-8"))
        reg_rets = gates.get("registered_rets", {})
        my_idx = R1.index
        best = (0.0, None)
        for rid, rl in reg_rets.items():
            k = min(len(rl), len(my_idx) - 1)
            rs_ = pd.Series(rl[:k], index=my_idx[1:k + 1])
            ca = abs(_pearson(netA, rs_))
            cb = abs(_pearson(netB, rs_))
            c = max(ca if np.isfinite(ca) else 0.0,
                    cb if np.isfinite(cb) else 0.0)
            if c > best[0]:
                best = (c, rid)
        d6["vs_registered_six"] = {"max_abs_corr": round(best[0], 4),
                                   "argmax": best[1],
                                   "note": "arms are blends OF the corps "
                                           "members -- structural "
                                           "containment, disclose-only "
                                           "(t27 blend precedent)"}
    except FileNotFoundError:
        d6["vs_registered_six"] = {"max_abs_corr": None, "argmax": None,
                                   "note": "t33 gates json absent"}

    # D face: vs B_MAXDIV production static assembly (upgrade target)
    w_prod = mdp_weights(R1[R1.index < pd.Timestamp(OOS_START)])
    wv = np.array([w_prod["weights"][c] for c in R1.columns], dtype=float)
    prod_gross = pd.Series((R1.to_numpy() * wv).sum(axis=1),
                           index=R1.index)
    prod_face = prod_gross[prod_gross.index >= lo]
    d6["vs_b_maxdiv_production_face"] = {
        "A": round(abs(_pearson(netA, prod_face)), 4),
        "B": round(abs(_pearson(netB, prod_face)), 4),
        "production_weights_sha_note": "t27 B_MAXDIV registered assembly "
                                       "sha 9b112d51583aeeb7 (SPM v1 "
                                       "28-member face)"}

    facts = {
        "probe": "W8 COV-SHRINK-AB-P1 freeze-window D6 cells probe",
        "machine": "bm-b", "round": "r450",
        "evidence_cutoff": str(R1.index[-1].date()),
        "panel": {"roster_n": len(FROZEN_ROSTER),
                  "matrix_shape": list(R1.shape),
                  "matrix_first": str(R1.index[0].date()),
                  "matrix_last": str(R1.index[-1].date()),
                  "accrual_lo": faceA["lo_date"],
                  "singular_carried_A": faceA["n_singular_carried"],
                  "n_weight_events_A": faceA["n_weight_events"],
                  "n_weight_events_B": faceB["n_weight_events"]},
        "d6_cells_face": d6,
        "cost_face": "ce_transfer.COST_X1_RATE imported (13.041bp/side); "
                     "arm series = x1 net convention via runner "
                     "arm_series (transition costs on, initial "
                     "deployment included), no metric persisted",
        "merge_clause_threshold": D6_REJECT,
        "machinery": "scripts/innovation_quota_w8.py derive_anchors + "
                     "arm_series (single implementation; the runner "
                     "carries this d6 block frozen verbatim at burn)",
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print("batch internal A-vs-B |corr| =",
          d6["batch_internal_A_vs_B"])
    print("vs T33 cells:", d6["vs_t33_cells"])
    print("merge clause applied:", d6["merge_clause_applied"] or "NONE")
    print("vs registered six max |corr| =",
          d6["vs_registered_six"]["max_abs_corr"], "argmax",
          d6["vs_registered_six"]["argmax"])
    print("vs B_MAXDIV production face:",
          d6["vs_b_maxdiv_production_face"])
    return 0


if __name__ == "__main__":
    sys.exit(run())
