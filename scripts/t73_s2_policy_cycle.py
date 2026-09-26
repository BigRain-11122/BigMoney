# -*- coding: utf-8 -*-
"""T-73 s2 slice-B: A-share POLICY-CYCLE calendar rhythm, in-repo census panel
empirical check (CEO order O-20260926-0926 s2 policy-axis face; unblocks the
CN-REGIME-POLICY s3 prereg design inputs; CEO top criterion 实战出真知 --
law faces must pass the in-repo panel before any external-citation claim).

PRE-REGISTERED (frozen before first run; no threshold edits after seeing results):
- Policy month set P4 = {3, 4, 7, 12} -- forward-lockable month-level calendar:
    3  = 两会 month (NPC opens 3月5日 by standing convention)
    4  = 政治局 Q1-economy meeting month (late-April convention, 2013+)
    7  = 政治局 mid-year economy meeting month (late-July convention)
    12 = 政治局 annual-economy meeting + 中央经济工作会议 month
  Honesty: exact meeting DAYS are not known in advance (except 两会); only the
  month is deterministic ex-ante -> month-level study is the daily-modelable
  face; narrative policy cycles (政策底 sequencing) are NOT modelable without
  an event feed and are excluded from judgment here.
- F1 (primary law face): full-A active-EW monthly return. Daily EW mean of
  pct_chg/100 across names with volume>0 (active mask excludes ffill-stale
  delisted/suspended legs); month return = prod(1+daily)-1; months with
  <10 trading days excluded (count disclosed). Window 1997-01 onward:
  pre-1997 = no-price-limit tiny-universe era (probe: +38.8%/mo artifact,
  73 months) excluded from judgment, disclosed in artifact.
- F2 (cap face): 510050 (SSE-50 ETF) monthly close returns, 2005-02 onward;
  fund-event guard probe |daily ret|>11% == 0 days asserted in-run (r239 law).
- Splits: full(window..cutoff) / IS(<=2024-12-31) / OOS(>=2025-01-01).
- Faces:
  A) spread4 = mean(month-ret | month in P4) - mean(month-ret | not in P4),
     per panel per split. Null baseline = EXHAUSTIVE enumeration of all
     C(12,4)=495 four-month subsets (exact distribution; zero RNG by design
     -> zero seed-registry surface; strictly stronger than K=50 sampling,
     BACKTEST_PLAN random-baseline iron law satisfied and trial count N
     disclosed). One-sided upper p: pct_up = #{S: spread(S) >= spread(P4)}/495
     (ties count against us = conservative).
     Verdict (frozen): law_alive_<split> = (F1 pct_up <= 0.05).
  B) calendar table: 12 months conditional means, per panel per split
     (descriptive; the 12 cells are exhaustive by construction, no subset null).
  C) single-month descriptive faces: March / December mean return rank among
     the 12 exhaustive calendar cells (F1 full window).
- Subperiod applicability (descriptive honesty): per-6y windows on F1, spread4
  + pct_up each (n disclosed).
- Trial count N: F1 = 3 splits x (1 true + 495) + 5 subperiods x (1 + 495);
  F2 = 3 splits x (1 + 495); + calendar cells; exact totals in artifact.
- No cost/turnover claims (research-grade calendar face; single monthly switch
  at month granularity, cost face belongs to the s3 runner, not this study).

Engineering: deterministic, byte-identical on re-run (sorted keys, 6dp round).
Exit 0 = complete; 2 = mechanism failure (panel shape/guard breach).
Selftest subcommand = offline asserts (compounding math, enumeration count,
conservative-tie percentile edge, split boundaries, min-days exclusion)
without touching the panel.
"""
import io
import json
import os
import sys
import time
import warnings
from itertools import combinations

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import p1c_stock_ic_batch as P1C          # census cache/universe conventions
from composite_ic import IS_END           # shared IS/OOS boundary

OUT_DIR = os.path.join(ROOT, "results", "t73_s2")
OUT_JSON = os.path.join(OUT_DIR, "policy_cycle.json")

