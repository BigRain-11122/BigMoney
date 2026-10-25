"""Does the beta-targeted book deliver the beta it prints on the label, and can the cash
leg be financed at the repo rate we actually observe?

r1254 sold the package at a stated beta and beat a same-beta index+cash mix by +2.5 / +4.9 /
+7.2pp/yr, but it left two honesty gaps that a product cannot carry:

  1. the label is not the exposure -- the expanding-window OLS estimator runs high, so the
     overlay delivered only ~77% of the requested beta (0.30 -> 0.229). An investor buying
     "beta 0.30" got 0.23 of market exposure plus an unexplained 34% cash drag;
  2. the unused capital earned a flat ASSUMED rate (0% base / 2% financed), because no repo
     series was wired in. r1254 listed that as a caveat; `data/repo_daily/GC001.csv` has
     been on disk since 2026-10-19, so the assumption can be replaced by observation.

This module answers both on one pass:

  A) five beta estimators -- expanding (min 126 bars, the r1254 rule), rolling 252 / 126 /
     63 / 42 bars -- scored by |delivered beta - target| and by the excess they keep;
  B) three cash legs -- flat 0%, flat 2%, and GC001 (1-day repo) accrued over the ACTUAL
     calendar gap between bars, at the rate quoted on the close of the prior bar.

Rules inherited unchanged from r1254 (never re-litigated here): decision every R=20 bars on
the close; k = target / beta_hat clipped to [0,1] (de-risk only, no implicit leverage); the
decision applies from the next bar; |delta k| x 8bp per side is charged on BOTH the overlay
and the benchmark. The book itself, its cost model and its fills come from
`CR.phase_book_cost`, i.e. the same engine as every ETF note since r1245.

Causality note on the repo leg: GC001's close on bar t is an annualised yield, known at
t's close, and it is used for the t -> t+1 calendar gap. A missing quote accrues nothing
(no silent fallback to the flat rate) and is counted in `cash_missing_bars`.

Exploratory: no preregistration, no verdict, no ledger booking.

Usage:
  python scripts/etf_phase_beta_window.py --selftest
  python scripts/etf_phase_beta_window.py
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F  # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts import etf_phase_cost_rolling as CR  # noqa: E402
from scripts import etf_phase_beta_target as BT  # noqa: E402
from scripts.etf_asset_class import classify  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOR = BT.ANCHOR
OOS = BT.OOS
REBAL = BT.REBAL
N_HOLD = BT.N_HOLD
COST_BP = BT.COST_BP
MKT = BT.MKT
TARGETS = BT.TARGETS
MIN_HIST = BT.MIN_HIST
REPO_PATH = os.path.join(BASE, "data", "repo_daily", "GC001.csv")
OUT_PATH = os.path.join(BASE, "results", "etf_phase_beta_window.json")

# estimator name -> rolling window in bars (None = expanding, the r1254 rule)
ESTIMATORS = (("expanding", None), ("roll252", 252), ("roll126", 126),
              ("roll63", 63), ("roll42", 42))


# ---------------------------------------------------------------------------------------
# beta estimators
# ---------------------------------------------------------------------------------------
def rolling_beta(rp, rm, win):
    """Causal slope of package on market returns over the last `win` bars.

    `win=None` reproduces the r1254 expanding estimator (min 2 observations), so the grid
    always contains the previous answer for reference.
    """
    if win is None:
        cov = rp.rolling(len(rp), min_periods=2).cov(rm)
        var = rm.rolling(len(rm), min_periods=2).var()
        return cov / var
    w = int(win)
    cov = rp.rolling(w, min_periods=w).cov(rm)
    var = rm.rolling(w, min_periods=w).var()
    return cov / var


def min_hist_for(win):
    """Decisions need a full estimation window; the expanding rule keeps r1254's 126."""
    return MIN_HIST if win is None else max(MIN_HIST, int(win))


def k_schedule_win(rp, rm, target, win, step=REBAL):
    """[(decision_date, k, beta_hat)] with the estimator window `win` (None = expanding)."""
    betas = rolling_beta(rp, rm, win)
    out, n = [], len(rp)
    i = min_hist_for(win)
    while i < n:
        b = betas.iloc[i]
        if b is None or not np.isfinite(b) or b <= 1e-6:
            i += step
            continue
        out.append((rp.index[i], float(min(1.0, max(0.0, target / b))), float(b)))
        i += step
    return out


