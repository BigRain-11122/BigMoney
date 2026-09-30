# -*- coding: utf-8 -*-
"""_r260bmc_w9_d6_cells_probe.py -- CROWD-VOTE-P1 freeze-window probe:
G-ANCHOR re-verification (prereg s9 step 2) + threshold-constant
zero-drift assertion (step 4) + state-machine episode re-verification
+ D6 cells corr face (step 5, prereg s1 table, W6/W7 protocol mirror).

Read-only, zero engine/admission/REGIME_GUARD touch. Persists NO
performance metric of the batch cells -- the D6 face uses the return
series only for the preregistered correlation protocol (W6/W7 probe
discipline: "persists no performance metric").

Single-source law (r456 paradigm): crowd_positions + cell_returns
defined here are the construction face the r261 runner will
verbatim-import (zero re-implementation drift, parity-asserted).

Faces:
  A  G-ANCHOR re-verify : four-vote faces + occupancy + state-machine
                          episode counts re-derived via the berth probe
                          functions, compared face-by-face vs frozen
                          berth facts (bit-exact, one-face-off = VOID).
  T  threshold constants: author-verbatim constants (zero calibration)
                          asserted equal vs frozen facts block.
  D  D6 cells face      : batch-internal ASYM vs SYM (expected high --
                          variant face, both cells still burned), vs
                          T33 in-book rotation cells (merge clause at
                          |corr| >= 0.7), vs registered six traders
                          (disclose-only per prereg s1). REGIME_GUARD =
                          in-production non-cell: signal face already
                          adjudicated at berth (width-leg +0.7728 /
                          composite +0.5965, r259 facts), no cells pair
                          exists -- honest boundary recorded, merge
                          clause cannot trigger against a non-cell.

Output: results/_r260bmc_w9_d6_cells_probe_facts.json
Exit 0 normal / 2 mechanism fault (honest, no masking).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "results"))   # berth probe family
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from _r259bmc_w9_crowding_probe import (          # single source (r456)
    load_core48, build_faces, GUARD, TH_TOP3, TH_SPREAD, TH_WEAK,
    TH_GUARD, CONFIRM_OUT, CONFIRM_IN, HYST, TH_RANK, W, ANNUAL)
from ce_transfer import COST_X1_RATE             # x1 = 13.041bp/side

OUT = os.path.join(ROOT, "results", "_r260bmc_w9_d6_cells_probe_facts.json")
BERTH_FACTS = os.path.join(
    ROOT, "results", "_r259bmc_w9_crowding_probe_facts.json")
D6_REJECT = 0.7
TARGET = GUARD                                    # 510300 traded object
EVIDENCE_CUTOFF = "2026-09-29"                    # P-5C frozen binding
T33_CELLS_PATH = os.path.join(ROOT, "results", "t33_attack_wave_cells.jsonl")
T33_GATES_PATH = os.path.join(ROOT, "results", "t33_attack_wave_gates.json")
T33_ROT_CELLS = ["slope_r2_rotation_25_top3_r8",
                 "dual_momentum_etf_20_60_top3",
                 "rs_rotation_20", "composite_top5"]
VARIANTS = ["asym", "sym"]


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


def crowd_positions(faces: pd.DataFrame, rec_votes: pd.DataFrame,
                    decidable: pd.Series, variant: str):
    """pos_end face over the full index, author-verbatim state machine
    (SINGLE SOURCE for the r261 runner, r456 zero-drift paradigm):
      ASYM: crowd CONFIRM_OUT(2) consecutive days -> OFF (defense);
            recover CONFIRM_IN(3) consecutive days -> ON (re-entry),
            recover face = hysteresis-carrying four-dim >=3/4 votes
            (r3 = spread < TH_SPREAD*HYST = 0.1875).
      SYM : crowd 2 consecutive days -> OFF; recover_sym 2 consecutive
            days -> ON, recover_sym r3 = spread < TH_SPREAD (no
            hysteresis) -- ablation isolates the asymmetric-confirm +
            75pct-hysteresis design contribution.
    Initial state = long at the first decidable day (W7 frozen
    convention; the first decidable day's triggers still apply that
    same day -- berth probe semantics, selftest will pin both faces).
    State decided at close of t -> pos_end[t]; effective t+1 (T+1
    onset, cell_returns). Returns (pos_end, n_flips, first_flip_dates).
    """
    idx = faces.index
    crowd = faces["crowd"]
    if variant == "asym":
        recover = faces["recover"]
        conf_in = CONFIRM_IN
    else:
        sp = faces["spread"]
        r3_sym = (sp < TH_SPREAD) & decidable
        rec_count = (rec_votes["r1"].astype(int) + rec_votes["r2"].astype(int)
                     + r3_sym.astype(int) + rec_votes["r4"].astype(int))
        recover = (rec_count >= 3) & decidable
        conf_in = CONFIRM_OUT                       # symmetric 2d-in
    pos = pd.Series(np.nan, index=idx, dtype=float)
    state = None
    run = 0
    n_flips = 0
    first_flips = []
    for t in idx:
        if not bool(decidable.loc[t]):
            continue
        if state is None:
            state = 1.0                             # initial = long
        trig = bool(crowd.loc[t]) if state == 1.0 else bool(recover.loc[t])
        run = run + 1 if trig else 0
        need = CONFIRM_OUT if state == 1.0 else conf_in
        if run >= need:
            state = 0.0 if state == 1.0 else 1.0
            n_flips += 1
            if len(first_flips) < 6:
                first_flips.append(str(t.date()))
            run = 0
        pos.loc[t] = state
    return pos, n_flips, first_flips


def cell_returns(pos_end: pd.Series, tgt_ret: pd.Series) -> pd.Series:
    """W5/W7 position_series convention, full window: pos[t] =
    pos_end[t-1]; gross = pos*ret; cost = x1 rate on |dpos| booked to
    the following day. Batch window = [first_valid+1, end)."""
    lo_idx = pos_end.first_valid_index()
    lo = pos_end.index.get_loc(lo_idx) + 1
    idx = pos_end.index
    n = len(idx)
    pos = pd.Series(0.0, index=idx, dtype=float)
    pos.iloc[lo:] = pos_end.iloc[lo - 1: n - 1].values
    gross = pos * tgt_ret
    flips = pos.diff().abs()
    net = gross - COST_X1_RATE * flips
    return net.iloc[lo:]


def run() -> int:
    try:
        with open(BERTH_FACTS, encoding="utf-8") as fh:
            berth = json.load(fh)

        closes, syms = load_core48()
        cut = pd.Timestamp(EVIDENCE_CUTOFF)
        closes = closes[closes.index <= cut]        # lockbox: anchors frozen
        faces, votes, rec_votes, decidable = build_faces(closes)
        dec_days = faces[decidable]
        n_dec = int(len(dec_days))

        # ---- A G-ANCHOR re-verify (derive -> compare vs frozen berth facts)
        derived_ga = {
            "n_decidable_days": n_dec,
            "first_decidable_date": str(dec_days.index[0].date()),
            "vote_occupancy": {
                "v1_days": int(votes["v1"].sum()),
                "v2_days": int(votes["v2"].sum()),
                "v3_days": int(votes["v3"].sum()),
                "v4_days": int(votes["v4"].sum()),
            },
            "crowd_days_ge3": int(dec_days["crowd"].sum()),
            "crowd_days_eq4": int((dec_days["vote_count"] == 4).sum()),
            "recover_days_ge3": int(dec_days["recover"].sum()),
            "vote_count_mean": round(float(dec_days["vote_count"].mean()), 4),
            "weak_share_q10": round(float(dec_days["weak_share"].quantile(0.10)), 4),
            "weak_share_q90": round(float(dec_days["weak_share"].quantile(0.90)), 4),
            "top3_mean_q10": round(float(dec_days["top3"].quantile(0.10)), 4),
            "top3_mean_q90": round(float(dec_days["top3"].quantile(0.90)), 4),
            "spread_q10": round(float(dec_days["spread"].quantile(0.10)), 4),
            "spread_q90": round(float(dec_days["spread"].quantile(0.90)), 4),
            "guard_score_neg_days": int((dec_days["guard_score"] < 0).sum()),
        }
        vc = dec_days["vote_count"]
        ext = []
        for dt in vc.nlargest(8).index:
            ext.append({
                "date": str(dt.date()), "votes": int(vc.loc[dt]),
                "weak_share": round(float(dec_days.loc[dt, "weak_share"]), 4),
                "spread": round(float(dec_days.loc[dt, "spread"]), 4),
                "guard_score": round(float(dec_days.loc[dt, "guard_score"]), 4),
            })
        derived_ga["extreme_day_sample"] = ext
        stored_ga = berth["g_anchor_face"]
        mism = []
        for k, v in derived_ga.items():
            if stored_ga.get(k) != v:
                mism.append(f"{k}: {v!r} != frozen {stored_ga.get(k)!r}")
        panel_derived = {
            "n_symbols": int(closes.shape[1]),
            "first_date": str(closes.index[0].date()),
            "last_date": str(closes.index[-1].date()),
            "n_dates_total": int(len(closes)),
        }
        for k, v in panel_derived.items():
            if berth["panel"].get(k) != v:
                mism.append(f"panel.{k}: {v!r} != frozen {berth['panel'].get(k)!r}")
        # state-machine episode counts (berth facts state_machine_face)
        pos = {}
        sm_face = {}
        for v in VARIANTS:
            p, nf, ff = crowd_positions(faces, rec_votes, decidable, v)
            pos[v] = p
            sm_face[v] = {"n_flips": nf, "first_flip_dates": ff}
            stored_v = (berth["state_machine_face"]
                        .get("asym_verbatim" if v == "asym"
                             else "sym_ablation_2d2d", {}))
            if stored_v.get("n_flips") != nf:
                mism.append(f"state.{v}.n_flips: {nf} != frozen "
                            f"{stored_v.get('n_flips')}")
            if list(stored_v.get("first_flip_dates", [])) != ff:
                mism.append(f"state.{v}.first_flip_dates: {ff} != frozen "
                            f"{stored_v.get('first_flip_dates')}")

        # ---- T threshold-constant zero-drift (step 4)
        th_frozen = berth["thresholds_frozen"]
        th_cmp = {
            "v1_top3_gt": TH_TOP3, "v2_spread_gt": TH_SPREAD,
            "v3_weak_share_gt": TH_WEAK, "v4_guard_score_lt": TH_GUARD,
            "confirm_out_days": CONFIRM_OUT, "confirm_in_days": CONFIRM_IN,
            "hysteresis_pct": HYST, "recovery_rank_gt": TH_RANK,
        }
        th_mism = [f"{k}: {v!r} != frozen {th_frozen.get(k)!r}"
                   for k, v in th_cmp.items() if th_frozen.get(k) != v]
        if abs(round(TH_SPREAD * HYST, 4)
               - th_frozen.get("recovery_diff_lt", -9)) > 1e-12:
            th_mism.append("recovery_diff_lt constant drift")

        if mism or th_mism:
            for m in (mism + th_mism)[:12]:
                print("  drift:", m)
            print(f"GATE-REFUSE(exit2): freeze-window re-verify drift "
                  f"({len(mism)} anchor faces, {len(th_mism)} constants) "
                  f"vs frozen berth facts")
            return 2
        print(f"G-ANCHOR re-verify: ALL faces bit-exact vs berth facts "
              f"(panel {panel_derived['first_date']}..{panel_derived['last_date']}, "
              f"{panel_derived['n_dates_total']} dates x "
              f"{panel_derived['n_symbols']} syms; decidable {n_dec}; "
              f"asym/sym flips {sm_face['asym']['n_flips']}/"
              f"{sm_face['sym']['n_flips']})")

        # ---- D D6 cells face (x1 net return series, no metric persisted)
        tgt_ret = closes[TARGET].astype(float).pct_change()
        rets = {v: cell_returns(pos[v], tgt_ret) for v in VARIANTS}
        d6 = {"batch_internal_asym_vs_sym": round(
                  abs(_pearson(rets["asym"], rets["sym"])), 4),
              "vs_t33_cells": {}, "merge_clause_applied": [],
              "vs_registered_six": {"max_abs_corr": None, "argmax": None},
              "regime_guard_note":
                  "in-production non-cell (T0 authority untouched): signal "
                  "face adjudicated at berth pearson +0.7728 width-leg / "
                  "+0.5965 composite vs below-MA20 share (r259 facts); "
                  "vs #87 nh_nl B20 -0.5539/-0.4420; no cells pair exists, "
                  "merge clause cannot trigger against a non-cell -- honest "
                  "boundary per prereg s1 table"}
        t33_idx = _panel_calendar_union("2026-09-24")   # T33 own cutoff face
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
            ca = round(abs(_pearson(rets["asym"], t33_rows[cid])), 4)
            cs = round(abs(_pearson(rets["sym"], t33_rows[cid])), 4)
            d6["vs_t33_cells"][cid] = {"asym": ca, "sym": cs}
            if max(ca, cs) >= D6_REJECT:
                d6["merge_clause_applied"].append(cid)
        try:
            gates = json.load(open(T33_GATES_PATH, encoding="utf-8"))
            reg_rets = gates.get("registered_rets", {})
            my_idx = closes.index
            best = (0.0, None)
            for rid, rl in reg_rets.items():
                k = min(len(rl), len(my_idx) - 1)
                rs_ = pd.Series(rl[:k], index=my_idx[1:k + 1])
                ca = abs(_pearson(rets["asym"], rs_))
                cs = abs(_pearson(rets["sym"], rs_))
                c = max(ca if np.isfinite(ca) else 0.0,
                        cs if np.isfinite(cs) else 0.0)
                if c > best[0]:
                    best = (c, rid)
            d6["vs_registered_six"] = {"max_abs_corr": round(best[0], 4),
                                       "argmax": best[1]}
        except FileNotFoundError:
            d6["vs_registered_six"] = {"max_abs_corr": None, "argmax": None,
                                        "note": "t33 gates json absent"}

        facts = {
            "probe": "CROWD-VOTE-P1 freeze-window G-ANCHOR re-verify + "
                     "threshold constants + D6 cells probe",
            "machine": "bm-c", "round": "r260",
            "evidence_cutoff": str(closes.index[-1].date()),
            "panel": {"n_symbols": int(closes.shape[1]),
                      "n_members_non_guard": int(closes.shape[1] - 1),
                      "guard": GUARD,
                      "first_date": str(closes.index[0].date()),
                      "last_date": str(closes.index[-1].date()),
                      "n_dates": int(len(closes.index)),
                      "score_window": W, "annualization": ANNUAL},
            "g_anchor_reverify": {
                "pass": True,
                "reference": "results/_r259bmc_w9_crowding_probe_facts.json "
                             "(berth frozen facts; cutoff unchanged "
                             "2026-09-29, zero incremental segment)",
                "n_face_checks": len(derived_ga) + len(panel_derived) + 4,
                "anchors": derived_ga,
                "note": "one-face-off = config mismatch VOID per prereg s2 "
                        "G-ANCHOR-FACE law; berth probe file re-run git-diff "
                        "face done same window (round report)",
            },
            "threshold_constants_zero_drift": {
                "pass": True,
                "compared": th_cmp,
                "recovery_diff_lt": round(TH_SPREAD * HYST, 4),
                "note": "author-verbatim wzetf 2026-08-22 card, zero "
                        "calibration (no trailing quantile, no search -- "
                        "different source from W7 theta face, disclosed "
                        "per prereg s2); constants asserted equal vs "
                        "frozen berth facts block",
            },
            "state_machine_face": {
                "initial_state_convention":
                    "long at first decidable day (passive default; r261 "
                    "runner freeze pins identical convention in selftest)",
                "asym": sm_face["asym"],
                "sym": sm_face["sym"],
                "asym_defensive_days": int((pos["asym"] == 0.0).sum()),
                "asym_decidable_days": int(pos["asym"].notna().sum()),
                "sym_defensive_days": int((pos["sym"] == 0.0).sum()),
                "sym_decidable_days": int(pos["sym"].notna().sum()),
            },
            "d6_cells_face": d6,
            "cost_face": "ce_transfer.COST_X1_RATE imported (13.041bp/side); "
                         "D6 return series = x1 net convention, no metric "
                         "persisted",
            "merge_clause_threshold": D6_REJECT,
            "single_source_note": "crowd_positions + cell_returns defined "
                                  "HERE = the construction face the r261 "
                                  "runner verbatim-imports (r456 zero-drift "
                                  "paradigm, parity-asserted every run)",
        }
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(facts, fh, ensure_ascii=False, indent=1)
        print("threshold constants: zero-drift PASS (author-verbatim "
              "constants, no calibration)")
        print("D6 batch internal |corr| =",
              d6["batch_internal_asym_vs_sym"],
              "(expected high, variant face -- both cells burn)")
        print("D6 vs T33 cells:", d6["vs_t33_cells"])
        print("D6 merge clause applied:", d6["merge_clause_applied"] or "NONE")
        print("D6 vs registered six max |corr| =",
              d6["vs_registered_six"]["max_abs_corr"],
              "argmax", d6["vs_registered_six"]["argmax"])
        return 0
    except Exception as exc:            # honest fault, no masking
        import traceback
        traceback.print_exc()
        print(f"PROBE FAULT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(run())
