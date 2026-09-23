"""IV6 portfolio risk-budget batch -> one-shot report (report-only pass 2).

PRE-REGISTERED before running (research/IV6_PORTFOLIO.md, frozen commit
precedes any run; prereg sha256 embedded in the output JSON). Do NOT tune
weights/windows/thresholds after seeing results (iron rule 3).

Report-only pass 2 (charter firm/portfolio.md s1.1 "EW baseline -> IV risk
budget upgrade path"; EW6 continuation pointer s6.7-1). ZERO registration,
ZERO capital reallocation, ZERO carrier switch (EW stays the validated
baseline; IV adoption = charter s5 T1 route, not decided here).

Members are FIXED (no search): the same 6-trader roster as EW6, rebuilt
verbatim via live.paper SIGNAL_BUILDERS + ExitPatch/CostPatch (reused,
never re-implemented). Engine cells identical to EW6 (anchor-cum-sleeve);
the ONLY delta = additive engine flag report_num_entries=True (F6 dual
trade gate; PnL path untouched, metrics gain one key -- additive iron rule).

New gates in this batch (pre-registered):
  - twin determinism gate vs results/portfolio_ew6.json: member stats, corr
    averages, and the EW portfolio RE-DERIVATION must match recorded values
    |d|<1e-9 (data-drift tripwire; EW6 landed 00:54 same day). Mismatch =>
    batch VOID, no verdict, no repair-rerun (new prereg instead).
  - G1' v2 primary verdict via science_gates.g1_prime_v2 (skill_line_v2 +
    stationary bootstrap CI + F6 entries_ok on member-entry sums);
  - IV vs EW head-to-head table (the P3 question) + corr(IV6, EW6) disclosed
    as a construction-variant fact (D6 scope note in prereg s1);
  - first results/gate_attrition.json entry (closes science_audit C4 honest
    finding; EW6 entry retro-filled, flagged retro_fill=true).
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
from firm.hr import TRADERS_DIR, load_trader
from firm.risk.regime import (CAP_MAJOR_BEAR, CAP_NORMAL, MA_WINDOW,
                              load_benchmark_close, major_bear_state)
from live.paper import (OOS_START, SIGNAL_BUILDERS, CostPatch, ExitPatch,
                        build_panels, evidence_cutoff, seg_metrics,
                        self_test_patches)
from parallel_runner import run_cells_parallel, worker_cap
from science_gates import append_ledger, cutoff_meta, g1_prime_v2

import ew6_portfolio as E          # EW6 harness: reuse, never rewrite
from ew6_portfolio import (MAX_WORKERS, anchor_checks, bear_series, combine,
                           corr_block, g1_clauses, self_test_portfolio_math,
                           yearly_returns)

PREREG = os.path.join(PATHS.root, "research", "IV6_PORTFOLIO.md")
BATCH = "IV6-portfolio-riskbudget"
BATCH_CELLS = 14                   # frozen prereg s0 (12 engine + 2 IV evals)
CRASH_YEAR = -0.30
TOL = 1e-9                         # twin-gate tolerance (deterministic engine)
RESULTS_JSON = os.path.join(PATHS.results_dir, "portfolio_iv6.json")
EW6_JSON = os.path.join(PATHS.results_dir, "portfolio_ew6.json")
ATTRITION_JSON = os.path.join(PATHS.results_dir, "gate_attrition.json")
CSV_PATH = os.path.join(PATHS.root, "research", "iv6_results.csv")


def _init_worker():
    E._init_worker()               # sets ew6_portfolio.PRICES_FULL per worker


def member_run_iv6(tid: str, cost_mult=None) -> dict:
    """E.member_run verbatim + report_num_entries=True (additive metric key
    only; PnL path byte-identical -- F6 dual trade gate for the portfolio)."""
    prices_full = E.PRICES_FULL
    t = load_trader(tid)
    cutoff = evidence_cutoff(t, prices_full)
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    idx = P["close"].index
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    params["report_num_entries"] = True            # additive engine flag (F6)
    from contextlib import nullcontext
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    with cctx, ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0))
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_tr = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    is_part = eq[eq.index < pd.Timestamp(OOS_START)]
    return {"tid": tid, "cost_mult": cost_mult or 1, "cutoff": cutoff,
            "n_entries": int(res["metrics"].get("num_entries", 0)),
            "dates": [str(d.date()) for d in eq.index],
            "eq": [round(float(v), 6) for v in eq],
            "full": res["metrics"],
            "is": seg_metrics(is_part), "is2": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"], "oos_trades": oos_tr}


def iv_weights(sleeves: dict) -> dict:
    """Frozen prereg s3: w_i = (1/sigma_i-IS) / sum -- IS-segment member
    sleeve daily-return std, member's own equity axis, P3 precedent."""
    tids = sorted(sleeves)
    vol, raw = {}, {}
    for tid in tids:
        eq_s = sleeves[tid]["x1"]["eq_s"]
        is_ret = eq_s[eq_s.index < pd.Timestamp(OOS_START)].pct_change().dropna()
        vol[tid] = round(float(is_ret.std()), 6)
        raw[tid] = 1.0 / float(is_ret.std())
    s = sum(raw.values())
    w = {tid: round(raw[tid] / s, 6) for tid in tids}
    return {"weights": w, "sum": round(sum(w.values()), 6),
            "is_vol": vol, "raw_inverse_vol": {k: round(v, 8) for k, v in raw.items()}}


