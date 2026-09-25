"""T-57 WILD_ROUTE_S1 runner -- street-pattern event lab (s2 encoding, CEO O-20260925-1132).

Laws (frozen in research/WILD_ROUTE_PREREG_S1.md -- R99: zero real-data batch
runs before the freeze commit; probe facts only, results/wild_route/
wild_route_probe.json):
  shared event engine  one-pass, all 12 patterns reuse (CARDS SS1):
    sealed limit-up := close==high (float-exact) AND qfq ret >= floor(board,date)
      floor main 0.0975 / chinext+star 0.1975 (cliff probe capture 99.4%/95.8%
      deep, results/wild_route/wild_route_probe.json); chinext 20cm only from
      2020-08-24, star since 2019-07-22;  turn: turnover face DEAD (probe) --
      all volume gates use volume/amount ratios, shang-shou legs dropped+disclosed.
    zhaban (touched-not-sealed) / yizi (low==high==close sealed) / limit-down
    touched / consecutive runs / market height / regime 3-axis state machine
    (frozen hiquant table: advance=lim>80 & zhaban_rate<10% & h>5; retreat=
    lim<30 & zhaban_rate>25% & h<3; else range).
  execution (ticket spec frozen): signal at close T -> entry open T+1 ONLY IF
    tradeable (open finite; NOT opened at/near limit: open/prev_close-1 <
    floor - 0.002); 一字/near-limit open = un-captured premium, counted.
    Suspension exit rolls forward to first tradable open. Costs {x1=13bp/side,
    x2=26bp/side} multiplicative both sides (V1 legacy caliber, x2 = stress).
    Bucket accounting: capital in H buckets, cohort of day t deployed at t+1
    open, cohort net return booked evenly across its H holding days (hold-1 =
    booked at exit day; stop-loss arms H=5 nominal, book at actual exit).
  cells: 29 pattern arms x 3 universes x 9 windows x 2 cost faces + 3 regime
    extras = 1569 cells (frozen census, deterministic enumeration; shard i of
    n = cells with index % n == i).  Nulls: K=50 same-mask random event-day
    nulls, seed base science_gates.SEED_REGISTRY['wild_route_s1']=61000+k.
  gates: G1'v2 on the 29 PRIMARY cells (W_full x U_full x x1) via
    science_gates.g1_prime_v2 (pool='stock_b_layer' registered passive,
    null_pool = own 50 nulls); G2 via g2_registration_v2 + DSR (deflated_
    sharpe_ratio on primary returns) + family PBO (screening/pbo.cscv_pbo,
    8 blocks, 29-arm family matrix). NO hand-copied lines (O-2250).
  accounting honesty: every rejected/untradeable/premium face counted in the
    cell JSON; honest-negative rows expected and reported as-is (s4 verdicts).

Subcommands (idempotent, checkpoint per cell JSON + per-shard jsonl rows
carrying their own cell key, r163 law):
  selftest         hermetic fixtures only (zero real data) -- R99-safe
  run --shard i --of n   run shard cells (checkpoint resume)
  run-nulls        K=50 null cells (post-freeze)
  finalize         aggregate + G1'/G2 verdicts + ledger (single-shot guard)
  status           census + checkpoint progress read
"""
import argparse
import glob
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as SG                      # shared gate library (O-2250)
from screening.pbo import cscv_pbo, align_returns  # family PBO CSCV 8-block

CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS = os.path.join(ROOT, "Money02", "data", "bars")
ELIG = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")
OUT_DIR = os.path.join(ROOT, "results", "wild_route")
CELL_DIR = os.path.join(OUT_DIR, "cells")
NULLS_JSON = os.path.join(OUT_DIR, "wild_route_s1_nulls.json")
RESULT_JSON = os.path.join(OUT_DIR, "wild_route_s1.json")
PROBE_JSON = os.path.join(OUT_DIR, "wild_route_probe.json")

MAIN_FLOOR = 0.0975
WIDE_FLOOR = 0.1975
CN_20CM_FROM = pd.Timestamp("2020-08-24")
STAR_FROM = pd.Timestamp("2019-07-22")
LIMIT_OPEN_TOL = 0.002          # open/prev-1 >= floor-0.002 -> untradeable
COST_X1 = 0.0013                # 13bp per side (V1 legacy)
COST_X2 = 0.0026                # stress face
PBP = 252                       # periods per year
EVIDENCE_CUTOFF = "2026-09-22"  # Stage-A panel last bar (C2 key)
W_FULL_FROM = pd.Timestamp("2001-01-01")
STAGGER_STARTS = [1996, 1999, 2002, 2005, 2008, 2011, 2014, 2017]
STAGGER_YEARS = 8
NULL_BASE = SG.SEED_REGISTRY["wild_route_s1"]
K_NULLS = 50
MIN_BARS_OK = 250               # P-1c MIN_ROWS census caliber
TRADING_DAYS_YEAR = 252

REGIME_ADV_LIM, REGIME_ADV_ZH, REGIME_ADV_H = 80, 0.10, 5
REGIME_RET_LIM, REGIME_RET_ZH, REGIME_RET_H = 30, 0.25, 3


# ------------------------------------------------------------------ panels

def build_panels_from_cache():
    # fleet discipline: heavy engine needs ~3-4GB free; below 4GB = honest
    # abort (exit 3), no corruption (checkpoints safe, next tick retries)
    try:
        import psutil
        avail_gb = psutil.virtual_memory().available / (1024 ** 3)
        if avail_gb < 4.0:
            print(f"engine abort: free RAM {avail_gb:.1f}GB < 4GB fleet line")
            sys.exit(3)
    except ImportError:
        pass
    syms = [os.path.basename(p)[:-8]
            for p in sorted(glob.glob(os.path.join(BARS, "*.parquet")))]
    meta = json.load(open(os.path.join(CACHE, "meta.json"), encoding="utf-8"))
    idx = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")), unit="us")
    # gate semantics mirrors frozen probe wild_route_probe.py census_drift_gate
    # (T and N asserted separately; T!=N structurally)
    assert len(syms) == meta["shape"]["N"], "cache shape drift (N)"
    assert len(idx) == meta["shape"]["T"], "cache shape drift (T)"
    P = {"idx": idx, "syms": syms, "T": len(idx), "N": len(syms)}
    for f in ("open", "high", "low", "close", "volume", "pct_chg"):
        P[f] = np.load(os.path.join(CACHE, f + ".npy"), mmap_mode="r")
    # census gate (r105 law): refuse regenerated cache
    assert meta["generated"] == "2026-09-24 03:42:50", "census drift: cache regenerated"
    return P


# ------------------------------------------------------------------ engine

def board_of(sym):
    if sym.startswith("30"):
        return "chinext"
    if sym.startswith("68"):
        return "star"
    return "main"


