"""P3 portfolio validation -> one-shot verdict (pre-registered).

PRE-REGISTERED before running (research/portfolio_report.md, written
first). Do NOT tune thresholds or switch the primary scheme after
seeing results (p-hacking ban, iron rule 3).

Question (BACKTEST_PLAN sec.4 P3): do the 3 registered traders form a
portfolio with (a) real diversification benefit, (b) portfolio-level
skill above the G1' line, (c) cost-x2 survival?

Members are FIXED (no search): the 3 firm/traders registrations,
rebuilt verbatim via live.paper SIGNAL_BUILDERS + ExitPatch (reused,
not re-implemented). Sleeves run TRUNCATED at each trader's
evidence_cutoff. Two combination schemes, both pre-registered:
  S-EW (PRIMARY, parameter-free): 1/3 initial weights, no rebalance.
  S-IV (secondary): inverse-vol weights from IS (2020-2024) daily
      returns only, fixed for the whole history (no look-ahead).

Hard anchors (batch void if any fails):
  1x run must reproduce registered in_sample/out_sample evidence
  (live.paper._evidence_matches semantics); 2x run must match the
  registered backtest.cost_x2 sharpe/oos_sharpe within 0.002.

Verdict (EW is the pre-registered carrier):
  validated <=> benefit>0 AND all six G1' clauses on the combined
  equity AND worst calendar year > -30% AND x2 survive
  (full sharpe > 0.4004 AND oos sharpe > 0).

No new traders, no new subsystems this batch (measurement, not search).
Products: research/p3_portfolio_results.csv + results/p3_portfolio.json
+ research/portfolio_report.md sec.6 (appended after the run).
Trial ledger: cumulative from ce_transfer.json + actual runs.
"""
import csv
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import annual_return, max_drawdown, sharpe
from firm.hr import TRADERS_DIR, load_trader
from live.paper import (ANCHOR_TOL, COST_X1_RATE, COST_X2_RATE, OOS_START,
                        SIGNAL_BUILDERS, CostPatch, ExitPatch, build_panels,
                        evidence_cutoff, load_core, seg_metrics, self_test_patches,
                        _evidence_matches)

SCHEMES = ("EW", "IV")            # EW = pre-registered primary carrier
CRASH_YEAR = -0.30
CORR_BANDS = ((0.60, "low"), (0.80, "moderate"), (None, "high"))
TRIALS_PRIOR = "ce_transfer.json"  # latest cumulative ledger


def load_constants() -> dict:
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        calib = json.load(fh)
    g = calib["g1_prime_gate"]
    passive = calib["families"]["C_passive"]["runs"]
    with open(os.path.join(PATHS.results_dir, TRIALS_PRIOR),
              encoding="utf-8") as fh:
        prior = json.load(fh)
    return {
        "i_bar": g["i_full_sharpe_gt"],          # 0.3521 random p95
        "vi_bar": g["vi_full_sharpe_gt"],         # 0.4004 passive+0.1
        "dd_min": g["iii_dd_min"], "trades_min": g["iv_trades_min"],
        "passive_ew48_buyhold": passive["ew48_buyhold"],
        "passive_ew48_monthly": passive["ew48_monthly_rebal"],
        "prior_ledger": prior["trials_ledger"],
        "prior_n": sum(x["n"] for x in prior["trials_ledger"]),
    }


def member_run(t: dict, prices_full: dict, cost_mult=None) -> dict:
    """Registered trader rerun, truncated at evidence_cutoff (anchor-gate
    pattern). Same code path as live.paper.anchor_gate, kept identical
    so the sleeve IS the anchor run (no double engine runs)."""
    cutoff = evidence_cutoff(t, prices_full)
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    idx = P["close"].index
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    cctx = CostPatch(cost_mult) if cost_mult else nullcontext()
    with cctx, ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0))
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos_trades = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    return {"eq": eq, "cutoff": cutoff,
            "full": res["metrics"], "oos": seg_metrics(eq, OOS_START),
            "n_trades": res["metrics"]["num_trades"],
            "oos_trades": oos_trades}


def anchor_checks(t: dict, r1: dict, r2: dict) -> dict:
    """Hard gates: registered evidence @1x AND registered x2 evidence."""
    got_is = {**seg_metrics(r1["eq"][r1["eq"].index < OOS_START]),
              "trades": r1["n_trades"] - r1["oos_trades"]}
    got_oos = {**r1["oos"], "trades": r1["oos_trades"]}
    a_ok = (_evidence_matches(got_is, t["backtest"]["in_sample"])
            and _evidence_matches(got_oos, t["backtest"]["out_sample"]))
    x2 = t["backtest"]["cost_x2"]
    x_ok = (abs(r2["full"]["sharpe"] - x2["sharpe"]) < ANCHOR_TOL
            and abs(r2["oos"]["sharpe"] - x2["oos_sharpe"]) < ANCHOR_TOL)
    return {"anchor_ok": bool(a_ok), "x2_ok": bool(x_ok),
            "got_is": got_is, "got_oos": got_oos,
            "got_x2_full": r2["full"]["sharpe"], "got_x2_oos": r2["oos"]["sharpe"],
            "want_x2_full": x2["sharpe"], "want_x2_oos": x2["oos_sharpe"]}


