"""P4_PAIRS: zoo #41 -- ETF cointegration pairs, long-only spread reversion.

PRE-REGISTERED before running (research/P4_PAIRS.md, commit 79750f5).
Do NOT tune thresholds or re-run after seeing results (iron rule 3).

Lane chain: O-1819 queue-never-empty -> zoo #41 (A-layer queued) ->
claim MSG-20260924-0520 (F-04, commit d1f801a).

Frozen method (prereg s3): IS-only Engle-Granger scan over all C(48,2)
unordered pairs (log-close OLS, ADF(1) t-stat on residuals, lexicographic
A<B orientation); rank by t ascending; greedy symbol-non-overlap top K=8;
spread = logA - (alpha+beta*logB) full-history (beta IS-frozen); z on
rolling 60d (causal); entry z<=-2.0 on the CHEAP leg (long-only), exit
z>=0.0; engine default exit machine additionally applies.

Nulls: n=50 random-pair draws, SAME structure (greedy non-overlap 8 pairs
from the eligible pool, same beta estimation, same z rules, same pooled
max_positions=8) -- captures the cointegration-SELECTION effect. Seeds
48_000+k (SEED_REGISTRY "p4_pairs").

Gates: NEW BATCH = v2 -> science_gates.g1_prime_v2 (skill_line_v2 live
chain head + stationary bootstrap CI + F6 entries>=30). Recorded lines
0.3521 / 0.4004 = legacy descriptive columns only. NO registration this
batch; G2 deepening requires separate prereg even if v2 passes.

Hard gates (batch VOID if broken): patch self-test + 6 trader anchor
reproduction (member_run 1x + live.paper._evidence_matches, folk-screen
precedent; member_run IS the anchor run, no double engine runs).

Trials = 67 (prereg s0): pooled 1x + pooled x2 + 8 singles + 50 nulls +
6 anchors + 1 passive. Ledger: science_gates.append_ledger (dict schema,
prev = live chain head, evidence_cutoff 2026-09-22).

Panels truncated to EVIDENCE_CUT=2026-09-22 (ACTIVE truncation disclosed
in prereg s2; raw end is 09-23).
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # p2/p3 imports

import numpy as np
import pandas as pd

from config import PATHS
from engine import run_backtest
from knowledge.rules import FeeSchedule
from live.paper import (OOS_START, CostPatch, _evidence_matches,
                        build_panels, load_core, seg_metrics,
                        self_test_patches)
from firm.hr import TRADERS_DIR, load_trader
from p2_null_calibration import passive_buyhold
from p3_portfolio import member_run
from science_gates import (append_ledger, cutoff_meta, g1_prime_v2,
                           ledger_head, recorded_lines)

EVIDENCE_CUT = "2026-09-22"
MIN_OVERLAP = 500                  # IS common days (prereg s2)
K_PAIRS = 8
Z_ENTRY, Z_EXIT, Z_WIN = -2.0, 0.0, 60
N_NULLS = 50
SEED_BASE = 48_000                 # SEED_REGISTRY "p4_pairs"
TRIALS = 67                        # frozen in prereg s0
EG_CRIT_5PCT = -3.37               # descriptive marker only (prereg s3)
VI_BAR_RECORDED = 0.4004           # legacy descriptive column
I_LINE_RECORDED = 0.3521
SLEEVE_MAX_CORR = 0.30
LEDGER_KEY = "p4-pairs"
RESULTS_JSON = os.path.join(PATHS.root, "results", "shortline_p4_pairs.json")
CSV_PATH = os.path.join(PATHS.root, "research", "shortline",
                        "p4_pairs_results.csv")


# ---------------- core math (pure, selftested offline) ----------------

def adf_t1(e: np.ndarray) -> float:
    """ADF(1) t-stat: d e_t = g e_{t-1} + f d e_{t-1} + c. Frozen in prereg s3."""
    e = np.asarray(e, dtype=float)
    de = np.diff(e)
    y = de[1:]
    X = np.column_stack([e[1:-1], de[:-1], np.ones(len(y))])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    dof = len(y) - X.shape[1]
    s2 = float(resid @ resid) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(coef[0] / np.sqrt(cov[0, 0]))


def fit_is(loga: np.ndarray, logb: np.ndarray) -> dict:
    """IS OLS logA ~ c + beta*logB + ADF(1) t on residuals (prereg s3)."""
    X = np.column_stack([logb, np.ones(len(logb))])
    coef, *_ = np.linalg.lstsq(X, loga, rcond=None)
    beta, alpha = float(coef[0]), float(coef[1])
    e = loga - (alpha + beta * logb)
    return {"alpha": alpha, "beta": beta, "adf_t": adf_t1(e)}


def z_series(s: pd.Series) -> pd.Series:
    """Causal rolling-60 z of the spread (prereg s3; NaN -> no signal)."""
    m = s.rolling(Z_WIN, min_periods=Z_WIN).mean()
    sd = s.rolling(Z_WIN, min_periods=Z_WIN).std(ddof=1)
    return (s - m) / sd


def greedy_nonoverlap(ranked: list, k: int) -> list:
    """Walk ranked list (already ordered), take pairs whose symbols are
    unused. Deterministic; frozen in prereg s3."""
    used, out = set(), []
    for p in ranked:
        if len(out) >= k:
            break
        if p["a"] in used or p["b"] in used:
            continue
        used.add(p["a"])
        used.add(p["b"])
        out.append(p)
    return out


def null_draw(perm: np.ndarray, eligible: list, k: int) -> list:
    """One random draw: permuted eligible order -> greedy non-overlap k."""
    ranked = [eligible[int(i)] for i in perm]
    return greedy_nonoverlap(ranked, k)


def pair_frames(logc: pd.DataFrame, pair: dict, idx: pd.Index,
                syms: list) -> tuple:
    """Entry/exit boolean frames (single pair leg) on the full history."""
    entry = pd.DataFrame(False, index=idx, columns=syms)
    exit_ = pd.DataFrame(False, index=idx, columns=syms)
    a, b = pair["a"], pair["b"]
    la, lb = logc[a], logc[b]
    s = la - (pair["alpha"] + pair["beta"] * lb)
    common = s.notna()
    s = s[common]
    z = z_series(s)
    za = z.reindex(idx)
    za = za.where(common.reindex(idx, fill_value=False))
    ent = (za <= Z_ENTRY).fillna(False)
    exi = (za >= Z_EXIT).fillna(False)
    entry.loc[ent[ent].index, a] = True
    exit_.loc[exi[exi].index, a] = True
    return entry, exit_


def merged_frames(logc: pd.DataFrame, pairs: list, idx: pd.Index,
                  syms: list) -> tuple:
    """OR-merge pair legs (symbols disjoint by construction)."""
    entry = pd.DataFrame(False, index=idx, columns=syms)
    exit_ = pd.DataFrame(False, index=idx, columns=syms)
    for p in pairs:
        e1, x1 = pair_frames(logc, p, idx, syms)
        entry = entry | e1
        exit_ = exit_ | x1
    return entry, exit_


def run_engine(prices: dict, idx: pd.Index, entry: pd.DataFrame,
               exit_: pd.DataFrame, params: dict, name: str,
               cost_mult=None) -> dict:
    from contextlib import nullcontext
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    with cctx:
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=exit_)
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_trades = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    m = res["metrics"]
    return {"name": name, "eq": eq, "full": m,
            "oos": seg_metrics(eq, OOS_START),
            "n_trades": m["num_trades"],
            "n_entries": m.get("num_entries"),
            "oos_trades": oos_trades}


# ---------------- offline selftest (prereg hard-gate pattern) ----------

def _syn_cointegrated(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    logb = np.cumsum(rng.normal(0, 0.01, n)) + 5.0
    noise = np.zeros(n)
    for t in range(1, n):
        noise[t] = 0.3 * noise[t - 1] + rng.normal(0, 0.004)
    loga = 0.5 + 2.0 * logb + noise
    return loga, logb


def selftest() -> int:
    ok = []

    # T1 ADF sanity: unit-root residual (spurious-pair case) NOT below
    # EG crit; stationary (white-noise) residual strongly below.
    rng = np.random.default_rng(11)
    t_rw = adf_t1(np.cumsum(rng.normal(0, 0.01, 1500)))
    rng = np.random.default_rng(12)
    t_white = adf_t1(rng.normal(0, 0.01, 1500))
    ok.append(("T1a random-walk residual above EG crit",
               EG_CRIT_5PCT < t_rw < 0.5))
    ok.append(("T1b stationary residual deep below", t_white < -10.0))

    # T2 cointegrated synthetic -> t below EG 5% marker
    loga, logb = _syn_cointegrated()
    fit = fit_is(loga, logb)
    ok.append(("T2 synthetic cointegrated adf < -3.37",
               fit["adf_t"] < EG_CRIT_5PCT))
    ok.append(("T3 beta recovered", abs(fit["beta"] - 2.0) < 0.01))
    ok.append(("T3 alpha recovered", abs(fit["alpha"] - 0.5) < 0.01))

    # T4 z causality + known entry point (flat base + one injected dip)
    idx = pd.bdate_range("2020-01-01", periods=400)
    s = pd.Series(0.0, index=idx)
    s.iloc[200] = -0.20                     # deep dip vs zero sigma base
    z = z_series(s)
    ok.append(("T4a warmup NaN", bool(z.iloc[:Z_WIN - 1].isna().all())))
    ent = (z <= Z_ENTRY).fillna(False)
    ok.append(("T4c entry only at injected dip", list(ent[ent].index) == [idx[200]]))
    # degenerate flat window: std=0 -> z=0/0=NaN -> NO signal (honest, safe)
    ok.append(("T4b degenerate std0 window -> NaN no-signal",
               bool(z.loc[idx[300]] != z.loc[idx[300]])
               and np.isfinite(z.loc[idx[200]])))

    # T5 greedy non-overlap determinism
    ranked = [{"a": "x", "b": "y"}, {"a": "y", "b": "z"},
              {"a": "p", "b": "q"}, {"a": "x", "b": "z"}]
    sel = greedy_nonoverlap(ranked, 2)
    ok.append(("T5 non-overlap", [(p["a"], p["b"]) for p in sel] ==
               [("x", "y"), ("p", "q")]))

    # T6 null draw determinism
    eligible = [{"a": f"a{i}", "b": f"b{i}"} for i in range(20)]
    r1 = np.random.default_rng(SEED_BASE).permutation(len(eligible))
    r2 = np.random.default_rng(SEED_BASE).permutation(len(eligible))
    r3 = np.random.default_rng(SEED_BASE + 1).permutation(len(eligible))
    ok.append(("T6a same-seed deterministic", bool((r1 == r2).all())))
    ok.append(("T6b diff-seed differs", not bool((r1 == r3).all())))
    d1 = null_draw(r1, eligible, 4)
    ok.append(("T6c null disjoint legs",
               len({s_ for p in d1 for s_ in (p["a"], p["b"])}) == 8))

    # T7 OR-merge disjointness (constructive: flat legs + final deep dip
    # on the traded side -> guaranteed z <= entry at the last row)
    syms = ["x", "y", "p", "q"]
    idx7 = idx[:60]
    logc = pd.DataFrame(1.0, index=idx7, columns=syms)
    logc.iloc[-1, logc.columns.get_loc("x")] = 0.5
    logc.iloc[-1, logc.columns.get_loc("p")] = 0.5
    pr = [{"a": "x", "b": "y", "alpha": 0.0, "beta": 1.0},
          {"a": "p", "b": "q", "alpha": 0.0, "beta": 1.0}]
    e7, x7 = merged_frames(logc, pr, idx7, syms)
    ok.append(("T7a merge only traded legs",
               list(e7.columns[e7.any()]) == ["x", "p"]))
    ok.append(("T7b entry exactly at dip row",
               int(e7.any(axis=1).sum()) == 1 and int(e7.iloc[-1].sum()) == 2))
    ok.append(("T7c exit empty (flat spread)",
               not bool(x7.any().any())))

    # T8 evidence comparison helper (anchor path)
    got = {"sharpe": 1.0, "max_drawdown": -0.2, "annual_return": 0.05,
           "trades": 10}
    want = {"sharpe": 1.0, "max_dd": -0.2, "annual": 0.05, "trades": 10}
    ok.append(("T8a match", _evidence_matches(got, want)))
    want2 = dict(want, trades=11)
    ok.append(("T8b trade mismatch caught", not _evidence_matches(got, want2)))

    bad = [n for n, v in ok if not v]
    for n, v in ok:
        print(f"  [{'PASS' if v else 'FAIL'}] {n}")
    print(f"selftest: {len(ok) - len(bad)}/{len(ok)} PASS"
          + (f"  BAD: {bad}" if bad else ""))
    return 1 if bad else 0


# ---------------- batch ----------------

def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "selftest" in argv:
        return selftest()

    t0 = time.time()
    if not self_test_patches():
        print("VOID: engine patch self-test failed")
        return 2

    prices_full = load_core()
    ps = pd.Timestamp(EVIDENCE_CUT)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    close = P["close"]
    idx = close.index
    syms = list(close.columns)
    logc = np.log(close)
    is_mask = idx < pd.Timestamp(OOS_START)
    n_is = int(is_mask.sum())
    print(f"panel: {len(syms)} syms x {len(idx)} bars "
          f"(IS {n_is} to {OOS_START}); cut {EVIDENCE_CUT}")

    # ---------- scan (IS-only, prereg s3) ----------
    t1 = time.time()
    eligible, dropped = [], 0
    for i in range(len(syms)):
        for j in range(i + 1, len(syms)):
            a, b = syms[i], syms[j]
            m = (logc[a].notna() & logc[b].notna()) & is_mask
            if int(m.sum()) < MIN_OVERLAP:
                dropped += 1
                continue
            la = logc[a][m].to_numpy()
            lb = logc[b][m].to_numpy()
            f = fit_is(la, lb)
            eligible.append({"a": a, "b": b, **f,
                             "is_days": int(m.sum())})
    eligible.sort(key=lambda p: (p["adf_t"], p["a"], p["b"]))
    print(f"scan: {len(eligible)} eligible pairs ({dropped} dropped "
          f"< {MIN_OVERLAP} IS days) in {time.time() - t1:.1f}s")
    if not eligible:
        print("DATA GATE FAIL: no eligible pair (prereg s2) -- honest close")
        return 2
    n_eg = sum(1 for p in eligible if p["adf_t"] < EG_CRIT_5PCT)
    print(f"pairs below EG 5% marker ({EG_CRIT_5PCT}): {n_eg}")
    for p in eligible[:12]:
        print(f"   {p['a']}/{p['b']}  t={p['adf_t']:.2f}  beta={p['beta']:.3f}"
              f"  is_days={p['is_days']}")

    selected = greedy_nonoverlap(eligible, K_PAIRS)
    print(f"selected {len(selected)} non-overlapping pairs:")
    for p in selected:
        print(f"   {p['a']}/{p['b']}  t={p['adf_t']:.2f}  beta={p['beta']:.3f}")

    n_runs = 0

    # ---------- pooled candidate (1x + x2) ----------
    entry, exit_ = merged_frames(logc, selected, idx, syms)
    pooled = run_engine(prices, idx, entry, exit_,
                        {"max_positions": K_PAIRS, "report_num_entries": True},
                        "pairs_pooled", None)
    n_runs += 1
    pooled_x2 = run_engine(prices, idx, entry, exit_,
                           {"max_positions": K_PAIRS,
                            "report_num_entries": True},
                           "pairs_pooled_x2", cost_mult=2.0)
    n_runs += 1
    print(f"pooled:  full_s={pooled['full']['sharpe']:.3f} "
          f"oos_s={pooled['oos'].get('sharpe')} "
          f"trades={pooled['n_trades']} entries={pooled['n_entries']}")

    # ---------- per-pair singles ----------
    singles = []
    for p in selected:
        e1, x1 = pair_frames(logc, p, idx, syms)
        r = run_engine(prices, idx, e1, x1,
                       {"max_positions": 1, "report_num_entries": True},
                       f"single_{p['a']}_{p['b']}")
        r["pair"] = f"{p['a']}/{p['b']}"
        singles.append(r)
        n_runs += 1
        print(f"  single {r['pair']:<16} s={r['full']['sharpe']:>7.3f} "
              f"oos={r['oos'].get('sharpe')} trades={r['n_trades']}")

    # ---------- nulls: random pairs, same structure ----------
    nulls = []
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED_BASE + k)
        perm = rng.permutation(len(eligible))
        drawn = null_draw(perm, eligible, K_PAIRS)
        e_n, x_n = merged_frames(logc, drawn, idx, syms)
        r = run_engine(prices, idx, e_n, x_n, {"max_positions": K_PAIRS},
                       f"null_{k}")
        nulls.append(r)
        n_runs += 1
    null_sharpes = np.array([r["full"]["sharpe"] for r in nulls], float)
    p95 = float(np.quantile(null_sharpes, 0.95))
    print(f"nulls: n={N_NULLS} p50={np.median(null_sharpes):.3f} "
          f"p95={p95:.3f} max={null_sharpes.max():.3f}")

    # ---------- anchors (member_run = the anchor run) ----------
    tids = [p.stem for p in sorted(TRADERS_DIR.glob("*.json"))
            if not p.name.startswith("_")]
    anchors, trader_eq = {}, {}
    for tid in tids:
        t = load_trader(tid)
        r1 = member_run(t, prices, None)
        got_is = {**seg_metrics(r1["eq"][r1["eq"].index < pd.Timestamp(OOS_START)]),
                  "trades": r1["n_trades"] - r1["oos_trades"]}
        got_oos = {**r1["oos"], "trades": r1["oos_trades"]}
        ok = (_evidence_matches(got_is, t["backtest"]["in_sample"])
              and _evidence_matches(got_oos, t["backtest"]["out_sample"]))
        anchors[tid] = {"ok": bool(ok)}
        trader_eq[tid] = r1["eq"]
        n_runs += 1
        print(f"anchor {tid:<20} {'OK' if ok else 'FAIL'}")
    if not all(v["ok"] for v in anchors.values()):
        print("VOID: anchor reproduction failed (prereg s3 hard gate)")
        return 2

    # ---------- passive info column ----------
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee
                 + fee.supervision_fee + fee.slippage_a)
    eq_passive = passive_buyhold(close, cost_rate)
    passive_rows = {"ew48_buyhold": {"full": seg_metrics(eq_passive),
                                     "oos": seg_metrics(eq_passive, OOS_START)}}

    # ---------- gates ----------
    rets = pooled["eq"].pct_change().dropna()
    g1v2 = g1_prime_v2(pooled["full"]["sharpe"], rets, batch_cells=TRIALS,
                       pool="core48", n_trades=pooled["n_trades"],
                       n_entries=pooled["n_entries"])
    rec = recorded_lines()
    trader_rets = {tid: trader_eq[tid].pct_change().dropna() for tid in tids}
    corr_vs = {tid: round(float(rets.corr(trader_rets[tid])), 4)
               for tid in tids}
    max_corr = max(abs(v) for v in corr_vs.values())
    oos = pooled["oos"]
    clauses = {
        "annual_pos": pooled["full"]["annual_return"] > 0,
        "oos_dual_pos": bool(oos.get("sharpe", 0) > 0
                             and oos.get("annual_return", 0) > 0),
        "dd_ok": pooled["full"]["max_drawdown"] >= -0.35,
        "trades_ge_30": pooled["n_trades"] >= 30,
        "beats_inbatch_null_p95": bool(pooled["full"]["sharpe"] > p95),
        "beats_vi_recorded": bool(pooled["full"]["sharpe"] > VI_BAR_RECORDED),
        "x2_survives_vi": bool(pooled_x2["full"]["sharpe"] > VI_BAR_RECORDED),
        "d6_max_corr_lt_0.7": bool(max_corr < 0.70),
    }
    v2_pass = bool(g1v2["pass_v2"])
    verdict = {
        "v2_gate": g1v2,
        "g1_prime_descriptive_clauses": clauses,
        "descriptive_g1_pass": all(clauses.values()),
        "v2_pass": v2_pass,
        "n_selected_pairs": len(selected),
        "registration": "NONE this batch (prereg s4: G2 deepening requires "
                        "separate pre-registration even if v2 passes)",
        "fail_branch": None if v2_pass else (
            "zoo #41 honest verdict: long-only cointegration pairs do not "
            "clear the v2 registration-grade line on core48 at daily "
            "granularity + 13bp; NO threshold tuning, NO re-run (iron rule 3)"),
    }

    # ---------- ledger + outputs ----------
    head = ledger_head()
    ledger = append_ledger(LEDGER_KEY, TRIALS, "shortline_p4_pairs.json",
                           evidence_cutoff=EVIDENCE_CUT)

    out = {
        "batch": LEDGER_KEY,
        "prereg": "research/P4_PAIRS.md (79750f5)",
        "claim": "MSG-20260924-0520-bm-a-p4-pairs-claim (d1f801a)",
        "evidence_cutoff": cutoff_meta(EVIDENCE_CUT),
        "selected_pairs": [{k: (round(v, 6) if isinstance(v, float) else v)
                            for k, v in p.items()} for p in selected],
        "eligible_pairs": len(eligible),
        "pairs_below_eg_marker": n_eg,
        "pooled": {k: pooled[k] for k in ("full", "oos", "n_trades",
                                          "n_entries", "oos_trades")},
        "pooled_x2": {"full": pooled_x2["full"], "oos": pooled_x2["oos"]},
        "singles": [{"pair": r["pair"], "full": r["full"], "oos": r["oos"],
                     "n_trades": r["n_trades"]} for r in singles],
        "nulls": {"n": N_NULLS, "p50": round(float(np.median(null_sharpes)), 4),
                  "p95": round(p95, 4), "max": round(float(null_sharpes.max()), 4),
                  "seed_base": SEED_BASE},
        "passive": passive_rows,
        "anchors": anchors,
        "gate_lines": {"vi_bar_recorded": rec["vi_bar"],
                       "i_line_recorded": rec["i_line"],
                       "inbatch_null_p95": round(p95, 4)},
        "corr_vs_traders": corr_vs,
        "max_corr": round(float(max_corr), 4),
        "verdict": verdict,
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs,
                  "trials_counted": TRIALS,
                  "workers": 1,
                  "cpu_parallel": "serial (single-process)"},
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=str)

    cols = ["name", "kind", "pair", "adf_t", "beta", "sharpe_full",
            "sharpe_oos", "annual_return", "max_drawdown", "n_trades",
            "n_entries", "note"]
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        rows = ([["pairs_pooled", "candidate", "K" + str(len(selected)), "", "",
                  pooled["full"]["sharpe"], pooled["oos"].get("sharpe"),
                  pooled["full"]["annual_return"], pooled["full"]["max_drawdown"],
                  pooled["n_trades"], pooled["n_entries"],
                  "v2_pass=" + str(v2_pass)],
                 ["pairs_pooled_x2", "cost_x2", "K" + str(len(selected)), "", "",
                  pooled_x2["full"]["sharpe"], pooled_x2["oos"].get("sharpe"),
                  pooled_x2["full"]["annual_return"],
                  pooled_x2["full"]["max_drawdown"], pooled_x2["n_trades"], "",
                  "survives_vi=" + str(clauses["x2_survives_vi"])]]
                + [["single_" + r["pair"].replace("/", "_"), "single",
                    r["pair"], "", "", r["full"]["sharpe"],
                    r["oos"].get("sharpe"), r["full"]["annual_return"],
                    r["full"]["max_drawdown"], r["n_trades"], "", ""]
                   for r in singles]
                + [["null_" + str(k), "null", "K" + str(K_PAIRS), "", "",
                    r["full"]["sharpe"], r["oos"].get("sharpe"),
                    r["full"]["annual_return"], r["full"]["max_drawdown"],
                    r["n_trades"], "", ""] for k, r in enumerate(nulls)]
                + [["ew48_buyhold", "passive", "", "", "",
                    passive_rows["ew48_buyhold"]["full"]["sharpe"],
                    passive_rows["ew48_buyhold"]["oos"].get("sharpe"), "", "",
                    "", "", ""]])
        w.writerows(rows)

    print(f"\n===== v2 gate: pass={v2_pass} "
          f"(line={g1v2['skill_line']['line']}, "
          f"ci_lb_pos={g1v2['ci_lower_bound_positive']})")
    print(f"===== descriptive clauses: {clauses}")
    print(f"===== sleeve corr max={max_corr:.3f} (D6 gate <0.70)")
    print(f"===== ledger: prev={head['total']} + {TRIALS} "
          f"-> {ledger['total']} ({ledger['file']})")
    print(f"done in {time.time() - t0:.1f}s, {n_runs} engine runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
