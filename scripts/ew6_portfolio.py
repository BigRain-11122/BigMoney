"""EW6 portfolio validation batch -> one-shot report (T-2026-09-23-06).

PRE-REGISTERED before running (research/shortline/EW6_PORTFOLIO.md, frozen
commit precedes this run; prereg sha256 embedded in the output JSON).
Do NOT tune thresholds or switch scheme after seeing results (iron rule 3).

REPORT-ONLY pass 1 (charter firm/portfolio.md): measurement of the 6-trader
equal-weight merged portfolio. ZERO registration, ZERO capital reallocation,
ZERO touches of trader level/paper fields.

Members are FIXED (no search): all non-underscore firm/traders/*.json
(= STRATEGY_LIBRARY s2 pointer), rebuilt verbatim via live.paper
SIGNAL_BUILDERS + ExitPatch/CostPatch (reused, never re-implemented).
Sleeves run TRUNCATED at each trader's evidence_cutoff (anchor-cum-sleeve
P3 pattern -- the sleeve IS the anchor run, no double engine runs).

New in EW6 vs P3 (per T-06 spec, all pre-registered):
  - regime slices mandatory (portfolio.md s3): IS/IS2 + calendar years +
    R-pei3 bear-state vs normal-day slices;
  - R-pei3 application layer REPORTING-ONLY pass 1: daily bear series
    derived from firm/risk/regime.py constants (single source, imported;
    final-day consistency gate vs major_bear_state -- mismatch => VOID),
    overlay cap(t)=state(t-1) (causal), cash leg earns 0 this pass;
  - execution via scripts/parallel_runner.py (audit.workers recorded);
  - trials ledger via science_gates.append_ledger (dict schema, F3);
  - D2 forward-lockbox disclosure: 2025+ segment labelled IS2 (demoted
    in-sample), true OOS = post-cutoff locked box (paper accrual).

Verdict template = P3 EW continuity clauses (report-only, no promotion or
allocation consequences; regime-premium applicability disclosed).
"""
import csv
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import annual_return, max_drawdown, sharpe
from firm.hr import TRADERS_DIR, load_trader
from firm.risk import regime as REGIME
from firm.risk.regime import (CAP_MAJOR_BEAR, CAP_NORMAL, DD_LINE, MA_WINDOW,
                              load_benchmark_close, major_bear_state)
from live.paper import (ANCHOR_TOL, SIGNAL_BUILDERS, CostPatch, ExitPatch,
                        OOS_START, _evidence_matches, build_panels,
                        evidence_cutoff, load_core, seg_metrics,
                        self_test_patches)
from parallel_runner import run_cells_parallel, worker_cap
from science_gates import append_ledger

PREREG = os.path.join(PATHS.root, "research", "shortline", "EW6_PORTFOLIO.md")
SCHEMES = ("EW",)                     # EW only this batch (prereg s2.2)
CRASH_YEAR = -0.30
CORR_BANDS = ((0.60, "low"), (0.80, "moderate"), (None, "high"))
MAX_WORKERS = 6                       # polite cap while P-1c chain runs

# ---- worker globals (initializer pattern; NO closures over jobs) ----
PRICES_FULL = None


def _init_worker():
    global PRICES_FULL
    PRICES_FULL = load_core()


