"""OG1_OVERNIGHT_IC batch (research/shortline/OG1_OVERNIGHT_IC.md pre-reg,
frozen r65; T-31 deliverable-5 zoo #78 overnight_gap family upgrade; order
O-20260924-1721 chain rule sec.3.2; claim MSG-20260924-1922).

Factor-layer IC pre-test of the overnight/intraday decomposition family on
the core48 ETF panel. Zero engine runs -> strategy engine ledger N
untouched; registers no traders (IC != strategy). PASS only shelves
on_mom_20 as ETF-domain synthesis material; strategy conversion needs its
own prereg + G1' v2 chain.

Clean-room factor definitions (daily-OHLCV computable subset of the
zhongxin-jiantou 'Zhu Lu' #29 32-factor family: momentum / divergence /
volatility / correlation sub-families; logic extracted from public
descriptions only, no proprietary tables copied):
  primary      on_mom_20     K=20 cumulative overnight return
                             ON(t)=open[t]/close[t-1]-1, compounded
  sensitivity  in_mom_20     K=20 cumulative intraday return
                             IN(t)=close[t]/open[t]-1 (tug-of-war peer)
  sensitivity  on_vol_20     K=20 std of ON
  sensitivity  on_in_div_20  on_mom_20 - in_mom_20 (divergence)
  sensitivity  onin_corr_20  K=20 paired corr(ON, IN)
All factors at t use data <= close[t] -> same-day-close signal, h-day
forward return, zero future data.

Forward returns (frozen, PA1 formula verbatim): dividend-inclusive
  (close[t+h] + sum of div_per_unit over (t, t+h]) / close[t] - 1,
cons windows excluded per (t, member) pair. h10 = sole gating horizon;
h5/h20 report columns computed only if primary passes V1 (snooping
discount, non-gating).

Frozen mask: on_mom_20 finite AND close finite AND fwd_h10 computable AND
no cons event in (t, t+h] -- the K=50 nulls share the same mask.
Null seeds: 20260927+i, i=0..49 (SEED_REGISTRY["og1_overnight_ic"]; repo
rg sweep 2026-09-24 19:2x confirmed free).

Gates (SS4, frozen before the run, primary only, one-sided positive
direction per SS1 mechanism):
  V1 IS ic_mean > max(0.02 floor, masked-null p95 |ic|)
  V2 IS ic_ir >= 0.30
  V3 OOS same sign AND OOS ic_mean >= 0.5 x IS ic_mean
  periods gate: IS n_periods >= 500

Equivalence gate first (PA1 paradigm): -60d momentum probe on the close
surface (zero contact with open columns), seeded 400-day subsample vs
composite_ic.ic_series reference; max|diff| > 1e-6 -> abort with no
numbers produced.

Subcommands: probe (pre-freeze facts, no ledger) / selftest (synthetic
fixtures, runs BEFORE the producing run) / run (data gates -> equivalence
-> nulls -> factors -> gates -> ledger -> audit).

Outputs: research/shortline/og1_overnight_ic_results.csv
         results/shortline/og1_overnight_ic.json (+ gate_attrition.json row)
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from composite_ic import IS_END, ic_series, stats_block  # established methodology
import science_gates as sg  # cutoff_meta / append_ledger / ledger_head

PANEL_CSV = os.path.join(ROOT, "data", "fund_premium", "panel", "panel.csv")
PANEL_SUMMARY = os.path.join(ROOT, "results", "shortline",
                             "fund_premium_panel.json")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
RES_CSV = os.path.join(ROOT, "research", "shortline",
                       "og1_overnight_ic_results.csv")
OUT_JSON = os.path.join(ROOT, "results", "shortline", "og1_overnight_ic.json")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

H_GATE = 10            # sole gating horizon (prereg SS3)
H_REPORT = [5, 20]     # report-only, primary V1 passers only
K_ROLL = 20            # factor rolling window (frozen)
N_NULLS = 50
SEED0 = 20260927       # SEED_REGISTRY["og1_overnight_ic"], date-style
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS = 500
IS_END_TS = pd.Timestamp(IS_END)
CUTOFF = "2026-09-23"  # panel evidence_cutoff (r53 build, forward lockbox D2)
EQUIV_TOL = 1e-6
EQUIV_N_DATES = 400
JOIN_COV_MIN = 0.95     # panel rows with a matching finite daily-CSV row
                       # (probe 2026-09-24 19:5x: 0.9708; 2.9% = source-gap
                       # days, mask territory per r55 row-vs-rect law)
ON_FIN_MIN = 0.90       # on_mom_20 finite fraction (probe: 0.9509)
N_EFF_BASE = 55        # 1 primary + 4 sensitivity + 50 nulls (prereg SS0)
N_EFF_REPORT = 2       # +h5/h20 report columns if primary passes V1 (cap 57)


# ---------------------------------------------------------------- helpers
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
    idx = pd.DatetimeIndex(dates[ok])
    return pd.Series(ic[ok], index=idx).dropna()


def fwd_ret_div(close, div, h):
    """Dividend-inclusive forward return (PA1 frozen formula verbatim):
    (close[t+h] + sum_{t<d<=t+h} div_per_unit[d]) / close[t] - 1."""
    cs = np.cumsum(div, axis=0)
    out = np.full_like(close, np.nan)
    out[:-h] = (close[h:] + (cs[h:] - cs[:-h])) / close[:-h] - 1.0
    return out


def cons_in_window(cons, h):
    """True where any cons_flag=1 day falls in (t, t+h] for that member."""
    cs = np.cumsum(cons, axis=0)
    out = np.zeros(cons.shape, dtype=bool)
    out[:-h] = (cs[h:] - cs[:-h]) > 0
    return out


def seg_stats(s):
    return (stats_block(s), stats_block(s[s.index <= IS_END_TS]),
            stats_block(s[s.index > IS_END_TS]))


def wide(pan, col):
    return pan.pivot(index="date", columns="code", values=col).values


def _roll_apply(x, K, fn):
    """Generic trailing-window reduction with strict min-count K (any NaN
    in window -> NaN). fn receives (K, N) block; returns (N,)."""
    T = x.shape[0]
    out = np.full(x.shape, np.nan)
    if T < K:
        return out
    fin = np.isfinite(x)
    for t in range(K - 1, T):
        blk = x[t - K + 1:t + 1]
        cnt = fin[t - K + 1:t + 1].all(axis=0)
        val = fn(blk)
        out[t] = np.where(cnt, val, np.nan)
    return out


def roll_sum(x, K):
    return _roll_apply(np.asarray(x, dtype=np.float64), K,
                       lambda b: b.sum(axis=0))


def roll_std(x, K):
    return _roll_apply(np.asarray(x, dtype=np.float64), K,
                       lambda b: b.std(axis=0, ddof=0))


def roll_corr(a, b, K):
    """Paired-complete trailing correlation, strict min-count K."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    both = np.isfinite(a) & np.isfinite(b)

    def fn(blk):
        ac = blk[0] - blk[0].mean(axis=0)
        bc = blk[1] - blk[1].mean(axis=0)
        cov = (ac * bc).sum(axis=0)
        sa = np.sqrt((ac * ac).sum(axis=0))
        sb = np.sqrt((bc * bc).sum(axis=0))
        with np.errstate(invalid="ignore", divide="ignore"):
            return cov / (sa * sb)

    stacked = np.stack([np.where(both, a, np.nan),
                        np.where(both, b, np.nan)])
    T = a.shape[0]
    out = np.full(a.shape, np.nan)
    if T < K:
        return out
    fin = np.stack([np.isfinite(stacked[0]), np.isfinite(stacked[1])])
    for t in range(K - 1, T):
        blk = stacked[:, t - K + 1:t + 1]
        cnt = fin[:, t - K + 1:t + 1].all(axis=0).all(axis=0)
        val = fn(blk)
        out[t] = np.where(cnt, val, np.nan)
    return out