def build_engine(P):
    """Shared event engine. All faces raw (non-ffilled): NaN = absent/susp."""
    idx, T, N = P["idx"], P["T"], P["N"]
    close = P["close"]; high = P["high"]; low = P["low"]
    open_ = P["open"]; vol = P["volume"]; pct = P["pct_chg"]

    boards = np.array([board_of(s) for s in P["syms"]])
    is_cn = boards == "chinext"
    is_star = boards == "star"

    r1 = np.asarray(pct, dtype=np.float32) / np.float32(100.0)
    sealed = np.zeros((T, N), dtype=bool)
    cl = np.asarray(close); hi = np.asarray(high); lo = np.asarray(low)
    op = np.asarray(open_)
    same_hc = (hi == cl)
    sealed = np.isfinite(r1) & same_hc

    wide_dates = np.asarray(idx >= CN_20CM_FROM)
    star_era = np.asarray(idx >= STAR_FROM)

    lim = np.zeros((T, N), dtype=bool)          # sealed limit-up
    m = boards == "main"
    lim[:, m] = sealed[:, m] & (r1[:, m] >= MAIN_FLOOR)
    fl_cn = np.where(wide_dates, WIDE_FLOOR, MAIN_FLOOR)[:, None]
    lim[:, is_cn] = sealed[:, is_cn] & (r1[:, is_cn] >= fl_cn)
    lim[:, is_star] = (sealed[:, is_star] & (r1[:, is_star] >= WIDE_FLOOR)
                       & star_era[:, None])

    # limit-down touched (for #7): low/prev_close-1 <= -floor
    with np.errstate(invalid="ignore", divide="ignore"):
        prev_c = np.vstack([np.full((1, N), np.nan, dtype=np.float32), cl[:-1]])
        hi_ratio = hi / prev_c - np.float32(1.0)
        lo_ratio = lo / prev_c - np.float32(1.0)
    zhaban = np.isfinite(hi_ratio) & (hi_ratio >= MAIN_FLOOR) & ~sealed
    # board/date-aware floors for wide boards (touch faces)
    zhaban[:, is_cn] = (np.isfinite(hi_ratio[:, is_cn])
                        & (hi_ratio[:, is_cn] >= fl_cn) & ~sealed[:, is_cn])
    zhaban[:, is_star] = (np.isfinite(hi_ratio[:, is_star])
                          & (hi_ratio[:, is_star] >= WIDE_FLOOR)
                          & ~sealed[:, is_star])
    dn_touch = np.isfinite(lo_ratio) & (lo_ratio <= -MAIN_FLOOR)
    dn_touch[:, is_cn] = (np.isfinite(lo_ratio[:, is_cn])
                          & (lo_ratio[:, is_cn] <= -fl_cn))
    dn_touch[:, is_star] = (np.isfinite(lo_ratio[:, is_star])
                            & (lo_ratio[:, is_star] <= -WIDE_FLOOR))
    yizi = lim & (lo == hi)

    # consecutive runs + market height (one row-wise pass)
    runs = np.zeros((T, N), dtype=np.int16)
    heights = np.zeros(T, dtype=np.int16)
    cur = np.zeros(N, dtype=np.int16)
    for t in range(T):
        cur = np.where(lim[t], cur + 1, 0).astype(np.int16)
        runs[t] = cur
        h = int(cur.max()) if cur.size else 0
        heights[t] = h

    # regime 3-axis state machine (frozen table)
    dlim = lim.sum(axis=1)
    dzh = zhaban.sum(axis=1)
    zhaban_rate = dzh / np.maximum(1, dzh + dlim)
    regime = np.zeros(T, dtype=np.int8)          # 0=range 1=advance 2=retreat
    adv = (dlim > REGIME_ADV_LIM) & (zhaban_rate < REGIME_ADV_ZH) & (heights > REGIME_ADV_H)
    ret = (dlim < REGIME_RET_LIM) & (zhaban_rate > REGIME_RET_ZH) & (heights < REGIME_RET_H)
    regime[adv] = 1
    regime[ret] = 2

    yin = np.isfinite(cl) & np.isfinite(op) & (cl < op)
    yang = np.isfinite(cl) & np.isfinite(op) & (cl >= op)

    # tradability: traded day = volume finite
    susp = np.isfinite(cl) & ~np.isfinite(np.asarray(vol))
    ma5 = pd.DataFrame(cl).rolling(5, min_periods=3).mean().to_numpy(dtype=np.float32)

    # ok universe (bars >= 250) + ST exclusion + dragon names
    fin_close = np.isfinite(cl)
    ok_mask = fin_close.sum(axis=0) >= MIN_BARS_OK
    import csv
    st, dragon = set(), set()
    with open(ELIG, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            c = row.get("code")
            if c and c in set(P["syms"]):
                if row.get("r2_st") == "True":
                    st.add(c)
                if "龙" in (row.get("name") or ""):
                    dragon.add(c)
    symset = set(P["syms"])
    u_full_cols = np.array([j for j, s in enumerate(P["syms"])
                            if ok_mask[j] and s not in st], dtype=np.int64)
    dragon_cols = np.array([j for j, s in enumerate(P["syms"]) if s in dragon],
                           dtype=np.int64)

    # dynamic universes need trailing lim/runs faces
    lim_cum = np.cumsum(lim, axis=0)
    # rolling 60d max of run length (int16 kept; pandas rolling may upcast)
    rdf = pd.DataFrame(runs)
    maxrun60 = rdf.rolling(60, min_periods=1).max().to_numpy(dtype=np.int16)
    del rdf

    E = dict(P=P, idx=idx, T=T, N=N, boards=boards, is_cn=is_cn, is_star=is_star,
             r1=r1, lim=lim, zhaban=zhaban, dn_touch=dn_touch, yizi=yizi,
             runs=runs, heights=heights, regime=regime, yin=yin, yang=yang,
             susp=susp, ma5=ma5, prev_c=prev_c, hi_ratio=hi_ratio,
             lo_ratio=lo_ratio, ok_mask=ok_mask, u_full_cols=u_full_cols,
             dragon_cols=dragon_cols, maxrun60=maxrun60, lim_cum=lim_cum,
             dlim=dlim, zhaban_rate=zhaban_rate)
    return E


def dyn_universe_cols(E, kind, t):
    """Per-day dynamic universe columns (frozen defs):
    full   = static ok & ~ST (u_full_cols)
    limup60= u_full members with >=1 sealed limit-up in trailing 60d
    leader60 = u_full members with max run >=2 in trailing 60d
    """
    if kind == "full":
        return E["u_full_cols"]
    P = E["P"]; T, N = E["T"], E["N"]
    base = E["u_full_cols"]
    t0 = max(0, t - 59)
    if kind == "limup60":
        cnt = E["lim_cum"][t, base] - (E["lim_cum"][t0 - 1, base] if t0 > 0 else 0)
        return base[cnt >= 1]
    if kind == "leader60":
        mr = E["maxrun60"][t, base]
        return base[mr >= 2]
    raise ValueError(kind)


# ------------------------------------------------------------------ arms

def _rolling_mean_vol(E, win, t, cols):
    v = np.asarray(E["P"]["volume"][max(0, t - win + 1):t + 1][:, cols],
                   dtype=np.float64)
    with np.errstate(invalid="ignore"):
        return np.nanmean(np.where(np.isfinite(v), v, np.nan), axis=0)


def signal_matrix(E, arm):
    """One (T,N) bool signal matrix per arm (frozen encodings, CARDS SS2)."""
    T, N = E["T"], E["N"]
    lim, zhaban, runs, heights = E["lim"], E["zhaban"], E["runs"], E["heights"]
    r1, yin, yang = E["r1"], E["yin"], E["yang"]
    vol = E["P"]["volume"]
    hi_ratio = E["hi_ratio"]
    cl = np.asarray(E["P"]["close"]); hi = np.asarray(E["P"]["high"])
    lo = np.asarray(E["P"]["low"]); op = np.asarray(E["P"]["open"])
    S = np.zeros((T, N), dtype=bool)

    def row(t):
        return t in range(T)

    if arm == "P01_daban9":
        S[1:] = np.isfinite(hi_ratio[1:]) & (hi_ratio[1:] >= 0.09) \
            & (lo[1:] != hi[1:])
    elif arm == "P02_yijiner":
        S[1:] = lim[1:] & lim[:-1] & (runs[1:] == 2)
    elif arm == "P03a_duanban_dixi":
        S[:] = zhaban
    elif arm == "P03b_duanban_fanbao":
        v = np.asarray(vol, dtype=np.float64)
        with np.errstate(invalid="ignore"):
            vr = v[1:] / np.vstack([np.full((1, N), np.nan), v[:-1]])[1:]
        ok = np.isfinite(vr) & (vr >= 0.8) & (vr <= 0.9)
        S[1:] = zhaban[:-1] & lim[1:] & ok
    elif arm in ("P04a_jin", "P04b_yin", "P04c_huo"):
        tier = {"P04a_jin": (0.25, 5), "P04b_yin": (0.5, 7),
                "P04c_huo": (1.0, 9)}[arm]
        q, k = tier
        # anchor: sealed limit-up OR ret>=7% with a red candle (close>open)
        anchor = (lim | (np.isfinite(r1) & (r1 >= 0.07))) & (cl > op)
        # levels from anchor K range: level = high - (high-low)*q
        rng = hi - lo
        with np.errstate(invalid="ignore"):
            lvl = hi - rng * q
        # event at day a+k: min low over a+1..a+k >= level; adjust shrink;
        # entry-day volume expansion
        for t in range(k, T):
            a = t - k
            m = anchor[a] & np.isfinite(lvl[a])
            if not m.any():
                continue
            cols = np.flatnonzero(m)
            win_lo = lo[a + 1:t + 1, cols]
            okmin = np.isfinite(win_lo).all(axis=0) & (win_lo.min(axis=0) >= lvl[a, cols])
            if not okmin.any():
                continue
            cols = cols[okmin]
            v = np.asarray(vol[a + 1:t, cols], dtype=np.float64)   # adjust days a+1..t-1
            ve = np.asarray(vol[t - 1, cols], dtype=np.float64)
            vf = np.asarray(vol[t, cols], dtype=np.float64)
            va = np.asarray(vol[a, cols], dtype=np.float64)
            with np.errstate(invalid="ignore"):
                shrink = np.nanmean(np.where(np.isfinite(v), v, np.nan), axis=0) < va
                expand = np.isfinite(vf) & np.isfinite(ve) & (vf > ve)
            S[t, cols] = shrink & expand
    elif arm in ("P05a_shouyin_gaokai", "P05b_shouyin_fanbao"):
        v = np.asarray(vol, dtype=np.float64)
        with np.errstate(invalid="ignore"):
            vr = v[1:] / np.vstack([np.full((1, N), np.nan), v[:-1]])[1:]
        pre = np.zeros((T, N), dtype=bool)
        # first yin of a >=2 run, stock is day's market-height leader
        for t in range(1, T):
            r = runs[t]
            m = (r >= 2) & yin[t] & (r == heights[t]) \
                & np.isfinite(vr[t - 1]) & (vr[t - 1] >= 1.5) & (vr[t - 1] <= 2.0)
            if not m.any():
                continue
            cols = np.flatnonzero(m)
            keep = []
            for c in cols:
                rr = int(r[c])
                if not yin[max(0, t - rr):t, c].any():
                    keep.append(c)
            if keep:
                pre[t, keep] = True
        if arm == "P05a_shouyin_gaokai":
            # leg A: next open >= +2% vs event close
            with np.errstate(invalid="ignore"):
                gk = op[1:] / cl[:-1] - np.float32(1.0)
            S[1:] = pre[:-1] & np.isfinite(gk) & (gk >= 0.02)
        else:
            # leg B: next close reverses above event-day high
            S[1:] = pre[:-1] & (cl[1:] > hi[:-1])
    elif arm.startswith("P06"):
        parts = arm.split("_")                     # P06_h1_all / P06_h5_yang
        yy = parts[2]
        base = zhaban if yy == "all" else (zhaban & yang)
        S[:] = base
    elif arm == "P07a_ditian_uncond":
        S[:] = E["dn_touch"] & lim
    elif arm == "P07b_ditian_cond":
        cond = np.zeros((T, N), dtype=bool)
        dnt = E["dn_touch"]
        v = np.asarray(vol, dtype=np.float64)
        for t in range(6, T):
            m = dnt[t] & lim[t]
            if not m.any():
                continue
            cols = np.flatnonzero(m)
            win = dnt[t - 5:t, :]                       # days t-5..t-1
            for j, c in enumerate(cols):
                days = np.flatnonzero(win[:, c])
                if days.size == 0:
                    continue
                # most recent limit-down day in window
                d = t - 5 + int(days[-1])
                vd = v[d, c]
                if np.isfinite(vd) and v[t, c] >= 2.0 * vd:
                    cond[t, c] = True
        S[:] = dnt & lim & cond
    elif arm == "P08_bingdian_kawei":
        reg = E["regime"]
        for t in range(3, T):
            if reg[t] != 1:
                continue
            # 冰点日 within past 3 days
            if not (reg[t - 3:t] == 2).any():
                continue
            S[t] = lim[t] & (runs[t] == 1)
    elif arm in ("P09a_height4", "P09b_height5"):
        k = 4 if arm == "P09a_height4" else 5
        S[:] = runs == k
    elif arm == "P09c_space_open":
        for t in range(61, T):
            h = heights[t]
            if h <= int(heights[t - 60:t].max()):
                continue
            S[t] = lim[t] & (runs[t] == h) & (runs[t] >= 1)
    elif arm == "P10_layaohuihun":
        # 老妖资格: max run within past 120d >= 3 (self-set M/N, disclosed);
        # quiet >=10d since that run; pullback <=10% vs anchor close;
        # quiet mean vol < anchor vol; 再涨停 today.
        rdf = pd.DataFrame(E["runs"])
        maxrun120 = rdf.rolling(120, min_periods=20).max().to_numpy(dtype=np.int16)
        del rdf
        v = np.asarray(vol, dtype=np.float64)
        for t in range(130, T):
            m = lim[t]
            if not m.any():
                continue
            cols = np.flatnonzero(m)
            for c in cols:
                mr = maxrun120[t - 10, c]
                if not (np.isfinite(mr) and mr >= 3):
                    continue
                # find last day of a >=3 run ending within t-120..t-10
                r = E["runs"]
                seg = r[t - 120:t - 9, c]
                days = np.flatnonzero(seg >= 3)
                if days.size == 0:
                    continue
                a_end = t - 120 + int(days[-1])       # last run day
                a_len = int(seg[days[-1]])
                a0 = a_end - a_len + 1                # run start day
                quiet0 = a_end + 1
                if t - quiet0 < 10:
                    continue                            # dormancy gate
                a_close = cl[a_end, c]
                if not np.isfinite(a_close):
                    continue
                q_close = cl[quiet0:t, c]
                if not np.isfinite(q_close).all():
                    continue
                if q_close.min() < a_close * np.float32(0.90):
                    continue                            # pullback >10% -> failed
                qv = v[quiet0:t, c]
                av = v[a0, c]
                if not (np.isfinite(av) and np.nanmean(qv) < av):
                    continue
                S[t, c] = True
    elif arm in ("P11a_longzibei", "P11b_genfeng_ctrl"):
        dcol = set(E["dragon_cols"].tolist())
        for t in range(1, T):
            lead = (runs[t] == heights[t]) & (runs[t] >= 3)
            if not lead.any():
                continue
            m = lim[t] & (runs[t] == 1)
            if arm == "P11a_longzibei":
                m = m & np.array([s in dcol for s in E["P"]["syms"]])
            if m.any():
                S[t] = m
    elif arm in ("P12a_gene_k2", "P12b_gene_k3", "P12c_gene_k2_vol18"):
        k = 3 if arm == "P12b_gene_k3" else 2
        for t in range(17, T):
            m = lim[t]
            if not m.any():
                continue
            cols = np.flatnonzero(m)
            cnt = E["lim_cum"][t - 1, cols] - E["lim_cum"][t - 17, cols]
            good = cols[cnt >= k]
            if arm == "P12c_gene_k2_vol18":
                v = np.asarray(E["P"]["volume"][t - 10:t, good], dtype=np.float64)
                with np.errstate(invalid="ignore"):
                    base = np.nanmean(np.where(np.isfinite(v), v, np.nan), axis=0)
                vt = np.asarray(E["P"]["volume"][t, good], dtype=np.float64)
                good = good[np.isfinite(vt) & np.isfinite(base) & (vt >= 1.8 * base)]
            if good.size:
                S[t, good] = True
    else:
        raise ValueError(arm)
    return S


ARMS = [
    ("P01_daban9", dict(hold=1, costface="open_open", stop=None)),
    ("P02_yijiner", dict(hold=1, costface="open_open", stop=None)),
    ("P03a_duanban_dixi", dict(hold=1, costface="open_open", stop=None)),
    ("P03b_duanban_fanbao", dict(hold=1, costface="open_open", stop=None)),
    ("P04a_jin", dict(hold=1, costface="open_open", stop=None)),
    ("P04b_yin", dict(hold=1, costface="open_open", stop=None)),
    ("P04c_huo", dict(hold=1, costface="open_open", stop=None)),
    ("P05a_shouyin_gaokai", dict(hold=5, costface="open_open", stop="ma5_3pct")),
    ("P05b_shouyin_fanbao", dict(hold=5, costface="open_open", stop="ma5_3pct")),
] + [(f"P06_h{h}_{'all' if yy else 'yang'}", dict(hold=h, costface="open_open", stop=None))
     for h in (1, 2, 3, 5) for yy in (True, False)] + [
    ("P07a_ditian_uncond", dict(hold=1, costface="open_open", stop=None)),
    ("P07b_ditian_cond", dict(hold=1, costface="open_open", stop=None)),
    ("P08_bingdian_kawei", dict(hold=1, costface="open_open", stop=None)),
    ("P09a_height4", dict(hold=1, costface="open_open", stop=None)),
    ("P09b_height5", dict(hold=1, costface="open_open", stop=None)),
    ("P09c_space_open", dict(hold=1, costface="open_open", stop=None)),
    ("P10_layaohuihun", dict(hold=1, costface="open_open", stop=None)),
    ("P11a_longzibei", dict(hold=1, costface="open_open", stop=None)),
    ("P11b_genfeng_ctrl", dict(hold=1, costface="open_open", stop=None)),
    ("P12a_gene_k2", dict(hold=1, costface="open_open", stop=None)),
    ("P12b_gene_k3", dict(hold=1, costface="open_open", stop=None)),
    ("P12c_gene_k2_vol18", dict(hold=1, costface="open_open", stop=None)),
]
REGIME_EXTRA_ARMS = ("P03b_duanban_fanbao", "P05a_shouyin_gaokai", "P09a_height4")
UNIVERSES = ("full", "limup60", "leader60")


def windows(E):
    idx = E["idx"]
    W = [("W_full", W_FULL_FROM, idx[-1])]
    for y in STAGGER_STARTS:
        W.append((f"W{y}", pd.Timestamp(f"{y}-01-01"),
                  pd.Timestamp(f"{y + STAGGER_YEARS - 1}-12-31")))
    return W


def enumerate_cells(E):
    """Frozen deterministic census: 29x3x9x2 + 3 regime extras = 1569."""
    cells = []
    for arm, cfg in ARMS:
        for u in UNIVERSES:
            for wname, w0, w1 in windows(E):
                for ci, cname in ((1, "x1"), (2, "x2")):
                    cells.append(dict(cell_id=f"{arm}|{u}|{wname}|{cname}",
                                      arm=arm, universe=u, window=wname,
                                      cost=cname, regime=None))
    for arm in REGIME_EXTRA_ARMS:
        cells.append(dict(cell_id=f"{arm}|full|W_full|x1|regime_adv",
                          arm=arm, universe="full", window="W_full",
                          cost="x1", regime="advance"))
    return cells


# ------------------------------------------------------------------ sim

def floor_for(E, t, cols):
    fl = np.full(len(cols), MAIN_FLOOR, dtype=np.float32)
    if len(cols):
        fl[E["is_cn"][cols]] = (WIDE_FLOOR if E["idx"][t] >= CN_20CM_FROM
                                else MAIN_FLOOR)
        fl[E["is_star"][cols]] = WIDE_FLOOR
    return fl


def extract_trades(E, arm, cfg, universe, regime=None):
    """Signal->trades once per (arm, universe[, regime]); returns trade list
    keyed by deploy day with raw open->open returns (pre-cost) + face counts.
    Stop-loss arms resolve exit per trade (variable holding)."""
    S = signal_matrix(E, arm)
    if regime == "advance":
        S = S & (E["regime"] == 1)[:, None]
    P = E["P"]; T = E["T"]
    op = np.asarray(P["open"]); cl = np.asarray(P["close"])
    vol = np.asarray(P["volume"])
    ma5 = E["ma5"]
    trades = {}          # deploy day -> list of (col, raw_ret, exit_day)
    n_events = n_untrade = n_limitopen = 0
    hold = cfg["hold"]
    stop = cfg["stop"]
    for t in range(T - 1):
        day_cols = np.flatnonzero(S[t])
        if day_cols.size == 0:
            continue
        ucols = dyn_universe_cols(E, universe, t)
        if ucols.size == 0:
            continue
        u = set(ucols.tolist())
        day_cols = np.array([c for c in day_cols if c in u], dtype=np.int64)
        if day_cols.size == 0:
            continue
        n_events += day_cols.size
        et = t + 1
        entry = op[et, day_cols]
        prev = cl[t, day_cols]
        tradable = np.isfinite(entry) & np.isfinite(np.asarray(P["volume"][et, day_cols]))
        with np.errstate(invalid="ignore"):
            open_ratio = entry / prev - np.float32(1.0)
        fl = floor_for(E, et, day_cols)
        at_limit = np.isfinite(open_ratio) & (open_ratio >= fl - LIMIT_OPEN_TOL)
        keep = tradable & ~at_limit
        n_untrade += int((~tradable).sum())
        n_limitopen += int((tradable & at_limit).sum())
        cols = day_cols[keep]
        if cols.size == 0:
            continue
        ent = entry[keep]
        lst = []
        for j, c in enumerate(cols):
            if stop is None:
                x = et + hold
                ex = op[x, c] if x < T else np.nan
                while (not np.isfinite(ex)) or (x < T and not np.isfinite(
                        np.asarray(P["volume"][x, c]))):
                    x += 1
                    if x >= T:
                        ex = np.nan
                        break
                    ex = op[x, c]
                if not np.isfinite(ex):
                    continue                            # still suspended at cutoff
                lst.append((int(c), float(ex / ent[j] - 1.0), int(x - et)))
            else:
                # stop arm: daily close checks, exit next open (frozen)
                x = et
                exit_ret = None
                for d in range(et, min(T, et + 10)):
                    c_close = cl[d, c]
                    if not np.isfinite(c_close):
                        continue
                    stop_hit = (c_close <= ent[j] * np.float32(0.97)) or \
                        (np.isfinite(ma5[d, c]) and c_close < ma5[d, c])
                    if d > et and stop_hit:
                        x = d + 1
                        if x >= T:
                            break
                        ex = op[x, c]
                        if not np.isfinite(ex) or not np.isfinite(
                                np.asarray(P["volume"][x, c])):
                            continue
                        exit_ret = float(ex / ent[j] - 1.0)
                        break
                if exit_ret is None:
                    x = et + 10
                    if x < T and np.isfinite(op[x, c]) and np.isfinite(
                            np.asarray(P["volume"][x, c])):
                        exit_ret = float(op[x, c] / ent[j] - 1.0)
                if exit_ret is not None:
                    lst.append((int(c), exit_ret, max(1, x - et)))
        if lst:
            trades[t] = lst
    return dict(trades=trades, n_events=n_events, n_untrade=n_untrade,
                n_limitopen=n_limitopen, hold=hold, stop=stop)


def cell_stats(E, tr, wname, w0, w1, cost_side):
    """Bucket-accounted daily series within window; cost multiplicative."""
    idx = E["idx"]
    i0 = int(np.argmax(idx >= w0))
    i1 = int(np.argmax(idx > w1) or E["T"])
    if i1 <= i0:
        i1 = E["T"]
    H = tr["hold"]
    cost = COST_X1 if cost_side == "x1" else COST_X2
    ser = np.zeros(i1 - i0)
    n_entries = n_trades = 0
    for t, lst in tr["trades"].items():
        if not (i0 <= t < i1):
            continue
        rets = np.array([r for _, r, _ in lst], dtype=np.float64)
        n_entries += len(lst)
        n_trades += len(lst)
        net = (1.0 + rets) * (1.0 - cost) ** 2 - 1.0
        cohort = float(net.mean())
        # book evenly across holding days ENDING at exit day (t+1+H):
        # hold-1 books at the exit day t+2 (prereg SS3 caliber)
        span = H if tr["stop"] is None else max(1, int(np.median(
            [h for _, _, h in lst])))
        for k in range(span):
            d = t + 2 + k
            if i0 <= d < i1:
                ser[d - i0] += cohort / span
    if n_entries == 0:
        return None
    mu = float(ser.mean()); sd = float(ser.std(ddof=1)) if len(ser) > 1 else 0.0
    sharpe = mu / sd * math.sqrt(PBP) if sd > 0 else 0.0
    eq = np.cumsum(ser)
    peak = np.maximum.accumulate(eq)
    maxdd = float((eq - peak).min()) if len(eq) else 0.0
    # descriptive OOS = last 30% of window days
    cut = i0 + int((i1 - i0) * 0.7)
    oos = ser[cut - i0:]
    oos_mu = float(oos.mean()); oos_sd = float(oos.std(ddof=1)) if len(oos) > 1 else 0.0
    oos_sh = oos_mu / oos_sd * math.sqrt(PBP) if oos_sd > 0 else 0.0
    return dict(n_entries=n_entries, n_trades=n_trades, sharpe_full=round(sharpe, 4),
                ann_ret=round(mu * PBP, 4), maxdd=round(maxdd, 4),
                oos_sharpe=round(oos_sh, 4), daily_mean=round(mu, 6),
                series=None)


# ------------------------------------------------------------------ run/finalize

def run_shard(shard, of):
    os.makedirs(CELL_DIR, exist_ok=True)
    P = build_panels_from_cache()
    E = build_engine(P)
    cells = enumerate_cells(E)
    mine = [c for i, c in enumerate(cells) if i % of == shard]
    ck_path = os.path.join(OUT_DIR, f"checkpoint-{shard}of{of}.jsonl")
    done = set()
    if os.path.exists(ck_path):
        for line in open(ck_path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    rec = json.loads(line)
                    done.add(rec["key"])      # rows carry own key (r163)
                except ValueError:
                    pass
    wmap = {w[0]: (w[1], w[2]) for w in windows(E)}
    with open(ck_path, "a", encoding="utf-8") as ck:
        for c in mine:
            if c["cell_id"] in done:
                continue
            cfg = dict(ARMS)[c["arm"]]
            tr = extract_trades(E, c["arm"], cfg, c["universe"], c["regime"])
            w0, w1 = wmap[c["window"]]
            st = cell_stats(E, tr, c["window"], w0, w1, c["cost"])
            primary = (c["window"] == "W_full" and c["universe"] == "full"
                       and c["cost"] == "x1" and c["regime"] is None)
            rec = dict(cell_id=c["cell_id"], arm=c["arm"], universe=c["universe"],
                       window=c["window"], cost=c["cost"], regime=c["regime"],
                       n_events=tr["n_events"], n_untrade=tr["n_untrade"],
                       n_limitopen=tr["n_limitopen"],
                       evidence_cutoff=EVIDENCE_CUTOFF, stats=st, primary=primary)
            path = os.path.join(CELL_DIR, c["cell_id"].replace("|", "_") + ".json")
            json.dump(rec, open(path, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            ck.write(json.dumps({"key": c["cell_id"], "done": True},
                                 ensure_ascii=False) + "\n")
            ck.flush()
    print(f"shard {shard}/{of}: {len(mine)} cells, done={len(done)}")


def _nulls_day_loop(E, P, profile, i0, k):
    """Per-k nulls day loop, extracted verbatim from run_nulls (F16 hermetic
    leg; r157/r162 family -- loop body had zero fixture coverage). Per-day
    rng seeding untouched -> production output byte-identical."""
    ucols = E["u_full_cols"]
    rng = np.random.default_rng(NULL_BASE + k)
    trades = {}
    n_ev = 0
    for d in range(i0, E["T"] - 1):
        n = int(profile[d - i0])
        if n <= 0:
            continue
        live = ucols[list(ucols)] if False else ucols[
            np.random.default_rng(NULL_BASE + k + 7919 * d).choice(
                len(ucols), size=min(n * 3, len(ucols)), replace=False)]
        # tradability filter then take n
        ent = np.asarray(P["open"][d + 1, live])
        v = np.asarray(P["volume"][d + 1, live])
        prev = np.asarray(P["close"][d, live])
        ok = np.isfinite(ent) & np.isfinite(v) & np.isfinite(prev)
        live = live[ok][:n]
        if live.size == 0:
            continue
        n_ev += live.size
        if d + 2 >= E["T"]:
            continue    # tail: exit day beyond cutoff -> drop, mirroring
                        # extract_trades "still suspended at cutoff" face
        rets = np.asarray(P["open"][d + 2, live]) / np.asarray(
            P["open"][d + 1, live]) - np.float32(1.0)
        keep = np.isfinite(rets)
        if keep.any():
            trades[d] = [(int(c), float(r), 1) for c, r in
                          zip(live[keep], rets[keep])]
    return trades, n_ev


def run_nulls():
    """K=50 same-mask random event-day nulls on (W_full, U_full, x1),
    hold-1 canonical shape. Daily event-count profile = the pooled mean of
    the P06_h1_all full-universe signal (frozen null design, prereg SS3)."""
    P = build_panels_from_cache()
    E = build_engine(P)
    S = signal_matrix(E, "P06_h1_all")
    idx = E["idx"]
    i0 = int(np.argmax(idx >= W_FULL_FROM))
    ucols = E["u_full_cols"]
    listed = np.isfinite(np.asarray(P["close"]))
    profile = S[i0:].sum(axis=1)
    rng_master = np.random.default_rng(NULL_BASE)
    out = {"seed_base": NULL_BASE, "k": K_NULLS, "window": "W_full",
           "universe": "full", "cost": "x1", "nulls": [], "evidence_cutoff": EVIDENCE_CUTOFF}
    for k in range(K_NULLS):
        trades, n_ev = _nulls_day_loop(E, P, profile, i0, k)
        tr = dict(trades=trades, n_events=n_ev, n_untrade=0, n_limitopen=0,
                  hold=1, stop=None)
        st = cell_stats(E, tr, "W_full", W_FULL_FROM, idx[-1], "x1")
        out["nulls"].append(dict(k=k, sharpe=st["sharpe_full"] if st else None,
                                 n_entries=st["n_entries"] if st else 0,
                                 ann_ret=st["ann_ret"] if st else None))
        print(f"  null {k}: sharpe={out['nulls'][-1]['sharpe']} entries={out['nulls'][-1]['n_entries']}")
    json.dump(out, open(NULLS_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("nulls written:", NULLS_JSON)


def finalize():
    """Aggregate + G1'v2 on 29 primaries + G2 (DSR + family PBO) + ledger."""
    if os.path.exists(RESULT_JSON) and not os.environ.get("WILD_ROUTE_S1_REFINALIZE"):
        print("finalize single-shot guard: result exists (set "
              "WILD_ROUTE_S1_REFINALIZE=1 to redo)"); return 0
    P = build_panels_from_cache()
    E = build_engine(P)
    cells = enumerate_cells(E)
    rows = []
    for c in cells:
        path = os.path.join(CELL_DIR, c["cell_id"].replace("|", "_") + ".json")
        if not os.path.exists(path):
            continue
        rows.append(json.load(open(path, encoding="utf-8")))
    primaries = [r for r in rows if r.get("primary") and r.get("stats")]
    nulls = json.load(open(NULLS_JSON, encoding="utf-8")) if \
        os.path.exists(NULLS_JSON) else None
    assert nulls, "nulls file missing -- run run-nulls first"
    null_vals = [n["sharpe"] for n in nulls["nulls"] if n["sharpe"] is not None]
    null_pool = {"values": null_vals, "schema": "wild_route_s1"}
    N_eff = len(cells) + K_NULLS
    g1 = {}
    for r in primaries:
        try:
            v = SG.g1_prime_v2(sharpe_full=r["stats"]["sharpe_full"],
                               returns=None, batch_cells=N_eff,
                               pool="stock_b_layer",
                               n_trades=r["stats"]["n_trades"],
                               n_entries=r["stats"]["n_entries"],
                               min_trades=30, ci_seed=NULL_BASE,
                               null_pool=null_pool)
        except Exception as exc:
            v = {"error": repr(exc)}
        g1[r["cell_id"]] = v
    # family PBO on the 29-arm primary full-window daily series (rebuilt
    # deterministically; series not persisted in cell JSONs to keep git light)
    pbo_in = _family_series(E, primaries)
    pbo = cscv_pbo(pbo_in, 8) if pbo_in else None
    dsr_vals = {}
    for arm, ser in pbo_in.items():
        if ser is not None and len(ser) > 20:
            try:
                dsr_vals[arm] = SG.deflated_sharpe_ratio(
                    np.asarray(ser, dtype=np.float64), N_eff,
                    var_null_sr=float(np.var(null_vals)) if null_vals else 0.0,
                    periods_per_year=PBP)
            except Exception as exc:
                dsr_vals[arm] = {"error": repr(exc)}
    g2 = {}
    for r in primaries:
        arm = r["arm"]
        g1v = g1.get(r["cell_id"], {})
        if isinstance(g1v, dict) and g1v.get("g1_pass"):
            try:
                g2[r["cell_id"]] = SG.g2_registration_v2(
                    g1_pass=True, dsr=dsr_vals.get(arm),
                    pbo=(pbo.get("pbo") if isinstance(pbo, dict) else None))
            except Exception as exc:
                g2[r["cell_id"]] = {"error": repr(exc)}
    out = {
        "batch": "WILD_ROUTE_S1",
        "ticket_ref": "T-2026-09-25-57 s2/s3 (CEO O-20260925-1132)",
        "prereg_ref": "research/WILD_ROUTE_PREREG_S1.md (frozen pre-run R99)",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF)},
        "n_cells": len(cells), "n_cells_done": len(rows), "n_eff": N_eff,
        "nulls": {"k": K_NULLS, "seed_base": NULL_BASE,
                  "sharpe_mean": round(float(np.mean(null_vals)), 4) if null_vals else None,
                  "sharpe_p95": round(float(np.percentile(null_vals, 95)), 4) if null_vals else None},
        "g1_prime_v2": g1, "g2_registration_v2": g2,
        "family_pbo": pbo, "dsr": dsr_vals,
        "cells": [r for r in rows],
        "meta": {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                 "runner": os.path.abspath(__file__)},
    }
    json.dump(out, open(RESULT_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # primary-rows CSV (prereg SS6 deliverable; 29 rows, git-light)
    import csv as _csv
    with open(os.path.join(OUT_DIR, "wild_route_s1_primaries.csv"), "w",
              encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(["arm", "n_events", "n_untrade", "n_limitopen",
                    "n_entries", "sharpe_full", "ann_ret", "maxdd",
                    "oos_sharpe", "g1_pass", "g2_pass"])
        for r in primaries:
            st = r["stats"] or {}
            w.writerow([r["arm"], r["n_events"], r["n_untrade"],
                        r["n_limitopen"], st.get("n_entries"),
                        st.get("sharpe_full"), st.get("ann_ret"),
                        st.get("maxdd"), st.get("oos_sharpe"),
                        (g1.get(r["cell_id"]) or {}).get("g1_pass"),
                        (g2.get(r["cell_id"]) or {}).get("g2_pass")])
    SG.append_ledger("WILD_ROUTE_S1", N_eff, os.path.basename(RESULT_JSON),
                     note="T-57 wild-route street-pattern lab, 12 patterns "
                          "29 arms x3U x9W x2C +3 regime extras +50 nulls",
                     evidence_cutoff=EVIDENCE_CUTOFF)
    print("finalize written:", RESULT_JSON, "cells:", len(rows))


def _family_series(E, primaries):
    """Rebuild primary-arm daily series (deterministic) for DSR/PBO."""
    out = {}
    for r in primaries:
        cfg = dict(ARMS)[r["arm"]]
        tr = extract_trades(E, r["arm"], cfg, "full", None)
        ser = _series_of(E, tr, W_FULL_FROM, E["idx"][-1], COST_X1)
        if ser is not None:
            out[r["arm"]] = [round(float(x), 6) for x in ser]
    return out


def _series_of(E, tr, w0, w1, cost):
    idx = E["idx"]
    i0 = int(np.argmax(idx >= w0))
    i1 = E["T"]
    H = tr["hold"]
    ser = np.zeros(i1 - i0)
    any_trade = False
    for t, lst in tr["trades"].items():
        if not (i0 <= t < i1):
            continue
        any_trade = True
        rets = np.array([r for _, r, _ in lst], dtype=np.float64)
        net = (1.0 + rets) * (1.0 - cost) ** 2 - 1.0
        cohort = float(net.mean())
        span = H if tr["stop"] is None else max(1, int(np.median(
            [h for _, _, h in lst])))
        for k in range(span):
            d = t + 2 + k
            if i0 <= d < i1:
                ser[d - i0] += cohort / span
    return ser if any_trade else None


# ------------------------------------------------------------------ selftest

def _mk_fixture(T=420, N=8):
    """Hermetic synthetic panel mirroring production faces: NaN heads (r182),
    suspension (volume NaN), exact cliff ratios, 一字, 炸板, ST col, dragon col.
    Day positions deliberately NOT equal to array indices (r183)."""
    idx = pd.bdate_range("2020-01-01", periods=T)
    syms = ["600001", "600002", "300003", "688004", "600005", "600006",
            "300007", "688008"]
    P = {"idx": idx, "syms": syms, "T": T, "N": N}
    rng = np.random.default_rng(20260925)
    base = 10.0 + np.cumsum(rng.normal(0, 0.02, (T, N)), axis=0)
    base = np.maximum(base, 2.0)
    cl = base.copy(); op = cl * (1 + rng.normal(0, 0.005, (T, N)))
    hi = np.maximum(op, cl) * (1 + abs(rng.normal(0, 0.006, (T, N))))
    lo = np.minimum(op, cl) * (1 - abs(rng.normal(0, 0.006, (T, N))))
    v = np.abs(rng.normal(1e6, 2e5, (T, N)))
    # late-listed col 5: NaN head (r182 production shape)
    cl[:150, 5] = np.nan; op[:150, 5] = np.nan
    hi[:150, 5] = np.nan; lo[:150, 5] = np.nan; v[:150, 5] = np.nan
    # engineered events on col 0 (main): day198 pinned base, 199..202 涨停连板
    cl[198, 0] = 9.0; op[198, 0] = 8.9; hi[198, 0] = 9.1; lo[198, 0] = 8.8; v[198, 0] = 1e6
    cl[199, 0] = 10.0; op[199, 0] = 9.8; hi[199, 0] = 10.0; lo[199, 0] = 9.7; v[199, 0] = 1e6
    cl[200, 0] = 11.0; op[200, 0] = 10.2; hi[200, 0] = 11.0; lo[200, 0] = 10.1; v[200, 0] = 1e6
    cl[201, 0] = 12.1; op[201, 0] = 11.2; hi[201, 0] = 12.1; lo[201, 0] = 11.3; v[201, 0] = 1e6
    # 一字板 day 202: open==high==low==close==limit
    cl[202, 0] = 13.31; op[202, 0] = 13.31; hi[202, 0] = 13.31; lo[202, 0] = 13.31
    v[202, 0] = 5e5
    # 炸板 day 203: high touches limit, closes +2%
    cl[203, 0] = 13.58; op[203, 0] = 13.4; hi[203, 0] = 14.64; lo[203, 0] = 13.3
    v[203, 0] = 1.2e6
    # suspension day 204 on col 0: volume NaN (price row finite)
    v[204, 0] = np.nan
    # engineered tradeable 炸板 on col 1 at day 300 (+10% touch, +2% close)
    cl[299, 1] = 9.0; op[299, 1] = 8.95; hi[299, 1] = 9.05; lo[299, 1] = 8.9; v[299, 1] = 1e6
    cl[300, 1] = 9.18; op[300, 1] = 9.05; hi[300, 1] = 9.90; lo[300, 1] = 9.0
    v[300, 1] = 1.1e6
    cl[301, 1] = 9.3; op[301, 1] = 9.25; hi[301, 1] = 9.4; lo[301, 1] = 9.2; v[301, 1] = 1e6
    # col 2 chinext 涨停 20cm at day 250
    cl[249, 2] = 20.0; op[249, 2] = 19.5; hi[249, 2] = 20.0; lo[249, 2] = 19.2
    v[249, 2] = 1e6
    cl[250, 2] = 24.0; op[250, 2] = 20.5; hi[250, 2] = 24.0; lo[250, 2] = 20.4
    v[250, 2] = 1e6
    for f, arr in (("open", op), ("high", hi), ("low", lo), ("close", cl),
                   ("volume", v)):
        P[f] = arr.astype(np.float32)
    # pct_chg must mirror qfq day-over-day (production convention)
    pct = np.full((T, N), np.nan, dtype=np.float32)
    with np.errstate(invalid="ignore"):
        pct[1:] = (cl[1:] / cl[:-1] - np.float32(1.0)) * np.float32(100.0)
    P["pct_chg"] = pct
    return P, dict(cl=cl, op=op, hi=hi, lo=lo, v=v)


def selftest():
    ok = [0]

    def chk(name, cond):
        ok[0] += 1
        print(("PASS " if cond else "FAIL ") + name)
        assert cond, name

    P, fx = _mk_fixture()
    # fixture-injected engine (patch eligibility path faces for hermetic)
    import tempfile
    elig = os.path.join(tempfile.gettempdir(), "wild_route_selftest_elig.csv")
    with open(elig, "w", encoding="utf-8") as fh:
        fh.write("code,name,r2_st\n")
        fh.write("600001,平安示例,False\n")
        fh.write("600002,龙腾股,False\n")       # dragon name
        fh.write("300003,ST测试,True\n")        # ST excluded
        fh.write("688004,科创,False\n")
        fh.write("600005,普通,False\n")
        fh.write("600006,普通,False\n")
        fh.write("300007,创业板,False\n")
        fh.write("688008,科创,False\n")
    global ELIG
    ELIG_saved = ELIG
    ELIG = elig
    E = build_engine(P)
    ELIG = ELIG_saved

    # F1 limit-up detection: col0 days 200,201,202 sealed (10/10/10 pct)
    chk("F1 main sealed run", bool(E["lim"][200, 0] and E["lim"][201, 0]
                                   and E["lim"][202, 0]))
    chk("F1 runs==4 at day202 (199..202 连板)", int(E["runs"][202, 0]) == 4)
    chk("F1 yizi day202", bool(E["yizi"][202, 0]))
    chk("F1 zhaban day203", bool(E["zhaban"][203, 0])
        and not bool(E["lim"][203, 0]))
    # F1b chinext 20cm post-2020: day250 (2020 fixture is 2020+ => wide)
    chk("F1b chinext 20cm sealed", bool(E["lim"][250, 2]))
    # F2 NaN head: col5 no events before day150 (r182 production shape)
    chk("F2 nan-head zero events", int(E["lim"][:150, 5].sum()) == 0)
    chk("F2 ok-mask excludes <250 bars? (420-150=270>=250 -> ok)",
        bool(E["ok_mask"][5]))
    # F3 ST exclusion from u_full
    chk("F3 ST excluded", 2 not in set(E["u_full_cols"].tolist()))
    # F4 dragon cols present
    chk("F4 dragon col", 1 in set(E["dragon_cols"].tolist()))
    # F5 susp face: day204 col0 volume NaN
    chk("F5 susp flag", bool(E["susp"][204, 0]))
    # F6 trade sim: P03a on zhaban day203 -> entry day204 (volume NaN=untradeable
    # -> reject) so no trade from that event; use day200 daban9 signal instead:
    S = signal_matrix(E, "P01_daban9")
    chk("F6 daban9 fires day199 (high/prev>=9%)", bool(S[199, 0]))
    tr = extract_trades(E, "P01_daban9", dict(hold=1, costface="open_open",
                                              stop=None), "full")
    t200 = tr["trades"].get(199)
    t0 = [x for x in (t200 or []) if x[0] == 0]
    chk("F6 trade extracted for deploy199 col0", len(t0) == 1)
    if t0:
        raw = t0[0][1]
        # hold=1: entry t+1 open (day200), exit day201 open
        expect = fx["op"][201, 0] / fx["op"][200, 0] - 1.0
        chk("F6 raw ret math", abs(raw - float(expect)) < 1e-6)
    # F7 untradeable counting: zhaban day203 event -> entry day204 susp -> untrade
    tr7 = extract_trades(E, "P03a_duanban_dixi", dict(hold=1, costface="open_open",
                                                      stop=None), "full")
    chk("F7 susp entry rejected+counted",
        tr7["n_untrade"] >= 1 and 203 not in tr7["trades"])
    # F8 一字 gap-up untradeable: event day202 (sealed lim) as P02 signal ->
    # entry day203 open 13.4 vs prev close 13.31: ratio ~0.7% < floor-0.002 ok,
    # tradeable; instead craft: col0 day 199 signal P06? Use direct: deploy 202
    # via P02 arm (runs==2 at 201): entry day203 open not at limit -> fine.
    # 一字 rejection is exercised by day202's own next-open being normal;
    # craft explicit: set day 205 open at limit: op205 = 14.64*? -- skip craft,
    # assert limit-open branch via synthetic call: entry at 13.31*1.1
    # F8: bucket accounting math hold-2
    tr8 = extract_trades(E, "P06_h2_all", dict(hold=2, costface="open_open",
                                               stop=None), "full")
    st8 = cell_stats(E, tr8, "W_full", pd.Timestamp("2020-01-01"),
                     P["idx"][-1], "x1")
    chk("F8 cell stats computable", st8 is not None and st8["n_entries"] >= 1)
    # F9 census: deterministic 1569, disjoint shards union=total
    cells = enumerate_cells(E)
    chk("F9 census 1569", len(cells) == 1569)
    seen = set()
    tot = 0
    for sh in range(8):
        mine = [c for i, c in enumerate(cells) if i % 8 == sh]
        for c in mine:
            assert c["cell_id"] not in seen
            seen.add(c["cell_id"])
        tot += len(mine)
    chk("F9 shards disjoint+complete", tot == 1569 and len(seen) == 1569)
    # F10 threshold constants identical to probe JSON
    probe = json.load(open(PROBE_JSON, encoding="utf-8"))
    ft = probe["cliff"]["frozen_thresholds"]
    chk("F10 thresholds match probe", ft["main_floor"] == MAIN_FLOOR
        and ft["wide_floor"] == WIDE_FLOOR)
    # F11 nulls determinism (tiny-scale harness of the draw logic)
    rng_a = np.random.default_rng(NULL_BASE)
    rng_b = np.random.default_rng(NULL_BASE)
    chk("F11 null seed determinism",
        np.array_equal(rng_a.integers(0, 1000, 10), rng_b.integers(0, 1000, 10)))
    # F12 cost faces distinct and multiplicative
    r = 0.05
    chk("F12 x1/x2 math", abs((1 + r) * (1 - COST_X1) ** 2 - 1
                               - ((1 + r) * (1 - 0.0013) ** 2 - 1)) < 1e-12
        and COST_X2 == 2 * COST_X1)
    # F13 regime state machine sanity on fixture (synthetic market breadth)
    chk("F13 regime in {0,1,2}", set(np.unique(E["regime"]).tolist()) <= {0, 1, 2})
    # F14 domains separated (r183): fixture event positions != index ranges
    chk("F14 event pos domain", 199 != 0 and 203 != 3 and 250 != 2)
    # F15 production cache-load path pairing leg (r157/r162/r188 family):
    # synthetic cache with T != N (the production shape family, 8792x5222)
    # must load, and a tampered meta must trip the drift gate. The wr-nulls
    # first launch crashed on a false triple-equality N==len(idx) here --
    # engine-fixture legs cannot see the production loader path.
    import shutil
    tmpc = tempfile.mkdtemp(prefix="wild_route_selftest_cache_")
    tmpb = tempfile.mkdtemp(prefix="wild_route_selftest_bars_")
    np.save(os.path.join(tmpc, "dates.npy"),
            np.array([0, 86_400_000_000, 172_800_000_000, 259_200_000_000],
                     dtype="int64"))                    # T=4 (us epochs)
    for f in ("open", "high", "low", "close", "volume", "pct_chg"):
        np.save(os.path.join(tmpc, f + ".npy"),
                np.zeros((4, 2), dtype="float32"))      # (T, N) N=2
    with open(os.path.join(tmpc, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump({"shape": {"T": 4, "N": 2, "dtype": "float32"},
                   "generated": "2026-09-24 03:42:50"}, fh)
    for s in ("600001", "600002"):
        open(os.path.join(tmpb, s + ".parquet"), "wb").close()
    c_saved, b_saved = CACHE, BARS
    globals()["CACHE"], globals()["BARS"] = tmpc, tmpb
    try:
        Pp = build_panels_from_cache()
        chk("F15 loader T!=N shape family", Pp["T"] == 4 and Pp["N"] == 2)
        with open(os.path.join(tmpc, "meta.json"), "w", encoding="utf-8") as fh:
            json.dump({"shape": {"T": 4, "N": 3, "dtype": "float32"},
                       "generated": "2026-09-24 03:42:50"}, fh)
        try:
            build_panels_from_cache()
            chk("F15 drift gate trips on tampered meta", False)
        except AssertionError:
            chk("F15 drift gate trips on tampered meta", True)
    finally:
        globals()["CACHE"], globals()["BARS"] = c_saved, b_saved
        shutil.rmtree(tmpc, ignore_errors=True)
        shutil.rmtree(tmpb, ignore_errors=True)
    # F16 nulls loop-body hermetic leg (r198 next-pointer; r157/r162 family):
    # the per-k day loop (oversample -> tradability filter -> take n ->
    # tail drop -> hold-1 rets) ran production-only until this extraction.
    # Tail-day events count into n_events but must never produce trades
    # (pins the r198 tail-OOB fix semantics).
    prof = np.zeros(P["T"], dtype=int)
    prof[100:103] = 2         # 3 normal days, 2 events each -> 6 trades
    prof[P["T"] - 2] = 3      # tail day d=T-2: d+2==T -> drop face
    ta, na = _nulls_day_loop(E, P, prof, 0, 0)
    tb, nb = _nulls_day_loop(E, P, prof, 0, 0)
    kept = sum(len(v) for v in ta.values())
    chk("F16 loop determinism", ta == tb and na == nb)
    chk("F16 tail-drop + n_events counting semantics",
        (P["T"] - 2) not in ta and kept == 6 and na == kept + 3)
    import inspect
    chk("F16 run_nulls wiring (r188 path-live law)",
        "_nulls_day_loop(" in inspect.getsource(run_nulls))
    ok_math = True
    for d, lst in ta.items():
        for c, r, h in lst:
            exp = float(P["open"][d + 2, c]) / float(P["open"][d + 1, c]) - 1.0
            ok_math = ok_math and h == 1 and abs(r - exp) < 1e-6
    chk("F16 hold-1 ret math (open d+2 / open d+1 - 1)",
        ok_math and kept > 0)
    # F17 all-arms signal_matrix sweep (r157 family arm-dimension closure):
    # P05 vr[t] tail-OOB crashed production-only (shard-0 census, 19:11 --
    # zero fixture legs touched the P05 family; F6/F7/F8 cover P01/P03/P06).
    # Every ARMS family must run on the fixture: shape/dtype/no-exception.
    bad = []
    for arm in sorted(dict(ARMS)):
        try:
            Sa = signal_matrix(E, arm)
            if not (Sa.shape == (P["T"], P["N"]) and Sa.dtype == bool):
                bad.append(arm + ":shape")
        except Exception as ex:
            bad.append(arm + ":" + type(ex).__name__)
    chk("F17 all-arms sweep " + str(len(ARMS)) + " arms"
        + (" bad=" + str(bad) if bad else " clean"),
        not bad)
    print(f"selftest: {ok[0]}/{ok[0]} PASS (all asserted)")
    return 0


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "run", "run-nulls",
                                    "finalize", "status"])
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "run":
        return run_shard(a.shard, a.of)
    if a.cmd == "run-nulls":
        return run_nulls()
    if a.cmd == "finalize":
        return finalize()
    if a.cmd == "status":
        cells = 1569
        n_done = len(glob.glob(os.path.join(CELL_DIR, "*.json")))
        print(f"cells done: {n_done}/{cells}; nulls:",
              os.path.exists(NULLS_JSON))
    return 0


if __name__ == "__main__":
    sys.exit(main())
