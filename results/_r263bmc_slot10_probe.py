# -*- coding: utf-8 -*-
"""r263 bm-c SLOT-10 supply-wave probe: two fresh A-layer gate candidates.

A) repo_rate_state gate   -- GC001 close percentile-stress state (data/repo_daily, bm-a lane face)
B) etf_premium_disp gate  -- core48 ETF premium cross-mean/z dispersion state (data/fund_premium, bm-c lane face)

Descriptive occupancy + fwd20d conditional means only (W9/W10 probe lineage).
Deterministic, zero network, zero engine touch. Facts JSON to results/_r263bmc_slot10_probe_facts.json.
"""
import csv
import json
import math
import os

OUT = "results/_r263bmc_slot10_probe_facts.json"


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


def pct_rank_state(series_sorted_dates, values, window=252, q_hi=0.90, q_lo=0.10, min_periods=120):
    """Rolling percentile state: (hi, lo) when value > rolling q_hi / < q_lo of own history."""
    dates = series_sorted_dates
    out = {}
    buf = []
    for i, d in enumerate(dates):
        buf.append(values[i])
        if len(buf) >= min_periods:
            s = sorted(buf)
            k_hi = s[min(len(s) - 1, int(math.floor(q_hi * len(s))))]
            k_lo = s[int(math.floor(q_lo * len(s)))]
            out[d] = (values[i] > k_hi, values[i] < k_lo)
        if len(buf) > window:
            buf.pop(0)
    return out


def fwd_ret(px_sorted_dates, px, d, horizon=20):
    """Forward horizon-day close-to-close return from d (T+1 proxy: d -> d+h)."""
    try:
        i = px_sorted_dates.index(d)
    except ValueError:
        return None
    j = i + horizon
    if j >= len(px_sorted_dates):
        return None
    return px[j] / px[i] - 1.0