def member_run(tid: str, cost_mult=None) -> dict:
    """Registered trader rerun truncated at evidence_cutoff -- IDENTICAL code
    path to live.paper anchor gate (the sleeve IS the anchor run)."""
    global PRICES_FULL
    t = load_trader(tid)
    cutoff = evidence_cutoff(t, PRICES_FULL)
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in PRICES_FULL.items()}
    P = build_panels(prices)
    idx = P["close"].index
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    from contextlib import nullcontext
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    with cctx, ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0))
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_tr = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    is_part = eq[eq.index < pd.Timestamp(OOS_START)]
    return {"tid": tid, "cost_mult": cost_mult or 1, "cutoff": cutoff,
            "dates": [str(d.date()) for d in eq.index],
            "eq": [round(float(v), 6) for v in eq],
            "full": res["metrics"],
            "is": seg_metrics(is_part), "is2": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"], "oos_trades": oos_tr}


def anchor_checks(t: dict, r1: dict, r2: dict) -> dict:
    got_is = {**r1["is"], "trades": r1["n_trades"] - r1["oos_trades"]}
    got_is2 = {**r1["is2"], "trades": r1["oos_trades"]}
    a_ok = (_evidence_matches(got_is, t["backtest"]["in_sample"])
            and _evidence_matches(got_is2, t["backtest"]["out_sample"]))
    x2 = t["backtest"]["cost_x2"]
    # CE-era registrations carry {sharpe, oos_sharpe}; folk-era (G2_FOLK)
    # registrations carry {sharpe, survive} only -- check the fields that
    # are REGISTERED (schema-compat, not a threshold change).
    x_ok = abs(r2["full"]["sharpe"] - x2["sharpe"]) < ANCHOR_TOL
    if "oos_sharpe" in x2:
        x_ok = x_ok and abs(r2["is2"]["sharpe"] - x2["oos_sharpe"]) < ANCHOR_TOL
    return {"anchor_ok": bool(a_ok), "x2_ok": bool(x_ok),
            "got_x2_full": r2["full"]["sharpe"],
            "got_x2_is2": r2["is2"]["sharpe"],
            "want_x2_full": x2["sharpe"],
            "want_x2_is2": x2.get("oos_sharpe")}


def yearly_returns(equity: pd.Series) -> dict:
    out = {}
    for year, seg in equity.groupby(equity.index.year):
        out[int(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1), 4)
    return out


def combine(eqs: dict, weights: dict) -> pd.Series:
    tids = list(weights)
    norm = pd.concat({tid: eqs[tid] / eqs[tid].iloc[0] for tid in tids},
                     axis=1, join="inner").dropna()
    return norm[tids].mul(pd.Series(weights)).sum(axis=1)


def corr_block(returns: pd.DataFrame, mask=None) -> dict:
    r = returns if mask is None else returns[mask]
    m = r.corr()
    tids = list(m.columns)
    pairs = [(tids[i], tids[j]) for i in range(len(tids))
             for j in range(i + 1, len(tids))]
    vals = [round(float(m.loc[a, b]), 4) for a, b in pairs]
    avg = round(sum(vals) / len(vals), 4) if vals else None
    band = next(label for cap, label in CORR_BANDS if avg < cap)
    return {"matrix": {a: {b: round(float(m.loc[a, b]), 4) for b in tids}
                       for a in tids},
            "pairs": {f"{a}|{b}": v for (a, b), v in zip(pairs, vals)},
            "avg_pairwise": avg, "band": band}


def g1_clauses(port: dict, n_trades: int, K: dict) -> dict:
    f_, s_ = port["full"], port["is2"]
    return {"i_beats_rand_p95": f_["sharpe"] > K["i_bar"],
            "ii_ann_pos": f_["annual_return"] > 0,
            "iii_dd_ok": f_["max_drawdown"] >= K["dd_min"],
            "iv_trades_ok": n_trades >= K["trades_min"],
            "v_is2_ok": s_["sharpe"] > 0 and s_["annual_return"] > 0,
            "vi_beats_passive": f_["sharpe"] > K["vi_bar"]}


def bear_series(close: pd.Series) -> pd.Series:
    """Daily major-bear bool from regime.py constants (single source).
    Warmup (<250 bars) -> False (normal), counted + disclosed by caller."""
    ma = close.rolling(MA_WINDOW).mean()
    high = close.rolling(MA_WINDOW).max()
    below = close < ma
    dd = close / high - 1.0
    return (below & (dd <= DD_LINE)).fillna(False).astype(bool)


def self_test_portfolio_math() -> bool:
    idx = pd.bdate_range("2024-01-01", "2024-03-31")   # IS range, not IS2
    a = pd.Series([1.0, 1.01, 1.02, 1.03], index=idx[:4])
    b = pd.Series([1.0, 1.05, 0.90, 1.10], index=idx[:4])
    port = combine({"A": a, "B": b}, {"A": 0.5, "B": 0.5})
    exp = 0.5 * (a / 1.0) + 0.5 * (b / 1.0)
    ok = bool((port - exp).abs().max() < 1e-12) and float(port.iloc[0]) == 1.0
    # regime constants sanity (single source import path)
    ok &= (MA_WINDOW == 250 and abs(DD_LINE + 0.20) < 1e-12
           and CAP_MAJOR_BEAR == 0.20 and CAP_NORMAL == 0.80)
    # bear_series vs major_bear_state on synthetic bear (selftest case A)
    bear = pd.Series([100.0] * 250 + [78.0] * 10,
                     index=pd.bdate_range("2024-01-01", periods=260))
    s = bear_series(bear)
    st = major_bear_state(bear)
    ok &= bool(s.iloc[-1]) and st["is_major_bear"]
    # normal case B: below MA250, dd ~ -10% -> not bear
    nb = pd.Series([100.0] * 250 + [89.5] * 10,
                    index=pd.bdate_range("2024-01-01", periods=260))
    ok &= (not bool(bear_series(nb).iloc[-1])) and (not major_bear_state(nb)["is_major_bear"])
    return bool(ok)


def main() -> int:
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    if not self_test_portfolio_math():
        print("portfolio-math/regime self-test FAILED -- abort")
        return 2
    print("patch + portfolio-math + regime-constant self-tests: PASS")

    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        calib = json.load(fh)
    g = calib["g1_prime_gate"]
    K = {"i_bar": g["i_full_sharpe_gt"], "vi_bar": g["vi_full_sharpe_gt"],
         "dd_min": g["iii_dd_min"], "trades_min": g["iv_trades_min"],
         "passive_ew48_buyhold": calib["families"]["C_passive"]["runs"]
                                          ["ew48_buyhold"],
         "passive_ew48_monthly": calib["families"]["C_passive"]["runs"]
                                          ["ew48_monthly_rebal"]}
    print(f"constants: i>{K['i_bar']} vi>{K['vi_bar']} dd>={K['dd_min']} "
          f"trades>={K['trades_min']}")

    tids = sorted(p.stem for p in TRADERS_DIR.glob("*.json")
                  if not p.name.startswith("_"))
    print(f"members ({len(tids)}): {tids}")

    # ---------- sleeves via parallel_runner (anchor-cum-member) ----------
    jobs = [(f"{tid}|{mult}", member_run, (tid, mult))
            for tid in tids for mult in (None, 2)]
    res = run_cells_parallel(jobs, workers=min(worker_cap(), MAX_WORKERS),
                             desc="ew6-sleeves", initializer=_init_worker)
    workers = int(res.pop("__workers__"))
    sleeves = {}
    for tid in tids:
        r1 = res[f"{tid}|None"]
        r2 = res[f"{tid}|2"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
        print(f"  {tid:<16} x1 full_s={r1['full']['sharpe']:>7.4f} "
              f"is2_s={r1['is2']['sharpe']:>7.4f} trades={r1['n_trades']:<5} "
              f"| x2 full_s={r2['full']['sharpe']:>7.4f}")

    traders = {tid: load_trader(tid) for tid in tids}
    anchors = {tid: anchor_checks(traders[tid], sleeves[tid]["x1"],
                                 sleeves[tid]["x2"]) for tid in tids}
    for tid, a in anchors.items():
        print(f"  anchor {tid:<12} ok={a['anchor_ok']} x2_ok={a['x2_ok']}")
    if not all(a["anchor_ok"] and a["x2_ok"] for a in anchors.values()):
        print("ANCHOR/X2 BROKEN -- batch void, no verdict")
        return write_outputs(K, tids, sleeves, anchors, None, None, None,
                             None, workers, t0, void=True, extra_runs=12)

    # ---------- correlations (member daily returns) ----------
    norm1 = pd.concat({tid: sleeves[tid]["x1"]["eq_s"] /
                       sleeves[tid]["x1"]["eq_s"].iloc[0] for tid in tids},
                      axis=1, join="inner").dropna()
    rets = norm1.pct_change().dropna()
    is2_mask = rets.index >= pd.Timestamp(OOS_START)
    corr = {"full": corr_block(rets), "is": corr_block(rets, ~is2_mask),
            "is2": corr_block(rets, is2_mask)}
    print(f"corr(full) avg={corr['full']['avg_pairwise']} "
          f"band={corr['full']['band']}")

    # ---------- EW portfolio (x1 + x2) ----------
    weights = {tid: round(1.0 / len(tids), 6) for tid in tids}
    ports = {}
    for mult, key in ((1, "x1"), (2, "x2")):
        eq = combine({tid: sleeves[tid][key]["eq_s"] for tid in tids}, weights)
        n_tr = sum(sleeves[tid][key]["n_trades"] for tid in tids)
        yr = yearly_returns(eq)
        ports[key] = {"scheme": "EW", "cost_mult": mult, "weights": weights,
                      "equity": eq, "full": seg_metrics(eq),
                      "is2": seg_metrics(eq, OOS_START), "n_trades": n_tr,
                      "yearly": yr, "worst_year": min(yr.values())}
    p, px = ports["x1"], ports["x2"]
    c = g1_clauses(p, p["n_trades"], K)
    member_s = {tid: sleeves[tid]["x1"]["full"]["sharpe"] for tid in tids}
    w_mean = sum(weights[tid] * member_s[tid] for tid in tids)
    p["clauses"] = c
    p["member_sharpes"] = member_s
    p["weighted_mean_member_sharpe"] = round(w_mean, 4)
    p["benefit"] = round(p["full"]["sharpe"] - w_mean, 4)
    p["dr"] = round(p["full"]["sharpe"] / w_mean, 4) if w_mean else None
    p["x2_survive"] = bool(px["full"]["sharpe"] > K["vi_bar"]
                           and px["is2"]["sharpe"] > 0)
    p["validated"] = bool(p["benefit"] > 0 and all(c.values())
                          and p["worst_year"] > CRASH_YEAR and p["x2_survive"])
    print(f"  port EW x1: full_s={p['full']['sharpe']:>7.4f} "
          f"is2_s={p['is2']['sharpe']:>7.4f} benefit={p['benefit']:>7.4f} "
          f"DR={p['dr']} worst_year={p['worst_year']} | "
          f"x2 full_s={px['full']['sharpe']:>7.4f} "
          f"survive={p['x2_survive']} -> validated={p['validated']}")

    # ---------- R-pei3 regime layer (report-only) ----------
    bench = load_benchmark_close()
    bear = bear_series(bench)
    st_last = major_bear_state(bench)
    # consistency gate: derived final-day state == regime.py single source
    n_warm = int((bench.rolling(MA_WINDOW).mean().isna()).sum())
    cons_ok = (bool(bear.iloc[-1]) == st_last["is_major_bear"]
               and bool(bench.iloc[-1] < bench.rolling(MA_WINDOW)
                        .mean().iloc[-1]) == st_last["below_ma250"])
    print(f"regime consistency gate: {'PASS' if cons_ok else 'FAIL'} "
          f"(last={st_last['as_of']} bear={st_last['is_major_bear']}, "
          f"warmup_days={n_warm})")
    if not cons_ok:
        print("REGIME SINGLE-SOURCE MISMATCH -- batch void")
        return write_outputs(K, tids, sleeves, anchors, corr, None, None,
                             None, workers, t0, void=True, extra_runs=12)

    port = p["equity"]
    r = port.pct_change()
    s_same = bear.reindex(port.index, method="ffill")   # same-day (slice)
    s_prev = s_same.shift(1)                            # causal (overlay)
    cap = s_prev.map(lambda b: CAP_MAJOR_BEAR if b else CAP_NORMAL)
    first_day_na = int(cap.isna().sum())
    cap = cap.fillna(CAP_NORMAL)
    r_star = (r * cap).fillna(0.0)
    overlay = (1.0 + r_star).cumprod()
    overlay = overlay / overlay.iloc[0]
    ovr_yr = yearly_returns(overlay)
    overlay_metrics = {
        "full": seg_metrics(overlay), "is2": seg_metrics(overlay, OOS_START),
        "yearly": ovr_yr, "worst_year": min(ovr_yr.values()),
        "bear_days_used": int(s_prev.fillna(False).sum()),
        "first_day_defaults": first_day_na,
    }

    def _slice(rr: pd.Series, mask: pd.Series) -> dict:
        x = rr[mask]
        if len(x) < 10 or x.std() == 0:
            return {"n_days": int(len(x)), "sharpe": None,
                    "ann_return": None}
        return {"n_days": int(len(x)),
                "sharpe": round(float(x.mean() / x.std() * 252 ** 0.5), 4),
                "ann_return": round(float((1 + x).prod() **
                                          (252 / len(x)) - 1), 4)}

    regime_slices = {
        "classification": "same-day bear state (descriptive; overlay uses "
                          "t-1 causal state per prereg s2.9)",
        "bear_days": _slice(r, s_same.fillna(False)),
        "normal_days": _slice(r, ~s_same.fillna(False)),
        "bear_ann_return_share": None,
    }
    bear_ret = float((1 + r[s_same.fillna(False)]).prod() - 1) \
        if s_same.fillna(False).any() else 0.0
    regime_slices["bear_ann_return_share"] = {
        "bear_cum_return": round(bear_ret, 4),
        "normal_cum_return": round(float((1 + r[~s_same.fillna(False)])
                                         .prod() - 1), 4)}
    print(f"regime slices: bear={regime_slices['bear_days']} "
          f"normal={regime_slices['normal_days']} "
          f"overlay full_s={overlay_metrics['full']['sharpe']} "
          f"worst_year={overlay_metrics['worst_year']}")

    return write_outputs(K, tids, sleeves, anchors, corr, ports,
                         {"overlay": overlay_metrics,
                          "slices": regime_slices,
                          "state_latest": st_last,
                          "warmup_days": n_warm},
                         workers, t0, void=False, extra_runs=12)


def write_outputs(K, tids, sleeves, anchors, corr, ports, regime, workers,
                  t0, void=False, extra_runs=0):
    n_runs = 0 if sleeves is None else 2 * len(tids)
    n_evals = 0 if ports is None else 2 * len(SCHEMES)
    ledger = append_ledger(
        "EW6-portfolio-validation", n_runs + n_evals + extra_runs,
        file_name="results/portfolio_ew6.json",
        note=f"{n_runs} engine member runs (anchor-cum-sleeve, x1+x2) + "
             f"{n_evals} portfolio evaluations (derived, non-engine) + "
             f"{extra_runs} voided runs from first attempt (crashed on "
             f"folk-registration cost_x2 schema KeyError AFTER sleeves "
             f"completed, zero partial output; deterministic rerun, "
             f"G2_FOLK double-count precedent); report-only pass 1, zero "
             f"search => zero nulls (composition disclosed per prereg s2.3; "
             f"n deviates from frozen budget 14 by the voided attempt)")
    prereg_sha = hashlib.sha256(open(PREREG, "rb").read()).hexdigest()

    rows = []
    for tid in tids:
        for mult, key in ((1, "x1"), (2, "x2")):
            rr = sleeves[tid][key]
            yr = yearly_returns(rr["eq_s"])
            rows.append({"kind": "member", "id": tid, "cost_mult": mult,
                         "full_sharpe": rr["full"]["sharpe"],
                         "full_ann": rr["full"]["annual_return"],
                         "full_dd": rr["full"]["max_drawdown"],
                         "n_trades": rr["n_trades"],
                         "is2_sharpe": rr["is2"]["sharpe"],
                         "is2_ann": rr["is2"]["annual_return"],
                         "worst_year": min(yr.values()) if yr else "",
                         "anchor_ok": anchors[tid]["anchor_ok"]
                         if mult == 1 else anchors[tid]["x2_ok"]})
    if ports:
        for mult, key in ((1, "x1"), (2, "x2")):
            q = ports[key]
            src = ports["x1"]
            rows.append({"kind": "portfolio", "id": "EW6", "cost_mult": mult,
                         "full_sharpe": q["full"]["sharpe"],
                         "full_ann": q["full"]["annual_return"],
                         "full_dd": q["full"]["max_drawdown"],
                         "n_trades": q["n_trades"],
                         "is2_sharpe": q["is2"]["sharpe"],
                         "is2_ann": q["is2"]["annual_return"],
                         "worst_year": q["worst_year"],
                         "anchor_ok": ""})
    csv_path = os.path.join(PATHS.root, "research", "shortline",
                            "ew6_results.csv")
    cols = ["kind", "id", "cost_mult", "full_sharpe", "full_ann", "full_dd",
            "n_trades", "is2_sharpe", "is2_ann", "worst_year", "anchor_ok"]
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    print(f"saved: {csv_path} ({len(rows)} rows)")

    p = ports["x1"] if ports else None
    px = ports["x2"] if ports else None
    out = {
        "batch": "EW6-portfolio-validation",
        "task": "T-2026-09-23-06 (report-only pass 1)",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/shortline/EW6_PORTFOLIO.md",
        "prereg_sha256_at_run": prereg_sha,
        "universe": {"pool": "core48-bare-codes",
                     "members": tids,
                     "member_cutoffs": {tid: sleeves[tid]["x1"]["cutoff"]
                                        for tid in tids} if sleeves else None},
        "oos_start": OOS_START,
        "d2_note": "2025+ segment = IS2 (forward-lockbox demotion); true OOS "
                   "= post-cutoff locked box via paper accrual, not consumed",
        "void": void,
        "constants": {"g1_prime_i_bar": K["i_bar"],
                      "g1_prime_vi_bar": K["vi_bar"],
                      "crash_year": CRASH_YEAR,
                      "passive_ew48_buyhold": K["passive_ew48_buyhold"],
                      "passive_ew48_monthly": K["passive_ew48_monthly"],
                      "cost_basis": "legacy fee path (additive engine flags "
                                    "all OFF; cost_v2 not used this batch)"},
        "members": {tid: {"cutoff": sleeves[tid]["x1"]["cutoff"],
                          "x1": {k: sleeves[tid]["x1"][k] for k in
                                 ("full", "is", "is2", "n_trades",
                                  "oos_trades")},
                          "x2": {k: sleeves[tid]["x2"][k] for k in
                                 ("full", "is2", "n_trades")},
                          "yearly_returns":
                              yearly_returns(sleeves[tid]["x1"]["eq_s"])}
                    for tid in tids} if sleeves else None,
        "anchors": anchors,
        "correlation": corr,
        "portfolios": {key: {k: v for k, v in q.items() if k != "equity"}
                       for key, q in ports.items()} if ports else None,
        "regime": regime,
        "verdict": {
            "template": "EW6 report-only pass 1 (pre-registered EW carrier)",
            "void": void,
            "corr_band_full": None if not corr else corr["full"]["band"],
            "ew_validated": None if not p else p["validated"],
            "ew_clauses": None if not p else p["clauses"],
            "ew_benefit": None if not p else p["benefit"],
            "ew_dr": None if not p else p["dr"],
            "ew_x2_survive": None if not p else p["x2_survive"],
            "ew_worst_year": None if not p else p["worst_year"],
            "applicability": "descriptive continuity metrics only -- no "
                             "promotion, no allocation; regime premium "
                             "(P-5B 6/6 fail 0.70 beat line) discounts all "
                             "Sharpe reads; allocation = charter s5 T1 route",
        },
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "n_portfolio_evals": n_evals,
                  "workers": workers,
                  "parallel": f"parallel_runner ProcessPool workers={workers}"},
    }
    json_path = os.path.join(PATHS.results_dir, "portfolio_ew6.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    if void:
        summary = "VOID (anchor or regime-consistency broken)"
    else:
        summary = (f"EW6 validated={p.get('validated')} "
                   f"benefit={p.get('benefit')} "
                   f"x2_survive={p.get('x2_survive')}")
    print(f"\n===== EW6 verdict: {summary} =====")
    print(f"runs={n_runs} evals={n_evals} elapsed={time.time()-t0:.0f}s "
          f"ledger N={ledger['total']} (prev={ledger['prev_total']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