def eval_port(eqs: dict, weights: dict, scheme: str, cost_mult: int,
              member_s: dict, n_trades: int, n_entries: int, K: dict) -> dict:
    """Derive one portfolio off member sleeves (same combine semantics as
    EW6 -- no rebalancing; pure derivation, non-engine)."""
    eq = combine(eqs, weights)
    yr = yearly_returns(eq)
    p = {"scheme": scheme, "cost_mult": cost_mult, "weights": dict(weights),
         "equity": eq, "full": seg_metrics(eq),
         "is2": seg_metrics(eq, OOS_START), "n_trades": int(n_trades),
         "n_entries": int(n_entries), "yearly": yr,
         "worst_year": min(yr.values())}
    p["clauses"] = g1_clauses(p, p["n_trades"], K)
    w_mean = sum(weights[tid] * member_s[tid] for tid in weights)
    p["weighted_mean_member_sharpe"] = round(w_mean, 4)
    p["benefit"] = round(p["full"]["sharpe"] - w_mean, 4)
    p["dr"] = round(p["full"]["sharpe"] / w_mean, 4) if w_mean else None
    return p


def self_test_iv_math() -> bool:
    idx = pd.bdate_range("2024-01-01", "2025-06-30")
    # IS portion = 2024 (weight window); IS2 portion = 2025 H1 (~120 bars,
    # keeps seg_metrics out of the insufficient_data path -- J18 pitfall
    # family: synthetic selftest data must cross OOS_START)
    n = len(idx)
    # sleeve A: +1% on odd steps; sleeve B = A's daily returns scaled x2
    # => sigma_B = 2*sigma_A EXACTLY (std is scale-linear) => IV weights
    # ratio exactly 2:1 (frozen formula check)
    a = pd.Series(1.0, index=idx)
    a[1::2] = 1.01
    r_a = a.pct_change().fillna(0.0)
    b = (1.0 + 2.0 * r_a).cumprod()
    sl = {"A": {"x1": {"eq_s": a}}, "B": {"x1": {"eq_s": b}}}
    iv = iv_weights(sl)
    ok = abs(iv["weights"]["A"] - 2.0 / 3.0) < 1e-5 and \
         abs(iv["weights"]["B"] - 1.0 / 3.0) < 1e-5
    ok &= abs(iv["weights"]["A"] + iv["weights"]["B"] - 1.0) < 2e-6
    # eval_port smoke: EW of the two sleeves == combine at 0.5/0.5 (no
    # hard-coded parity constant -- derive the expectation from the inputs)
    port = eval_port({"A": a, "B": b}, {"A": 0.5, "B": 0.5}, "T", 1,
                     {"A": 1.0, "B": 1.0}, 10, 10,
                     {"i_bar": 0.0, "vi_bar": 0.0, "dd_min": -1.0,
                      "trades_min": 1})
    exp_last = 0.5 * float(a.iloc[-1]) + 0.5 * float(b.iloc[-1])
    ok &= abs(float(port["equity"].iloc[-1]) - exp_last) < 1e-9
    ok &= port["n_trades"] == 10 and port["n_entries"] == 10
    return bool(ok)


