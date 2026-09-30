# -*- coding: utf-8 -*-
"""_r265bmc_w10_freeze_probe.py -- PREMIUM-SENT-P1 freeze-window probe:
G-ANCHOR face re-verification (prereg s9 step 2) + degeneracy identity
re-check + threshold-constant zero-drift assertion (step 4) + D6 cells
corr face (step 5, prereg s1 table, W9 r260 protocol mirror).

Read-only, zero engine/admission/REGIME_GUARD touch. Persists NO
performance metric of the batch cells -- the D6 face uses indicator and
return series only for the preregistered correlation protocol (W9 probe
discipline: "persists no performance metric").

Single-source law (r456 paradigm): all faces re-derived via verbatim
import from results/_r264bmc_w10_berth_probe.py (pct_rank_state /
load_csv_series / pearson_ind / episodes_confirm2) -- the same
construction face the r266 runner will verbatim-import and
parity-assert (zero re-implementation drift).

Faces:
  A  G-ANCHOR re-verify : panel anchors + degeneracy identity + state
                          face + fwd conditional means + D6 signal face
                          + 2d-confirm episodes, compared face-by-face
                          vs frozen berth facts (one-face-off = VOID).
                          Berth probe re-run git-face zero-diff done
                          same window (round report; bit-exact proof).
  T  threshold constants: author-verbatim constants (zero calibration)
                          asserted vs code defaults + prereg text tokens
                          (q90/q10, window 252, min_periods 120, h 20/5,
                          split 2023-07-01, nulls K=2000, N_eff 2004,
                          seed 20326500).
  D  D6 cells face      : batch-internal HOT vs COLD (structural
                          complement -- both tails burn independently
                          per family rule), h20 vs h5 (identical signal
                          series by construction -- horizon axis, not a
                          variant axis), vs five in-register measurable
                          faces (berth mirror), vs T33 in-book rotation
                          cells + registered six via the prereg s1
                          signal/conditional-expectation face protocol
                          substitution (IC batch has no return-series
                          cells -- honest note), merge clause at
                          |corr| >= 0.7.

Output: results/_r265bmc_w10_freeze_probe_facts.json
Exit 0 normal / 2 drift or mechanism fault (honest, no masking).
"""
import inspect
import json
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)                         # live.paper import face
sys.path.insert(0, os.path.join(ROOT, "results"))   # berth probe family
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from _r264bmc_w10_berth_probe import (        # single source (r456)
    pct_rank_state, load_csv_series, pearson_ind, episodes_confirm2,
    PANEL, REPO_GC001)
from _r259bmc_w9_crowding_probe import (      # W9 in-tree faces
    load_core48, below_ma20_share, nhnl_b20, build_faces)

OUT = os.path.join(ROOT, "results", "_r265bmc_w10_freeze_probe_facts.json")
BERTH_FACTS = os.path.join(
    ROOT, "results", "_r264bmc_w10_berth_probe_facts.json")
PREREG = os.path.join(ROOT, "research", "INNOVATION_QUOTA_W10_PREREG.md")
D6_REJECT = 0.7
T33_CELLS_PATH = os.path.join(ROOT, "results", "t33_attack_wave_cells.jsonl")
T33_GATES_PATH = os.path.join(ROOT, "results", "t33_attack_wave_gates.json")
T33_ROT_CELLS = ["slope_r2_rotation_25_top3_r8",
                 "dual_momentum_etf_20_60_top3",
                 "rs_rotation_20", "composite_top5"]
FWD_HORIZONS = (20, 5)          # prereg s0: h20 primary / h5 secondary
SPLIT_DATE = "2023-07-01"        # prereg s4 V3 pre-frozen calendar split
NULLS_K = 2000                   # prereg s3
BATCH_CELLS = 2004               # prereg s0 N_eff counting law
SEED_INTENDED = 20326500         # prereg s4, registered this window


def _panel_calendar_union(cutoff: str) -> pd.DatetimeIndex:
    from live.paper import load_core
    ps = pd.Timestamp(cutoff)
    all_idx = set()
    for df in load_core().values():
        all_idx.update(df.index[df.index <= ps])
    return pd.DatetimeIndex(sorted(all_idx))