def main():
    facts = {
        "artifact": "r263 bm-c SLOT-10 supply-wave probe (two fresh A-layer gate candidates, descriptive only)",
        "machine": "bm-c",
        "round": 263,
        "lane_note": "research/supply lane, zero network, zero engine touch, marks +0",
        "candidates": {},
    }

    # ---------------- A) repo rate state ----------------
    repo = load_csv_series("data/repo_daily/GC001.csv", "date", "close")
    rd = sorted(repo)
    rvals = [repo[d] for d in rd]
    state = pct_rank_state(rd, rvals)
    stress_me = stress_n = 0
    for d, (hi, lo) in state.items():
        if hi:
            stress_n += 1
            if d[8:10] >= "28" or d[8:10] <= "03":
                stress_me += 1
    px = load_csv_series("data/daily/sh510300.csv", "date", "close")
    pxd = sorted(px)
    pxv = [px[x] for x in pxd]
    fwd20_stress, fwd20_other = [], []
    for d, (hi, lo) in state.items():
        r = fwd_ret(pxd, pxv, d)
        if r is None:
            continue
        (fwd20_stress if hi else fwd20_other).append(r)
    mean = lambda xs: (sum(xs) / len(xs)) if xs else None
    facts["candidates"]["A_repo_rate_state"] = {
        "definition": "GC001 close > rolling-252 q90 of own history (min_periods=120); annualized % face",
        "data_face": "data/repo_daily/GC001.csv (bm-a collector lane, in-repo shared)",
        "n_days_total": len(rd),
        "first_date": rd[0],
        "last_date": rd[-1],
        "n_state_days": len(state),
        "stress_open_rate": round(stress_n / len(state), 4) if state else None,
        "stress_month_end_adjacent_share": round(stress_me / stress_n, 4) if stress_n else None,
        "fwd20d_510300_mean_stress": round(mean(fwd20_stress), 5) if fwd20_stress else None,
        "n_fwd_stress": len(fwd20_stress),
        "fwd20d_510300_mean_other": round(mean(fwd20_other), 5) if fwd20_other else None,
        "n_fwd_other": len(fwd20_other),
        "near_family_disclosure": "W1/W2 revrepo-CALENDAR judged-negative (calendar usage face); this = rate-LEVEL state face, distinct usage; D6 corr audit deferred to berth prereg",
    }

    # ---------------- B) ETF premium dispersion ----------------
    members = {}
    with open("data/fund_premium/panel/panel.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = r["date"]
            try:
                pz = float(r["premium_z"]) if r["premium_z"] not in ("", None) else None
                pa = float(r["premium_adj"]) if r["premium_adj"] not in ("", None) else None
            except ValueError:
                continue
            members.setdefault(d, []).append((pa, pz))
    pd_dates = sorted(members)
    cross_mean_z, n_member = [], []
    for d in pd_dates:
        pzs = [x[1] for x in members[d] if x[1] is not None]
        pas = [x[0] for x in members[d] if x[0] is not None]
        if not pzs:
            continue
        cross_mean_z.append((d, sum(pzs) / len(pzs)))
        n_member.append((d, len(pzs)))
    cmd = [x[0] for x in cross_mean_z]
    cmv = [x[1] for x in cross_mean_z]
    cstate = pct_rank_state(cmd, cmv)
    hot_fwd, cold_fwd, mid_fwd = [], [], []
    for d, (hi, lo) in cstate.items():
        r = fwd_ret(pxd, pxv, d)
        if r is None:
            continue
        if hi:
            hot_fwd.append(r)
        elif lo:
            cold_fwd.append(r)
        else:
            mid_fwd.append(r)
    n_hot = sum(1 for d, (hi, lo) in cstate.items() if hi)
    n_cold = sum(1 for d, (hi, lo) in cstate.items() if lo)
    facts["candidates"]["B_etf_premium_disp"] = {
        "definition": "cross-mean premium_z over core48 > rolling-252 q90 (hot) / < q10 (cold) of own history",
        "data_face": "data/fund_premium/panel/panel.csv (bm-c collector lane)",
        "n_dates_panel": len(pd_dates),
        "first_date": pd_dates[0] if pd_dates else None,
        "last_date": pd_dates[-1] if pd_dates else None,
        "n_members_first": n_member[0][1] if n_member else None,
        "n_members_last": n_member[-1][1] if n_member else None,
        "n_state_days": len(cstate),
        "n_hot": n_hot,
        "n_cold": n_cold,
        "fwd20d_510300_mean_hot": round(mean(hot_fwd), 5) if hot_fwd else None,
        "n_fwd_hot": len(hot_fwd),
        "fwd20d_510300_mean_cold": round(mean(cold_fwd), 5) if cold_fwd else None,
        "n_fwd_cold": len(cold_fwd),
        "fwd20d_510300_mean_mid": round(mean(mid_fwd), 5) if mid_fwd else None,
        "n_fwd_mid": len(mid_fwd),
        "thin_history_disclosure": "panel starts 2020-01-02 (NAV backfill boundary) = ~6.7y; deep-history three-window grid burden carried; forward-accumulation panel law applies",
        "near_family_disclosure": "no prior burn touched NAV-price wedge face (T-16 ARB-1 = arb consumer face, not gate); #84/#87 sentiment-cluster mechanism-neighbor risk disclosed (9-burn family-cluster burden)",
    }

    facts["evidence_cutoff"] = "2026-09-29"
    facts["generated_by"] = "results/_r263bmc_slot10_probe.py (deterministic re-run comparable)"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1)
    print("probe facts ->", OUT)
    print("A stress occupancy:", facts["candidates"]["A_repo_rate_state"]["stress_open_rate"],
          "fwd stress vs other:", facts["candidates"]["A_repo_rate_state"]["fwd20d_510300_mean_stress"],
          "vs", facts["candidates"]["A_repo_rate_state"]["fwd20d_510300_mean_other"])
    print("B hot/cold/mid fwd:", facts["candidates"]["B_etf_premium_disp"]["fwd20d_510300_mean_hot"],
          facts["candidates"]["B_etf_premium_disp"]["fwd20d_510300_mean_cold"],
          facts["candidates"]["B_etf_premium_disp"]["fwd20d_510300_mean_mid"])


if __name__ == "__main__":
    main()