def crosscheck(sleeves: dict, corr: dict, ew_repro: dict, rec: dict) -> dict:
    """Twin determinism gate vs portfolio_ew6.json (prereg s2 gate 3)."""
    mem = {}
    for tid, m in rec["members"].items():
        r1, r2 = sleeves[tid]["x1"], sleeves[tid]["x2"]
        mem[tid] = {
            "cutoff": str(m["cutoff"]) == str(r1["cutoff"]),
            "n_trades": int(m["x1"]["n_trades"]) == int(r1["n_trades"]),
            "oos_trades": int(m["x1"]["oos_trades"]) == int(r1["oos_trades"]),
            "x1_full_sharpe": abs(float(m["x1"]["full"]["sharpe"])
                                  - float(r1["full"]["sharpe"])) < TOL,
            "x1_is_sharpe": abs(float(m["x1"]["is"]["sharpe"])
                                - float(r1["is"]["sharpe"])) < TOL,
            "x1_is2_sharpe": abs(float(m["x1"]["is2"]["sharpe"])
                                 - float(r1["is2"]["sharpe"])) < TOL,
            "x2_full_sharpe": abs(float(m["x2"]["full"]["sharpe"])
                                  - float(r2["full"]["sharpe"])) < TOL,
            "x2_is2_sharpe": abs(float(m["x2"]["is2"]["sharpe"])
                                 - float(r2["is2"]["sharpe"])) < TOL,
            "x2_n_trades": int(m["x2"]["n_trades"]) == int(r2["n_trades"]),
        }
    corr_ok = {seg: abs(float(rec["correlation"][seg]["avg_pairwise"])
                       - float(corr[seg]["avg_pairwise"])) < TOL
               for seg in ("full", "is", "is2")}
    q1, q2 = rec["portfolios"]["x1"], rec["portfolios"]["x2"]
    p1, p2 = ew_repro["x1"], ew_repro["x2"]
    port = {
        "x1_full_sharpe": abs(float(q1["full"]["sharpe"])
                              - float(p1["full"]["sharpe"])) < TOL,
        "x1_ann": abs(float(q1["full"]["annual_return"])
                      - float(p1["full"]["annual_return"])) < TOL,
        "x1_dd": abs(float(q1["full"]["max_drawdown"])
                     - float(p1["full"]["max_drawdown"])) < TOL,
        "x1_n_trades": int(q1["n_trades"]) == int(p1["n_trades"]),
        "x1_worst_year": abs(float(q1["worst_year"])
                             - float(p1["worst_year"])) < TOL,
        "x1_benefit": abs(float(q1["benefit"]) - float(p1["benefit"])) < TOL,
        "x1_dr": abs(float(q1["dr"]) - float(p1["dr"])) < TOL,
        "x2_full_sharpe": abs(float(q2["full"]["sharpe"])
                              - float(p2["full"]["sharpe"])) < TOL,
        "x2_is2_sharpe": abs(float(q2["is2"]["sharpe"])
                             - float(p2["is2"]["sharpe"])) < TOL,
        "x2_survive": bool(q1["x2_survive"]) == bool(p1["x2_survive"]),
    }
    ok = (all(all(v.values()) for v in mem.values()) and all(corr_ok.values())
          and all(port.values()))
    return {"ok": bool(ok), "members": mem, "corr": corr_ok, "ew_port": port}