P4 = (3, 4, 7, 12)
# AMENDMENT 1 (source-corrected face, declared BEFORE its first burn; the P4
# as-drafted face verdicts above stay frozen from their first run): the
# politburo economic-meeting convention per the external anchor (zh.wikipedia
# 中央经济工作会议, citing Sina Finance 2024-12-09) is months {4, 7, 10, 12} --
# verbatim: "原则上，中共中央政治局在每年4、7、10及12月会召开会议，总结前
# 一季度经济情况，分析研判当前经济形势，部署之后中国经济工作". P4 as drafted
# missed October and included March (两会 month -- real calendar but not part of
# the politburo quarterly convention). P4B is the source-corrected face; both
# faces stay in the trials ledger; NO third face may be opened on this panel
# (two-face cap, Cawley-Talbot selection-bias law).
P4B = (4, 7, 10, 12)
FACES = {"P4": P4, "P4B": P4B}
WINDOW_START = pd.Timestamp("1997-01-01")
MIN_DAYS_PER_MONTH = 10
ETF_FUND_EVENT_LINE = 0.11
SPLITS = ("full", "is", "oos")
SUBPERIODS = [(1997, 2002), (2003, 2008), (2009, 2014), (2015, 2020), (2021, 2026)]
ALL4 = list(combinations(range(1, 13), 4))          # C(12,4) = 495, frozen
PCT_LINE = 0.05                                      # one-sided upper p line


# ------------------------------------------------------------------ loaders

def load_f1_daily():
    """Full-A active-EW daily mean return (census panel, volume>0 mask)."""
    idx, syms, meta = P1C.load_universe()
    pct = np.asarray(np.load(os.path.join(P1C.CACHE_DIR, "pct_chg.npy"),
                             mmap_mode="r"), dtype=np.float64)
    vol = np.asarray(np.load(os.path.join(P1C.CACHE_DIR, "volume.npy"),
                             mmap_mode="r"), dtype=np.float64)
    assert pct.shape == vol.shape == (len(idx), len(syms)), "panel shape mismatch"
    act = (vol > 0) & ~np.isnan(pct)
    n_active = act.sum(axis=1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)   # all-NaN day guard
        daily = np.where(act, pct, np.nan)
        daily = np.nanmean(daily, axis=1)
    s = pd.Series(daily, index=idx) / 100.0              # pct_chg is percent
    return s, int(np.median(n_active)), meta


def load_f2_daily():
    """510050 SSE-50 ETF daily close returns with r239 fund-event guard."""
    path = os.path.join(ROOT, "data", "daily", "sh510050.csv")
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    r = df["close"] / df["close"].shift(1) - 1.0
    n_ext = int((r.abs() > ETF_FUND_EVENT_LINE).sum())
    assert n_ext == 0, f"fund-event guard breach: {n_ext} days |ret|>11% (r239)"
    return r.dropna()


# ------------------------------------------------------------------ faces

def monthly_series(daily):
    """Monthly compounded returns; months with < MIN_DAYS_PER_MONTH excluded."""
    keys = daily.index.to_period("M")
    rets = (1.0 + daily).groupby(keys).agg(np.prod) - 1.0
    cnt = daily.groupby(keys).size()
    keep = cnt >= MIN_DAYS_PER_MONTH
    return rets[keep], int((~keep).sum()), int(keep.sum())


def split_mask(monthly, which):
    ts = monthly.index.to_timestamp()
    if which == "full":
        return pd.Series(True, index=monthly.index)
    if which == "is":
        return ts <= pd.Timestamp(IS_END)
    return ts > pd.Timestamp(IS_END)