def yearly_returns(equity: pd.Series) -> dict:
    out = {}
    for year, seg in equity.groupby(equity.index.year):
        out[int(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1), 4)
    return out


def combine(eqs: dict, weights: dict) -> pd.Series:
    """Fixed initial weights, no rebalance: port = sum w_i * (eq_i/eq_i0)."""
    tids = list(weights)
    norm = pd.concat({tid: eqs[tid] / eqs[tid].iloc[0] for tid in tids},
                     axis=1, join="inner").dropna()
    norm = norm[tids]
    return norm.mul(pd.Series(weights)).sum(axis=1)


def iv_weights(returns: pd.DataFrame) -> dict:
    """Inverse-vol from IS daily returns only (no look-ahead)."""
    is_ret = returns[returns.index < pd.Timestamp(OOS_START)]
    vol = is_ret.std()
    w = 1.0 / vol
    return {tid: float(w[tid] / w.sum()) for tid in w.index}


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
    f_, o_ = port["full"], port["oos"]
    return {"i_beats_rand_p95": f_["sharpe"] > K["i_bar"],
            "ii_ann_pos": f_["annual_return"] > 0,
            "iii_dd_ok": f_["max_drawdown"] >= K["dd_min"],
            "iv_trades_ok": n_trades >= K["trades_min"],
            "v_oos_ok": o_["sharpe"] > 0 and o_["annual_return"] > 0,
            "vi_beats_passive": f_["sharpe"] > K["vi_bar"]}


def self_test_portfolio_math() -> bool:
    """Synthetic 2-sleeve combine + IV weights must be exact."""
    idx = pd.bdate_range("2024-01-01", "2024-03-31")   # IS range (not OOS)
    a = pd.Series([1.0, 1.01, 1.02, 1.03], index=idx[:4])       # slow
    b = pd.Series([1.0, 1.05, 0.90, 1.10], index=idx[:4])       # wild
    eqs = {"A": a, "B": b}
    port = combine(eqs, {"A": 0.5, "B": 0.5})
    exp = 0.5 * (a / 1.0) + 0.5 * (b / 1.0)
    ok = bool((port - exp).abs().max() < 1e-12) and float(port.iloc[0]) == 1.0
    rets = pd.concat(eqs, axis=1).pct_change().dropna()
    w = iv_weights(rets)
    ok &= abs(w["A"] + w["B"] - 1.0) < 1e-12 and w["A"] > w["B"]  # calmer wins
    return bool(ok)