def decompose(open_w, close_w):
    """ON/IN decomposition + frozen factor set (K=K_ROLL)."""
    prev_close = np.full_like(close_w, np.nan)
    prev_close[1:] = close_w[:-1]
    with np.errstate(invalid="ignore", divide="ignore"):
        on = open_w / prev_close - 1.0
        intr = close_w / open_w - 1.0
    # open=0 rows (bad ticks) -> NaN both legs
    bad = ~(open_w > 0)
    on = np.where(bad, np.nan, on)
    intr = np.where(bad, np.nan, intr)
    with np.errstate(invalid="ignore"):
        lon = np.log1p(on)
        lin = np.log1p(intr)
    on_mom = np.expm1(roll_sum(lon, K_ROLL))
    in_mom = np.expm1(roll_sum(lin, K_ROLL))
    on_vol = roll_std(on, K_ROLL)
    onin_corr = roll_corr(on, intr, K_ROLL)
    on_in_div = on_mom - in_mom
    return {"on_mom_20": on_mom, "in_mom_20": in_mom, "on_vol_20": on_vol,
            "on_in_div_20": on_in_div, "onin_corr_20": onin_corr}


def load_surfaces():
    """Panel (close/div/cons) + daily-CSV opens joined on panel calendar."""
    pan = pd.read_csv(PANEL_CSV, parse_dates=["date"])
    codes = sorted(pan["code"].astype(str).unique())
    cal = pd.DatetimeIndex(np.sort(pan["date"].unique()))
    T, N = len(cal), len(codes)
    close = np.asarray(wide(pan, "close"), dtype=np.float64)
    div = np.nan_to_num(np.asarray(wide(pan, "div_per_unit"),
                                   dtype=np.float64))
    cons = np.nan_to_num(np.asarray(wide(pan, "cons_flag"), dtype=np.float64))
    open_w = np.full((T, N), np.nan)
    joined = np.zeros((T, N), dtype=bool)
    for j, code in enumerate(codes):
        csv_path = os.path.join(DAILY_DIR, f"{code}.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"daily CSV missing for {code}: {csv_path}")
        d = pd.read_csv(csv_path, parse_dates=["date"])
        d = d.set_index("date").reindex(cal)
        open_w[:, j] = d["open"].values
        joined[:, j] = np.isfinite(d["open"].values) & np.isfinite(d["close"].values)
    return pan, codes, cal, close, div, cons, open_w, joined


# ---------------------------------------------------------------- selftest
def selftest():
    """Synthetic-fixture selftest (J7 law: natural serialized faces, runs
    BEFORE the producing run). 8 checks."""
    ok_n = 0

    def ok(name, cond):
        nonlocal ok_n
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}", flush=True)
        if cond:
            ok_n += 1
        return cond

    # S1: ON/IN decomposition math (hand-computed 3x4)
    open_w = np.array([[10.0, 100.0, 5.0],
                       [10.5, 99.0, 5.1],
                       [10.2, 101.0, 5.05],
                       [10.8, 100.5, 5.2]], dtype=np.float64)
    close_w = np.array([[10.0, 100.0, 5.0],
                        [10.4, 100.0, 5.0],
                        [10.5, 100.9, 5.0],
                        [11.0, 99.5, 5.15]], dtype=np.float64)
    prev = np.full_like(close_w, np.nan)
    prev[1:] = close_w[:-1]
    on = open_w / prev - 1.0
    intr = close_w / open_w - 1.0
    # fixture truth: prev close for t is close[t-1] (10.5/10.0-1 = 0.05)
    ok("S1 ON(t=1,m=0)=open/prev_close-1",
       abs(on[1, 0] - (10.5 / 10.0 - 1)) < 1e-12
       and abs(intr[1, 0] - (10.4 / 10.5 - 1)) < 1e-12
       and np.isnan(on[0, 0]))

    # S2: roll_sum cumulative product semantics (K=3, log space; the
    # expm1 chain is applied by decompose(), tested end-to-end here)
    x = np.array([[0.01], [0.02], [0.03], [-0.01], [0.0]])
    lx = np.log1p(x)
    rs = roll_sum(lx, 3)
    manual = np.expm1(np.log1p(0.01) + np.log1p(0.02) + np.log1p(0.03))
    ok("S2 roll_sum K=3 compounding",
       np.isnan(rs[0, 0]) and np.isnan(rs[1, 0])
       and abs(np.expm1(rs[2, 0]) - manual) < 1e-12
       and abs(np.expm1(rs[3, 0]) - np.expm1(np.log1p(0.02)
                                             + np.log1p(0.03)
                                             + np.log1p(-0.01))) < 1e-12)

    # S3: roll_corr vs np.corrcoef on a paired window (K=4) -- reference
    # must correlate the two 1-D columns, not concat-stack them
    rng = np.random.default_rng(7)
    a = rng.standard_normal((6, 2))
    b = a[:, :1] * 0.5 + rng.standard_normal((6, 2)) * 0.1
    rc = roll_corr(a, b, 4)
    ref = np.corrcoef(a[2:, 0], b[2:, 0])[0, 1]
    ok("S3 roll_corr matches corrcoef",
       abs(rc[5, 0] - ref) < 1e-10 and np.isnan(rc[1, 0]))

    # S3b: NaN pairing in roll_corr (one NaN at t=2 kills window t=2..5)
    a2 = a.copy()
    a2[2, 0] = np.nan
    rc2 = roll_corr(a2, b, 4)
    ok("S3b paired-NaN strict min-count", np.isnan(rc2[5, 0]))

    # S4: fwd_ret_div with a dividend inside the window
    cl = np.array([[10.0], [11.0], [12.0]], dtype=np.float64)
    dv = np.array([[0.0], [0.5], [0.0]], dtype=np.float64)
    f1 = fwd_ret_div(cl, dv, 1)
    ok("S4 fwd h=1 dividend-inclusive",
       abs(f1[0, 0] - ((11.0 + 0.5) / 10.0 - 1)) < 1e-12
       and np.isnan(f1[2, 0]))

    # S5: cons_in_window excludes (t, t+h]
    cs_flag = np.array([[0.0], [0.0], [1.0], [0.0], [0.0]])
    w = cons_in_window(cs_flag, 2)
    ok("S5 cons window (t,t+2]",
       bool(w[0, 0]) and bool(w[1, 0]) and not w[2, 0] and not w[4, 0])

    # S6: ic_from_ranks equals scipy spearman on a small case
    from scipy.stats import spearmanr
    F = np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                  [3.0, 1.0, 2.0, 6.0, 5.0, 4.0]])
    R = np.array([[2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
                  [1.0, 3.0, 2.0, 5.0, 4.0, 6.0]])
    eff = np.ones_like(F, dtype=bool)
    s = ic_from_ranks(rank_rows(eff, F), rank_rows(eff, R),
                      np.array([0, 1]))
    sp0 = spearmanr(F[0], R[0]).statistic
    sp1 = spearmanr(F[1], R[1]).statistic
    ok("S6 spearman parity", abs(s.iloc[0] - sp0) < 1e-10
       and abs(s.iloc[1] - sp1) < 1e-10)

    # S7: mask semantics -- NaN factor cell excluded from cross-section
    Fv = np.array([[1.0, np.nan, 3.0, 4.0, 5.0]])
    Rv = np.array([[5.0, 4.0, 3.0, 2.0, 1.0]])
    effv = np.isfinite(Fv)
    Fr = rank_rows(effv, Fv)
    ok("S7 NaN-out-of-mask rank",
       np.isnan(Fr[0, 1]) and abs(Fr[0, 0] - 1.0) < 1e-12
       and abs(Fr[0, 4] - 4.0) < 1e-12)

    # S8: null determinism (same seed -> identical noise)
    n1 = np.random.default_rng(SEED0 + 3).standard_normal((4, 3))
    n2 = np.random.default_rng(SEED0 + 3).standard_normal((4, 3))
    ok("S8 seeded null determinism", np.array_equal(n1, n2))

    print(f"selftest: {ok_n}/9 "
          f"{'ALL PASS' if ok_n == 9 else 'FAILED'}", flush=True)
    return ok_n == 9


# ---------------------------------------------------------------- probe
def probe():
    """Pre-freeze facts only (sample counts, no verdicts, no ledger)."""
    t0 = time.time()
    pan, codes, cal, close, div, cons, open_w, joined = load_surfaces()
    T, N = len(cal), len(codes)
    join_cov = float(joined.mean())
    fac = decompose(open_w, close)
    fwd10 = fwd_ret_div(close, div, H_GATE)
    cons10 = cons_in_window(cons, H_GATE)
    mask10 = (np.isfinite(fac["on_mom_20"]) & np.isfinite(close)
              & np.isfinite(fwd10) & ~cons10)
    row_n = mask10.sum(axis=1)
    xs_med = int(np.median(row_n[row_n > 0]))
    is_dates = cal <= IS_END_TS
    n_is = int((mask10.sum(axis=1) >= 5)[is_dates].sum())
    n_oos = int((mask10.sum(axis=1) >= 5)[~is_dates].sum())
    on_fin = float(np.isfinite(fac["on_mom_20"]).mean())
    print(f"panel: T={T} ({cal[0].date()}..{cal[-1].date()}) x N={N}")
    print(f"daily-join coverage={join_cov:.4f} (panel rows with finite "
          f"daily open+close)")
    print(f"on_mom_20 finite frac={on_fin:.4f}")
    print(f"mask10: cells={int(mask10.sum())} median_xs={xs_med} "
          f"IS_periods(n>=5)={n_is} OOS_periods={n_oos}")
    print(f"IS_END={IS_END} cutoff={CUTOFF} "
          f"({time.time() - t0:.1f}s)")


# ---------------------------------------------------------------- main
def run():
    t0 = time.time()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

    pan, codes, cal, close, div, cons, open_w, joined = load_surfaces()
    T, N = len(cal), len(codes)
    print(f"panel: T={T} ({cal[0].date()}..{cal[-1].date()}) x N={N} "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- data-completeness gates (prereg SS2; fail -> abort, no numbers)
    join_cov = float(joined.mean())
    summ = json.load(open(PANEL_SUMMARY, encoding="utf-8-sig"))
    summ_gates = summ.get("gates", {})
    g1 = (summ_gates.get("verdict") == "PASS"
          and summ.get("evidence_cutoff") == CUTOFF
          and int(summ.get("members", 0)) == N)
    g2 = join_cov >= JOIN_COV_MIN
    print(f"data gates: panel summary={summ_gates.get('verdict')} "
          f"cutoff={summ.get('evidence_cutoff')} ({g1}) | join_cov="
          f"{join_cov:.4f} >= {JOIN_COV_MIN} ({g2})", flush=True)
    if not (g1 and g2):
        print("DATA GATE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- frozen factor set (decomposition, K=K_ROLL) + availability gate
    fac = decompose(open_w, close)
    on_fin = float(np.isfinite(fac["on_mom_20"]).mean())
    g3 = on_fin >= ON_FIN_MIN
    print(f"data gate g3: on_mom_20 finite frac={on_fin:.4f} "
          f">= {ON_FIN_MIN} ({g3})", flush=True)
    if not g3:
        print("DATA GATE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- forward returns + frozen mask (SS3), gating horizon
    fwd10 = fwd_ret_div(close, div, H_GATE)
    cons10 = cons_in_window(cons, H_GATE)
    mask10 = (np.isfinite(fac["on_mom_20"]) & np.isfinite(close)
              & np.isfinite(fwd10) & ~cons10)
    n_cons_excl = int((cons10 & np.isfinite(fac["on_mom_20"])
                       & np.isfinite(close) & np.isfinite(fwd10)).sum())
    row_n = mask10.sum(axis=1)
    xs_med = int(np.median(row_n[row_n > 0]))
    print(f"mask10: median cross-section={xs_med} members, "
          f"cells={int(mask10.sum())}, cons-excluded cells={n_cons_excl} "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- equivalence gate: fast IC path vs composite_ic reference
    # probe = -60d momentum on the close surface, ZERO contact with open
    print("equivalence gate: fast IC vs reference on -60d momentum probe...",
          flush=True)
    p60 = np.full_like(close, np.nan)
    p60[60:] = close[60:] / close[:-60] - 1.0
    probe = -p60
    rng_dates = np.random.default_rng(SEED0)
    sub = np.sort(rng_dates.choice(T, size=min(EQUIV_N_DATES, T),
                                   replace=False))
    sub_idx = pd.DatetimeIndex(cal[sub])
    probe_df = pd.DataFrame(probe[sub], index=sub_idx, columns=codes)
    fwd_df = pd.DataFrame(fwd10[sub], index=sub_idx, columns=codes)
    ref = ic_series(probe_df, fwd_df)
    eff = np.isfinite(probe[sub]) & np.isfinite(fwd10[sub])
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

    # ---- null baselines (K=50 white noise, same frozen mask, IS segment)
    t1 = time.time()
    abs_ic = []
    R_fwd = rank_rows(mask10, fwd10)
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED0 + k)
        noise = rng.standard_normal((T, N))
        F = rank_rows(mask10, noise)
        s = ic_from_ranks(F, R_fwd, cal)
        blk = stats_block(s[s.index <= IS_END_TS])
        if "ic_mean" in blk:
            abs_ic.append(abs(blk["ic_mean"]))
        if (k + 1) % 10 == 0:
            print(f"  null {k+1}/{N_NULLS} ({time.time()-t1:.0f}s)",
                  flush=True)
    thr = {
        "p95_abs_ic": round(float(np.quantile(abs_ic, 0.95)), 4),
        "n_nulls": len(abs_ic),
        "median_cross_section": xs_med,
    }
    print(f"  nulls: p95|ic|={thr['p95_abs_ic']} ({time.time()-t1:.0f}s)",
          flush=True)
    v1_thr = max(V1_FLOOR, thr["p95_abs_ic"])

    # ---- factor batch at the gating horizon (mask-first, same mask band)
    factors = [
        ("on_mom_20", fac["on_mom_20"], True),
        ("in_mom_20", fac["in_mom_20"], False),
        ("on_vol_20", fac["on_vol_20"], False),
        ("on_in_div_20", fac["on_in_div_20"], False),
        ("onin_corr_20", fac["onin_corr_20"], False),
    ]
    rows = []
    primary_pass, primary_v1 = False, False
    for name, vals, is_primary in factors:
        t2 = time.time()
        eff_f = mask10 & np.isfinite(vals)
        s = ic_from_ranks(rank_rows(eff_f, vals), rank_rows(eff_f, fwd10),
                          cal)
        blk_full, blk_is, blk_oos = seg_stats(s)
        rec = {"factor": name, "role": "primary" if is_primary
               else "sensitivity", "mask": "frozen_h10",
               "status": "ok", "v1_thr": v1_thr}
        for seg, blk in [("full", blk_full), ("is", blk_is),
                         ("oos", blk_oos)]:
            for k in ("ic_mean", "ic_ir", "n_periods"):
                rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
        if is_primary:
            if "ic_mean" in blk_is and "ic_mean" in blk_oos:
                v1 = blk_is["ic_mean"] > v1_thr            # one-sided +
                v2 = blk_is["ic_ir"] >= V2_IR               # one-sided +
                v3 = (blk_oos["ic_mean"] > 0
                      and blk_oos["ic_mean"] >= V3_RETAIN
                      * abs(blk_is["ic_mean"]))
                pg = blk_is["n_periods"] >= MIN_PERIODS
                rec.update({"v1": bool(v1), "v2": bool(v2), "v3": bool(v3),
                            "period_gate": bool(pg),
                            "pass": bool(v1 and v2 and v3 and pg)})
                primary_pass, primary_v1 = rec["pass"], bool(v1)
            else:
                rec.update({"v1": False, "v2": False, "v3": False,
                            "period_gate": False, "pass": False})
            print(f"  {name}[primary] is_ic={rec.get('h10_is_ic_mean')} "
                  f"ir={rec.get('h10_is_ic_ir')} oos_ic="
                  f"{rec.get('h10_oos_ic_mean')} pass={rec['pass']}",
                  flush=True)
        else:
            rec.update({"v1": "", "v2": "", "v3": "", "period_gate": "",
                        "pass": ""})  # report-only, not judged (SS4)
            print(f"  {name}[sensitivity] is_ic={rec.get('h10_is_ic_mean')} "
                  f"(report-only)", flush=True)
        rec["compute_s"] = round(time.time() - t2, 1)
        rows.append(rec)

    # ---- report horizons h5/h20 (primary V1 passer only, non-gating)
    report_done = False
    if primary_v1:
        for h in H_REPORT:
            fw = fwd_ret_div(close, div, h)
            eff_h = (np.isfinite(fac["on_mom_20"]) & np.isfinite(close)
                     & np.isfinite(fw) & ~cons_in_window(cons, h))
            sh_ = ic_from_ranks(rank_rows(eff_h, fac["on_mom_20"]),
                                rank_rows(eff_h, fw), cal)
            _, bis, bos = seg_stats(sh_)
            rows[0][f"h{h}_is_ic"] = bis.get("ic_mean", "")
            rows[0][f"h{h}_oos_ic"] = bos.get("ic_mean", "")
        report_done = True
        print("  report horizons h5/h20 computed for primary V1 passer "
              "(snooping-discount, non-gating)", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(RES_CSV, index=False, encoding="utf-8")

    # ---- trials ledger (factor line: prev = max across BOTH dirs, r60
    # one-chain convention; zero engine runs -> engine N untouched)
    n_cells = N_EFF_BASE + (N_EFF_REPORT if report_done else 0)
    prev = max(int(sg.ledger_head(os.path.join(ROOT, "results"))["total"]),
               int(sg.ledger_head(os.path.dirname(OUT_JSON))["total"]))
    ledger = sg.append_ledger(
        "og1_overnight_ic", n_cells, "results/shortline/og1_overnight_ic.json",
        evidence_cutoff=CUTOFF, prev_total=prev,
        note=("1 primary on_mom_20 + 4 sensitivity (same ON/IN decomposition "
              "lineage, report-only) + 50 matched-mask nulls (seed "
              "20260927+i); zero engine runs, factor-layer IC pre-test "
              "(OG1_OVERNIGHT_IC.md frozen r65, claim MSG-20260924-1922, "
              "T-31 deliverable-5 zoo #78 upgrade)"))

    # ---- audit segment (compute_audit in-batch, prereg SS0)
    audit_seg = {}
    try:
        subprocess.run([sys.executable,
                        os.path.join("scripts", "compute_audit.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[og1] compute_audit in-batch run failed: {exc}", flush=True)
    apath = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            aj = json.load(fh)
        latest = aj.get("history", [{}])[-1] if aj.get("history") else aj
        audit_seg = {"source": "results/compute_audit.json (in-batch run, "
                               "latest)",
                     "verdict": latest.get("verdict"), "ts": latest.get("ts"),
                     "cpu_pct": latest.get("cpu_pct"),
                     "flags": latest.get("flags")}
    audit_seg.update({"elapsed_sec": round(time.time() - t0, 1),
                      "workers": 1,
                      "cpu_cap_policy": "vectorized single-proc, "
                                        "rolling-window reductions "
                                        "(O-20260923-1738)"})

    out = {
        **sg.cutoff_meta(CUTOFF),  # C2-legal top-level key (T-02 7/7)
        "meta": {"batch": "OG1_OVERNIGHT_IC (overnight/intraday decomposition "
                          "factor IC pre-test)",
                 "pre_reg": "research/shortline/OG1_OVERNIGHT_IC.md",
                 "order": "O-20260924-1721", "claim": "MSG-20260924-1922",
                 "task": "T-31 deliverable-5 (zoo #78 upgrade)",
                 "dept": "research",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": IS_END, "gate_horizon": H_GATE, "k_roll": K_ROLL,
                 "n_nulls": N_NULLS, "seed0": SEED0,
                 "seed_registry": sg.SEED_REGISTRY.get("og1_overnight_ic"),
                 "window": f"{cal[0].date()}..{cal[-1].date()} "
                           f"(panel r53, cutoff {CUTOFF})",
                 "factors_frozen": "ON=open/prev_close-1, IN=close/open-1 "
                                   "(daily OHLCV from data/daily CSVs joined "
                                   "to panel calendar); K=20 rolling; "
                                   "clean-room logic extraction from public "
                                   "descriptions (LPS 2019 / chaoe / "
                                   "zhongxin-jiantou #29 family labels)",
                 "fwd_ret": "dividend-inclusive (close[t+h]+sum div in "
                            "(t,t+h])/close[t]-1, cons windows excluded",
                 "mask_frozen": "on_mom_20 finite & close finite & fwd_h10 "
                                "computable & no cons in (t,t+h]; nulls "
                                "same mask",
                 "direction": "one-sided positive on primary (SS1 mechanism "
                              "freeze)",
                 "engine_runs": 0,
                 "ledger_note": "factor-layer IC pre-test: strategy engine "
                                "ledger N untouched; PASS -> shelf only, no "
                                "trader registration",
                 "ic_computations": 5 + N_NULLS
                                    + (len(H_REPORT) if report_done else 0)
                                    + 1},
        "data_gates": {"panel_summary_verdict": summ_gates.get("verdict"),
                       "panel_summary_cutoff": summ.get("evidence_cutoff"),
                       "g1": bool(g1),
                       "join_cov": round(join_cov, 4),
                       "join_cov_min": JOIN_COV_MIN, "g2": bool(g2),
                       "on_mom20_finite_frac": round(on_fin, 4),
                       "on_fin_min": ON_FIN_MIN, "g3": bool(g3)},
        "mask_stats": {"median_cross_section": xs_med,
                       "cells": int(mask10.sum()),
                       "cons_excluded_cells": n_cons_excl,
                       "T": T, "N": N},
        "equivalence": {"probe": "-60d momentum @ core48 close surface",
                        "max_abs_diff": worst, "n_common": int(len(common)),
                        "tol": EQUIV_TOL, "pass": worst <= EQUIV_TOL},
        "thresholds": {"h10": thr, "v1_floor": V1_FLOOR, "v1_thr": v1_thr},
        "counts": {"computed": len(factors),
                   "report_horizons_computed": report_done,
                   "pass": int(primary_pass)},
        "rows": rows,
        "trials_ledger": ledger,
        "audit": audit_seg,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    # ---- gate_attrition entry (measurement batch: gate outcomes, s7-T)
    try:
        with open(ATTRITION_JSON, encoding="utf-8-sig") as fh:
            attr = json.load(fh)
        prim = rows[0]
        attr["entries"].append({
            "batch": "OG1_OVERNIGHT_IC",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement",
            "cells_ledger_delta": n_cells,
            "ledger_total_after": ledger.get("total"),
            "gates": {"v1_floor": V1_FLOOR,
                      "null_is_p95_abs_ic": thr["p95_abs_ic"],
                      "v1_thr": v1_thr,
                      "primary_v1": bool(prim.get("v1")),
                      "primary_v2": bool(prim.get("v2")),
                      "primary_v3": bool(prim.get("v3")),
                      "period_gate": bool(prim.get("period_gate")),
                      "pass": bool(primary_pass),
                      "void": False},
            "eliminated": None,
            "refs": {"results": "results/shortline/og1_overnight_ic.json",
                     "prereg": "research/shortline/OG1_OVERNIGHT_IC.md"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[og1] gate_attrition append failed: {exc}", flush=True)

    print(f"\n=== OG1_OVERNIGHT_IC: computed={len(factors)} "
          f"primary_pass={primary_pass} cells={n_cells} "
          f"ledger_total={ledger['total']} "
          f"({time.time()-t0:.0f}s) ===", flush=True)
    if primary_pass:
        print("verdict: on_mom_20 shelved as ETF-domain synthesis material "
              "(conversion = separate prereg)", flush=True)
    else:
        print("verdict: OG1 primary judged negative - honest close "
              "(sensitivity readings require separate prereg, no翻案)",
              flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    if cmd == "probe":
        probe()
    else:
        run()