def regime_block(port_eq: pd.Series) -> tuple:
    """R-pei3 slices + overlay for a portfolio equity (EW6 s2.8/2.9 verbatim
    semantics: cap(t)=state(t-1) causal, cash leg 0, single-source gate)."""
    bench = load_benchmark_close()
    bear = bear_series(bench)
    st_last = major_bear_state(bench)
    n_warm = int((bench.rolling(MA_WINDOW).mean().isna()).sum())
    cons_ok = (bool(bear.iloc[-1]) == st_last["is_major_bear"]
               and bool(bench.iloc[-1] < bench.rolling(MA_WINDOW)
                        .mean().iloc[-1]) == st_last["below_ma250"])
    r = port_eq.pct_change()
    s_same = bear.reindex(port_eq.index, method="ffill")
    s_prev = s_same.shift(1)
    cap = s_prev.map(lambda b: CAP_MAJOR_BEAR if b else CAP_NORMAL)
    first_na = int(cap.isna().sum())
    cap = cap.fillna(CAP_NORMAL)
    r_star = (r * cap).fillna(0.0)
    overlay = (1.0 + r_star).cumprod()
    overlay = overlay / overlay.iloc[0]
    ovr_yr = yearly_returns(overlay)
    overlay_metrics = {"full": seg_metrics(overlay),
                       "is2": seg_metrics(overlay, OOS_START),
                       "yearly": ovr_yr, "worst_year": min(ovr_yr.values()),
                       "bear_days_used": int(s_prev.fillna(False).sum()),
                       "first_day_defaults": first_na}

    def _slice(rr, mask):
        x = rr[mask]
        if len(x) < 10 or x.std() == 0:
            return {"n_days": int(len(x)), "sharpe": None, "ann_return": None}
        return {"n_days": int(len(x)),
                "sharpe": round(float(x.mean() / x.std() * 252 ** 0.5), 4),
                "ann_return": round(float((1 + x).prod()
                                          ** (252 / len(x)) - 1), 4)}

    same = s_same.fillna(False)
    slices = {
        "classification": "same-day bear state (descriptive; overlay uses "
                          "t-1 causal state per EW6 prereg s2.9)",
        "bear_days": _slice(r, same), "normal_days": _slice(r, ~same),
        "bear_ann_return_share": {
            "bear_cum_return": round(float((1 + r[same]).prod() - 1), 4)
            if same.any() else 0.0,
            "normal_cum_return": round(float((1 + r[~same]).prod() - 1), 4)},
    }
    return cons_ok, {"overlay": overlay_metrics, "slices": slices,
                     "state_latest": st_last, "warmup_days": n_warm}


def attrition_write(iv_entry: dict) -> None:
    """results/gate_attrition.json (science_audit C4): create-or-merge -- an
    existing file keeps other batches' entries (rerun-safe, dedupe by batch);
    EW6 entry retro-filled on first creation, flagged retro_fill=true."""
    with open(EW6_JSON, encoding="utf-8") as fh:
        ew6_rec = json.load(fh)
    v = ew6_rec["verdict"]
    ew6_entry = {
        "batch": "EW6-portfolio-validation",
        "ts": ew6_rec["generated"], "kind": "measurement", "retro_fill": True,
        "cells_ledger_delta": int(ew6_rec["trials_ledger"]["batch_trials"]),
        "ledger_total_after": int(ew6_rec["trials_ledger"]["total"]),
        "gates": {"descriptive_g1_clauses_all_pass": bool(all(
                      ew6_rec["portfolios"]["x1"]["clauses"].values())),
                  "x2_survive": bool(v["ew_x2_survive"]),
                  "worst_year_ok": bool(v["ew_worst_year"] > CRASH_YEAR),
                  "validated": bool(v["ew_validated"]),
                  "void": bool(ew6_rec["void"])},
        "eliminated": None,
        "refs": {"results": "results/portfolio_ew6.json",
                 "prereg": "research/shortline/EW6_PORTFOLIO.md"},
    }
    if os.path.exists(ATTRITION_JSON):
        with open(ATTRITION_JSON, encoding="utf-8") as fh:
            data = json.load(fh)
        data["entries"] = [e for e in data.get("entries", [])
                           if e.get("batch") != BATCH] + [iv_entry]
    else:
        data = {"schema": "gate-attrition-ledger v1",
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "purpose": "science_audit C4: per-batch gate-chain losses "
                           "account (s7-T retro mandatory; measurement "
                           "batches record gate outcomes, search batches "
                           "record eliminations)",
                "entries": [ew6_entry, iv_entry]}
        print("gate_attrition.json created (EW6 entry retro-filled)")
    with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print(f"saved: {ATTRITION_JSON} ({len(data['entries'])} entries)")