def main():
    t0 = time.time()
    if not self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    if not self_test_portfolio_math():
        print("portfolio math self-test FAILED -- abort")
        return 2
    print("patch + portfolio-math self-tests: PASS")

    K = load_constants()
    print(f"constants: i>{K['i_bar']} vi>{K['vi_bar']} "
          f"prior_N={K['prior_n']} passive(EW48 buyhold full)="
          f"{K['passive_ew48_buyhold']['full']['sharpe']}")

    prices_full = load_core()
    P = build_panels(prices_full)
    data_end = str(P["close"].index[-1].date())
    print(f"universe: {len(prices_full)} ETFs, data through {data_end}")

    tids = [p.stem for p in sorted(TRADERS_DIR.glob("*.json"))
            if not p.name.startswith("_")]
    traders = {tid: load_trader(tid) for tid in tids}
    print(f"members: {tids}")

    # ---------- sleeves (anchor-cum-member) ----------
    sleeves = {}
    anchors = {}
    for tid in tids:
        r1 = member_run(traders[tid], prices_full, None)
        r2 = member_run(traders[tid], prices_full, cost_mult=2)
        a = anchor_checks(traders[tid], r1, r2)
        anchors[tid] = a
        sleeves[tid] = {"x1": r1, "x2": r2}
        print(f"  {tid:<16} x1 full_s={r1['full']['sharpe']:>7.4f} "
              f"oos_s={r1['oos']['sharpe']:>7.4f} trades={r1['n_trades']:<5} "
              f"| x2 full_s={r2['full']['sharpe']:>7.4f} "
              f"anchor={'OK' if a['anchor_ok'] else 'BROKEN'} "
              f"x2={'OK' if a['x2_ok'] else 'BROKEN'}")
    if not all(a["anchor_ok"] and a["x2_ok"] for a in anchors.values()):
        print("ANCHOR/X2 BROKEN -- batch void, no verdict")
        return write_outputs(K, traders, sleeves, anchors, None, None,
                             t0, data_end, void=True)

    # ---------- correlations (member daily returns) ----------
    norm1 = pd.concat({tid: sleeves[tid]["x1"]["eq"] / sleeves[tid]["x1"]["eq"].iloc[0]
                       for tid in tids}, axis=1, join="inner").dropna()
    rets = norm1.pct_change().dropna()
    oos_mask = rets.index >= pd.Timestamp(OOS_START)
    corr = {"full": corr_block(rets),
            "is": corr_block(rets, ~oos_mask),
            "oos": corr_block(rets, oos_mask)}
    print(f"corr(full) avg={corr['full']['avg_pairwise']} "
          f"band={corr['full']['band']} pairs={corr['full']['pairs']}")

    # ---------- portfolios ----------
    weights = {"EW": {tid: round(1.0 / len(tids), 6) for tid in tids},
               "IV": iv_weights(rets)}
    ports = {}
    for scheme in SCHEMES:
        w = weights[scheme]
        for mult, key in ((1, "x1"), (2, "x2")):
            eqs = {tid: sleeves[tid][key]["eq"] for tid in tids}
            eq = combine(eqs, w)
            full = seg_metrics(eq)
            oos = seg_metrics(eq, OOS_START)
            n_tr = sum(sleeves[tid][key]["n_trades"] for tid in tids)
            ports[f"{scheme}_{key}"] = {
                "scheme": scheme, "cost_mult": mult, "weights": w,
                "equity": eq, "full": full, "oos": oos, "n_trades": n_tr,
                "yearly": yearly_returns(eq),
                "worst_year": min(yearly_returns(eq).values()),
            }
        p = ports[f"{scheme}_x1"]
        px = ports[f"{scheme}_x2"]
        c = g1_clauses(p, p["n_trades"], K)
        member_s = {tid: sleeves[tid]["x1"]["full"]["sharpe"] for tid in tids}
        w_mean = sum(w[tid] * member_s[tid] for tid in tids)
        p["clauses"] = c
        p["member_sharpes"] = member_s
        p["weighted_mean_member_sharpe"] = round(w_mean, 4)
        p["benefit"] = round(p["full"]["sharpe"] - w_mean, 4)
        p["dr"] = round(p["full"]["sharpe"] / w_mean, 4) if w_mean else None
        p["x2_survive"] = bool(px["full"]["sharpe"] > K["vi_bar"]
                               and px["oos"]["sharpe"] > 0)
        p["validated"] = bool(p["benefit"] > 0 and all(c.values())
                              and p["worst_year"] > CRASH_YEAR
                              and p["x2_survive"])
        print(f"  port {scheme} x1: full_s={p['full']['sharpe']:>7.4f} "
              f"oos_s={p['oos']['sharpe']:>7.4f} benefit={p['benefit']:>7.4f} "
              f"DR={p['dr']} worst_year={p['worst_year']} | "
              f"x2 full_s={px['full']['sharpe']:>7.4f} "
              f"survive={p['x2_survive']} -> validated={p['validated']}")

    return write_outputs(K, traders, sleeves, anchors, corr, ports,
                         t0, data_end, void=False)


