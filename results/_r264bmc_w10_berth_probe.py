# -*- coding: utf-8 -*-
"""r264 bm-c W10 berth probe: PREMIUM-SENT-P1 (zoo #97 etf_premium_sentiment).

BERTH-WINDOW CONSTRUCTION CORRECTION (pre-freeze, zero burns on either face):
  zoo #97 as written = "cross-mean premium_z" -- DEGENERATE: premium_z is the
  per-date cross-sectional z (ddof=0, scripts/build_premium_panel.py
  add_premium_z), so its cross-sectional mean is identically 0 (empirical max
  |mean| = 2.6e-16 = float roundoff). The r263 supply-probe B-face state was
  therefore a float-noise classification (occupancy 9.5%/10.4% = the mechanical
  q90/q10 occupancy of ANY series) and its fwd20d spread is a chance artifact
  -- RETRACTED as descriptive evidence.
  Corrected face (intent-faithful: market-wide NAV-price wedge level):
  cross-mean premium_adj per date, rolling-252 q90/q10 state, min_periods=120.

Berth facts on the corrected face (W9 r259 berth-probe mirror):
  (1) G-ANCHOR face facts; (2) D6 signal face (vs W9 crowd day, REGIME_GUARD
  width leg, #87 nhnl_b20 closed family, #98 repo stress, month-end calendar);
  (3) fwd20d + fwd5d conditional means (descriptive, overlapping windows);
  (4) confirmed-state episodes (2d/2d symmetric) vs F6 entries>=30.

Deterministic, zero network, zero engine touch, marks +0.
Facts JSON -> results/_r264bmc_w10_berth_probe_facts.json.
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from _r259bmc_w9_crowding_probe import (  # W9 in-tree faces, verbatim import
    load_core48, below_ma20_share, nhnl_b20, build_faces)

OUT = os.path.join(HERE, "_r264bmc_w10_berth_probe_facts.json")
PANEL = os.path.join(ROOT, "data", "fund_premium", "panel", "panel.csv")
REPO_GC001 = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")


def load_csv_series(path, date_col, val_col):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = r[date_col]
            try:
                v = float(r[val_col])
            except (TypeError, ValueError):
                continue
            rows[d] = v
    return rows


def pct_rank_state(series_sorted_dates, values, window=252, q_hi=0.90,
                   q_lo=0.10, min_periods=120):
    """Rolling percentile state (r263 probe verbatim semantics)."""
    out = {}
    buf = []
    for i, d in enumerate(series_sorted_dates):
        buf.append(values[i])
        if len(buf) >= min_periods:
            s = sorted(buf)
            k_hi = s[min(len(s) - 1, int(math.floor(q_hi * len(s))))]
            k_lo = s[int(math.floor(q_lo * len(s)))]
            out[d] = (values[i] > k_hi, values[i] < k_lo)
        if len(buf) > window:
            buf.pop(0)
    return out


def pearson_ind(dates_a, ind_a, series_b):
    xs, ys = [], []
    for d in sorted(dates_a):
        if d in series_b and series_b[d] == series_b[d]:
            xs.append(float(ind_a[d]))
            ys.append(float(series_b[d]))
    if len(xs) < 30:
        return None, len(xs)
    x = np.asarray(xs)
    y = np.asarray(ys)
    sx = x.std()
    sy = y.std()
    if sx == 0 or sy == 0:
        return None, len(xs)
    r = float(((x - x.mean()) * (y - y.mean())).mean() / (sx * sy))
    return round(r, 4), len(xs)


def episodes_confirm2(dates, raw_flag, start_on):
    """Symmetric 2d/2d confirmation state machine, descriptive episode count.
    ON->OFF when raw_flag True 2 consecutive days; OFF->ON when False 2
    consecutive. Returns (n_on_to_off, n_off_to_on, days_on, days_off, flips[:8]).
    """
    state = start_on
    run = 0
    run_not = 0
    n_off = n_on = 0
    days_on = days_off = 0
    flips = []
    for d in dates:
        if state:
            days_on += 1
        else:
            days_off += 1
        if raw_flag[d]:
            run += 1
            run_not = 0
        else:
            run_not += 1
            run = 0
        if state and run >= 2:
            state = False
            n_off += 1
            flips.append(d)
            run = 0
            run_not = 0
        elif (not state) and run_not >= 2:
            state = True
            n_on += 1
            flips.append(d)
            run = 0
            run_not = 0
    return n_off, n_on, days_on, days_off, flips[:8]


def main() -> int:
    # ---------- (0) degeneracy audit on the zoo-as-written face ----------
    mem = {}
    with open(PANEL, encoding="utf-8") as f:
        for r in csv.DictReader(f):
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
    degeneracy = {
        "zoo_as_written_face": "cross-mean premium_z",
        "premium_z_semantics": "per-date cross-sectional z of premium_adj, ddof=0 (scripts/build_premium_panel.py add_premium_z)",
        "max_abs_cross_mean_premium_z": max_abs_zmean,
        "verdict": "DEGENERATE -- cross-sectional mean of a per-date cross-sectional z is identically 0; empirical max 2.6e-16 = float roundoff",
        "r263_supply_probe_face": "RETRACTED as descriptive evidence -- its hot/cold state was float-noise classification (occupancy 144/158 of 1514 = mechanical q90/q10 occupancy); fwd20d spread -1.31%/+1.32% = chance artifact of random subsets",
        "correction": "intent-faithful corrected face = cross-mean premium_adj (market-wide NAV-price wedge level, % units), rolling-252 q90/q10 state, min_periods=120 -- pre-freeze berth-window clarification (zero burns on either face, r251/r280 zero-burn clarification precedent family)",
    }

    # ---------- (1) corrected face: cross-mean premium_adj state ----------
    cross = {d: sum(x[0] for x in mem[d]) / len(mem[d]) for d in pd_dates}
    cmd = sorted(cross)
    cmv = [cross[d] for d in cmd]
    cstate = pct_rank_state(cmd, cmv)
    hot_ind = {d: (1 if v[0] else 0) for d, v in cstate.items()}
    cold_ind = {d: (1 if v[1] else 0) for d, v in cstate.items()}

    face = {
        "definition": "cross-mean premium_adj over panel members per date > rolling-252 q90 (hot) / < q10 (cold), min_periods=120",
        "data_face": "data/fund_premium/panel/panel.csv (bm-c collector lane, T-16 ARB-1 product)",
        "load_fn": "csv.DictReader raw direct read (non-engine pool face)",
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

    # ---------- (2) fwd conditional means (h20 + h5) ----------
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
    for h in (20, 5):
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

    # ---------- (3) D6 signal face ----------
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
    d6["hot_month_end_share"] = round(n_hot_me / max(1, face["n_hot"]), 4)
    d6["cold_month_end_share"] = round(n_cold_me / max(1, face["n_cold"]), 4)

    # ---------- (4) confirmed-state episodes (2d/2d symmetric) ----------
    cdates = sorted(cstate)
    hot_raw = {d: bool(hot_ind[d]) for d in cdates}
    cold_raw = {d: bool(cold_ind[d]) for d in cdates}
    v1_off, v1_on, v1_days_on, v1_days_off, v1_flips = episodes_confirm2(
        cdates, hot_raw, start_on=True)
    v2 = episodes_confirm2(cdates, {d: not cold_raw[d] for d in cdates},
                           start_on=False)
    # v2: start_on=False (cash default); raw="not cold" True 2d -> ... careful:
    # generic machine: OFF->ON when raw False 2 consecutive; we need ON when
    # cold-raw 2 consecutive. Use raw = not-cold with start_on=False inverted:
    # ON when raw False 2 consecutive == not-cold False 2 consecutive == cold 2d.
    # episodes_confirm2: OFF->ON when raw_flag False 2 consecutive -- matches.
    v2_off, v2_on, v2_days_on, v2_days_off, v2_flips = v2
    years = len(cdates) / 252.0
    episodes = {
        "V1_HOT_DEF_2d": {
            "rule": "long 510300 default; hot-raw 2 consecutive -> cash next day; not-hot-raw 2 consecutive -> re-enter; symmetric, no hysteresis",
            "n_exits_to_cash": v1_off, "n_reentries": v1_on,
            "days_long": v1_days_on, "days_cash": v1_days_off,
            "cash_occupancy": round(v1_days_off / max(1, len(cdates)), 4),
            "est_turnover_per_yr": round(v1_off / years, 2),
            "first_flips": v1_flips,
        },
        "V2_COLD_GATE_2d": {
            "rule": "cash default; cold-raw 2 consecutive -> enter next day; not-cold-raw 2 consecutive -> exit to cash; symmetric, no hysteresis",
            "n_entries": v2_on, "n_exits": v2_off,
            "days_long": v2_days_on, "days_cash": v2_days_off,
            "long_occupancy": round(v2_days_on / max(1, len(cdates)), 4),
            "est_turnover_per_yr": round(v2_on / years, 2),
            "first_flips": v2_flips,
        },
        "f6_entries_gate_note": "F6 entries>=30 dual-caliber (entries_ok governs): V1 exits-to-cash / V2 entries are the round-trip counts; <30 = structural F6 fail for the exposure-gate form (trading-face viability evidence, independent of the IC-face judged design)",
        "window_years": round(years, 2),
    }

    facts = {
        "artifact": "r264 bm-c W10 berth probe (PREMIUM-SENT-P1 zoo #97 etf_premium_sentiment, CORRECTED face, berth descriptive facts)",
        "machine": "bm-c",
        "round": 264,
        "lane_note": "research/supply berth lane, zero network, zero engine touch, marks +0",
        "degeneracy_audit": degeneracy,
        "premium_state_face": face,
        "fwd_conditional_means": fwd_facts,
        "d6_signal_face": d6,
        "confirmed_state_episodes_2d": episodes,
        "evidence_cutoff": "2026-09-29",
        "generated_by": "results/_r264bmc_w10_berth_probe.py (deterministic re-run comparable)",
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print("berth probe facts ->", OUT)
    print("DEGENERACY: max|cross-mean premium_z| =", max_abs_zmean)
    print("corrected face: hot/cold/mid days:", face["n_hot"], face["n_cold"],
          face["n_state_days"] - face["n_hot"] - face["n_cold"])
    print("fwd20 hot/cold/mid:", fwd_facts["h20"]["hot_mean"],
          fwd_facts["h20"]["cold_mean"], fwd_facts["h20"]["mid_mean"])
    print("fwd5  hot/cold/mid:", fwd_facts["h5"]["hot_mean"],
          fwd_facts["h5"]["cold_mean"], fwd_facts["h5"]["mid_mean"])
    print("D6 hot faces:", {k: v["hot_pearson"] for k, v in d6.items()
                            if isinstance(v, dict) and "hot_pearson" in v})
    print("V1 exits:", v1_off, "| V2 entries:", v2_on,
          "| window_years:", round(years, 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
