"""P-A LHB attention factor IC batch (research/shortline/PA_LHB_IC.md pre-reg).

O-20260923-1850 research-dept lane (claim MSG-20260923-1910). Factor-layer IC
screening of the in-house 19y LHB event history against the P-1c Stage-A
stock panel. Zero engine runs -> strategy engine ledger N untouched; this
batch registers no traders (IC != strategy).

Pre-registered, written before the run: h10 sole gating horizon, K=50
white-noise nulls per availability mask (A/B/C), V1/V2/V3 strict gates,
IS<=2024-12-31 / OOS 2025+, events lagged one trade day (LHB disclosed
after close), forward-return columns in the source parquet never touched.

Methodology parity: per-date spearman = pearson of average ranks on the
pairwise-complete intersection (mask & finite(factor) & finite(fwd)),
>=5 names, zero-variance -> NaN - same semantics as composite_ic.ic_series,
gated by an equivalence check before the batch.

Outputs: research/shortline/pa_lhb_ic_results.csv
         results/shortline/pa_lhb_ic.json
"""
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from composite_ic import IS_END, ic_series, stats_block  # established methodology

CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
RES_DIR = os.path.join(ROOT, "research", "shortline")
OUT_DIR = os.path.join(ROOT, "results", "shortline")

WIN_START = "2007-01-01"
H_GATE = 10            # sole gating horizon (pre-reg SS3)
H_REPORT = [5, 20]     # report-only, computed for passers only
N_NULLS = 50
SEED0 = 20260923
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS = 500
W_COUNT, W_NETBUY, W_SHARE, W_DECAY = 20, 60, 20, 252
IS_END_TS = pd.Timestamp(IS_END)
EQUIV_TOL = 1e-6
EQUIV_N_DATES = 400


# ---------------------------------------------------------------- helpers
def rolling_sum(arr, w):
    """Trailing w-row sum; partial windows at panel start count what exists
    (LHB history itself begins 2007-01-04, so partials are factual)."""
    cs = np.vstack([np.zeros((1, arr.shape[1])), np.cumsum(arr, axis=0)])
    out = np.empty_like(arr)
    out[:w - 1] = cs[1:w]
    out[w - 1:] = cs[w:] - cs[:-w]
    return out


def shift1(a, fill=np.nan):
    """Event-time grid -> signal position: row t holds events <= t-1."""
    out = np.full_like(a, fill)
    out[1:] = a[:-1]
    return out


def rank_rows(eff, values):
    """Mask-first then rank (J7 pitfall family): average ties, NaN outside
    eff. eff = pairwise-complete mask for the (factor, fwd) pair."""
    return pd.DataFrame(np.where(eff, values, np.nan)).rank(axis=1).values


def ic_from_ranks(F, R, dates):
    """Spearman IC per date from rank arrays with identical support.

    n = pairwise count; >=5 names; zero-variance -> NaN. Index = dates."""
    with np.errstate(invalid="ignore"):
        fm = np.nanmean(F, axis=1)
        rm = np.nanmean(R, axis=1)
        dF = F - fm[:, None]
        dR = R - rm[:, None]
        cov = np.nansum(dF * dR, axis=1)
        sf = np.sqrt(np.nansum(dF * dF, axis=1))
        sr = np.sqrt(np.nansum(dR * dR, axis=1))
        ic = cov / (sf * sr)
    n = (np.isfinite(F) & np.isfinite(R)).sum(axis=1)
    ok = np.isfinite(ic) & (sf > 0) & (sr > 0) & (n >= 5)
    idx = pd.DatetimeIndex(dates[ok].astype("datetime64[us]"))
    return pd.Series(ic[ok], index=idx).dropna()


def fwd_ret(close, h):
    out = np.full_like(close, np.nan)
    out[:-h] = close[h:] / close[:-h] - 1.0
    return out


def seg_stats(s):
    return (stats_block(s), stats_block(s[s.index <= IS_END_TS]),
            stats_block(s[s.index > IS_END_TS]))


# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)

    # ---- panel slice (cache is float32 memmap; dates are int64 microseconds)
    dates_all = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    i0 = int(np.searchsorted(dates_all,
                             np.datetime64(WIN_START, "us").astype("int64")))
    cal = dates_all[i0:]
    T = len(cal)
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    syms = [os.path.basename(p)[:-8] for p in files]
    N = len(syms)
    sym_col = {s: i for i, s in enumerate(syms)}
    close = np.asarray(np.load(os.path.join(CACHE_DIR, "close.npy"),
                                mmap_mode="r")[i0:], dtype=np.float64)
    amount = np.asarray(np.load(os.path.join(CACHE_DIR, "amount.npy"),
                                mmap_mode="r")[i0:], dtype=np.float64)
    print(f"panel slice: T={T} (from {cal[0].astype('datetime64[us]')}) "
          f"x N={N} syms ({time.time()-t0:.0f}s)", flush=True)

    # ---- LHB events: dedup per (code, date) = row with max LHB turnover
    lhb = pd.read_parquet(LHB_PATH)
    n_raw = len(lhb)
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    n_events = len(ev)
    ev_us = (pd.to_datetime(ev["上榜日"]).values.astype("datetime64[us]")
             .astype("int64"))
    pos = np.searchsorted(cal, ev_us)
    in_cal = pos < T
    pos_safe = np.minimum(pos, T - 1)
    pos_ok = in_cal & (cal[pos_safe] == ev_us)
    cols = ev["代码"].map(sym_col)
    col_ok = cols.notna().values
    keep = pos_ok & col_ok
    r_idx = pos[keep]
    c_idx = cols.values[keep].astype(int)
    n_placed = int(keep.sum())
    n_drop_col = int((~col_ok).sum())
    n_drop_date = int((~pos_ok).sum())
    print(f"events: raw={n_raw} dedup={n_events} placed={n_placed} "
          f"(drop_no_col={n_drop_col} delisted-era syms, "
          f"drop_no_date={n_drop_date}) ({time.time()-t0:.0f}s)", flush=True)

    # ---- event-time grids (values AT the event-day position)
    ind = np.zeros((T, N))
    ind[r_idx, c_idx] = 1.0
    nb_grid = np.zeros((T, N))
    nb_grid[r_idx, c_idx] = ev["龙虎榜净买额"].values[keep]
    sh_grid = np.zeros((T, N))
    sh_grid[r_idx, c_idx] = ev["成交额占总成交比"].values[keep]

    count20 = rolling_sum(ind, W_COUNT)
    netbuy60 = rolling_sum(nb_grid, W_NETBUY)
    share20 = rolling_sum(sh_grid, W_SHARE)
    with np.errstate(invalid="ignore", divide="ignore"):
        amt_share20 = np.where(count20 > 0, share20 / count20, np.nan)
    ev_pos = np.where(ind > 0, np.arange(T)[:, None], -1.0)
    last_ev = np.maximum.accumulate(ev_pos, axis=0)
    days_since = np.arange(T)[:, None] - last_ev
    days_since[last_ev < 0] = np.nan
    days_capped = np.where(days_since <= W_DECAY, days_since, np.nan)

    # ---- shift to signal position (events <= t-1) and normalize
    count_s = shift1(count20, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        netbuy_s = shift1(netbuy60) / amount
    days_s = shift1(days_capped)
    share_s = shift1(amt_share20)

    A = np.isfinite(close) & np.isfinite(amount)
    B = A & (count_s >= 1)
    C = A & np.isfinite(days_s)
    masks = [("A", A), ("B", B), ("C", C)]
    factors = [
        ("lhb_count_20", count_s, A),
        ("lhb_netbuy_amt_60", netbuy_s, B),
        ("lhb_days_since", days_s, C),
        ("lhb_amt_share_20", share_s, B),
    ]
    xs_med = {k: int(np.median(m.sum(axis=1)[m.sum(axis=1) > 0]))
              for k, m in masks}
    print(f"mask median cross-section: {xs_med} ({time.time()-t0:.0f}s)",
          flush=True)

    fwd10 = fwd_ret(close, H_GATE)
    fwd10_ok = np.isfinite(fwd10)

    # ---- equivalence gate: fast path vs composite_ic.ic_series reference
    print("equivalence gate: fast IC vs reference on probe factor...", flush=True)
    p60 = np.full_like(close, np.nan)
    p60[60:] = close[60:] / close[:-60] - 1.0
    probe = -p60
    rng_dates = np.random.default_rng(SEED0)
    sub = np.sort(rng_dates.choice(T, size=min(EQUIV_N_DATES, T),
                                   replace=False))
    sub_idx = pd.DatetimeIndex(cal[sub].astype("datetime64[us]"))
    probe_df = pd.DataFrame(probe[sub], index=sub_idx)
    fwd_df = pd.DataFrame(fwd10[sub], index=sub_idx)
    ref = ic_series(probe_df, fwd_df)
    eff = A[sub] & np.isfinite(probe[sub]) & np.isfinite(fwd10[sub])
    F = rank_rows(eff, probe[sub])
    R = rank_rows(eff, fwd10[sub])
    fast = ic_from_ranks(F, R, cal[sub])
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) \
        else 9.9
    print(f"  n_ref={len(ref)} n_fast={len(fast)} common={len(common)} "
          f"max|diff|={worst:.2e}", flush=True)
    if worst > EQUIV_TOL or len(ref) != len(fast):
        print("EQUIVALENCE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- null baselines per availability mask (K=50 white noise, IS segment)
    thresholds = {}
    for mname, mask in masks:
        t1 = time.time()
        abs_ic, abs_ir = [], []
        eff_fwd = mask & fwd10_ok
        R_fwd = rank_rows(eff_fwd, fwd10)
        for k in range(N_NULLS):
            rng = np.random.default_rng(SEED0 + k)
            noise = rng.standard_normal((T, N))
            F = rank_rows(eff_fwd, noise)
            s = ic_from_ranks(F, R_fwd, cal)
            blk = stats_block(s[s.index <= IS_END_TS])
            if "ic_mean" in blk:
                abs_ic.append(abs(blk["ic_mean"]))
                abs_ir.append(abs(blk["ic_ir"]))
            if (k + 1) % 10 == 0:
                print(f"  null[{mname}] {k+1}/{N_NULLS} "
                      f"({time.time()-t1:.0f}s)", flush=True)
        thresholds[mname] = {
            "p95_abs_ic": round(float(np.quantile(abs_ic, 0.95)), 4),
            "p95_abs_ir": round(float(np.quantile(abs_ir, 0.95)), 4),
            "n_nulls": len(abs_ic),
            "median_cross_section": xs_med[mname],
        }
        print(f"  null[{mname}] p95|ic|={thresholds[mname]['p95_abs_ic']} "
              f"p95|ir|={thresholds[mname]['p95_abs_ir']} "
              f"({time.time()-t1:.0f}s)", flush=True)

    # ---- factor batch at gating horizon
    rows = []
    for name, vals, mask in factors:
        t1 = time.time()
        mname = "A" if mask is A else ("B" if mask is B else "C")
        eff = mask & np.isfinite(vals) & fwd10_ok
        F = rank_rows(eff, vals)
        R = rank_rows(eff, fwd10)
        s = ic_from_ranks(F, R, cal)
        blk_full, blk_is, blk_oos = seg_stats(s)
        rec = {"factor": name, "mask": mname, "status": "ok",
               "v1_thr": max(V1_FLOOR, thresholds[mname]["p95_abs_ic"])}
        for seg, blk in [("full", blk_full), ("is", blk_is), ("oos", blk_oos)]:
            for k in ("ic_mean", "ic_ir", "n_periods"):
                rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
        if "ic_mean" in blk_is and "ic_mean" in blk_oos:
            v1 = abs(blk_is["ic_mean"]) > rec["v1_thr"]
            v2 = abs(blk_is["ic_ir"]) >= V2_IR
            v3 = ((blk_oos["ic_mean"] > 0) == (blk_is["ic_mean"] > 0)
                  and abs(blk_oos["ic_mean"]) >= V3_RETAIN
                  * abs(blk_is["ic_mean"]))
            pg = blk_is["n_periods"] >= MIN_PERIODS
            rec.update({"v1": bool(v1), "v2": bool(v2), "v3": bool(v3),
                        "period_gate": bool(pg),
                        "pass": bool(v1 and v2 and v3 and pg)})
            if rec["pass"]:  # report-only horizons for passers (non-gating)
                for h in H_REPORT:
                    fw = fwd_ret(close, h)
                    eff_h = mask & np.isfinite(vals) & np.isfinite(fw)
                    sh_ = ic_from_ranks(rank_rows(eff_h, vals),
                                       rank_rows(eff_h, fw), cal)
                    _, bis, bos = seg_stats(sh_)
                    rec[f"h{h}_is_ic"] = bis.get("ic_mean", "")
                    rec[f"h{h}_oos_ic"] = bos.get("ic_mean", "")
        else:
            rec.update({"v1": False, "v2": False, "v3": False,
                        "period_gate": False, "pass": False})
        rec["compute_s"] = round(time.time() - t1, 1)
        rows.append(rec)
        print(f"  {name}[{mname}] is_ic={rec.get('h10_is_ic_mean')} "
              f"ir={rec.get('h10_is_ic_ir')} pass={rec['pass']}", flush=True)

    rows.append({"factor": "lhb_seat_top5_conc",
                 "status": "skip_no_seat_level_data",
                 "skip_reason": "in-house LHB (parquet+chunks) is per-criterion "
                                "aggregate; seat detail absent -> honest skip "
                                "(PA_LHB_IC SS2); seat-data source probe = "
                                "separate lane"})

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RES_DIR, "pa_lhb_ic_results.csv"), index=False,
              encoding="utf-8")
    n_pass = int(df["pass"].fillna(False).sum())
    out = {
        "meta": {"batch": "P-A LHB attention factor IC",
                 "pre_reg": "research/shortline/PA_LHB_IC.md",
                 "order": "O-20260923-1850", "claim": "MSG-20260923-1910",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": IS_END, "gate_horizon": H_GATE,
                 "n_nulls_per_mask": N_NULLS, "seed0": SEED0,
                 "window": f"{WIN_START} -> cache cutoff",
                 "dedup_rule": "per (code,date) keep max LHB-turnover row",
                 "lag_trade_days": 1,
                 "engine_runs": 0,
                 "ledger_note": "factor IC batch: strategy engine ledger N "
                                "untouched (P-4-2a precedent)",
                 "ic_computations": 4 + N_NULLS * 3},
        "equivalence": {"max_abs_diff": worst, "n_common": int(len(common)),
                        "tol": EQUIV_TOL, "pass": worst <= EQUIV_TOL},
        "thresholds": thresholds,
        "events": {"raw_rows": n_raw, "dedup_stock_days": n_events,
                   "placed": n_placed, "dropped_no_cache_col": n_drop_col,
                   "dropped_no_calendar_date": n_drop_date,
                   "survivorship_note": "LHB syms beyond the bars cache are "
                                        "delisted-era names; their post-event "
                                        "returns are unmeasurable in this "
                                        "panel (recorded limitation)"},
        "panel": {"T": T, "N": N,
                  "start": str(cal[0].astype("datetime64[us]")),
                  "end": str(cal[-1].astype("datetime64[us]"))},
        "counts": {"computed": 4, "skipped": 1, "pass": n_pass},
        "rows": rows,
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "workers": 1,
                  "cpu_cap_policy": "O-20260923-1738 (vectorized single-proc,"
                                    " memory-bound rank ops)"},
    }
    with open(os.path.join(OUT_DIR, "pa_lhb_ic.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\n=== P-A LHB batch: computed=4 skipped=1 pass={n_pass} "
          f"({time.time()-t0:.0f}s) ===", flush=True)


if __name__ == "__main__":
    main()