def write_outputs(K, traders, sleeves, anchors, corr, ports, t0, data_end,
                  void=False):
    tids = list(traders)
    n_runs = 0 if sleeves is None else 2 * len(tids)          # engine runs
    n_evals = 0 if ports is None else 2 * len(SCHEMES)        # portfolio evals
    ledger = list(K["prior_ledger"]) + [{
        "batch": "P3-portfolio-validation", "n": n_runs + n_evals,
        "note": f"{n_runs} engine member runs (anchor-cum-sleeve) + "
                f"{n_evals} portfolio evaluations (derived, non-engine)"}]

    # ---------- CSV ----------
    rows = []
    for tid in tids:
        for mult, key in ((1, "x1"), (2, "x2")):
            r = sleeves[tid][key]
            yr = yearly_returns(r["eq"])
            rows.append({"kind": "member", "id": tid, "scheme": "",
                         "cost_mult": mult, "weights": "",
                         "full_sharpe": r["full"]["sharpe"],
                         "full_ann": r["full"]["annual_return"],
                         "full_dd": r["full"]["max_drawdown"],
                         "n_trades": r["n_trades"],
                         "oos_sharpe": r["oos"]["sharpe"],
                         "oos_ann": r["oos"]["annual_return"],
                         "benefit": "", "dr": "",
                         "worst_year": min(yr.values()) if yr else "",
                         "x2_survive": "",
                         "anchor_ok": anchors[tid]["anchor_ok"] if mult == 1
                         else anchors[tid]["x2_ok"]})
    if ports:
        for name, p in ports.items():
            if name.endswith("_x2"):
                continue
            for mult, key in ((1, "x1"), (2, "x2")):
                q = ports[f"{p['scheme']}_{key}"]
                rows.append({"kind": "portfolio", "id": p["scheme"],
                             "scheme": p["scheme"], "cost_mult": mult,
                             "weights": json.dumps(p["weights"]),
                             "full_sharpe": q["full"]["sharpe"],
                             "full_ann": q["full"]["annual_return"],
                             "full_dd": q["full"]["max_drawdown"],
                             "n_trades": q["n_trades"],
                             "oos_sharpe": q["oos"]["sharpe"],
                             "oos_ann": q["oos"]["annual_return"],
                             "benefit": p["benefit"] if mult == 1 else "",
                             "dr": p["dr"] if mult == 1 else "",
                             "worst_year": q["worst_year"],
                             "x2_survive": p["x2_survive"] if mult == 2 else "",
                             "anchor_ok": ""})
    csv_path = os.path.join(PATHS.root, "research", "p3_portfolio_results.csv")
    cols = ["kind", "id", "scheme", "cost_mult", "weights", "full_sharpe",
            "full_ann", "full_dd", "n_trades", "oos_sharpe", "oos_ann",
            "benefit", "dr", "worst_year", "x2_survive", "anchor_ok"]
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    print(f"saved: {csv_path} ({len(rows)} rows)")

    # ---------- JSON ----------
    ew = ports["EW_x1"] if ports else None
    iv = ports["IV_x1"] if ports else None
    out = {
        "batch": "P3-portfolio-validation",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc":
            "research/portfolio_report.md (written before run)",
        "universe": {"pool": "core48-bare-codes", "history": f".. {data_end}"},
        "oos_start": OOS_START,
        "void": void,
        "constants": {
            "g1_prime_i_bar": K["i_bar"], "g1_prime_vi_bar": K["vi_bar"],
            "crash_year": CRASH_YEAR, "corr_bands":
                {"low": "<0.60", "moderate": "0.60-0.80", "high": ">0.80"},
            "passive_ew48_buyhold": K["passive_ew48_buyhold"],
            "passive_ew48_monthly": K["passive_ew48_monthly"],
            "note": "passive null = recorded p2_calibration constants "
                    "(no rerun; this batch is measurement, members+weights "
                    "pre-registered, zero new search)",
        },
        "members": {tid: {
            "cutoff": sleeves[tid]["x1"]["cutoff"],
            "x1": {k: sleeves[tid]["x1"][k] for k in
                   ("full", "oos", "n_trades", "oos_trades")},
            "x2": {k: sleeves[tid]["x2"][k] for k in
                   ("full", "oos", "n_trades")},
            "yearly_returns": yearly_returns(sleeves[tid]["x1"]["eq"]),
        } for tid in tids} if sleeves else None,
        "anchors": anchors,
        "correlation": corr,
        "portfolios": {name: {k: v for k, v in p.items() if k != "equity"}
                       for name, p in ports.items()} if ports else None,
        "verdict": {
            "template": "P3 one-shot (pre-registered; EW=primary carrier)",
            "void": void,
            "corr_band_full": None if not corr else corr["full"]["band"],
            "ew_validated": None if not ew else ew["validated"],
            "ew_clauses": None if not ew else ew["clauses"],
            "ew_benefit": None if not ew else ew["benefit"],
            "ew_dr": None if not ew else ew["dr"],
            "ew_x2_survive": None if not ew else ew["x2_survive"],
            "ew_worst_year": None if not ew else ew["worst_year"],
            "iv_validated": None if not iv else iv["validated"],
            "iv_clauses": None if not iv else iv["clauses"],
            "iv_benefit": None if not iv else iv["benefit"],
            "iv_x2_survive": None if not iv else iv["x2_survive"],
            "iv_worst_year": None if not iv else iv["worst_year"],
            "fail_branch": None if (void or (ew and ew["validated"])) else
            "EW portfolio not validated -> portfolio line closed this "
            "batch; NO weight/scheme/member retries (p-hacking ban); "
            "strategy line returns to J19 6.5-2 (low-frequency low-cost "
            "instrument family) via new pre-registration",
        },
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": n_runs, "n_portfolio_evals": n_evals,
                  "workers": 1, "cpu_parallel": "serial (single-process)"},
    }
    json_path = os.path.join(PATHS.results_dir, "p3_portfolio.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"saved: {json_path}")

    if void:
        summary = "VOID (anchor broken)"
    else:
        summary = (f"EW validated={ew.get('validated')} "
                   f"IV validated={iv.get('validated')}")
    print(f"\n===== P3 verdict: {summary} =====")
    print(f"runs={n_runs} evals={n_evals} elapsed: {time.time()-t0:.0f}s "
          f"ledger N={sum(x['n'] for x in ledger)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