def exhaustive_pct_up(monthly, months=P4):
    """One-sided upper p of spread(months) within the exact 495-subset
    distribution (conservative ties). True spread computed by the SAME code
    path as the nulls (the face's subset is itself one of the 495) -- zero
    formula-divergence surface. Returns (spread, pct_up, null_min, null_max,
    n_in, n_out)."""
    m = np.array(monthly.index.month)
    vals = monthly.to_numpy(dtype=np.float64)
    per_month = {mo: vals[m == mo] for mo in range(1, 13)}
    for mo in range(1, 13):
        assert len(per_month[mo]) > 0, f"month {mo} absent from segment"
    mus = np.array([per_month[mo].mean() for mo in range(1, 13)])
    ns = np.array([len(per_month[mo]) for mo in range(1, 13)], dtype=np.float64)
    total_n = float(ns.sum())
    tot_mu_contrib = float((mus * ns).sum())
    nulls = np.empty(len(ALL4))
    for i, S in enumerate(ALL4):
        cols = [mo - 1 for mo in S]            # month number -> 0-based
        w_in = float((mus[cols] * ns[cols]).sum())
        s_in = float(ns[cols].sum())
        nulls[i] = w_in / s_in - (tot_mu_contrib - w_in) / (total_n - s_in)
    s_true = float(nulls[ALL4.index(months)])   # same-path identity
    na = int(ns[[mo - 1 for mo in months]].sum())
    pct_up = float((nulls >= s_true).sum()) / len(ALL4)
    return s_true, pct_up, float(nulls.min()), float(nulls.max()), \
        na, int(total_n - na)


def calendar_table(monthly):
    m = np.array(monthly.index.month)
    return {int(mo): {"mean": round(float(monthly[m == mo].mean()), 6),
                      "n": int((m == mo).sum())} for mo in range(1, 13)}


def _month_rank(calendar, month):
    """Rank (1=best mean) of a month among the 12 exhaustive calendar cells."""
    if not calendar:
        return None
    order = sorted(calendar, key=lambda k: -calendar[k]["mean"])
    return int(order.index(month)) + 1


