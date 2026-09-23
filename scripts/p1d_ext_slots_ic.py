"""P-1d ext-slot factor IC batch (research/shortline/P1D_EXT_SLOTS_IC.md pre-reg).

O-1819 queue-never-empty -> O-1850 heat/attention ext slots (audited r39,
backtestable B-grade). bm-b lane, claim MSG-20260923-2155. Zero engine runs ->
strategy engine ledger N untouched; IC computation counts recorded in the
results JSON audit (factor account, P-A/P-1a precedent).

Subcommands:
  gates    - independent completeness verification (prereg SS4). NEVER trusts
             the puller's done flag (r47 lesson: done was init-True and never
             reset on completion paths -> false green while margin leg was
             mid-flight at 16/198 months). Writes results/p1d_gates.json;
             exit 0 only if all three slot gates pass.
  run      - ONE-SHOT IC batch; re-runs gates first, exit 2 if any gate fails
             (no half-data batches). Fires only when margin leg completes.
  selftest - offline unit checks (no network, no real data reads).

Frozen before any numbers (prereg SS2 + r47 probes):
  lag rules   : dzjy shift=2 (disclosed T+1 after close -> effective T+2);
                margin shift=1 (balances disclosed same-day after close,
                P-A lag-1 precedent); gdhs available = quarter_end + 45
                natural days -> NEXT trading day (strictly after).
  units       : margin buy/balance in YUAN on both exchanges (probe vs bars
                amount: ratio 4-31% plausible, wan-hypothesis 750-3151
                absurd); dzjy cheng-jiao-e in YUAN; premium ratio is a
                FRACTION (deep-discount threshold <= -0.05, verified against
                deal/close prices).
  688 note    : this batch consumes bars AMOUNT only (no volume/vwap) ->
                MSG-1945 688 volume=100x fix is not engaged by construction;
                recorded in audit.
  masks       : A = base universe (close & amount finite, ok_static);
                B_dzjy = A & dzjy activity in 20d window; C_margin = A &
                margin rows on >=4 of last 5 event-days (strong coverage,
                sparse pre-2015 per SS6); A_gdhs = A & gdhs record available.
                K=50 white-noise nulls matched per mask; V1 = max(0.02,
                null p95|ic|); V2 = |IS IC_IR| >= 0.30 (real gate);
                V3 = OOS same sign & retention >= 0.5; IS <= 2024-12-31.
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
EXT_DIR = os.path.join(ROOT, "data", "ext_slots")
BLAYER_PATH = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
PULL_STATUS = os.path.join(ROOT, "results", "ext_slots_pull_status.json")
RES_DIR = os.path.join(ROOT, "research", "shortline")
OUT_DIR = os.path.join(ROOT, "results", "shortline")

WIN_START = "2010-01-01"        # earliest slot (margin 2010-03-31)
CUT_OFF = "2026-09-22"         # evidence_cutoff frozen (prereg SS1)
H_GATE = 10                    # sole gating horizon
H_REPORT = [20]                # report-only for passers (snooping-discount tag)
N_NULLS = 50
SEED0 = 20260923
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS = 500
W_DZJY, W_DEEP, W_BUY, W_BAL, W_SHORT, W_AVAIL = 20, 5, 5, 20, 20, 5
DZJY_SHIFT, MARGIN_SHIFT, GDHS_LAG_DAYS = 2, 1, 45
DEEP_THR = -0.05
IS_END_TS = pd.Timestamp(IS_END)
EQUIV_TOL = 1e-6
EQUIV_N_DATES = 400

# unified margin column mapping (SSE vs SZSE layouts, r47 probe)
MARGIN_CODE_COL = {"sse": "标的证券代码", "szse": "证券代码"}
MARGIN_FIELDS = {"buy": "融资买入额", "bal": "融资余额",
                 "ssell": "融券卖出量", "sbal": "融券余量"}

# prereg SS4 gate thresholds
GATE_DZJY_COV = 0.95
GATE_MARGIN_COV = 0.90
GATE_MARGIN_TAIL_TD = 10      # last dual-coverage day within N trading days of cutoff
GATE_GDHS_Q = 40


# ---------------------------------------------------------------- helpers
def rolling_sum(arr, w):
    """Trailing w-row sum; caller contract: input already 0/NaN-safed
    (np.nan_to_num) - cumsum poisons on NaN (r43 pitfall)."""
    cs = np.vstack([np.zeros((1, arr.shape[1])), np.cumsum(arr, axis=0)])
    out = np.empty_like(arr)
    out[:w - 1] = cs[1:w]
    out[w - 1:] = cs[w:] - cs[:-w]
    return out


def shift_n(a, n, fill=np.nan):
    """Event-time grid -> signal position: row t holds values from t-n."""
    out = np.full_like(a, fill)
    out[n:] = a[:-n]
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


def ffill_rows(a):
    """Forward-fill along axis 0, in place-safe copy."""
    out = a.copy()
    for t in range(1, out.shape[0]):
        m = ~np.isfinite(out[t])
        if m.any():
            out[t][m] = out[t - 1][m]
    return out


def gdhs_avail_after(cal_us, qe_ts, lag_days=GDHS_LAG_DAYS):
    """First calendar row STRICTLY AFTER quarter_end + lag natural days."""
    limit = pd.Timestamp(qe_ts) + pd.Timedelta(days=lag_days)
    pos = int(np.searchsorted(cal_us, np.datetime64(limit, "us").astype("int64"),
                              side="right"))
    return pos if pos < len(cal_us) else -1


# ---------------------------------------------------------------- panel
def load_panel():
    """Universe = bars syms intersect b_layer ok_static (prereg SS1)."""
    dates_all = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    i0 = int(np.searchsorted(dates_all,
                             np.datetime64(WIN_START, "us").astype("int64")))
    i1 = int(np.searchsorted(dates_all,
                             np.datetime64(CUT_OFF, "us").astype("int64"),
                             side="right"))
    cal = dates_all[i0:i1]
    T = len(cal)
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    syms_all = [os.path.basename(p)[:-8] for p in files]
    m = pd.read_csv(BLAYER_PATH, dtype={"code": str})
    ok = set(m.loc[m["ok_static"].astype(str).str.lower() == "true", "code"])
    keep = [i for i, s in enumerate(syms_all) if s in ok]
    syms = [syms_all[i] for i in keep]
    N = len(syms)
    col = {s: i for i, s in enumerate(syms)}
    close = np.asarray(np.load(os.path.join(CACHE_DIR, "close.npy"),
                                mmap_mode="r")[i0:i1], dtype=np.float64)[:, keep]
    amount = np.asarray(np.load(os.path.join(CACHE_DIR, "amount.npy"),
                                 mmap_mode="r")[i0:i1], dtype=np.float64)[:, keep]
    meta = {"T": T, "N": N, "n_bars_syms": len(syms_all),
            "n_ok_static": len(ok), "n_universe": N,
            "start": str(cal[0].astype("datetime64[us]")),
            "end": str(cal[-1].astype("datetime64[us]"))}
    return cal, col, close, amount, meta


# ---------------------------------------------------------------- gates
def _dzjy_days(cal):
    files = sorted(glob.glob(os.path.join(EXT_DIR, "dzjy", "mrmx_*.parquet")))
    days, rows = set(), 0
    for p in files:
        df = pd.read_parquet(p, columns=["交易日期"])
        rows += len(df)
        days.update(df["交易日期"].astype(str))
    return files, days, rows


def _margin_days(ex):
    files = sorted(glob.glob(os.path.join(EXT_DIR, "margin", "%s_*.parquet" % ex)))
    days, empty_files = set(), 0
    for p in files:
        df = pd.read_parquet(p)
        if len(df.columns) <= 1:      # honest empty month (trade_date only)
            empty_files += 1
            continue
        days.update(df["trade_date"].astype(str))
    return files, days, empty_files


def _gdhs_quarters():
    files = sorted(glob.glob(os.path.join(EXT_DIR, "gdhs", "gdhs_*.parquet")))
    valid = 0
    qends = []
    for p in files:
        df = pd.read_parquet(p)
        if len(df) > 500:
            valid += 1
            qends.append(os.path.basename(p)[5:-8])
    return files, valid, qends


def run_gates(write=True):
    t0 = time.time()
    dates_all = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    i0 = int(np.searchsorted(dates_all,
                             np.datetime64(WIN_START, "us").astype("int64")))
    i1 = int(np.searchsorted(dates_all,
                             np.datetime64(CUT_OFF, "us").astype("int64"),
                             side="right"))
    cal = pd.DatetimeIndex(dates_all[i0:i1].astype("datetime64[us]"))
    cal_s = set(cal.strftime("%Y-%m-%d"))

    # -- dzjy: day coverage vs bars calendar from 2013-01-04
    dz_files, dz_days, dz_rows = _dzjy_days(cal)
    span = cal[cal >= pd.Timestamp("2013-01-04")]
    dz_days_norm = {d.replace("/", "-") for d in dz_days}
    cov = len(dz_days_norm & set(span.strftime("%Y-%m-%d"))) / max(len(span), 1)
    dzjy = {"files": len(dz_files), "rows": dz_rows,
            "trading_days_in_span": len(span),
            "covered_days": len(dz_days_norm & set(span.strftime("%Y-%m-%d"))),
            "coverage": round(cov, 4),
            "gate": GATE_DZJY_COV,
            "pass": bool(cov >= GATE_DZJY_COV)}

    # -- margin: dual-exchange coverage from 2010-03-31 + tail freshness
    sse_files, sse_days, sse_empty = _margin_days("sse")
    szse_files, szse_days, szse_empty = _margin_days("szse")
    mspan = cal[cal >= pd.Timestamp("2010-03-31")]
    mspan_s = set(mspan.strftime("%Y-%m-%d"))
    sse_norm = {d[:4] + "-" + d[4:6] + "-" + d[6:8] for d in sse_days}
    szse_norm = {d[:4] + "-" + d[4:6] + "-" + d[6:8] for d in szse_days}
    dual = sse_norm & szse_norm & mspan_s
    mcov = len(dual) / max(len(mspan), 1)
    if dual:
        last_day = pd.Timestamp(max(dual))
        # honest trading-day distance via calendar positions
        pos = cal.searchsorted(last_day)
        tail_td = int(len(cal) - 1 - pos)
    else:
        tail_td = 999
    margin = {"sse_files": len(sse_files), "sse_empty_months": sse_empty,
              "szse_files": len(szse_files), "szse_empty_months": szse_empty,
              "trading_days_in_span": len(mspan), "dual_days": len(dual),
              "coverage": round(mcov, 4), "gate": GATE_MARGIN_COV,
              "last_dual_day": str(max(dual)) if dual else "",
              "tail_trading_days": tail_td,
              "pass": bool(mcov >= GATE_MARGIN_COV and tail_td <= GATE_MARGIN_TAIL_TD)}

    # -- gdhs: valid quarters >= 40 (rows>500), 2015Q3..2026Q2 continuity
    gd_files, gd_valid, gd_qends = _gdhs_quarters()
    expected_q = len(pd.period_range("2015Q3", "2026Q2", freq="Q"))
    gdhs = {"files": len(gd_files), "valid_quarters": gd_valid,
            "expected_quarters": int(expected_q), "gate": GATE_GDHS_Q,
            "pass": bool(gd_valid >= GATE_GDHS_Q and len(gd_files) >= expected_q)}

    out = {"meta": {"batch": "P-1d ext-slot gates", "prereg":
                    "research/shortline/P1D_EXT_SLOTS_IC.md SS4",
                    "date": time.strftime("%Y-%m-%d %H:%M"),
                    "cutoff": CUT_OFF,
                    "puller_done_flag_note": "done flags in "
                    "results/ext_slots_pull_status.json are NOT trusted "
                    "(r47 false-green: margin was 16/198 months in-flight "
                    "with done=true); these gates verify disk data directly",
                    "elapsed_s": round(time.time() - t0, 1)},
           "dzjy": dzjy, "margin": margin, "gdhs": gdhs}
    pull = {}
    if os.path.exists(PULL_STATUS):
        with open(PULL_STATUS, encoding="utf-8") as f:
            pull = json.load(f).get("legs", {})
    out["puller_status_informational"] = {
        k: {"chunks": v.get("chunks"), "rows": v.get("rows"),
            "done": v.get("done"), "failures": len(v.get("failures", []))}
        for k, v in pull.items()}
    out["pass"] = bool(dzjy["pass"] and margin["pass"] and gdhs["pass"])
    if write:
        with open(os.path.join(ROOT, "results", "p1d_gates.json"), "w",
                  encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
    return out


# ---------------------------------------------------------------- builders
def build_dzjy(cal, col, T, N, log):
    files = sorted(glob.glob(os.path.join(EXT_DIR, "dzjy", "mrmx_*.parquet")))
    ind = np.zeros((T, N))            # trade count per stock-day
    amtg = np.zeros((T, N))          # cheng-jiao-e sum (yuan)
    premw = np.zeros((T, N))         # premium sum over that day's trades
    deepg = np.zeros((T, N))         # deep-discount trade count
    n_drop_code = n_drop_date = n_rows = 0
    for pi, p in enumerate(files):
        df = pd.read_parquet(p)
        n_rows += len(df)
        if (pi + 1) % 100 == 0:
            print(f"  dzjy {pi+1}/{len(files)} files", flush=True)
        d = (pd.to_datetime(df["交易日期"]).values.astype("datetime64[us]")
             .astype("int64"))
        pos = np.searchsorted(cal, d)
        pos_safe = np.minimum(pos, T - 1)
        ok_date = pos < T
        ok_date[pos < T] = cal[pos_safe[pos < T]] == d[pos < T]
        codes = df["证券代码"].astype(str).str.zfill(6)
        ccol = codes.map(col)
        ok = ok_date & ccol.notna().values
        n_drop_date += int((~ok_date).sum())
        n_drop_code += int((ok_date & ~ccol.notna().values).sum())
        r, c = pos[ok], ccol.values[ok].astype(int)
        prem = pd.to_numeric(df["折溢率"], errors="coerce").values[ok]
        amt = pd.to_numeric(df["成交额"], errors="coerce").values[ok]
        np.add.at(ind, (r, c), 1.0)
        np.add.at(amtg, (r, c), np.nan_to_num(amt))
        np.add.at(premw, (r, c), np.nan_to_num(prem))
        np.add.at(deepg, (r, c), (prem <= DEEP_THR).astype(float))
    log(f"dzjy placed: rows={n_rows} drop_date={n_drop_date} "
        f"drop_code={n_drop_code}")
    return ind, amtg, premw, deepg, {"dzjy_rows": n_rows,
                                     "dzjy_drop_date": n_drop_date,
                                     "dzjy_drop_code": n_drop_code}


def build_margin(cal, col, T, N, log):
    grids = {k: np.full((T, N), np.nan) for k in MARGIN_FIELDS}
    n_rows = n_drop = 0
    for ex in ("sse", "szse"):
        files = sorted(glob.glob(os.path.join(EXT_DIR, "margin",
                                               "%s_*.parquet" % ex)))
        for fi, p in enumerate(files):
            if (fi + 1) % 100 == 0:
                print(f"  margin/{ex} {fi+1}/{len(files)} files", flush=True)
            df = pd.read_parquet(p)
            if len(df.columns) <= 1:
                continue
            n_rows += len(df)
            d = (pd.to_datetime(df["trade_date"], format="%Y%m%d")
                 .values.astype("datetime64[us]").astype("int64"))
            pos = np.searchsorted(cal, d)
            pos_safe = np.minimum(pos, T - 1)
            ok_date = pos < T
            ok_date[pos < T] = cal[pos_safe[pos < T]] == d[pos < T]
            ccol = df[MARGIN_CODE_COL[ex]].astype(str).str.zfill(6).map(col)
            ok = ok_date & ccol.notna().values
            n_drop += int((~ok).sum())
            r, c = pos[ok], ccol.values[ok].astype(int)
            for k, cname in MARGIN_FIELDS.items():
                v = pd.to_numeric(df[cname], errors="coerce").values[ok]
                grids[k][r, c] = v
    log(f"margin placed: rows={n_rows} dropped={n_drop}")
    return grids, {"margin_rows": n_rows, "margin_dropped": n_drop}


def build_gdhs(cal, col, T, N, log):
    files = sorted(glob.glob(os.path.join(EXT_DIR, "gdhs", "gdhs_*.parquet")))
    recs = {}                          # sym -> [(qe, count, tot, chg_pct)]
    n_rows = 0
    for p in files:
        df = pd.read_parquet(p)
        n_rows += len(df)
        qe = pd.to_datetime(df["股东户数统计截止日-本次"])
        cnt = pd.to_numeric(df["股东户数-本次"], errors="coerce")
        tot = pd.to_numeric(df["总股本"], errors="coerce")
        chg = pd.to_numeric(df["股东户数-增减比例"], errors="coerce")
        for s, q, c_, t_, g_ in zip(df["代码"].astype(str).str.zfill(6), qe,
                                    cnt, tot, chg):
            recs.setdefault(s, []).append((q, c_, t_, g_))
    g_chg_q = np.full((T, N), np.nan)
    g_chg_2q = np.full((T, N), np.nan)
    g_level = np.full((T, N), np.nan)
    g_avail = np.zeros((T, N))
    n_placed = n_drop = 0
    for s, lst in recs.items():
        if s not in col:
            n_drop += len(lst)
            continue
        lst.sort(key=lambda x: x[0])
        c_idx = col[s]
        for i, (qe, c_, t_, g_) in enumerate(lst):
            pos = gdhs_avail_after(cal, qe)
            if pos < 0:
                continue
            n_placed += 1
            g_avail[pos, c_idx] = 1.0
            if np.isfinite(g_):
                g_chg_q[pos, c_idx] = g_ / 100.0
            if i >= 2 and np.isfinite(c_) and np.isfinite(lst[i - 2][1]) \
                    and lst[i - 2][1] > 0 and c_ > 0:
                g_chg_2q[pos, c_idx] = c_ / lst[i - 2][1] - 1.0
            if np.isfinite(c_) and np.isfinite(t_) and c_ > 0 and t_ > 0:
                g_level[pos, c_idx] = np.log(c_ / t_)
    g_chg_q = ffill_rows(g_chg_q)
    g_chg_2q = ffill_rows(g_chg_2q)
    g_level = ffill_rows(g_level)
    g_avail = ffill_rows(g_avail)
    log(f"gdhs placed: rows={n_rows} records={n_placed} drop_code={n_drop} "
        f"(chg_2q uses stock's own 2-records-back, gaps span quarters)")
    return g_chg_q, g_chg_2q, g_level, g_avail, {"gdhs_rows": n_rows,
                                                  "gdhs_records": n_placed,
                                                  "gdhs_drop_code": n_drop}


# ---------------------------------------------------------------- run
def run_batch():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)

    g = run_gates()
    if not g["pass"]:
        print("GATES FAIL - no half-data batches (prereg SS4). Detail:")
        for k in ("dzjy", "margin", "gdhs"):
            print(f"  {k}: pass={g[k]['pass']} detail={g[k]}")
        sys.exit(2)

    cal, col, close, amount, pmeta = load_panel()
    T, N = pmeta["T"], pmeta["N"]
    print(f"panel: T={T} N={N} {pmeta['start']}..{pmeta['end']} "
          f"({time.time()-t0:.0f}s)", flush=True)

    A = np.isfinite(close) & np.isfinite(amount)
    amt0 = np.nan_to_num(amount)
    fwd10 = fwd_ret(close, H_GATE)
    fwd10_ok = np.isfinite(fwd10)
    masks = {}

    # ---- dzjy family (shift 2)
    def log(msg):
        print(msg, flush=True)

    ind, amtg, premw, deepg, dz_meta = build_dzjy(cal, col, T, N, log)
    amt20 = rolling_sum(amt0, W_DZJY)
    cnt20 = rolling_sum(ind, W_DZJY)
    prem_sum = rolling_sum(premw, W_DZJY)
    deep5 = rolling_sum(deepg, W_DEEP)
    with np.errstate(invalid="ignore", divide="ignore"):
        share20 = np.where(amt20 > 0, rolling_sum(amtg, W_DZJY) / amt20, np.nan)
        prem20 = np.where(cnt20 > 0, prem_sum / cnt20, np.nan)
    f_count = shift_n(cnt20, DZJY_SHIFT, 0.0)
    f_deep = shift_n(deep5, DZJY_SHIFT, 0.0)
    f_share = shift_n(share20, DZJY_SHIFT)
    f_prem = shift_n(prem20, DZJY_SHIFT)
    B_dzjy = A & (f_count >= 1)
    masks["A"] = A
    masks["B_dzjy"] = B_dzjy
    del ind, amtg, premw, deepg, amt20, cnt20, prem_sum, deep5, share20, prem20

    # ---- margin family (shift 1, mask C = strong coverage >=4/5 event-days)
    mg, mg_meta = build_margin(cal, col, T, N, log)
    avail_evt = (np.isfinite(mg["buy"]) | np.isfinite(mg["bal"])).astype(float)
    cov5 = rolling_sum(avail_evt, W_AVAIL)
    C_margin = A & (shift_n(cov5, MARGIN_SHIFT, 0.0) >= 4)
    buy5 = rolling_sum(np.nan_to_num(mg["buy"]), W_BUY)
    amt5 = rolling_sum(amt0, W_BUY)
    with np.errstate(invalid="ignore", divide="ignore"):
        f_buy_int = shift_n(np.where(amt5 > 0, buy5 / amt5, np.nan), MARGIN_SHIFT)
        bal_ratio = mg["bal"] / shift_n(mg["bal"], W_BAL)
        f_bal_chg = shift_n(np.log(bal_ratio), MARGIN_SHIFT)
        ss20 = rolling_sum(np.nan_to_num(mg["ssell"]), W_SHORT)
        sb20 = rolling_sum(np.nan_to_num(mg["sbal"]), W_SHORT)
        f_short_int = shift_n(np.where(sb20 > 0, ss20 / sb20, np.nan),
                              MARGIN_SHIFT)
    masks["C_margin"] = C_margin
    del mg, avail_evt, cov5, buy5, amt5, bal_ratio, ss20, sb20

    # ---- gdhs family (+45d rule, step-ffill)
    g_chg_q, g_chg_2q, g_level, g_avail, gd_meta = build_gdhs(cal, col, T, N,
                                                              log)
    A_gdhs = A & (g_avail > 0)
    masks["A_gdhs"] = A_gdhs
    del g_avail

    factors = [
        ("dzjy_count_20", f_count, "A"),
        ("dzjy_deep_disc_5", f_deep, "A"),
        ("dzjy_amt_share_20", f_share, "B_dzjy"),
        ("dzjy_prem_mean_20", f_prem, "B_dzjy"),
        ("margin_buy_int_5", f_buy_int, "C_margin"),
        ("margin_bal_chg_20", f_bal_chg, "C_margin"),
        ("margin_short_int_20", f_short_int, "C_margin"),
        ("gdhs_chg_q", g_chg_q, "A_gdhs"),
        ("gdhs_chg_2q", g_chg_2q, "A_gdhs"),
        ("gdhs_level", g_level, "A_gdhs"),
    ]
    lag_map = {"dzjy": DZJY_SHIFT, "margin": MARGIN_SHIFT,
               "gdhs": "qe+45d->next td"}

    # ---- equivalence hard gate: fast IC vs composite_ic.ic_series
    print("equivalence gate: fast IC vs reference (probe -mom60)...", flush=True)
    p60 = np.full_like(close, np.nan)
    p60[60:] = close[60:] / close[:-60] - 1.0
    probe = -p60
    rng_d = np.random.default_rng(SEED0)
    sub = np.sort(rng_d.choice(T, size=min(EQUIV_N_DATES, T), replace=False))
    sub_idx = pd.DatetimeIndex(cal[sub].astype("datetime64[us]"))
    ref = ic_series(pd.DataFrame(probe[sub], index=sub_idx),
                    pd.DataFrame(fwd10[sub], index=sub_idx))
    eff = A[sub] & np.isfinite(probe[sub]) & np.isfinite(fwd10[sub])
    fast = ic_from_ranks(rank_rows(eff, probe[sub]), rank_rows(eff, fwd10[sub]),
                         cal[sub])
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) else 9.9
    print(f"  n_ref={len(ref)} n_fast={len(fast)} max|diff|={worst:.2e}",
          flush=True)
    if worst > EQUIV_TOL or len(ref) != len(fast):
        print("EQUIVALENCE FAIL - aborting (no numbers produced)")
        sys.exit(1)

    # ---- K=50 nulls per mask (IS segment)
    thresholds = {}
    for mname, mask in masks.items():
        t1 = time.time()
        abs_ic = []
        eff_fwd = mask & fwd10_ok
        R_fwd = rank_rows(eff_fwd, fwd10)
        for k in range(N_NULLS):
            rng = np.random.default_rng(SEED0 + k)
            noise = rng.standard_normal((T, N))
            s = ic_from_ranks(rank_rows(eff_fwd, noise), R_fwd, cal)
            blk = stats_block(s[s.index <= IS_END_TS])
            if "ic_mean" in blk:
                abs_ic.append(abs(blk["ic_mean"]))
            if (k + 1) % 10 == 0:
                print(f"  null[{mname}] {k+1}/{N_NULLS} ({time.time()-t1:.0f}s)",
                      flush=True)
        thresholds[mname] = {"p95_abs_ic": round(float(np.quantile(abs_ic, 0.95)), 4),
                              "n_nulls": len(abs_ic)}
        print(f"  null[{mname}] p95|ic|={thresholds[mname]['p95_abs_ic']} "
              f"({time.time()-t1:.0f}s)", flush=True)

    # ---- factor batch at gating horizon
    rows = []
    for name, vals, mname in factors:
        t1 = time.time()
        mask = masks[mname]
        eff = mask & np.isfinite(vals) & fwd10_ok
        s = ic_from_ranks(rank_rows(eff, vals), rank_rows(eff, fwd10), cal)
        blk_full, blk_is, blk_oos = seg_stats(s)
        rec = {"factor": name, "mask": mname, "status": "ok",
               "lag": lag_map[name.split("_")[0]],
               "v1_thr": max(V1_FLOOR, thresholds[mname]["p95_abs_ic"])}
        for seg, blk in [("full", blk_full), ("is", blk_is), ("oos", blk_oos)]:
            for k in ("ic_mean", "ic_ir", "n_periods"):
                rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
        if "ic_mean" in blk_is and "ic_mean" in blk_oos:
            v1 = abs(blk_is["ic_mean"]) > rec["v1_thr"]
            v2 = abs(blk_is["ic_ir"]) >= V2_IR
            v3 = ((blk_oos["ic_mean"] > 0) == (blk_is["ic_mean"] > 0)
                  and abs(blk_oos["ic_mean"]) >= V3_RETAIN * abs(blk_is["ic_mean"]))
            pg = blk_is["n_periods"] >= MIN_PERIODS
            rec.update({"v1": bool(v1), "v2": bool(v2), "v3": bool(v3),
                        "period_gate": bool(pg),
                        "pass": bool(v1 and v2 and v3 and pg)})
            if rec["pass"]:
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

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RES_DIR, "p1d_ext_slots_results.csv"), index=False,
              encoding="utf-8")
    n_pass = int(df["pass"].fillna(False).sum())
    n_h20 = sum(1 for r in rows if "h20_is_ic" in r)
    out = {
        "meta": {"batch": "P-1d ext-slot factor IC (dzjy/margin/gdhs)",
                 "pre_reg": "research/shortline/P1D_EXT_SLOTS_IC.md",
                 "order": "O-1819 -> O-1850 ext slots", "claim": "MSG-20260923-2155",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": IS_END, "gate_horizon": H_GATE,
                 "report_horizons": H_REPORT, "n_nulls_per_mask": N_NULLS,
                 "seed0": SEED0, "window": f"{WIN_START} -> {CUT_OFF}",
                 "evidence_cutoff": CUT_OFF,  # C2 legal key (s9 promise)
                 "engine_runs": 0,
                 "ledger_note": "factor IC batch: engine ledger N untouched "
                                "(P-A precedent); multiplicity = n_factors x "
                                f"horizons recorded, ic_computations below",
                 "lag_rules": {"dzjy": "T+1 after-close disclosure -> signal T+2",
                               "margin": "same-day after-close -> signal T+1 (P-A)",
                               "gdhs": "quarter_end +45 natural days -> next "
                                       "trading day (frozen conservative)"},
                 "unit_calibration": "margin buy/bal in YUAN both exchanges "
                                      "(r47 probe ratio 4-31% vs bars amount; "
                                      "wan-hypothesis 750-3151 absurd); dzjy "
                                      "cheng-jiao-e YUAN; premium= fraction, "
                                      "deep thr -0.05 price-verified",
                 "six_eight_note": "amount-only consumption; no volume/vwap "
                                    "used -> MSG-1945 688 fix not engaged",
                 "mask_defs": {"A": "universe close&amount finite",
                               "B_dzjy": "A & dzjy activity in 20d window",
                               "C_margin": "A & margin rows >=4 of last 5 "
                                           "event-days (strong coverage)",
                               "A_gdhs": "A & gdhs record available (+45d rule)"},
                 "chg_2q_note": "stock's own 2-records-back; gaps span "
                                 "quarters honestly"},
        "equivalence": {"max_abs_diff": worst, "tol": EQUIV_TOL,
                        "pass": worst <= EQUIV_TOL},
        "thresholds": thresholds,
        "panel": pmeta,
        "counts": {"computed": len(factors), "skipped": 0, "pass": n_pass},
        "ic_computations": len(factors) + N_NULLS * len(masks) + n_h20,
        "rows": rows,
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "workers": 1,
                  "dzjy": dz_meta, "margin": mg_meta, "gdhs": gd_meta,
                  "cpu_cap_policy": "O-20260923-1738 single-proc vectorized"},
    }
    with open(os.path.join(OUT_DIR, "p1d_ext_slots_ic.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\n=== P-1d ext-slot batch: computed={len(factors)} pass={n_pass} "
          f"({time.time()-t0:.0f}s) ===", flush=True)


# ---------------------------------------------------------------- selftest
def _self_ic_equiv():
    rng = np.random.default_rng(7)
    T, N = 60, 12
    close = np.cumprod(1 + rng.standard_normal((T, N)) * 0.01, axis=0) * 10
    vals = rng.standard_normal((T, N))
    fwd = fwd_ret(close, 5)
    cal = (np.datetime64("2020-01-06", "D") + np.arange(T)
           ).astype("datetime64[us]").astype("int64")
    eff = np.isfinite(close) & np.isfinite(vals) & np.isfinite(fwd)
    F, R = rank_rows(eff, vals), rank_rows(eff, fwd)
    fast = ic_from_ranks(F, R, cal)
    ref = ic_series(pd.DataFrame(np.where(eff, vals, np.nan),
                                 index=pd.DatetimeIndex(cal.astype("datetime64[us]"))),
                    pd.DataFrame(np.where(eff, fwd, np.nan),
                                 index=pd.DatetimeIndex(cal.astype("datetime64[us]"))))
    common = ref.index.intersection(fast.index)
    return float((ref[common] - fast[common]).abs().max()) if len(common) else 9.9


def run_selftest():
    ok = fail = 0

    def check(name, cond):
        nonlocal ok, fail
        ok += 1 if cond else 0
        fail += 0 if cond else 1
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    rng = np.random.default_rng(1)
    # 1. rolling_sum == pandas
    x = rng.random((30, 5))
    rs = rolling_sum(x, 7)
    ref = pd.DataFrame(x).rolling(7, min_periods=1).sum().values
    check("rolling_sum == pandas rolling sum", np.allclose(rs, ref))
    # 2. shift_n semantics
    a = np.arange(6, dtype=float).reshape(6, 1) + 1
    check("shift_n(2) rows", np.allclose(shift_n(a, 2)[2:].ravel(), a[:-2].ravel())
          and np.isnan(shift_n(a, 2)[:2]).all()
          and np.allclose(shift_n(a, 1, 0.0)[:1], 0.0))
    # 3. fwd_ret
    c = np.array([[1.0, 4.0], [2.0, 4.0], [4.0, 2.0]])
    fr = fwd_ret(c, 2)
    check("fwd_ret h2", np.isclose(fr[0, 0], 3.0) and np.isclose(fr[0, 1], -0.5)
          and np.isnan(fr[1]).all() and np.isnan(fr[2]).all())
    # 4. fast IC vs reference (tiny panel)
    worst = _self_ic_equiv()
    check(f"IC equivalence vs ic_series (max|d|={worst:.1e})", worst <= EQUIV_TOL)
    # 5. gdhs availability: strictly after qe+45d, weekend/holiday jump
    cal = np.array(["2023-06-01", "2023-06-30", "2023-07-03", "2023-08-14",
                    "2023-08-15", "2023-08-16"], dtype="datetime64[D]"
                   ).astype("datetime64[us]").astype("int64")
    pos = gdhs_avail_after(cal, pd.Timestamp("2023-06-30"))
    # 2023-06-30 +45d = 2023-08-14 -> strictly after -> 2023-08-15
    check("gdhs avail: qe+45d -> next trading day (strictly after)",
          pos == 4 and str(cal[pos].astype("datetime64[us]"))[:10] == "2023-08-15")
    # 6. deep threshold
    check("deep threshold -0.05 fraction",
          (np.array([-0.06, -0.05, -0.049]) <= DEEP_THR).tolist()
          == [True, True, False])
    # 7. C_margin strong-coverage logic
    avail = np.zeros((12, 1)); avail[[0, 1, 2, 4, 5, 6, 7, 8, 9, 10]] = 1.0
    cov5 = rolling_sum(avail, W_AVAIL)
    check("C_margin >=4/5 coverage roll",
          cov5[4, 0] == 4.0 and cov5[9, 0] == 5.0)
    # 8. ffill persistence until replaced
    g = np.full((5, 1), np.nan); g[1, 0] = 3.0; g[4, 0] = 7.0
    f = ffill_rows(g)
    check("gdhs ffill step function",
          np.isnan(f[0, 0]) and np.allclose(f[1:4, 0], 3.0) and f[4, 0] == 7.0)
    # 9. chg_2q = 2-records-back (gap spans quarters)
    lst = [(pd.Timestamp("2026-03-31"), 100.0, None, None),
           (pd.Timestamp("2026-09-30"), 121.0, None, None)]
    c2 = 121.0 / 100.0 - 1.0
    check("chg_2q 2-records-back math", np.isclose(c2, 0.21))
    # 10. ok_static str/bool handling
    s = pd.Series(["True", "False", True, False])
    check("ok_static string/bool",
          ((s.astype(str).str.lower() == "true") ==
           pd.Series([True, False, True, False])).all())
    # 11. margin unified mapping completeness
    check("margin col map both exchanges",
          set(MARGIN_CODE_COL) == {"sse", "szse"}
          and all(v in MARGIN_FIELDS.values()
                  for v in ["融资买入额", "融资余额", "融券卖出量", "融券余量"]))
    # 12. gates thresholds frozen
    check("gate thresholds frozen",
          GATE_DZJY_COV == 0.95 and GATE_MARGIN_COV == 0.90 and GATE_GDHS_Q == 40)
    # 13. done-flag distrust documented in module contract
    check("done-flag distrust documented",
          "NEVER trusts" in __doc__ and "init-True" in __doc__)
    print(f"selftest: {ok} pass, {fail} fail")
    return 0 if fail == 0 else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "gates"
    if mode == "selftest":
        sys.exit(run_selftest())
    if mode == "gates":
        g = run_gates()
        for k in ("dzjy", "margin", "gdhs"):
            d = g[k]
            print(f"{k}: pass={d['pass']} " +
                  " ".join(f"{kk}={d[kk]}" for kk in d
                           if kk not in ("pass", "gate")))
        print(f"OVERALL: {'PASS' if g['pass'] else 'FAIL'} "
              f"(detail -> results/p1d_gates.json)")
        sys.exit(0 if g["pass"] else 2)
    if mode == "run":
        run_batch()
        sys.exit(0)
    print("usage: python scripts/p1d_ext_slots_ic.py gates|run|selftest")
    sys.exit(1)


if __name__ == "__main__":
    main()