# ---------------------------------------------------------------------------------------
# cash legs
# ---------------------------------------------------------------------------------------
def load_repo_rates(path=REPO_PATH):
    """GC001 annualised yield (%) indexed by its own trading date; empty if absent."""
    if not os.path.exists(path):
        return pd.Series(dtype=float)
    df = pd.read_csv(path)
    d = pd.to_datetime(df["date"])
    s = pd.Series(df["close"].astype(float).to_numpy(), index=d)
    return s[~s.index.duplicated(keep="last")].sort_index()


def repo_daily_cash(idx, rates):
    """Daily cash accrual for bar-to-bar steps, from the rate quoted on the PRIOR bar.

    1-day repo pays for calendar days, so a Friday-to-Monday step earns three days and a
    holiday gap earns however long it was -- that is where the "flat 2%" assumption was
    most wrong. A missing quote accrues nothing and is counted, never silently replaced.
    """
    idx = pd.DatetimeIndex(idx)
    out = pd.Series(0.0, index=idx, dtype=float)
    missing = 0
    for i in range(1, len(idx)):
        p, d = idx[i - 1], idx[i]
        gap = max(int((d - p).days), 1)
        r = rates.get(p, np.nan) if len(rates) else np.nan
        if r is None or not np.isfinite(r):
            missing += 1
            continue
        out.iloc[i] = float(r) / 100.0 * gap / 365.0
    return out, missing


# ---------------------------------------------------------------------------------------
# accounting
# ---------------------------------------------------------------------------------------
def beta_exact_series(rm, idx, beta, rf):
    """Constant-weight index book at the beta actually delivered, same cash leg both ways."""
    nav, out = 1.0, []
    for d in idx:
        rf_day = float(rf.get(d, 0.0) or 0.0) if isinstance(rf, pd.Series) else float(rf)
        nav *= 1.0 + beta * float(rm.loc[d]) + (1.0 - beta) * rf_day
        out.append(nav)
    return pd.Series(out, index=idx)


def k_stats(sched):
    ks = [k for _, k, _ in sched]
    if not ks:
        return {"n": 0}
    turn = sum(abs(ks[i] - ks[i - 1]) for i in range(1, len(ks)))
    return {"n": len(ks), "mean": round(float(np.mean(ks)), 3),
            "min": round(float(np.min(ks)), 3), "max": round(float(np.max(ks)), 3),
            "cap_share": round(sum(1 for k in ks if k >= 0.999) / float(len(ks)), 3),
            "k_turnover": round(float(turn), 3),
            "k_cost_pct_of_nav": round(turn * COST_BP / 100.0, 3)}


