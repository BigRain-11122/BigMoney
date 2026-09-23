"""PC_L2_IC — heat L2 popularity-history first factor IC batch (prereg frozen).

Prereg: research/shortline/PC_L2_IC.md (commit 3c09369, before run).
Reuses pa_lhb_ic helpers verbatim (rank_rows / ic_from_ranks / fwd_ret) and
composite_ic.stats_block — no re-implementation (anti-duplication rule).

Zero engine runs: factor-reference batch, IC counts go to the factor ledger
(audit block only); the engine trials ledger N is untouched.
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

from pa_lhb_ic import rank_rows, ic_from_ranks, fwd_ret  # noqa: E402
from composite_ic import stats_block  # noqa: E402
from science_gates import cutoff_meta  # noqa: E402

RANK_DIR = os.path.join(ROOT, "data", "heat", "rank_history")
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
OUT_PATH = os.path.join(ROOT, "results", "shortline", "pc_l2_ic.json")

H_GATE = 10
H_REPORT = [5, 20]
N_NULLS = 50
SEED0 = 45_000                      # SEED_REGISTRY["pc_l2_ic"]
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
IS_END = pd.Timestamp("2026-06-30")  # sub-window split (prereg S2), NOT regime OOS
MIN_PERIODS_IS = 100
MIN_PERIODS_OOS = 30
Z_WIN = 60
MOM_WIN = 20
W_LHB = 20
EVIDENCE_CUTOFF = "2026-09-22"
D6_MAX_CORR = 0.7
D6_MIN_DAYS = 30


def load_rank_grids():
    """Per-stock (grid_dates, rank, new_uid_rate) on the union calendar of
    rank rows; returns list of dicts keyed by bare 6-digit code."""
    stocks = []
    for fp in sorted(glob.glob(os.path.join(RANK_DIR, "*.json"))):
        with open(fp, encoding="utf-8") as f:
            j = json.load(f)
        rows = j.get("rows") or []
        if not rows:
            continue
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").drop_duplicates("date", keep="last")
        code = j["sc"].upper()
        if code.startswith("SH") or code.startswith("SZ"):
            code = code[2:]
        stocks.append({"code": code, "df": df.set_index("date")})
    return stocks


def build_panels(stocks, cal):
    """Align rank rows onto the trading calendar (ffill, date<=t) -> per-stock
    rank / new_uid grids of shape (T, n_stocks) on the p1c cache calendar
    restricted to the L2 window."""
    codes = [s["code"] for s in stocks]
    T = len(cal)
    rank = np.full((T, len(stocks)), np.nan)
    uid = np.full((T, len(stocks)), np.nan)
    cal_ts = pd.DatetimeIndex(cal.astype("datetime64[us]"))
    for j, s in enumerate(stocks):
        df = s["df"]
        pos = df.index.searchsorted(cal_ts, side="right") - 1
        ok = pos >= 0
        rank[ok, j] = df["rank"].values[pos[ok]]
        uid[ok, j] = df["new_uid_rate"].values[pos[ok]]
        # rows after the last rank date stay NaN (no forward fill past data)
        after = cal_ts > df.index[-1]
        rank[after, j] = np.nan
        uid[after, j] = np.nan
    return codes, rank, uid


def roll_z(a, w):
    """Trailing w-row z-score, strict min_periods=w (NaN until warm)."""
    out = np.full_like(a, np.nan)
    if len(a) <= w:
        return out
    s = pd.DataFrame(a)
    m = s.rolling(w, min_periods=w).mean().values
    sd = s.rolling(w, min_periods=w).std().values
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (a - m) / sd
    out[w - 1:] = z[w - 1:]
    return out


def shift1(a, fill=np.nan):
    out = np.full_like(a, fill)
    out[1:] = a[:-1]
    return out


def selftest():
    """Offline synthetic checks: alignment law / late-start NaN / z window /
    shift1 / delta sign / fwd_ret."""
    cal = pd.bdate_range("2025-09-01", periods=40).values.astype("datetime64[us]")
    rows = pd.DataFrame({
        "date": list(pd.bdate_range("2025-09-01", periods=40)),
        "rank": list(range(1, 41)),
        "new_uid_rate": [0.5] * 40,
    })
    codes, rank, uid = build_panels([{"code": "SH000001",
                                      "df": rows.set_index("date")}], cal)
    assert codes[0] == "SH000001" and rank[0, 0] == 1.0 and uid[0, 0] == 0.5
    late = pd.DataFrame({
        "date": list(pd.bdate_range("2025-09-01", periods=40))[10:],
        "rank": list(range(11, 41)),
        "new_uid_rate": [0.5] * 30,
    })
    _, rank2, _ = build_panels([{"code": "SZ000002",
                                 "df": late.set_index("date")}], cal)
    assert np.isnan(rank2[9, 0]) and rank2[10, 0] == 11.0  # late start stays NaN
    a = np.arange(100.0).reshape(100, 1)
    z = roll_z(a, 60)
    assert np.isnan(z[:59, 0]).all() and np.isfinite(z[59:, 0]).all()
    assert abs(z[99, 0]) < 3.1
    g = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert shift1(g)[1, 0] == 1.0 and np.isnan(shift1(g)[0, 0])
    r = np.array([[100.0], [90.0], [95.0], [80.0]])
    dgrid = np.vstack([np.full((1, 1), np.nan), r[:-1] - r[1:]])
    assert dgrid[1, 0] == 10.0 and dgrid[2, 0] == -5.0  # delta sign gate
    c = np.array([1.0, 1.1, 1.21]).reshape(-1, 1)
    assert abs(fwd_ret(c, 1)[0, 0] - 0.1) < 1e-12
    print("selftest: 8/8 PASS")
    return 0


def main():
    t0 = time.time()
    assert len(sys.argv) >= 2 and sys.argv[1] in ("run", "selftest"), \
        "usage: pc_l2_ic.py run|selftest"
    if sys.argv[1] == "selftest":
        return selftest()

    # ---- trading calendar + close panel from p1c cache (evidence cutoff)
    dates_all = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    win_start = np.datetime64("2025-09-23", "us").astype("int64")
    i0 = int(np.searchsorted(dates_all, win_start))
    cal = dates_all[i0:]
    T = len(cal)
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    syms = [os.path.basename(p)[:-8] for p in files]
    sym_col = {s: i for i, s in enumerate(syms)}
    close_all = np.load(os.path.join(CACHE_DIR, "close.npy"), mmap_mode="r")
    close = np.asarray(close_all[i0:], dtype=np.float64)
    print(f"window: T={T} ({cal[0].astype('datetime64[us]')} .. "
          f"{cal[-1].astype('datetime64[us]')}) N_pool={len(syms)}", flush=True)

    # ---- L2 rank grids
    stocks = load_rank_grids()
    codes, rank, uid = build_panels(stocks, cal)
    in_pool = [c in sym_col for c in codes]
    n_dropped = int((~np.array(in_pool)).sum())
    if n_dropped:
        keep = [j for j, ok in enumerate(in_pool) if ok]
        sel = np.array(keep)
        codes = [codes[j] for j in keep]
        rank, uid = rank[:, sel], uid[:, sel]
    col_idx = np.array([sym_col[c] for c in codes])
    close = np.asarray(close_all[i0:], dtype=np.float64)[:, col_idx]
    print(f"L2 universe: {len(codes)} stocks, {n_dropped} without bars col",
          flush=True)

    # ---- factors on event grid, then shift1 (T+1 strict lag, prereg S3)
    ncol = rank.shape[1]
    fac = {
        "guba_hot_rank_z": shift1(roll_z(rank, Z_WIN)),
        # delta at event-grid row t = rank[t-1] - rank[t]  (positive = rank
        # improved = popularity surging; prereg S3 table, selftest sign gate)
        "guba_rank_delta": shift1(np.vstack(
            [np.full((1, ncol), np.nan), rank[:-1] - rank[1:]])),
        "guba_new_uid_rate": shift1(uid),
        "guba_rank_mom_20": shift1(np.vstack(
            [np.full((MOM_WIN, ncol), np.nan), rank[:-MOM_WIN] - rank[MOM_WIN:]])),
    }

    fwd10 = fwd_ret(close, H_GATE)
    fwd_ok = np.isfinite(fwd10)
    A = fwd_ok & np.isfinite(close)
    xs_sizes = A.sum(axis=1)[A.sum(axis=1) > 0]
    print(f"mask A median cross-section={int(np.median(xs_sizes))} "
          f"days={len(xs_sizes)}", flush=True)

    # ---- nulls (K=50 same-mask white noise, IS segment, prereg S5)
    R_fwd = rank_rows(A & fwd_ok, fwd10)
    abs_ic, abs_ir = [], []
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED0 + k)
        noise = rng.standard_normal((T, len(codes)))
        eff = A & np.isfinite(noise)
        s = ic_from_ranks(rank_rows(eff, noise), R_fwd, cal)
        blk = stats_block(s[s.index <= IS_END])
        if "ic_mean" in blk:
            abs_ic.append(abs(blk["ic_mean"]))
            abs_ir.append(abs(blk["ic_ir"]))
    v1_thr = max(V1_FLOOR, round(float(np.quantile(abs_ic, 0.95)), 4))
    null_p95_ir = round(float(np.quantile(abs_ir, 0.95)), 4)
    print(f"null: p95|ic|={v1_thr} p95|ir|={null_p95_ir} n={len(abs_ic)}",
          flush=True)

    # ---- D6 family check vs lhb_count_20 on this universe (P-A dedup law)
    d6 = {"reference": "lhb_count_20", "min_days": D6_MIN_DAYS}
    lhb_grid = np.full((T, len(codes)), np.nan)
    try:
        lhb = pd.read_parquet(LHB_PATH)
        lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
        ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
        ev_us = (pd.to_datetime(ev["上榜日"]).values.astype("datetime64[us]")
                 .astype("int64"))
        pos = np.searchsorted(cal, ev_us)
        in_win = pos < T
        col_of = {c: j for j, c in enumerate(codes)}
        cc = ev["代码"].map(col_of)
        both = in_win & cc.notna().values
        r_idx, c_idx = pos[both], cc.values[both].astype(int)
        ind = np.zeros((T, len(codes)))
        ind[r_idx, c_idx] = 1.0
        cs = np.vstack([np.zeros((1, ind.shape[1])), np.cumsum(ind, axis=0)])
        cnt = np.empty_like(ind)
        cnt[:W_LHB - 1] = cs[1:W_LHB]
        cnt[W_LHB - 1:] = cs[W_LHB:] - cs[:-W_LHB]
        lhb_grid = shift1(cnt, 0.0)
        d6["lhb_events_in_window"] = int(both.sum())
    except Exception as e:  # honest degradation, never silent pass
        d6["lhb_events_in_window"] = 0
        d6["load_error"] = repr(e)

    # ---- factor batch at gating horizon
    rows = []
    for name, vals in fac.items():
        eff = A & np.isfinite(vals)
        F = rank_rows(eff, vals)
        R = rank_rows(eff, fwd10)
        s = ic_from_ranks(F, R, cal)
        blk_full = stats_block(s)
        blk_is = stats_block(s[s.index <= IS_END])
        blk_oos = stats_block(s[s.index > IS_END])
        rec = {"factor": name, "mask": "A",
               "is_n_periods": blk_is.get("n_periods", 0),
               "oos_n_periods": blk_oos.get("n_periods", 0)}
        for seg, blk in [("full", blk_full), ("is", blk_is), ("oos", blk_oos)]:
            for k in ("ic_mean", "ic_ir", "n_periods"):
                rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
        if "ic_mean" in blk_is and "ic_mean" in blk_oos:
            v1 = abs(blk_is["ic_mean"]) > v1_thr
            v2 = abs(blk_is["ic_ir"]) >= V2_IR
            v3 = ((blk_oos["ic_mean"] > 0) == (blk_is["ic_mean"] > 0)
                  and abs(blk_oos["ic_mean"]) >= V3_RETAIN * abs(blk_is["ic_mean"]))
            pg = (blk_is["n_periods"] >= MIN_PERIODS_IS
                  and blk_oos["n_periods"] >= MIN_PERIODS_OOS)
            rec.update({"v1": bool(v1), "v2": bool(v2), "v3": bool(v3),
                        "period_gate": bool(pg),
                        "pass": bool(v1 and v2 and v3 and pg)})
            if rec["pass"]:
                for h in H_REPORT:
                    fw = fwd_ret(close, h)
                    eff_h = A & np.isfinite(vals) & np.isfinite(fw)
                    sh_ = ic_from_ranks(rank_rows(eff_h, vals),
                                        rank_rows(eff_h, fw), cal)
                    _, bis, bos = (stats_block(sh_),
                                   stats_block(sh_[sh_.index <= IS_END]),
                                   stats_block(sh_[sh_.index > IS_END]))
                    rec[f"h{h}_is_ic"] = bis.get("ic_mean", "")
                    rec[f"h{h}_oos_ic"] = bos.get("ic_mean", "")
        else:
            rec.update({"v1": False, "v2": False, "v3": False,
                        "period_gate": False, "pass": False})
        # D6 corr vs lhb_count_20
        bothm = eff & np.isfinite(lhb_grid)
        nboth = bothm.sum(axis=1)
        day_ok = nboth >= 5
        corrs = []
        for t in np.where(day_ok)[0]:
            with np.errstate(invalid="ignore"):
                sl = pd.Series(vals[t, bothm[t]]).corr(
                    pd.Series(lhb_grid[t, bothm[t]]), method="spearman")
            if np.isfinite(sl):
                corrs.append(float(sl))
        d6_days = len(corrs)
        rec["d6_max_abs_corr"] = round(float(np.max(np.abs(corrs))), 4) \
            if corrs else ""
        rec["d6_days_with_corr"] = d6_days
        rec["d6_verdict"] = ("weak_check_insufficient_coverage"
                             if d6_days < D6_MIN_DAYS else
                             ("reject" if rec["d6_max_abs_corr"] >= D6_MAX_CORR
                              else "ok"))
        rows.append(rec)
        print(f"  {name}: IS ic={blk_is.get('ic_mean', '')} "
              f"IR={blk_is.get('ic_ir', '')} pass={rec['pass']} "
              f"d6={rec['d6_verdict']} ({time.time()-t0:.0f}s)", flush=True)

    out = {
        "batch": "pc_l2_ic",
        "lane": "bm-a P-C continuation, open-pool item (MSG-20260924-0426)",
        **cutoff_meta(EVIDENCE_CUTOFF),
        "window": {"start": str(cal[0].astype("datetime64[us]")),
                   "end": str(cal[-1].astype("datetime64[us]")),
                   "is_end": str(IS_END.date()),
                   "note": "sub-window split inside the 2025+ regime (prereg S2)"},
        "universe": {"n_files": len(codes), "n_without_bars_col": n_dropped,
                     "median_cross_section": int(np.median(xs_sizes)),
                     "survivorship": "top-100-of-2026-09-23 forward-selected "
                                     "universe; all ICs discounted (PC_COLLECTOR S4.1)"},
        "gates": {"h_gate": H_GATE, "v1_thr": v1_thr,
                  "v1_floor": V1_FLOOR, "null_p95_abs_ir": null_p95_ir,
                  "v2_ir_min": V2_IR, "v3_retain_min": V3_RETAIN,
                  "min_periods_is": MIN_PERIODS_IS,
                  "min_periods_oos": MIN_PERIODS_OOS,
                  "null_n": N_NULLS, "seed_base": SEED0},
        "d6": d6,
        "rows": rows,
        "ledger": {"engine_trials_added": 0,
                   "note": "factor-reference batch: IC counts recorded here "
                           "only; engine ledger N untouched (P-A convention)"},
        "prereg": "research/shortline/PC_L2_IC.md (commit 3c09369 pre-run)",
        "runtime_s": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"written {OUT_PATH} ({time.time()-t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
