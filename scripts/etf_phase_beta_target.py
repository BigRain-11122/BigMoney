"""Can the 20-phase book be sold at a stated beta?

r1253 measured the package beta at 0.328 (full) / 0.295 (2024+), so part of the published
+6.8pp/yr excess over the equal weight is factor exposure. The open follow-up was: if we
scale the book to an explicit beta target (0.10 / 0.20 / 0.30), does the excess survive
against a *same-beta* index mix -- i.e. would an investor who only wanted that much market
exposure have been better off buying 510300 in that proportion and holding cash?

Rules of the overlay (all causal, applied next bar):
  * decision every R=20 bars, on the close of the decision day;
  * beta = expanding OLS slope of package daily returns on 510300, using returns through
    the decision day only (min 126 bars before the first decision);
  * k = target / beta, clipped to [0, 1] -- only de-risking, never implicit leverage
    (beta-targets here are all below the book beta, so the clip is not binding);
  * unused capital earns a flat cash rate: 0% (base) and 2%/yr (financed scenario);
  * both the overlay and the benchmark pay |delta k| * 8bp per side when k moves, so the
    comparison is not won on free rebalancing.

Benchmark = the overlay's own market exposure bought directly in 510300 (k*beta of NAV)
plus cash -- i.e. "if you only wanted that much market exposure, buy the index".

Engine reused, never rewritten: `CR.phase_book_cost` -> `PK.fast_next_open_vt` (pinned to
`V.fast_next_open` at 1e-12 by its own selftest). --selftest pins the overlay arithmetic on
fixtures where the answer is known by construction (see selftest()).

Exploratory: no preregistration, no verdict, no ledger booking.
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
from scripts.etf_asset_class import classify  # noqa: E402

ANCHOR = "2020-01-01"
OOS = pd.Timestamp("2024-01-01")
REBAL = 20
N_HOLD = F.N_HOLD
COST_BP = 8.0
MKT = ("510300", "sh510300")
MIN_HIST = 126
TARGETS = (0.10, 0.20, 0.30)
CASH_RATES = (0.0, 0.02)
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "results", "etf_phase_beta_target.json")


# ---------------------------------------------------------------------------------------
# chipless core
# ---------------------------------------------------------------------------------------
def rets(ser):
    return ser.pct_change().dropna()


def expanding_beta(rp, rm):
    """Causal beta: at each date, slope of package on market using returns up to that date."""
    cov = rp.rolling(len(rp), min_periods=2).cov(rm)
    var = rm.rolling(len(rm), min_periods=2).var()
    return cov / var


def k_schedule(rp, rm, target, step=REBAL, min_hist=MIN_HIST):
    """[(decision_date, k)] -- k applied from the next bar to the next decision date."""
    betas = expanding_beta(rp, rm)
    out = []
    n = len(rp)
    i = min_hist
    prev_k = None
    while i < n:
        b = betas.iloc[i]
        if b is None or not np.isfinite(b) or b <= 1e-6:
            i += step
            continue
        k = float(min(1.0, max(0.0, target / b)))
        if prev_k is None:
            prev_k = k
        out.append((rp.index[i], k, float(b)))
        i += step
    return out


def apply_overlay(rp, rm, sched, cash_ann, cost_bp):
    """Daily NAV series of the overlay and of the beta-matched benchmark, both cost-charged.

    A decision taken on the close of day d applies from day d+1 (same convention as the
    book's next-open fill), so no decision can earn the return it was made on.
    """
    if not sched:
        return None, None, None
    cost = cost_bp / 10000.0
    rf_d = cash_ann / 252.0
    dates = rp.index
    marks = pd.Series(np.nan, index=dates, dtype=float)
    bmarks = pd.Series(np.nan, index=dates, dtype=float)
    for d, k, b in sched:
        marks.loc[d] = k
        bmarks.loc[d] = k * b            # benchmark weights the index at the overlay's beta
    applied = marks.shift(1).ffill()          # k in force for THIS day's return
    bapp = bmarks.shift(1).ffill()
    live = applied.dropna()
    if not len(live):
        return None, None, None
    idx = live.index
    strat, bench, kk = [1.0], [1.0], []
    prev = prev_b = None
    for d in idx:
        k = float(applied.loc[d])
        kb = float(bapp.loc[d])
        # cost when a weight moves (each leg trades its own notional fraction)
        fee = 0.0 if prev is None else abs(k - prev) * cost
        fee_b = 0.0 if prev_b is None else abs(kb - prev_b) * cost
        r_s = k * float(rp.loc[d]) + (1.0 - k) * rf_d - fee
        r_b = kb * float(rm.loc[d]) + (1.0 - kb) * rf_d - fee_b
        strat.append(strat[-1] * (1.0 + r_s))
        bench.append(bench[-1] * (1.0 + r_b))
        kk.append(k)
        prev, prev_b = k, kb
    return (pd.Series(strat[1:], index=idx), pd.Series(bench[1:], index=idx),
            pd.Series(kk, index=idx))


def realised_beta(ser, mkt):
    """Beta of the overlay daily returns on the market *level* series, common dates only."""
    idx = ser.index.intersection(mkt.index)
    a = ser.reindex(idx).pct_change().dropna()
    b = mkt.reindex(idx).pct_change().reindex(a.index)
    x, y = np.asarray(b, float), np.asarray(a, float)
    vx = float(np.var(x))
    return float(np.cov(y, x, bias=True)[0, 1] / vx) if vx > 0 and len(x) > 3 else None


def year_table(ser, bench):
    idx = ser.index.intersection(bench.index)
    a, b = ser.reindex(idx), bench.reindex(idx)
    rows = {}
    for y in sorted({d.year for d in idx}):
        m = [d.year == y for d in idx]
        pa = (float(a[m].iloc[-1] / a[m].iloc[0]) - 1.0) * 100 if sum(m) else 0.0
        pb = (float(b[m].iloc[-1] / b[m].iloc[0]) - 1.0) * 100 if sum(m) else 0.0
        rows[str(y)] = {"strat_pct": round(pa, 2), "bench_pct": round(pb, 2),
                        "excess_pp": round(pa - pb, 2)}
    return rows


def beta_exact_bench(rm, idx, beta, cash_ann):
    """Constant-weight index+cash book at the beta the overlay actually delivered.

    The scheduled benchmark above holds the *targeted* exposure; because the expanding
    beta estimate runs high relative to the beta that shows up in the segment, the overlay
    usually delivers less market exposure than it asked for. This second benchmark removes
    that mismatch (post-hoc calibration, rebalanced daily at zero cost) so the alpha read
    is not flattered by an accidentally defensive overlay.
    """
    rf_d = cash_ann / 252.0
    nav, out = 1.0, []
    for d in idx:
        nav *= 1.0 + beta * float(rm.loc[d]) + (1.0 - beta) * rf_d
        out.append(nav)
    return pd.Series(out, index=idx)


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
    # package: beta 0.5 on the market + constant 0.0002/day alpha, no lookahead issues
    rp = 0.5 * rm + 0.0002
    pkg = (1.0 + rp).cumprod()
    mkt = (1.0 + rm).cumprod()

    # leg 1: target above the book beta => k must be 1 everywhere and equal raw returns
    s1 = k_schedule(rets(pkg), rets(mkt), 0.99)
    chk("leg1 target>=beta gives k=1", all(abs(k - 1.0) < 1e-12 for _, k, _ in s1),
        "n=%d" % len(s1))
    so, sb, kk = apply_overlay(rets(pkg), rets(mkt), s1, 0.0, 8.0)
    sub = rets(pkg).reindex(so.index).iloc[1:].to_numpy()
    got = so.pct_change().dropna().to_numpy()
    d = float(np.max(np.abs(got - sub)))
    chk("leg1 unit-k overlay == raw returns", d < 1e-12, "maxdiff=%.2e" % d)

    # leg 2: known beta half => targeting 0.25 must land at realised beta ~0.25
    s2 = k_schedule(rets(pkg), rets(mkt), 0.25)
    so2, sb2, kk2 = apply_overlay(rets(pkg), rets(mkt), s2, 0.0, 8.0)
    rb = realised_beta(so2, mkt)
    chk("leg2 realised beta tracks target", rb is not None and abs(rb - 0.25) < 0.02,
        "beta=%.3f" % (rb if rb is not None else float("nan")))
    chk("leg2 benchmark beta matches overlay (target)",
        abs(realised_beta(sb2, mkt) - 0.25) < 0.02,
        "bench beta=%.3f" % realised_beta(sb2, mkt))

    # leg 3: target 0 with 2% cash => exactly the cash rate, no package exposure
    s3 = k_schedule(rets(pkg), rets(mkt), 0.0)
    so3, _, kk3 = apply_overlay(rets(pkg), rets(mkt), s3, 0.02, 8.0)
    chk("leg3 target 0 => all cash", float(kk3.max()) == 0.0)
    cash_expect = (1.0 + 0.02 / 252.0) ** len(so3)
    chk("leg3 cash leg earns the flat rate", abs(float(so3.iloc[-1]) - cash_expect) < 1e-9,
        "nav=%.8f want=%.8f" % (float(so3.iloc[-1]), cash_expect))

    # leg 4: causality -- rewriting a FUTURE return may not move any earlier k
    rp_alt = rp.copy()
    rp_alt.iloc[-5:] = rp_alt.iloc[-5:] * 3.0        # only returns AFTER the last decision move
    s4 = k_schedule(rp_alt.iloc[1:], rets(mkt), 0.25)
    s2b = k_schedule(rp.iloc[1:], rets(mkt), 0.25)
    pa = [(str(d.date()), round(k, 12)) for d, k, _ in s2b]
    pb = [(str(d.date()), round(k, 12)) for d, k, _ in s4]
    chk("leg4 no lookahead in the k schedule", pa == pb, "n=%d" % len(pa))

    # leg 5: hand fixture -- 60 days, k 1.0 -> 0.5 at day 30, one 4bp fee event
    f_idx = pd.bdate_range("2021-01-04", periods=60)
    frp = pd.Series([0.01] * 60, index=f_idx)
    frm = pd.Series([0.01] * 60, index=f_idx)
    fk = [(f_idx[0], 1.0, 0.5), (f_idx[30], 0.5, 1.0)]
    fso, fsb, _ = apply_overlay(frp, frm, fk, 0.0, 8.0)
    expect = (1.01 ** 30) * 1.0046 * (1.005 ** 28)   # 30 days at k=1, then 29 at k=0.5 with one fee day
    chk("leg5 hand fixture arithmetic", abs(float(fso.iloc[-1]) - expect) < 1e-9,
        "got=%.6f want=%.6f" % (float(fso.iloc[-1]), expect))

    # leg 6: package == market => overlay and benchmark are the same curve
    s6 = k_schedule(rets(mkt), rets(mkt), 0.30)
    so6, sb6, _ = apply_overlay(rets(mkt), rets(mkt), s6, 0.01, 8.0)
    d6 = float((so6 - sb6).abs().max())
    chk("leg6 pkg==mkt => overlay==benchmark", d6 < 1e-9, "maxdiff=%.2e" % d6)

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
    ew = F.run_ew(close[cols], amt[cols], REBAL, start=ANCHOR)
    base = F.metrics(ew, "ew")
    print("panel %s bars=%d cols=%d | ew full %.2f%%"
          % (close.index[0].date(), close.shape[0], len(cols), base["cagr"] * 100), flush=True)

    t0 = time.time()
    pkg, cells = CR.phase_book_cost(score, close[cols], openp[cols], N_HOLD, COST_BP)
    m_pkg = F.metrics(pkg, "package")
    print("package ready %.0fs | full %.2f%% oos %.2f%%"
          % (time.time() - t0, m_pkg["cagr"] * 100,
             F.metrics(pkg[pkg.index >= OOS], "pkg:oos")["cagr"] * 100), flush=True)

    idx = pkg.index.intersection(mkt.index)
    rp_all = rets(pkg.reindex(idx))
    rm_all = rets(mkt.reindex(idx))
    out = {
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
        "anchor": ANCHOR, "rebal": REBAL, "n_hold": N_HOLD, "cost_bp_per_side": COST_BP,
        "universe": "bond_removed (equity/commodity/crossborder), %d instruments" % len(cols),
        "market_proxy": mkt_col,
        "overlay": {"decision_every_bars": REBAL, "beta_basis": "expanding OLS of package "
                    "daily returns on 510300, returns through the decision day only",
                    "min_hist_bars": MIN_HIST, "k": "target/beta clipped to [0,1] (de-risk "
                    "only, no implicit leverage)", "cash_rate_scenarios": list(CASH_RATES),
                    "rebalance_cost_bp_per_side": COST_BP,
                    "benchmark": "510300 held at the overlay's own market weight (k*beta) "
                                 "+ cash, priced on the same cost schedule"},
        "question": "scaled to an explicit beta target, does the book still beat a same-beta "
                    "index+cash mix?",
        "headline": {"package_raw": m_pkg, "control_ew": base,
                     "excess_pp": round((m_pkg["cagr"] - base["cagr"]) * 100, 2)},
        "targets": {},
        "caveats": [
            "survivorship: on-disk panel holds ETFs that still exist",
            "cash earns a flat assumed rate (no 国债逆回购 panel in this repo); the 2% leg is "
            "a scenario, not an observed series",
            "k is revised every 20 bars, so the realised beta wanders inside a segment; the expanding "
            "beta estimate runs high against the beta that actually shows up, so the overlay "
            "delivers ~75% of the requested exposure (a second benchmark at the realised beta "
            "is reported for that reason)",
            "expanding-window beta is slow to react; a shorter window would drift more",
            "exploratory: no preregistration, no verdict, no ledger booking",
        ],
    }

    for tgt in TARGETS:
        sched = k_schedule(rp_all, rm_all, tgt)
        for cash in CASH_RATES:
            so, sb, kk = apply_overlay(rp_all, rm_all, sched, cash, COST_BP)
            if so is None:
                continue
            m_s = F.metrics(so, "overlay")
            m_b = F.metrics(sb, "bench")
            oos_s = F.metrics(so[so.index >= OOS], "overlay:oos")
            oos_b = F.metrics(sb[sb.index >= OOS], "bench:oos")
            rb_ov = realised_beta(so, mkt) or 0.0
            be = beta_exact_bench(rm_all, so.index, rb_ov, cash)
            m_be = F.metrics(be, "bench_beta_exact")
            oos_be = F.metrics(be[be.index >= OOS], "bench_beta_exact:oos")
            roll = CR.rolling_excess(so, sb)
            ex = [r["excess_pp"] for r in roll]
            key = "t%.2f_cash%.2f" % (tgt, cash)
            out["targets"][key] = {
                "target_beta": tgt, "cash_rate": cash,
                "window": {"start": str(so.index[0].date()), "end": str(so.index[-1].date()),
                           "days": len(so)},
                "k": {"mean": round(float(kk.mean()), 3), "min": round(float(kk.min()), 3),
                      "max": round(float(kk.max()), 3),
                      "revisions": int((kk.diff().fillna(0) != 0).sum())},
                "full": {"overlay": m_s, "benchmark": m_b,
                         "excess_pp": round((m_s["cagr"] - m_b["cagr"]) * 100, 2),
                         "benchmark_beta_exact": m_be,
                         "excess_vs_beta_exact_pp": round((m_s["cagr"] - m_be["cagr"]) * 100, 2)},
                "oos_2024plus": {"overlay": oos_s, "benchmark": oos_b,
                                 "excess_pp": round((oos_s["cagr"] - oos_b["cagr"]) * 100, 2),
                                 "benchmark_beta_exact": oos_be,
                                 "excess_vs_beta_exact_pp": round(
                                     (oos_s["cagr"] - oos_be["cagr"]) * 100, 2)},
                "realised_beta": {"overlay": round(rb_ov, 3),
                                  "benchmark": round(realised_beta(sb, mkt) or 0.0, 3)},
                "per_year": year_table(so, sb),
                "per_year_vs_beta_exact": year_table(so, be),
                "rolling_504": {"n": len(ex), "positive": sum(1 for v in ex if v > 0),
                                "median_pp": round(sorted(ex)[len(ex) // 2], 2) if ex else None,
                                "min_pp": min(ex) if ex else None,
                                "max_pp": max(ex) if ex else None},
            }
            print("[t=%.2f cash=%.0f%%] %s..%s | overlay %.2f%% (SR %.2f) bench %.2f%% "
                  "(SR %.2f) | excess %+.2fpp full, %+.2fpp oos | vs beta-exact %+.2f / %+.2f | "
                  "realised beta %.2f | rolling +%d/%d"
                  % (tgt, cash * 100, so.index[0].date(), so.index[-1].date(),
                     m_s["cagr"] * 100, m_s["sharpe"], m_b["cagr"] * 100, m_b["sharpe"],
                     out["targets"][key]["full"]["excess_pp"],
                     out["targets"][key]["oos_2024plus"]["excess_pp"],
                     out["targets"][key]["full"]["excess_vs_beta_exact_pp"],
                     out["targets"][key]["oos_2024plus"]["excess_vs_beta_exact_pp"],
                     out["targets"][key]["realised_beta"]["overlay"],
                     out["targets"][key]["rolling_504"]["positive"],
                     out["targets"][key]["rolling_504"]["n"]), flush=True)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", OUT_PATH, "(%.0fs total)" % (time.time() - t_all), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())