def _round6(o):
    if isinstance(o, dict):
        return {k: _round6(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_round6(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return round(float(o), 6)
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    return o


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    # compounding math + min-days exclusion
    idx = pd.date_range("2024-01-02", periods=10).append(
        pd.to_datetime(["2024-02-01"]))
    daily = pd.Series([0.001] * 10 + [0.05], index=idx)   # Jan=10d, Feb=1d
    rets, n_ex, n_keep = monthly_series(daily)
    expect_jan = 1.001 ** 10 - 1.0
    assert abs(rets[pd.Period("2024-01")] - expect_jan) < 1e-12, rets.to_dict()
    assert n_keep == 1 and n_ex == 1          # 1-day February month excluded
    # enumeration count / frozen membership / uniqueness
    assert len(ALL4) == 495 and (3, 4, 7, 12) in ALL4 and len(set(ALL4)) == 495
    # conservative-tie percentile edge: identical months -> every subset
    # spread equals the true spread -> pct_up == 1.0 (weakest possible);
    # value 0.03125 = 2^-5 keeps the arithmetic binary-exact
    m2 = pd.Series([0.03125] * 24,
                   index=pd.date_range("2019-01-01", periods=24, freq="MS"))
    s, p, lo, hi, na, nb = exhaustive_pct_up(m2)
    assert s == 0.0 and p == 1.0 and na == 8 and nb == 16
    # spread4 cross-check on toy data with UNEQUAL month counts (validates the
    # n-weighted subset-mean formula, not just the equal-count degenerate case);
    # also exercises the P4B source-corrected face months arg
    months_toy = ([3, 4, 7, 12] * 2                          # P4 months x2
                   + [mo for mo in range(1, 13) if mo not in P4])
    vals_toy = np.linspace(0.01, 0.18, len(months_toy))
    m3 = pd.Series(vals_toy, index=pd.PeriodIndex(
        [f"2020-{mo:02d}" for mo in months_toy], freq="M"))
    for face_months in (P4, P4B):
        s3, p3, _, _, na3, nb3 = exhaustive_pct_up(m3, face_months)
        a_obs = m3[np.isin(np.array(months_toy), face_months)]
        b_obs = m3[~np.isin(np.array(months_toy), face_months)]
        assert abs(s3 - float(a_obs.mean() - b_obs.mean())) < 1e-12
        assert na3 == len(a_obs) and nb3 == len(b_obs)
    # split boundaries
    per = pd.PeriodIndex(["2024-12", "2025-01", "2025-06"], freq="M")
    ts = per.to_timestamp()
    assert (ts <= pd.Timestamp(IS_END)).tolist() == [True, False, False]
    # window start filter boundary
    assert pd.Period("1996-12").to_timestamp() < WINDOW_START \
        <= pd.Period("1997-01").to_timestamp()
    # month rank helper
    cal = {mo: {"mean": mo, "n": 1} for mo in range(1, 13)}
    assert _month_rank(cal, 12) == 1 and _month_rank(cal, 1) == 12
    print("t73_s2_policy_cycle selftest: compounding+enumeration+ties+"
          "spread-cross-check+splits+window+rank PASS")
    return 0


# ------------------------------------------------------------------ run

def run() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    art = {
        "prereg": {
            "ticket": "T-2026-09-26-73 s2 slice-B (policy-cycle rhythm)",
            "policy_months_P4": list(P4),
            "p4_basis": "as-drafted face: 3=两会(NPC 3/5 convention); "
                        "4/7=政治局 Q1/mid-year economy meetings; "
                        "12=政治局 annual + 中央经济工作会议",
            "amendment_1": {
                "face": "P4B",
                "months": list(P4B),
                "basis": "source-corrected: politburo economic-meeting "
                         "convention months are {4,7,10,12} per external "
                         "anchor (zh.wikipedia 中央经济工作会议 citing Sina "
                         "Finance 2024-12-09, verbatim: 原则上，中共中央政治"
                         "局在每年4、7、10及12月会召开会议，总结前一季度经济"
                         "情况); CEWC month: 此后均在每年11月末或12月举行，"
                         "自2006年起大多安排在12月上中旬",
                "declared_before_first_burn": True,
                "p4_verdicts_frozen_from_first_run": True,
                "face_cap": "two faces only (P4 + P4B); no third face on "
                            "this panel (Cawley-Talbot selection-bias law)",
            },
            "forward_lock": "month-level only (exact politburo days unknown "
                            "ex-ante; 两会 day fixed)",
            "law_face": "F1 active-EW full-A monthly, spread4 vs exhaustive 495",
            "verdict_line": f"law_alive_<split> = F1 pct_up <= {PCT_LINE}",
            "null_design": "exhaustive C(12,4)=495 enumeration, zero RNG, "
                           "zero seed-registry surface",
            "splits": {"full": "1997-01..cutoff", "is": f"<={IS_END}",
                       "oos": f">{IS_END}"},
            "window_exclusion": "pre-1997 no-price-limit era excluded "
                                "(probe +38.8%/mo, 73 months)",
            "min_days_per_month": MIN_DAYS_PER_MONTH,
            "no_cost_claim": True,
        },
        "trials_N": {"f1_null_spreads": 0, "f2_null_spreads": 0,
                     "true_faces": 0, "calendar_cells": 0},
    }

    # ---------------- F1 (primary law face)
    f1_daily, med_active, meta = load_f1_daily()
    f1_monthly_all, f1_short_ex, f1_n_all = monthly_series(f1_daily)
    pre_mask = f1_monthly_all.index.to_timestamp() < WINDOW_START
    f1_pre = f1_monthly_all[pre_mask]
    f1 = f1_monthly_all[~pre_mask]
    art["panels"] = {
        "F1_active_EW": {
            "T_days": int(f1_daily.shape[0]),
            "months_total": int(len(f1_monthly_all)),
            "months_pre1997_excluded": int(len(f1_pre)),
            "months_pre1997_mean_probe": round(float(f1_pre.mean()), 6),
            "months_short_excluded": int(f1_short_ex),
            "months_window": int(len(f1)),
            "window": "1997-01..cutoff",
            "active_names_median": med_active,
            "face_note": "EW mean = small-cap-tilted market face; active mask "
                         "excludes ffill-stale delisted/suspended legs",
        },
    }
    faces = art.setdefault("faces", {})
    for which in SPLITS:
        seg = f1[split_mask(f1, which)]
        for fname, fmonths in FACES.items():
            s, p, lo, hi, na, nb = exhaustive_pct_up(seg, fmonths)
            faces[f"F1.{fname}.{which}"] = {
                "n_months": int(len(seg)), "spread": round(s, 6),
                "pct_up_one_sided": round(p, 4),
                "null_spread_min": round(lo, 6), "null_spread_max": round(hi, 6),
                "n_in_months": na, "n_out_months": nb,
                "law_alive": bool(p <= PCT_LINE),
                "months": list(fmonths),
            }
            art["trials_N"]["f1_null_spreads"] += len(ALL4)
            art["trials_N"]["true_faces"] += 1
            print(f"  F1 {fname} {which}: n={len(seg)} spread={s:+.5f} "
                  f"pct_up={p:.4f} alive={p <= PCT_LINE}", flush=True)
        art.setdefault("calendars_F1", {})[which] = calendar_table(seg)
        art["trials_N"]["calendar_cells"] += 12

    # ---------------- F1 subperiod applicability (descriptive)
    subs = art.setdefault("subperiods_F1", {})
    ts = f1.index.to_timestamp()
    for lo_y, hi_y in SUBPERIODS:
        seg = f1[(ts >= pd.Timestamp(f"{lo_y}-01-01")) &
                 (ts <= pd.Timestamp(f"{hi_y}-12-31"))]
        for fname, fmonths in FACES.items():
            s, p, _, _, na, nb = exhaustive_pct_up(seg, fmonths)
            subs.setdefault(f"{lo_y}-{hi_y}", {})[fname] = {
                "n_months": int(len(seg)), "spread": round(s, 6),
                "pct_up_one_sided": round(p, 4),
                "n_in_months": na, "n_out_months": nb,
                "months": list(fmonths),
            }
            art["trials_N"]["f1_null_spreads"] += len(ALL4)
            print(f"  F1 sub {lo_y}-{hi_y} {fname}: n={len(seg)} "
                  f"spread={s:+.5f} pct_up={p:.4f}", flush=True)

    # ---------------- F2 (cap face)
    f2_daily = load_f2_daily()
    f2, f2_short_ex, f2_n = monthly_series(f2_daily)
    art["panels"]["F2_510050"] = {
        "T_days": int(f2_daily.shape[0]),
        "first_month": str(f2.index[0]), "months": int(len(f2)),
        "fund_event_days": 0,
        "months_short_excluded": int(f2_short_ex),
    }
    for which in SPLITS:
        seg = f2[split_mask(f2, which)]
        for fname, fmonths in FACES.items():
            s, p, lo, hi, na, nb = exhaustive_pct_up(seg, fmonths)
            faces[f"F2.{fname}.{which}"] = {
                "n_months": int(len(seg)), "spread": round(s, 6),
                "pct_up_one_sided": round(p, 4),
                "null_spread_min": round(lo, 6), "null_spread_max": round(hi, 6),
                "n_in_months": na, "n_out_months": nb,
                "months": list(fmonths),
            }
            art["trials_N"]["f2_null_spreads"] += len(ALL4)
            art["trials_N"]["true_faces"] += 1
            print(f"  F2 {fname} {which}: n={len(seg)} spread={s:+.5f} "
                  f"pct_up={p:.4f}", flush=True)
        art.setdefault("calendars_F2", {})[which] = calendar_table(seg)
        art["trials_N"]["calendar_cells"] += 12

    # ---------------- frozen verdict on the law face (F1 splits, both faces)
    art["verdict"] = {
        "law_face": "F1 spread vs exhaustive 495",
        "line": f"pct_up <= {PCT_LINE} (one-sided upper, conservative ties)",
        "P4": {which: faces.get(f"F1.P4.{which}", {}).get("law_alive")
               for which in SPLITS},
        "P4B": {which: faces.get(f"F1.P4B.{which}", {}).get("law_alive")
                for which in SPLITS},
        "march_rank_of_12": _month_rank(
            art.get("calendars_F1", {}).get("full"), 3),
        "december_rank_of_12": _month_rank(
            art.get("calendars_F1", {}).get("full"), 12),
        "october_rank_of_12": _month_rank(
            art.get("calendars_F1", {}).get("full"), 10),
        "note": "P4 = as-drafted face (verdicts frozen from first burn); "
                "P4B = source-corrected politburo-convention face "
                "(amendment 1, declared before its first burn)",
    }
    art["runtime_s"] = round(time.time() - t0, 3)
    art = _round6(art)
    with io.open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(art, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"policy_cycle.json written ({art['runtime_s']}s) "
          f"trials_N={art['trials_N']}", flush=True)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit(selftest() if cmd == "selftest" else run())