def _pb_corr(ind: dict, rets: pd.Series) -> float:
    """Point-biserial: state-day indicator vs a daily series (the prereg
    s1 signal/conditional-expectation face protocol substitution for
    non-signal faces -- IC batch has no return-series cells)."""
    s = pd.Series({pd.Timestamp(d): float(v) for d, v in ind.items()})
    j = pd.concat([s, rets], axis=1, join="inner").dropna()
    if len(j) < 20:
        return float("nan")
    c = np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]
    return float(c) if np.isfinite(c) else float("nan")


def run() -> int:
    try:
        with open(BERTH_FACTS, encoding="utf-8") as fh:
            berth = json.load(fh)

        # ---------- A G-ANCHOR re-verify (verbatim berth computation) ----------
        mem = {}
        with open(PANEL, encoding="utf-8") as f:
            for r in __import__("csv").DictReader(f):
                try:
                    pz = float(r["premium_z"]) if r["premium_z"] not in ("", None) else None
                    pa = float(r["premium_adj"]) if r["premium_adj"] not in ("", None) else None
                except ValueError:
                    continue
                if pa is None:
                    continue
                mem.setdefault(r["date"], []).append((pa, pz))
        pd_dates = sorted(mem)
        max_abs_zmean = 0.0
        for d in pd_dates:
            pzs = [x[1] for x in mem[d] if x[1] is not None]
            if pzs:
                max_abs_zmean = max(max_abs_zmean, abs(sum(pzs) / len(pzs)))

        cross = {d: sum(x[0] for x in mem[d]) / len(mem[d]) for d in pd_dates}
        cmd = sorted(cross)
        cmv = [cross[d] for d in cmd]
        cstate = pct_rank_state(cmd, cmv)
        hot_ind = {d: (1 if v[0] else 0) for d, v in cstate.items()}
        cold_ind = {d: (1 if v[1] else 0) for d, v in cstate.items()}

        derived = {
            "n_dates_panel": len(pd_dates),
            "first_date": pd_dates[0],
            "last_date": pd_dates[-1],
            "n_members_first": len(mem[pd_dates[0]]),
            "n_members_last": len(mem[pd_dates[-1]]),
            "cross_mean_min": round(min(cmv), 4),
            "cross_mean_max": round(max(cmv), 4),
            "cross_mean_mean": round(sum(cmv) / len(cmv), 4),
            "days_below_par": sum(1 for v in cmv if v < 0),
            "n_state_days": len(cstate),
            "first_decidable_date": min(cstate.keys()),
            "n_hot": sum(hot_ind.values()),
            "n_cold": sum(cold_ind.values()),
        }
        px = load_csv_series(os.path.join(ROOT, "data", "daily", "510300.csv"),
                             "date", "close")
        pxd = sorted(px)
        pxv = [px[x] for x in pxd]
        pxi = {d: i for i, d in enumerate(pxd)}

        def fwd(d, h):
            i = pxi.get(d)
            if i is None or i + h >= len(pxd):
                return None
            return pxv[i + h] / pxv[i] - 1.0

        fwd_facts = {}
        for h in FWD_HORIZONS:
            hot_f = [fwd(d, h) for d in sorted(cstate) if hot_ind[d]]
            cold_f = [fwd(d, h) for d in sorted(cstate) if cold_ind[d]]
            mid_f = [fwd(d, h) for d in sorted(cstate)
                     if not hot_ind[d] and not cold_ind[d]]
            hot_f = [x for x in hot_f if x is not None]
            cold_f = [x for x in cold_f if x is not None]
            mid_f = [x for x in mid_f if x is not None]
            mean = lambda xs: round(sum(xs) / len(xs), 5) if xs else None
            fwd_facts["h%d" % h] = {
                "hot_mean": mean(hot_f), "n_hot": len(hot_f),
                "cold_mean": mean(cold_f), "n_cold": len(cold_f),
                "mid_mean": mean(mid_f), "n_mid": len(mid_f),
                "hot_minus_cold_pp": (round((mean(hot_f) - mean(cold_f)) * 100, 3)
                                      if hot_f and cold_f else None),
                "note": "descriptive, overlapping windows, no cost, no prereg status",
            }

        panel, syms = load_core48()
        faces, votes, rec_votes, decidable = build_faces(panel)
        idx = [d.strftime("%Y-%m-%d") for d in faces.index]
        crowd_face = {d: (1.0 if bool(faces["crowd"].iloc[i]) else 0.0)
                      for i, d in enumerate(idx) if bool(decidable.iloc[i])}
        below = below_ma20_share(panel)
        below_face = {d.strftime("%Y-%m-%d"): float(v)
                      for d, v in below.items() if v == v}
        b20 = nhnl_b20(panel)
        b20_face = {d.strftime("%Y-%m-%d"): float(v)
                    for d, v in b20.items() if v == v}
        repo = load_csv_series(REPO_GC001, "date", "close")
        rd = sorted(repo)
        rstate = pct_rank_state(rd, [repo[x] for x in rd])
        stress_face = {d: (1.0 if v[0] else 0.0) for d, v in rstate.items()}
        me_face = {d: (1.0 if (d[8:10] >= "28" or d[8:10] <= "03") else 0.0)
                   for d in cstate}

        d6 = {}
        for label, sface in [("vs_w9_crowd_day", crowd_face),
                             ("vs_regime_guard_width_below_ma20", below_face),
                             ("vs_87_nhnl_b20_closed_family", b20_face),
                             ("vs_98_repo_stress_state", stress_face),
                             ("vs_month_end_adjacent_calendar", me_face)]:
            rh, nh = pearson_ind(list(cstate.keys()), hot_ind, sface)
            rc, nc = pearson_ind(list(cstate.keys()), cold_ind, sface)
            d6[label] = {"hot_pearson": rh, "cold_pearson": rc, "n_common": nh}
        n_hot_me = sum(1 for d in cstate if hot_ind[d] and me_face[d])
        n_cold_me = sum(1 for d in cstate if cold_ind[d] and me_face[d])
        d6["hot_month_end_share"] = round(n_hot_me / max(1, derived["n_hot"]), 4)
        d6["cold_month_end_share"] = round(n_cold_me / max(1, derived["n_cold"]), 4)

        cdates = sorted(cstate)
        hot_raw = {d: bool(hot_ind[d]) for d in cdates}
        cold_raw = {d: bool(cold_ind[d]) for d in cdates}
        v1_off, v1_on, v1_days_on, v1_days_off, v1_flips = episodes_confirm2(
            cdates, hot_raw, start_on=True)
        v2_off, v2_on, v2_days_on, v2_days_off, v2_flips = episodes_confirm2(
            cdates, {d: not cold_raw[d] for d in cdates}, start_on=False)
        years = len(cdates) / 252.0
        episodes = {
            "V1_HOT_DEF_2d": {"n_exits_to_cash": v1_off, "n_reentries": v1_on,
                              "days_long": v1_days_on, "days_cash": v1_days_off,
                              "cash_occupancy": round(v1_days_off / max(1, len(cdates)), 4),
                              "est_turnover_per_yr": round(v1_off / years, 2),
                              "first_flips": v1_flips},
            "V2_COLD_GATE_2d": {"n_entries": v2_on, "n_exits": v2_off,
                                "days_long": v2_days_on, "days_cash": v2_days_off,
                                "long_occupancy": round(v2_days_on / max(1, len(cdates)), 4),
                                "est_turnover_per_yr": round(v2_on / years, 2),
                                "first_flips": v2_flips},
            "window_years": round(years, 2),
        }

        mism = []
        stored_face = berth["premium_state_face"]
        for k, v in derived.items():
            if stored_face.get(k) != v:
                mism.append("face.%s: %r != frozen %r" % (k, v, stored_face.get(k)))
        for h in FWD_HORIZONS:
            sk = "h%d" % h
            for k, v in fwd_facts[sk].items():
                if berth["fwd_conditional_means"][sk].get(k) != v:
                    mism.append("fwd.%s.%s: %r != frozen %r"
                                % (sk, k, v,
                                   berth["fwd_conditional_means"][sk].get(k)))
        for k, v in d6.items():
            if berth["d6_signal_face"].get(k) != v:
                mism.append("d6.%s: %r != frozen %r"
                            % (k, v, berth["d6_signal_face"].get(k)))
        for vk, vv in [("V1_HOT_DEF_2d", episodes["V1_HOT_DEF_2d"]),
                       ("V2_COLD_GATE_2d", episodes["V2_COLD_GATE_2d"])]:
            for k in ("n_exits_to_cash", "n_reentries", "days_long", "days_cash",
                      "cash_occupancy", "est_turnover_per_yr", "long_occupancy",
                      "n_entries", "n_exits", "first_flips"):
                if k in vv and berth["confirmed_state_episodes_2d"][vk].get(k) != vv[k]:
                    mism.append("ep.%s.%s: %r != frozen %r"
                                % (vk, k, vv[k],
                                   berth["confirmed_state_episodes_2d"][vk].get(k)))
        if abs(max_abs_zmean
               - berth["degeneracy_audit"]["max_abs_cross_mean_premium_z"]) > 1e-24:
            mism.append("degeneracy.max_abs: %r != frozen %r"
                        % (max_abs_zmean,
                           berth["degeneracy_audit"]["max_abs_cross_mean_premium_z"]))
        if max_abs_zmean >= 1e-12:
            mism.append("degeneracy identity FAILED: %r >= 1e-12" % max_abs_zmean)
        panel_moved = derived["last_date"] != "2026-09-24"
        if berth.get("evidence_cutoff") != "2026-09-29":
            mism.append("evidence_cutoff drift: %r" % berth.get("evidence_cutoff"))

        # ---------- T threshold-constant zero-drift (step 4) ----------
        sig = inspect.signature(pct_rank_state)
        th_cmp = {
            "state_window": sig.parameters["window"].default,
            "state_q_hi": sig.parameters["q_hi"].default,
            "state_q_lo": sig.parameters["q_lo"].default,
            "state_min_periods": sig.parameters["min_periods"].default,
            "fwd_horizons_primary_secondary": list(FWD_HORIZONS),
            "v3_calendar_split": SPLIT_DATE,
            "nulls_K": NULLS_K,
            "batch_cells_N_eff": BATCH_CELLS,
            "seed_registered": SEED_INTENDED,
        }
        prereg_text = open(PREREG, encoding="utf-8").read()
        th_tokens = {
            "q90/q10 tail occupancy gate": ("q90" in prereg_text and "q10" in prereg_text),
            "window 252": "252" in prereg_text,
            "min_periods=120": "min_periods=120" in prereg_text,
            "split 2023-07-01": SPLIT_DATE in prereg_text,
            "nulls K=2,000": "K=**2,000**" in prereg_text,
            "N_eff 2004": "2004" in prereg_text,
            "seed 20326500": str(SEED_INTENDED) in prereg_text,
        }
        th_mism = []
        if th_cmp["state_window"] != 252:
            th_mism.append("state_window %r" % th_cmp["state_window"])
        if th_cmp["state_q_hi"] != 0.90 or th_cmp["state_q_lo"] != 0.10:
            th_mism.append("state q_hi/q_lo %r/%r" % (th_cmp["state_q_hi"], th_cmp["state_q_lo"]))
        if th_cmp["state_min_periods"] != 120:
            th_mism.append("state_min_periods %r" % th_cmp["state_min_periods"])
        if tuple(th_cmp["fwd_horizons_primary_secondary"]) != (20, 5):
            th_mism.append("fwd horizons %r" % (th_cmp["fwd_horizons_primary_secondary"],))
        for tok, ok in th_tokens.items():
            if not ok:
                th_mism.append("prereg token missing: %s" % tok)
        import science_gates as sg
        if sg.SEED_REGISTRY.get("innovation_quota_w10_premium") != SEED_INTENDED:
            th_mism.append("SEED_REGISTRY key != %r" % SEED_INTENDED)

        if mism or th_mism:
            for m in (mism + th_mism)[:12]:
                print("  drift:", m)
            print("GATE-REFUSE(exit2): freeze-window re-verify drift "
                  "(%d anchor faces, %d constants) vs frozen berth facts"
                  % (len(mism), len(th_mism)))
            return 2
        print("G-ANCHOR re-verify: ALL faces bit-exact vs berth facts "
              "(panel %s..%s %d dates, members %d->%d; state days %d, "
              "hot/cold %d/%d; degeneracy identity %r < 1e-12; "
              "cutoff 2026-09-29, panel last 2026-09-24 unmoved, zero "
              "incremental segment)"
              % (derived["first_date"], derived["last_date"],
                 derived["n_dates_panel"], derived["n_members_first"],
                 derived["n_members_last"], derived["n_state_days"],
                 derived["n_hot"], derived["n_cold"], max_abs_zmean))

        # ---------- D D6 cells face (step 5) ----------
        d6c = {
            "batch_internal_hot_vs_cold": None,
            "batch_internal_note":
                "HOT/COLD tails are structural complements of one state "
                "gate (disjoint tail occupancy of the same cross-mean "
                "series) -- NOT a variant pair and NOT merge-clause "
                "eligible; both tails burn independently per prereg s4 "
                "family rule (W9 'variant face both burn' analog)",
            "h20_vs_h5_signal_face": 1.0,
            "h20_h5_note":
                "h20/h5 cells share the identical state-day indicator "
                "series by construction (cell axis = evaluation horizon, "
                "pre-declared h20 primary + h5 secondary zero-family-"
                "weight); signal-face corr = 1.0 trivially, no variant "
                "implication, no merge clause",
            "vs_in_register_five_faces": {k: v for k, v in d6.items()
                                           if isinstance(v, dict)},
            "in_register_max_abs_corr": 0.3683,
            "vs_t33_cells": {}, "vs_registered_six": {"max_abs_corr": None,
                                                      "argmax": None},
            "merge_clause_applied": [],
            "protocol_substitution_note":
                "prereg s1: IC-type batch has no return-series cells -> "
                "registered-trader daily-return corr inapplicable; T33 "
                "in-book cells and registered six measured on the "
                "signal/conditional-expectation face (state-day indicator "
                "x daily series point-biserial) per prereg s1 substitution "
                "clause, honest protocol note",
        }
        rhc, nhc = pearson_ind(list(cstate.keys()), hot_ind,
                               {d: float(cold_ind[d]) for d in cstate})
        d6c["batch_internal_hot_vs_cold"] = rhc

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
                d6c["vs_t33_cells"][cid] = None
                continue
            ch = _pb_corr(hot_ind, t33_rows[cid])
            cc = _pb_corr(cold_ind, t33_rows[cid])
            d6c["vs_t33_cells"][cid] = {"hot": round(abs(ch), 4) if np.isfinite(ch) else None,
                                        "cold": round(abs(cc), 4) if np.isfinite(cc) else None}
            mx = max(abs(ch) if np.isfinite(ch) else 0.0,
                     abs(cc) if np.isfinite(cc) else 0.0)
            if mx >= D6_REJECT:
                d6c["merge_clause_applied"].append(cid)
        try:
            gates = json.load(open(T33_GATES_PATH, encoding="utf-8"))
            reg_rets = gates.get("registered_rets", {})
            my_idx = panel.index
            best = (0.0, None)
            for rid, rl in reg_rets.items():
                k = min(len(rl), len(my_idx) - 1)
                rs_ = pd.Series(rl[:k], index=my_idx[1:k + 1])
                ch = _pb_corr(hot_ind, rs_)
                cc = _pb_corr(cold_ind, rs_)
                c = max(abs(ch) if np.isfinite(ch) else 0.0,
                        abs(cc) if np.isfinite(cc) else 0.0)
                if c > best[0]:
                    best = (c, rid)
            d6c["vs_registered_six"] = {"max_abs_corr": round(best[0], 4),
                                         "argmax": best[1]}
        except FileNotFoundError:
            d6c["vs_registered_six"] = {"max_abs_corr": None, "argmax": None,
                                        "note": "t33 gates json absent"}
        in_reg_max = max(
            [abs(v[k]) for v in d6c["vs_in_register_five_faces"].values()
             for k in ("hot_pearson", "cold_pearson") if v.get(k) is not None]
            + [0.0])
        t33_max = max([max((x or {}).get("hot") or 0.0,
                           (x or {}).get("cold") or 0.0)
                       for x in d6c["vs_t33_cells"].values() if x] + [0.0])
        six_max = d6c["vs_registered_six"]["max_abs_corr"] or 0.0
        d6c["clause_eligible_max_abs_corr"] = round(
            max(in_reg_max, t33_max, six_max), 4)

        facts = {
            "probe": "PREMIUM-SENT-P1 freeze-window G-ANCHOR re-verify + "
                     "degeneracy identity + threshold constants + D6 cells "
                     "probe",
            "machine": "bm-c", "round": "r265",
            "evidence_cutoff": "2026-09-29",
            "panel": {"n_dates_panel": derived["n_dates_panel"],
                      "first_date": derived["first_date"],
                      "last_date": derived["last_date"],
                      "members_first_last": [derived["n_members_first"],
                                             derived["n_members_last"]],
                      "incremental_segment": ("NONE -- panel last date "
                                              "2026-09-24 unmoved vs berth "
                                              "facts" if not panel_moved
                                              else "MOVED")},
            "g_anchor_reverify": {
                "pass": True,
                "reference": "results/_r264bmc_w10_berth_probe_facts.json "
                             "(berth frozen facts; berth probe re-run "
                             "git-face zero-diff same window, bit-exact "
                             "proof in round report)",
                "n_face_checks": (len(derived) + 7 * 2 + len(d6) + 9 * 2 + 3),
                "anchors": derived,
                "fwd_conditional_means": fwd_facts,
                "d6_signal_face": d6,
                "confirmed_state_episodes_2d": episodes,
                "degeneracy_identity": {
                    "max_abs_cross_mean_premium_z": max_abs_zmean,
                    "identity_holds": max_abs_zmean < 1e-12,
                    "note": "construction-erratum mechanical self-proof "
                            "reproduced (per-date cross-sectional z ddof=0 "
                            "-> cross-mean identically 0)",
                },
                "note": "one-face-off = config mismatch VOID per prereg s2 "
                        "G-ANCHOR-FACE law",
            },
            "threshold_constants_zero_drift": {
                "pass": True,
                "compared": th_cmp,
                "prereg_tokens": th_tokens,
                "note": "author-verbatim constants, zero calibration "
                        "(q90/q10 tail occupancy = gate author verbatim; "
                        "no trailing-quantile search); code defaults "
                        "asserted via inspect.signature on the "
                        "single-source pct_rank_state + prereg text tokens",
            },
            "d6_cells_face": d6c,
            "merge_clause_threshold": D6_REJECT,
            "single_source_note": "construction single source = "
                                  "results/_r264bmc_w10_berth_probe.py "
                                  "(pct_rank_state + panel load + fwd) -- "
                                  "the r266 runner verbatim-imports and "
                                  "parity-asserts (r456 zero-drift paradigm)",
        }
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(facts, fh, ensure_ascii=False, indent=1)
        print("threshold constants: zero-drift PASS (author-verbatim, "
              "code defaults + prereg tokens)")
        print("D6 batch internal HOT vs COLD =", d6c["batch_internal_hot_vs_cold"],
              "(structural complement, disclosed)")
        print("D6 vs T33 cells:", d6c["vs_t33_cells"])
        print("D6 vs registered six max =", d6c["vs_registered_six"])
        print("D6 clause-eligible max |corr| =",
              d6c["clause_eligible_max_abs_corr"], "< 0.7:",
              d6c["clause_eligible_max_abs_corr"] < D6_REJECT)
        print("D6 merge clause applied:", d6c["merge_clause_applied"] or "NONE")
        return 0
    except Exception as exc:            # honest fault, no masking
        import traceback
        traceback.print_exc()
        print("PROBE FAULT: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(run())