# ---------------------------------------------------------------------------------------
# selftest -- fixtures where the right answer is known by construction
# ---------------------------------------------------------------------------------------
def selftest():
    ok = total = 0

    def chk(name, cond, extra=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[ok] %s %s" % (name, extra))
        else:
            print("[FAIL] %s %s" % (name, extra))

    rng = np.random.default_rng(20261025)
    idx = pd.bdate_range("2020-01-01", periods=400)
    rm = pd.Series(rng.normal(0.0002, 0.01, len(idx)), index=idx)
    rp = 0.5 * rm                      # package beta is exactly 0.5 by construction
    pkg = (1.0 + rp).cumprod()
    mkt = (1.0 + rm).cumprod()

    # leg 1: a rolling slope on a series built as 0.5*market must be exactly 0.5
    b63 = rolling_beta(rp, rm, 63).dropna()
    chk("leg1 rolling beta recovers a constant 0.5", bool(len(b63)) and
        float(np.max(np.abs(b63 - 0.5))) < 1e-9,
        "maxerr=%.2e n=%d" % (float(np.max(np.abs(b63 - 0.5))), len(b63)))

    # leg 2: warm-up -- no estimate before a full window
    b = rolling_beta(rp, rm, 63)
    chk("leg2 warm-up leaves win-1 NaN", int(b.iloc[:62].isna().sum()) == 62 and
        bool(np.isfinite(b.iloc[62])), "nan=%d" % int(b.iloc[:62].isna().sum()))

    # leg 3: causality -- a future rewrite may not move any earlier k
    rp_alt = rp.copy()
    rp_alt.iloc[-5:] = rp_alt.iloc[-5:] * 3.0
    a = [(str(d.date()), round(k, 12)) for d, k, _ in k_schedule_win(rp, rm, 0.25, 63)]
    b2 = [(str(d.date()), round(k, 12)) for d, k, _ in k_schedule_win(rp_alt, rm, 0.25, 63)]
    chk("leg3 rolling k schedule has no lookahead", a == b2, "n=%d" % len(a))

    # leg 4: the rf plumbing must reproduce the old flat-rate path bit for bit
    sched = k_schedule_win(rp, rm, 0.25, 126)
    flat = pd.Series(0.02 / 252.0, index=rp.index)
    _, nav_flat, _ = BT.apply_overlay(rp, rm, sched, 0.02, 8.0)
    _, nav_rf, _ = BT.apply_overlay(rp, rm, sched, 0.0, 8.0, rf=flat)
    chk("leg4 rf=const series == flat cash_ann", abs(float(nav_flat.iloc[-1]) -
                                                     float(nav_rf.iloc[-1])) < 1e-12,
        "d=%.2e" % abs(float(nav_flat.iloc[-1]) - float(nav_rf.iloc[-1])))

    # leg 5: calendar-gap accrual -- Fri->Mon earns three days, not one
    f_idx = pd.DatetimeIndex(["2021-01-08", "2021-01-11", "2021-01-12"])  # Fri, Mon, Tue
    rates = pd.Series([3.65, 3.65, 3.65], index=f_idx)
    cash, miss = repo_daily_cash(f_idx, rates)
    want = 3.65 / 100.0 * 3 / 365.0
    chk("leg5 weekend gap earns the calendar days", abs(float(cash.iloc[1]) - want) < 1e-15
        and abs(float(cash.iloc[2]) - 3.65 / 100.0 / 365.0) < 1e-15 and miss == 0,
        "mon=%.8f want=%.8f" % (float(cash.iloc[1]), want))

    # leg 6: the rate used for a step is the PRIOR bar's quote (no same-day lookahead)
    rates2 = pd.Series([1.0, 9.0, 9.0], index=f_idx)     # Monday's own quote must not matter
    cash2, _ = repo_daily_cash(f_idx, rates2)
    chk("leg6 step uses prior-bar quote only",
        abs(float(cash2.iloc[1]) - 1.0 / 100.0 * 3 / 365.0) < 1e-15,
        "mon=%.8f" % float(cash2.iloc[1]))

    # leg 7: missing quote accrues nothing and is counted, never faked
    rates3 = pd.Series([np.nan, 9.0, 9.0], index=f_idx)
    cash3, miss3 = repo_daily_cash(f_idx, rates3)
    chk("leg7 missing quote accrues zero and is counted",
        float(cash3.iloc[1]) == 0.0 and miss3 == 1, "miss=%d" % miss3)

    # leg 8: label vs delivery on an exactly-1.0-beta book -- the overlay must land on 0.30
    sched8 = k_schedule_win(rm, rm, 0.30, 63)
    so8, _, _ = BT.apply_overlay(rm, rm, sched8, 0.0, 8.0)
    got = BT.realised_beta(so8, mkt)
    chk("leg8 unbiased estimate delivers the target", got is not None and abs(got - 0.30) < 0.02,
        "beta=%.3f" % (got or float("nan")))

    # leg 8b: a shrunk k on a 0.5-beta book must deliver exactly k x 0.5
    sched8b = [(d, 0.5, 0.5) for d in rp.index[::REBAL]]
    so8b, _, _ = BT.apply_overlay(rp, rm, sched8b, 0.0, 0.0)
    got8b = BT.realised_beta(so8b, mkt)
    chk("leg8b delivered beta = k x true beta", got8b is not None and abs(got8b - 0.25) < 1e-9,
        "beta=%.6f" % (got8b or float("nan")))

    # leg 9: k is clipped to [0,1] -- asking for more beta than the book has is not leverage
    s9 = k_schedule_win(pkg.pct_change().dropna(), rm, 0.99, 63)
    chk("leg9 k clipped at 1.0", all(k <= 1.0 + 1e-12 for _, k, _ in s9),
        "maxk=%.3f" % max(k for _, k, _ in s9))

    # leg 10: a window longer than the history must not crash and must stay silent
    s10 = k_schedule_win(rp.iloc[:30], rm.iloc[:30], 0.2, 252)
    chk("leg10 over-long window yields no decisions", s10 == [], "n=%d" % len(s10))

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


# ---------------------------------------------------------------------------------------
def main():
    if "--selftest" in sys.argv:
        return selftest()
    t_all = time.time()
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    mkt_col = next((c for c in MKT if c in close.columns), None)
    if mkt_col is None:
        print("FATAL: no 510300 column on the panel")
        return 2
    mkt = close[mkt_col]

    t0 = time.time()
    pkg, cells = CR.phase_book_cost(score, close[cols], openp[cols], N_HOLD, COST_BP)
    print("package ready %.0fs | bars=%d cols=%d" % (time.time() - t0, close.shape[0],
                                                    len(cols)), flush=True)

    idx = pkg.index.intersection(mkt.index)
    rp_all, rm_all = BT.rets(pkg.reindex(idx)), BT.rets(mkt.reindex(idx))
    rates = load_repo_rates()
    cash_rf, cash_missing = repo_daily_cash(rp_all.index, rates)
    cash_rf = cash_rf.reindex(rp_all.index).fillna(0.0)
    cash_mean_ann = float(cash_rf.mean() * 252.0) if len(cash_rf) else 0.0
    print("repo leg: %d bars, %d missing quotes, mean accrual %.2f%%/yr (2020-07..%s)"
          % (len(cash_rf), cash_missing, cash_mean_ann * 100, idx[-1].date()), flush=True)

    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "anchor": ANCHOR, "rebal": REBAL, "n_hold": N_HOLD, "cost_bp_per_side": COST_BP,
        "universe": "bond_removed (equity/commodity/crossborder), %d instruments" % len(cols),
        "market_proxy": mkt_col,
        "question": "does the book deliver the beta it prints, and can the cash leg be "
                    "financed at the observed GC001 repo rate?",
        "estimators": {name: {"window": win, "min_hist": min_hist_for(win)}
                       for name, win in ESTIMATORS},
        "cash_legs": {"flat0": 0.0, "flat2": 0.02,
                      "gc001": {"source": "data/repo_daily/GC001.csv",
                                "accrual": "prior-bar close (%) x calendar gap days / 365",
                                "mean_accrual_ann_pct": round(cash_mean_ann * 100, 3),
                                "missing_bar_steps": cash_missing}},
        "grid": {}, "summary": {},
        "caveats": [
            "survivorship: on-disk panel holds ETFs that still exist",
            "GC001 is a single 1-day tenor; a real cash desk would ladder (GC001/007/014) "
            "and the short tenor is the cheapest assumption, not the best execution",
            "repo rolling is assumed cost-free; 1-day repo fees are negligible but non-zero",
            "k is revised every 20 bars so delivered beta still wanders inside a segment",
            "exploratory: no preregistration, no verdict, no ledger booking",
        ],
    }

    for est, win in ESTIMATORS:
        for tgt in TARGETS:
            sched = k_schedule_win(rp_all, rm_all, tgt, win)
            for leg, cash in (("flat0", 0.0), ("flat2", 0.02), ("gc001", None)):
                rf = cash_rf if leg == "gc001" else None
                so, sb, kk = BT.apply_overlay(rp_all, rm_all, sched,
                                              cash if cash is not None else 0.0,
                                              COST_BP, rf=rf)
                if so is None:
                    continue
                m_s, m_b = F.metrics(so, "overlay"), F.metrics(sb, "bench")
                oos_s = F.metrics(so[so.index >= OOS], "overlay:oos")
                oos_b = F.metrics(sb[sb.index >= OOS], "bench:oos")
                rb_ov = BT.realised_beta(so, mkt) or 0.0
                rb_oos = BT.realised_beta(so[so.index >= OOS], mkt) or 0.0
                be = beta_exact_series(rm_all, so.index, rb_ov,
                                       cash_rf if leg == "gc001" else cash / 252.0)
                m_be = F.metrics(be, "bench_beta_exact")
                oos_be = F.metrics(be[be.index >= OOS], "bench_beta_exact:oos")
                roll = CR.rolling_excess(so, sb)
                ex = [r["excess_pp"] for r in roll]
                key = "%s_t%.2f_%s" % (est, tgt, leg)
                out["grid"][key] = {
                    "estimator": est, "window": win, "target_beta": tgt, "cash_leg": leg,
                    "k": k_stats(sched),
                    "delivered_beta": {"full": round(rb_ov, 3), "oos_2024plus": round(rb_oos, 3),
                                       "ratio_to_target": round(rb_ov / tgt, 3) if tgt else None},
                    "full": {"overlay": m_s, "benchmark": m_b,
                             "excess_pp": round((m_s["cagr"] - m_b["cagr"]) * 100, 2),
                             "benchmark_beta_exact": m_be,
                             "excess_vs_beta_exact_pp": round((m_s["cagr"] - m_be["cagr"]) * 100, 2)},
                    "oos_2024plus": {"overlay": oos_s, "benchmark": oos_b,
                                     "excess_pp": round((oos_s["cagr"] - oos_b["cagr"]) * 100, 2),
                                     "benchmark_beta_exact": oos_be,
                                     "excess_vs_beta_exact_pp": round(
                                         (oos_s["cagr"] - oos_be["cagr"]) * 100, 2)},
                    "per_year": BT.year_table(so, sb),
                    "rolling_504": {"n": len(ex), "positive": sum(1 for v in ex if v > 0),
                                    "median_pp": round(sorted(ex)[len(ex) // 2], 2) if ex else None,
                                    "min_pp": min(ex) if ex else None},
                }
                if leg == "gc001":
                    print("[%s t=%.2f gc001] delivered %.3f (%.0f%% of label) | "
                          "overlay %.2f%% vs bench %.2f%% = %+.2fpp | vs beta-exact %+.2fpp | "
                          "k mean %.2f turn %.2f"
                          % (est, tgt, rb_ov, 100 * rb_ov / tgt, m_s["cagr"] * 100,
                             m_b["cagr"] * 100, out["grid"][key]["full"]["excess_pp"],
                             out["grid"][key]["full"]["excess_vs_beta_exact_pp"],
                             out["grid"][key]["k"]["mean"], out["grid"][key]["k"]["k_turnover"]),
                          flush=True)

    # summary: delivery accuracy per estimator, and what the cash leg is worth
    dl = {}
    for est, win in ESTIMATORS:
        rows = {}
        for tgt in TARGETS:
            g = out["grid"].get("%s_t%.2f_gc001" % (est, tgt))
            if not g:
                continue
            rows["t%.2f" % tgt] = {
                "delivered_beta": g["delivered_beta"]["full"],
                "ratio_to_target": g["delivered_beta"]["ratio_to_target"],
                "abs_miss_pp_beta": round(abs(g["delivered_beta"]["full"] - tgt), 3),
                "cagr_pct": round(g["full"]["overlay"]["cagr"] * 100, 2),
                "sharpe": g["full"]["overlay"]["sharpe"],
                "excess_pp": g["full"]["excess_pp"],
                "excess_vs_beta_exact_pp": g["full"]["excess_vs_beta_exact_pp"],
                "k_mean": g["k"]["mean"],
                "cap_share": g["k"]["cap_share"],
                "k_turnover": g["k"]["k_turnover"],
            }
        dl[est] = rows
    out["summary"]["delivery_by_estimator"] = dl
    out["summary"]["mean_abs_beta_miss"] = {
        est: round(float(np.mean([r["abs_miss_pp_beta"] for r in rows.values()])), 4)
        for est, rows in dl.items() if rows}
    out["summary"]["cash_leg_value_pp"] = {}
    for est, win in ESTIMATORS:
        for tgt in TARGETS:
            g0 = out["grid"].get("%s_t%.2f_flat0" % (est, tgt))
            g2 = out["grid"].get("%s_t%.2f_flat2" % (est, tgt))
            g1 = out["grid"].get("%s_t%.2f_gc001" % (est, tgt))
            if not (g0 and g1):
                continue
            out["summary"]["cash_leg_value_pp"]["%s_t%.2f" % (est, tgt)] = {
                "gc001_minus_flat0_pp": round((g1["full"]["overlay"]["cagr"] -
                                              g0["full"]["overlay"]["cagr"]) * 100, 2),
                "gc001_minus_flat2_pp": round((g1["full"]["overlay"]["cagr"] -
                                              g2["full"]["overlay"]["cagr"]) * 100, 2)
                if g2 else None,
            }
    best = min(out["summary"]["mean_abs_beta_miss"].items(), key=lambda kv: kv[1])
    out["summary"]["best_delivery_estimator"] = {"name": best[0],
                                                 "mean_abs_beta_miss": best[1]}

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("\nmean |delivered - target|: %s"
          % json.dumps(out["summary"]["mean_abs_beta_miss"], indent=0), flush=True)
    print("cash leg (gc001 - flat0) pp/yr: %s"
          % json.dumps({k: v["gc001_minus_flat0_pp"]
                        for k, v in out["summary"]["cash_leg_value_pp"].items()}, indent=0),
          flush=True)
    print("best delivery = %s (miss %.3f)" % (best[0], best[1]), flush=True)
    print("wrote %s (%.0fs total)" % (OUT_PATH, time.time() - t_all), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())