def main() -> int:
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort")
        return 2
    if not self_test_portfolio_math():
        print("portfolio-math/regime self-test FAILED -- abort")
        return 2
    if not self_test_iv_math():
        print("IV-math self-test FAILED -- abort")
        return 2
    print("patch + portfolio-math + IV-math self-tests: PASS")

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
    with open(EW6_JSON, encoding="utf-8") as fh:
        ew6rec = json.load(fh)

    tids = sorted(p.stem for p in TRADERS_DIR.glob("*.json")
                  if not p.name.startswith("_"))
    roster_ok = set(tids) == set(ew6rec["members"])
    print(f"members ({len(tids)}): {tids} roster_ok={roster_ok}")
    if not roster_ok:
        print("ROSTER DRIFT vs EW6 record -- batch void (twin gate scope)")
        return write_outputs(K, tids, None, None, None, None, None, None,
                            None, None, None, None, 0, t0, void=True,
                            void_reason="roster_drift_vs_ew6")

    # ---------- sleeves (12 engine runs, anchor-cum-sleeve) ----------
    jobs = [(f"{tid}|{mult}", member_run_iv6, (tid, mult))
            for tid in tids for mult in (None, 2)]
    res = run_cells_parallel(jobs, workers=min(worker_cap(), MAX_WORKERS),
                             desc="iv6-sleeves", initializer=_init_worker)
    workers = int(res.pop("__workers__"))
    sleeves = {}
    for tid in tids:
        r1, r2 = res[f"{tid}|None"], res[f"{tid}|2"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
        print(f"  {tid:<16} x1 full_s={r1['full']['sharpe']:>7.4f} "
              f"entries={r1['n_entries']:<4} trades={r1['n_trades']:<5} | "
              f"x2 full_s={r2['full']['sharpe']:>7.4f}")

    traders = {tid: load_trader(tid) for tid in tids}
    anchors = {tid: anchor_checks(traders[tid], sleeves[tid]["x1"],
                                 sleeves[tid]["x2"]) for tid in tids}
    for tid, a in anchors.items():
        print(f"  anchor {tid:<12} ok={a['anchor_ok']} x2_ok={a['x2_ok']}")
    if not all(a["anchor_ok"] and a["x2_ok"] for a in anchors.values()):
        print("ANCHOR/X2 BROKEN -- batch void, no verdict")
        return write_outputs(K, tids, sleeves, anchors, None, None, None,
                            None, None, None, None, None, workers, t0,
                            void=True, void_reason="anchor_broken")

    # ---------- correlations (member daily returns, EW6-identical) ----------
    norm1 = pd.concat({tid: sleeves[tid]["x1"]["eq_s"] /
                       sleeves[tid]["x1"]["eq_s"].iloc[0] for tid in tids},
                      axis=1, join="inner").dropna()
    rets = norm1.pct_change().dropna()
    is2_mask = rets.index >= pd.Timestamp(OOS_START)
    corr = {"full": corr_block(rets), "is": corr_block(rets, ~is2_mask),
            "is2": corr_block(rets, is2_mask)}
    print(f"corr(full) avg={corr['full']['avg_pairwise']} "
          f"is2 avg={corr['is2']['avg_pairwise']}")

    member_s = {tid: sleeves[tid]["x1"]["full"]["sharpe"] for tid in tids}
    n_tr_sum = sum(sleeves[tid]["x1"]["n_trades"] for tid in tids)
    n_ent_sum = sum(sleeves[tid]["x1"]["n_entries"] for tid in tids)
    ew_w = {tid: round(1.0 / len(tids), 6) for tid in tids}

    # ---------- twin gate leg 1: EW portfolio re-derivation ----------
    ew_repro = {}
    for mult, key in ((1, "x1"), (2, "x2")):
        ew_repro[key] = eval_port(
            {tid: sleeves[tid][key]["eq_s"] for tid in tids}, ew_w,
            "EW-repro", mult, member_s, n_tr_sum, n_ent_sum, K)
    p1 = ew_repro["x1"]
    p1["x2_survive"] = bool(ew_repro["x2"]["full"]["sharpe"] > K["vi_bar"]
                            and ew_repro["x2"]["is2"]["sharpe"] > 0)

    xchk = crosscheck(sleeves, corr, ew_repro, ew6rec)
    print(f"twin determinism gate vs portfolio_ew6.json: "
          f"{'PASS' if xchk['ok'] else 'FAIL'}")
    if not xchk["ok"]:
        print("TWIN GATE BROKEN (data drift since EW6) -- batch void")
        return write_outputs(K, tids, sleeves, anchors, corr, None, ew_repro,
                            None, None, xchk, None, None, workers, t0,
                            void=True, void_reason="twin_gate_drift")

    # ---------- IV weights (frozen formula) + IV portfolios ----------
    iv = iv_weights(sleeves)
    w_iv = iv["weights"]
    print(f"IV weights: {w_iv} (sum={iv['sum']})")
    ports = {}
    for mult, key in ((1, "x1"), (2, "x2")):
        ports[key] = eval_port(
            {tid: sleeves[tid][key]["eq_s"] for tid in tids}, w_iv,
            "IV", mult, member_s, n_tr_sum, n_ent_sum, K)
    p, px = ports["x1"], ports["x2"]
    p["x2_survive"] = bool(px["full"]["sharpe"] > K["vi_bar"]
                           and px["is2"]["sharpe"] > 0)
    p["validated"] = bool(p["benefit"] > 0 and all(p["clauses"].values())
                          and p["worst_year"] > CRASH_YEAR and p["x2_survive"])
    print(f"  port IV x1: full_s={p['full']['sharpe']:>7.4f} "
          f"is2_s={p['is2']['sharpe']:>7.4f} benefit={p['benefit']:>7.4f} "
          f"DR={p['dr']} worst_year={p['worst_year']} | "
          f"x2 full_s={px['full']['sharpe']:>7.4f} "
          f"survive={p['x2_survive']} -> validated={p['validated']}")

    # ---------- G1' v2 primary gates (science_gates, no hand-copied lines) --
    v2_iv = g1_prime_v2(p["full"]["sharpe"], p["equity"].pct_change().dropna(),
                        batch_cells=BATCH_CELLS, n_trades=n_tr_sum,
                        n_entries=n_ent_sum)
    v2_ew = g1_prime_v2(p1["full"]["sharpe"],
                        p1["equity"].pct_change().dropna(),
                        batch_cells=BATCH_CELLS, n_trades=n_tr_sum,
                        n_entries=n_ent_sum)
    print(f"v2 gate IV6: line={v2_iv['skill_line']['line']} "
          f"line_ok={v2_iv['line_ok']} ci_ok={v2_iv['ci_lower_bound_positive']} "
          f"entries_ok={v2_iv['trade_gate']['entries_ok']} -> "
          f"pass_v2={v2_iv['pass_v2']}")
    print(f"v2 today-line readout EW-repro: pass_v2={v2_ew['pass_v2']}")

    # ---------- head-to-head (the P3 question) + corr(IV6, EW6) ----------
    both = pd.concat({"IV6": p["equity"], "EW": p1["equity"]}, axis=1).dropna()
    corr_iv_ew = round(float(both.pct_change().dropna().corr()
                             .loc["IV6", "EW"]), 4)
    h2h = {
        "delta_full_sharpe": round(float(p["full"]["sharpe"]
                                         - p1["full"]["sharpe"]), 4),
        "delta_annual": round(float(p["full"]["annual_return"]
                                    - p1["full"]["annual_return"]), 4),
        "delta_max_dd": round(float(p["full"]["max_drawdown"]
                                    - p1["full"]["max_drawdown"]), 4),
        "delta_worst_year": round(float(p["worst_year"] - p1["worst_year"]), 4),
        "delta_benefit": round(float(p["benefit"] - p1["benefit"]), 4),
        "delta_dr": round(float(p["dr"] - p1["dr"]), 4),
        "delta_x2_full_sharpe": round(float(px["full"]["sharpe"]
                                            - ew_repro["x2"]["full"]["sharpe"]), 4),
        "corr_iv6_ew6": corr_iv_ew,
        "carrier_note": "EW stays the validated carrier (prereg s4: no "
                        "post-run switching; IV adoption = charter s5 T1)",
    }
    print(f"head-to-head IV vs EW: dSharpe={h2h['delta_full_sharpe']} "
          f"dDD={h2h['delta_max_dd']} dBenefit={h2h['delta_benefit']} "
          f"corr={corr_iv_ew}")

    # ---------- R-pei3 regime layer for IV6 (charter s3 mandatory) ----------
    cons_ok, regime = regime_block(p["equity"])
    print(f"regime consistency gate: {'PASS' if cons_ok else 'FAIL'} "
          f"(last={regime['state_latest']['as_of']} "
          f"bear={regime['state_latest']['is_major_bear']}, "
          f"warmup_days={regime['warmup_days']})")
    if not cons_ok:
        print("REGIME SINGLE-SOURCE MISMATCH -- batch void")
        return write_outputs(K, tids, sleeves, anchors, corr, ports, ew_repro,
                            iv, v2_iv, xchk, h2h,
                            {"v2_ew_repro_today_line": v2_ew, "regime": regime},
                            workers, t0, void=True, void_reason="regime_consistency")

    return write_outputs(K, tids, sleeves, anchors, corr, ports, ew_repro,
                         iv, v2_iv, xchk, h2h,
                         {"v2_ew_repro_today_line": v2_ew, "regime": regime},
                         workers, t0, void=False)


def write_outputs(K, tids, sleeves, anchors, corr, ports, ew_repro, iv, v2_iv,
                  xchk, h2h, extra, workers, t0, void=False,
                  void_reason="") -> int:
    n_runs = 0 if sleeves is None else 2 * len(tids)
    n_evals = 0 if ports is None else 2            # IV x1/x2 (ledger-counted)
    batch_trials = n_runs + n_evals               # actual runs, EW6 precedent
    ledger = append_ledger(
        BATCH, batch_trials,
        file_name="results/portfolio_iv6.json",
        evidence_cutoff="2026-09-22",
        note=f"{n_runs} engine member runs (anchor-cum-sleeve, x1+x2, "
             f"EW6-identical cells; only delta = additive "
             f"report_num_entries flag) + {n_evals} IV portfolio evaluations "
             f"(derived, non-engine); twin-gate EW re-derivations and v2 "
             f"readouts are gates/disclosures, not ledger cells; zero "
             f"search => zero nulls (composition disclosed, prereg s0); "
             f"actual={batch_trials} vs frozen budget {BATCH_CELLS}"
             + (f"; batch VOID ({void_reason})" if void else ""))
    prereg_sha = hashlib.sha256(open(PREREG, "rb").read()).hexdigest()

    rows = []
    if sleeves:
        for tid in tids:
            for mult, key in ((1, "x1"), (2, "x2")):
                rr = sleeves[tid][key]
                yr = yearly_returns(rr["eq_s"])
                rows.append({"kind": "member", "id": tid, "cost_mult": mult,
                             "full_sharpe": rr["full"]["sharpe"],
                             "full_ann": rr["full"]["annual_return"],
                             "full_dd": rr["full"]["max_drawdown"],
                             "n_trades": rr["n_trades"],
                             "n_entries": rr.get("n_entries", ""),
                             "is2_sharpe": rr["is2"]["sharpe"],
                             "is2_ann": rr["is2"]["annual_return"],
                             "worst_year": min(yr.values()) if yr else "",
                             "anchor_ok": anchors[tid]["anchor_ok"]
                             if mult == 1 else anchors[tid]["x2_ok"]})
    for tag, pp in (("portfolio", ports), ("portfolio-repro", ew_repro)):
        if not pp:
            continue
        label = "IV6" if tag == "portfolio" else "EW6-repro"
        for mult, key in ((1, "x1"), (2, "x2")):
            q = pp[key]
            rows.append({"kind": tag, "id": label, "cost_mult": mult,
                         "full_sharpe": q["full"]["sharpe"],
                         "full_ann": q["full"]["annual_return"],
                         "full_dd": q["full"]["max_drawdown"],
                         "n_trades": q["n_trades"], "n_entries": q["n_entries"],
                         "is2_sharpe": q["is2"]["sharpe"],
                         "is2_ann": q["is2"]["annual_return"],
                         "worst_year": q["worst_year"], "anchor_ok": ""})
    cols = ["kind", "id", "cost_mult", "full_sharpe", "full_ann", "full_dd",
            "n_trades", "n_entries", "is2_sharpe", "is2_ann", "worst_year",
            "anchor_ok"]
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    print(f"saved: {CSV_PATH} ({len(rows)} rows)")

    p, px = (ports["x1"], ports["x2"]) if ports else (None, None)
    verdict = {
        "template": "IV6 report-only pass 2 (pre-registered IV carrier "
                    "measurement; EW stays validated baseline)",
        "void": bool(void), "void_reason": void_reason or None,
        "crosscheck_ok": None if not xchk else bool(xchk["ok"]),
        "iv_validated": None if not p else bool(p["validated"]),
        "iv_clauses": None if not p else p["clauses"],
        "iv_benefit": None if not p else p["benefit"],
        "iv_dr": None if not p else p["dr"],
        "iv_x2_survive": None if not p else bool(p["x2_survive"]),
        "iv_worst_year": None if not p else p["worst_year"],
        "v2_pass": None if not v2_iv else bool(v2_iv["pass_v2"]),
        "skill_line_v2": None if not v2_iv else v2_iv["skill_line"]["line"],
        "head_to_head": h2h,
        "applicability": "descriptive continuity metrics + v2 gate readout; "
                         "no promotion, no allocation, no carrier switch; IV "
                         "adoption = charter s5 T1; regime premium (P-5B "
                         "6/6 fail 0.70 beat line) discounts all Sharpe reads",
    }
    out = {
        "batch": BATCH,
        "task": "EW6 continuation pointer s6.7-1 (report-only pass 2, "
                "charter s1.1 IV upgrade path)",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/IV6_PORTFOLIO.md",
        "prereg_sha256_at_run": prereg_sha,
        "oos_start": OOS_START,
        "d2_note": "2025+ segment = IS2 (forward-lockbox demotion); true OOS "
                   "= post-cutoff locked box via paper accrual, not consumed",
        "void": bool(void), "void_reason": void_reason or None,
        "constants": {"g1_prime_i_bar": K["i_bar"],
                      "g1_prime_vi_bar": K["vi_bar"],
                      "crash_year": CRASH_YEAR,
                      "batch_cells": BATCH_CELLS,
                      "passive_ew48_buyhold": K["passive_ew48_buyhold"],
                      "passive_ew48_monthly": K["passive_ew48_monthly"],
                      "cost_basis": "legacy fee path (additive engine flags "
                                    "OFF except report_num_entries metric "
                                    "key; cost_v2 not used this batch)"},
        "universe": {"pool": "core48-bare-codes", "members": tids,
                     "member_cutoffs": {tid: sleeves[tid]["x1"]["cutoff"]
                                        for tid in tids} if sleeves else None},
        "members": {tid: {"cutoff": sleeves[tid]["x1"]["cutoff"],
                          "n_entries": sleeves[tid]["x1"]["n_entries"],
                          "x1": {k: sleeves[tid]["x1"][k] for k in
                                 ("full", "is", "is2", "n_trades",
                                  "oos_trades")},
                          "x2": {k: sleeves[tid]["x2"][k] for k in
                                 ("full", "is2", "n_trades", "n_entries")}}
                    for tid in tids} if sleeves else None,
        "anchors": anchors,
        "crosscheck_twin_gate_vs_ew6": xchk,
        "correlation": corr,
        "iv_weights": iv,
        "portfolios_iv": {key: {k: v for k, v in q.items() if k != "equity"}
                          for key, q in ports.items()} if ports else None,
        "ew_repro": {key: {k: v for k, v in q.items() if k != "equity"}
                     for key, q in ew_repro.items()} if ew_repro else None,
        "head_to_head": h2h,
        "v2_gate_iv6": v2_iv,
        "extra": extra,
        "verdict": verdict,
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "n_portfolio_evals": n_evals,
                  "n_twin_repro_evals": 2 if ew_repro else 0,
                  "workers": workers,
                  "parallel": f"parallel_runner ProcessPool workers={workers}"},
    }
    out.update(cutoff_meta("2026-09-22"))
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {RESULTS_JSON}")

    attrition_write({
        "batch": BATCH, "ts": out["generated"], "kind": "measurement",
        "retro_fill": False, "cells_ledger_delta": int(batch_trials),
        "ledger_total_after": int(ledger["total"]),
        "gates": {"g1_prime_v2_pass": verdict["v2_pass"],
                  "descriptive_g1_clauses_all_pass": None if not p else bool(
                      all(p["clauses"].values())),
                  "x2_survive": verdict["iv_x2_survive"],
                  "worst_year_ok": None if not p else bool(
                      p["worst_year"] > CRASH_YEAR),
                  "twin_gate_crosscheck": verdict["crosscheck_ok"],
                  "validated": verdict["iv_validated"],
                  "void": bool(void), "void_reason": void_reason or None},
        "eliminated": None,
        "refs": {"results": "results/portfolio_iv6.json",
                 "prereg": "research/IV6_PORTFOLIO.md"},
    })
    summary = (f"IV6 validated={verdict['iv_validated']} "
               f"v2_pass={verdict['v2_pass']} "
               f"benefit={verdict['iv_benefit']} "
               f"x2_survive={verdict['iv_x2_survive']}"
               if not void else f"VOID ({void_reason})")
    print(f"\n===== IV6 verdict: {summary} =====")
    print(f"runs={n_runs} evals={n_evals} elapsed={time.time()-t0:.1f}s "
          f"ledger N={ledger['total']} (prev={ledger['prev_total']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
