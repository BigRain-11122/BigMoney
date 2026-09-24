"""T27 blend-method tournament -> one-shot ranked report (T-2026-09-24-27).

PRE-REGISTERED before running (research/T27_BLEND_TOURNAMENT.md, frozen
commit precedes any run; prereg sha256 embedded in the output JSON). Do NOT
tune weights/formulas/thresholds after seeing results (iron rule 3).

Five FROZEN blend-method candidates over the FIXED registered 6-member
roster (zero search, zero new signal functions -> zero nulls; D6 scoping
disclosed in prereg s1). Uniform evaluation frame = daily-rebalanced to
target weights on inner-joined member sleeve daily returns (prereg s3);
canon static-combine continuity is carried by the twin gate leg, NOT by
the ranking frame.

Methods (all weight estimation IS-segment-only = pre-OOS_START, causal;
x2 face reuses x1-frozen weights):
  A IV risk-budget       = iv6_portfolio.iv_weights verbatim (canon)
  B Max-diversification  = closed-form Sigma_IS^-1 sigma_IS (long-only; any
                           component <= 0 -> deterministic projected-gradient
                           ascent fallback, disclosed, best-seen tracked)
  C IV x momentum hybrid = raw_i = (1/sigma_i) * (1+m_i), clamp >= 0, m_i =
                           IS-segment cumulative return of member x1 sleeve
  D Regime-conditional   = defensive = A weights; offensive = IS-Sharpe-
                           proportional (max(S,0), EW fallback); state(t-1)
                           major-bear (firm/risk/regime.py bear_series, single
                           source, causal) -> defensive else offensive; first
                           day defaults to normal (EW6 overlay precedent)
  E Equal-weight         = control

Gates (frozen prereg s4): twin determinism vs portfolio_iv6.json (members /
corr / static EW-repro / IV weights+portfolio, |d| < 1e-9, mismatch => VOID);
per-candidate primary gates = G1' v2 (42 cells) + six clauses + benefit > 0
+ DR > 1 + x2 survival + robustness (IS sharpe > 0, worst_year > -0.30).
Winner = best MEDIAN rank across 3 faces (benefit / drawdown / x2 margin)
among eligible; tie -> benefit face; zero eligible -> no winner, IV canon
retained. Adoption = GM ratify + 7-day veto (ticket item 3) -- NOT wired
in this batch; zero engine changes, zero paper-canon touches.

CLI: run | selftest | status.
"""
import csv
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
from firm.hr import TRADERS_DIR, load_trader
from firm.risk.regime import (load_benchmark_close, major_bear_state,
                              MA_WINDOW)
from live.paper import OOS_START, seg_metrics, self_test_patches
from parallel_runner import run_cells_parallel, worker_cap
from science_gates import append_ledger, cutoff_meta, g1_prime_v2

import ew6_portfolio as W
from ew6_portfolio import (anchor_checks, bear_series, corr_block,
                           g1_clauses, self_test_portfolio_math,
                           yearly_returns)
import iv6_portfolio as V
from iv6_portfolio import (_init_worker, eval_port, iv_weights,
                           member_run_iv6, self_test_iv_math)

PREREG = os.path.join(PATHS.root, "research", "T27_BLEND_TOURNAMENT.md")
IV6_JSON = os.path.join(PATHS.results_dir, "portfolio_iv6.json")
OUT_JSON = os.path.join(PATHS.results_dir, "portfolio_blend_tournament.json")
ATTRITION_JSON = os.path.join(PATHS.results_dir, "gate_attrition.json")
CSV_PATH = os.path.join(PATHS.root, "research", "shortline",
                        "t27_results.csv")
LOG_PATH = os.path.join(PATHS.root, "logs", "iteration-loop",
                        "t27_tournament.log")
BATCH = "T27-blend-tournament"
BATCH_CELLS = 42          # frozen prereg s3/s4 (12 engine + 10 frame + 20 seg)
TOL = 1e-9                # twin-gate tolerance (deterministic engine)
CRASH_YEAR = -0.30
MAX_WORKERS = 12          # polite cap; worker_cap() RAM guard still applies
METHODS = ("A_IV", "B_MAXDIV", "C_IVMOM", "D_REGIME", "E_EW")


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


# ---------------------------------------------------------- weight rules

def _proj_simplex(v: np.ndarray) -> np.ndarray:
    """Euclidean projection onto the probability simplex (deterministic)."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u) - 1.0
    rho = np.nonzero(u * np.arange(1, len(v) + 1) > css)[0]
    if len(rho) == 0:
        theta = css[-1] / len(v)
    else:
        theta = css[rho[-1]] / (rho[-1] + 1)
    return np.maximum(v - theta, 0.0)


def _div_ratio(w: np.ndarray, sigma: np.ndarray, cov: np.ndarray) -> float:
    q = float(w @ cov @ w)
    return float(w @ sigma) / np.sqrt(q) if q > 0 else 0.0


def mdp_weights(rets_is: pd.DataFrame) -> dict:
    """B. Maximum diversification (prereg s3): closed form w ~ Sigma^-1 sigma;
    long-only violation -> deterministic projected-gradient ascent (2000
    iterations, step 0.005, EW init, best-seen tracked)."""
    sigma = rets_is.std().values
    cov = rets_is.cov().values
    tids = list(rets_is.columns)
    w_raw = np.linalg.solve(cov, sigma)
    dr_ew = _div_ratio(np.full(len(tids), 1.0 / len(tids)), sigma, cov)
    if (w_raw > 0).all():
        w = w_raw / w_raw.sum()
        path = "closed_form"
    else:
        w = np.full(len(tids), 1.0 / len(tids))
        best_w, best_dr = w.copy(), _div_ratio(w, sigma, cov)
        step = 0.005
        for _ in range(2000):
            q = float(w @ cov @ w)
            if q <= 0:
                break
            grad = sigma / np.sqrt(q) - float(w @ sigma) * (cov @ w) / (q ** 1.5)
            w = _proj_simplex(w + step * grad)
            dr = _div_ratio(w, sigma, cov)
            if dr > best_dr:
                best_w, best_dr = w.copy(), dr
        w = best_w
        path = "pg_fallback_local_optimum"
    return {"weights": {t: round(float(x), 6) for t, x in zip(tids, w)},
            "sum": round(float(w.sum()), 6), "solver_path": path,
            "dr_solution": round(_div_ratio(w, sigma, cov), 6),
            "dr_ew_baseline": round(dr_ew, 6)}


def ivmom_weights(sleeves: dict) -> dict:
    """C. Inverse-vol x momentum hybrid (prereg s3): raw_i = (1/sigma_i,IS)
    * (1 + m_i), m_i = IS-segment cumulative return of member x1 sleeve;
    clamp raw >= 0; EW fallback if the raw vector sums to <= 0."""
    raw, vol, mom = {}, {}, {}
    for tid, s in sleeves.items():
        eq = s["x1"]["eq_s"]
        is_eq = eq[eq.index < pd.Timestamp(OOS_START)]
        r = is_eq.pct_change().dropna()
        vol[tid] = round(float(r.std()), 6)
        mom[tid] = round(float(is_eq.iloc[-1] / is_eq.iloc[0] - 1.0), 6)
        raw[tid] = max(0.0, (1.0 / float(r.std())) * (1.0 + mom[tid]))
    total = sum(raw.values())
    if total <= 0:
        w = {tid: round(1.0 / len(raw), 6) for tid in raw}
        path = "ew_fallback_zero_raw"
    else:
        w = {tid: round(v / total, 6) for tid, v in raw.items()}
        path = "ivmom"
    return {"weights": w, "sum": round(sum(w.values()), 6), "path": path,
            "is_vol": vol, "is_momentum": mom,
            "raw": {k: round(v, 8) for k, v in raw.items()}}


def sharpe_offensive_weights(sleeves: dict) -> dict:
    """D offensive vector (prereg s3): w_i ~ max(S_i, 0), S_i = member x1
    sleeve IS-segment Sharpe; EW fallback if no positive Sharpe remains."""
    s_is = {tid: float(s["x1"]["is"]["sharpe"]) for tid, s in sleeves.items()}
    raw = {tid: max(v, 0.0) for tid, v in s_is.items()}
    total = sum(raw.values())
    if total <= 0:
        w = {tid: round(1.0 / len(raw), 6) for tid in raw}
        path = "ew_fallback_no_positive_sharpe"
    else:
        w = {tid: round(v / total, 6) for tid, v in raw.items()}
        path = "is_sharpe_proportional"
    return {"weights": w, "sum": round(sum(w.values()), 6), "path": path,
            "is_sharpe": {k: round(v, 4) for k, v in s_is.items()}}


def daily_ret_matrix(sleeves: dict, key: str) -> pd.DataFrame:
    eqs = pd.concat({tid: sleeves[tid][key]["eq_s"] for tid in sleeves},
                    axis=1, join="inner").dropna()
    return eqs.pct_change().dropna()


# ---------------------------------------------------------- frame + gates

def _guard_weights(weights: dict, columns) -> None:
    if set(weights) != set(columns):
        raise ValueError(f"weight/column key mismatch: "
                         f"{sorted(set(weights) ^ set(columns))}")


def _weight_matrix(R: pd.DataFrame, static_w: dict | None,
                   regime_w: dict | None, bear: pd.Series | None) -> pd.DataFrame:
    cols = list(R.columns)
    if static_w is not None:
        _guard_weights(static_w, cols)
        return pd.DataFrame([static_w] * len(R), index=R.index, columns=cols)
    d, o = regime_w["defensive"], regime_w["offensive"]
    _guard_weights(d, cols)
    _guard_weights(o, cols)
    s_prev = bear.reindex(R.index, method="ffill").shift(1).fillna(False)
    return pd.DataFrame([d if b else o for b in s_prev], index=R.index,
                        columns=cols)


def _frame_returns(R: pd.DataFrame, static_w: dict | None = None,
                   regime_w: dict | None = None,
                   bear: pd.Series | None = None) -> pd.Series:
    """Daily-rebalanced portfolio return series (v2 CI input)."""
    return (R * _weight_matrix(R, static_w, regime_w, bear)).sum(axis=1)


def eval_frame(R: pd.DataFrame, K: dict, member_s: dict, n_tr_sum: int,
               n_ent_sum: int, static_w: dict | None = None,
               regime_w: dict | None = None, bear: pd.Series | None = None):
    """Uniform daily-rebalanced evaluation frame (prereg s3). Exactly one of
    static_w (A/B/C/E) or regime_w={defensive,offensive} (D) is supplied."""
    W_df = _weight_matrix(R, static_w, regime_w, bear)
    port_ret = (R * W_df).sum(axis=1)
    equity = (1.0 + port_ret).cumprod()
    is_part = equity[equity.index < pd.Timestamp(OOS_START)]
    yr = yearly_returns(equity)
    w_mean = {t: round(float(x), 6) for t, x in W_df.mean().items()}
    wms = sum(w_mean[t] * member_s[t] for t in w_mean)
    full = seg_metrics(equity)
    is2 = seg_metrics(equity, OOS_START)
    out = {
        "full": full, "is": seg_metrics(is_part), "is2": is2,
        "yearly": yr, "worst_year": min(yr.values()) if yr else None,
        "n_trades": n_tr_sum, "n_entries": n_ent_sum,
        "weights_mean": w_mean,
        "port_ret_head": [round(float(x), 6) for x in port_ret.iloc[:3]],
    }
    if "sharpe" not in full or "sharpe" not in is2:
        # F4 honesty path (short synthetic frames in selftest only)
        out.update({"weighted_mean_member_sharpe": None, "benefit": None,
                    "dr": None, "clauses": None})
        return out
    out["weighted_mean_member_sharpe"] = round(wms, 4)
    out["benefit"] = round(full["sharpe"] - wms, 4)
    out["dr"] = round(full["sharpe"] / wms, 4) if wms else None
    out["clauses"] = g1_clauses({"full": full, "is2": is2}, n_tr_sum, K)
    return out


def _regime_slices(port_ret: pd.Series, bear: pd.Series) -> dict:
    s_same = bear.reindex(port_ret.index, method="ffill").fillna(False)

    def _sl(rr):
        if len(rr) < 10 or rr.std() == 0:
            return {"n_days": int(len(rr)), "sharpe": None,
                    "ann_return": None}
        return {"n_days": int(len(rr)),
                "sharpe": round(float(rr.mean() / rr.std() * 252 ** 0.5), 4),
                "ann_return": round(float((1 + rr).prod()
                                          ** (252 / len(rr)) - 1), 4)}

    return {"bear_days": _sl(port_ret[s_same]),
            "normal_days": _sl(port_ret[~s_same])}


def twin_gate(sleeves: dict, corr: dict, anchors: dict, rec: dict,
              K: dict, member_s: dict, n_tr_sum: int, n_ent_sum: int) -> dict:
    """Twin determinism leg vs portfolio_iv6.json (prereg s2 gate 2)."""
    mem = {}
    for tid, m in rec["members"].items():
        r1, r2 = sleeves[tid]["x1"], sleeves[tid]["x2"]
        mem[tid] = {
            "cutoff": str(m["cutoff"]) == str(r1["cutoff"]),
            "n_entries": int(m["n_entries"]) == int(r1["n_entries"]),
            "x1_full_s": abs(float(m["x1"]["full"]["sharpe"])
                             - float(r1["full"]["sharpe"])) < TOL,
            "x1_is_s": abs(float(m["x1"]["is"]["sharpe"])
                           - float(r1["is"]["sharpe"])) < TOL,
            "x1_is2_s": abs(float(m["x1"]["is2"]["sharpe"])
                            - float(r1["is2"]["sharpe"])) < TOL,
            "x1_n_trades": int(m["x1"]["n_trades"]) == int(r1["n_trades"]),
            "x1_oos_trades": int(m["x1"]["oos_trades"])
                             == int(r1["oos_trades"]),
            "x2_full_s": abs(float(m["x2"]["full"]["sharpe"])
                             - float(r2["full"]["sharpe"])) < TOL,
            "x2_is2_s": abs(float(m["x2"]["is2"]["sharpe"])
                            - float(r2["is2"]["sharpe"])) < TOL,
            "x2_n_trades": int(m["x2"]["n_trades"]) == int(r2["n_trades"]),
            "x2_n_entries": int(m["x2"]["n_entries"]) == int(r2["n_entries"]),
        }
    corr_ok = {seg: abs(float(rec["correlation"][seg]["avg_pairwise"])
                       - float(corr[seg]["avg_pairwise"])) < TOL
               for seg in ("full", "is", "is2")}
    ew_w = {tid: round(1.0 / len(sleeves), 6) for tid in sleeves}
    ew_repro = {}
    for mult, key in ((1, "x1"), (2, "x2")):
        ew_repro[key] = eval_port(
            {tid: sleeves[tid][key]["eq_s"] for tid in sleeves}, ew_w,
            "EW-repro", mult, member_s, n_tr_sum, n_ent_sum, K)
    ew_repro["x1"]["x2_survive"] = bool(
        ew_repro["x2"]["full"]["sharpe"] > K["vi_bar"]
        and ew_repro["x2"]["is2"]["sharpe"] > 0)
    iv = iv_weights(sleeves)
    iv_repro = {}
    for mult, key in ((1, "x1"), (2, "x2")):
        iv_repro[key] = eval_port(
            {tid: sleeves[tid][key]["eq_s"] for tid in sleeves},
            iv["weights"], "IV-repro", mult, member_s, n_tr_sum, n_ent_sum, K)
    iv_repro["x1"]["x2_survive"] = bool(
        iv_repro["x2"]["full"]["sharpe"] > K["vi_bar"]
        and iv_repro["x2"]["is2"]["sharpe"] > 0)

    def _legs(repro: dict, rec_block: dict) -> dict:
        q1, q2 = rec_block["x1"], rec_block["x2"]
        p1, p2 = repro["x1"], repro["x2"]
        return {
            "x1_full_s": abs(float(q1["full"]["sharpe"])
                             - float(p1["full"]["sharpe"])) < TOL,
            "x1_ann": abs(float(q1["full"]["annual_return"])
                          - float(p1["full"]["annual_return"])) < TOL,
            "x1_dd": abs(float(q1["full"]["max_drawdown"])
                         - float(p1["full"]["max_drawdown"])) < TOL,
            "x1_n_trades": int(q1["n_trades"]) == int(p1["n_trades"]),
            "x1_worst_year": abs(float(q1["worst_year"])
                                 - float(p1["worst_year"])) < TOL,
            "x1_benefit": abs(float(q1["benefit"])
                              - float(p1["benefit"])) < TOL,
            "x1_dr": abs(float(q1["dr"]) - float(p1["dr"])) < TOL,
            "x2_full_s": abs(float(q2["full"]["sharpe"])
                             - float(p2["full"]["sharpe"])) < TOL,
            "x2_is2_s": abs(float(q2["is2"]["sharpe"])
                            - float(p2["is2"]["sharpe"])) < TOL,
            "x2_survive": bool(q1["x2_survive"]) == bool(p1["x2_survive"]),
        }

    ew_leg = _legs(ew_repro, rec["ew_repro"])
    iv_leg = _legs(iv_repro, rec["portfolios_iv"])
    iv_w_ok = {t: abs(float(rec["iv_weights"]["weights"][t])
                      - float(iv["weights"][t])) < TOL
               for t in iv["weights"]}
    anchors_ok = all(a["anchor_ok"] and a["x2_ok"] for a in anchors.values())
    ok = (all(all(v.values()) for v in mem.values())
          and all(corr_ok.values()) and all(ew_leg.values())
          and all(iv_leg.values()) and all(iv_w_ok.values()) and anchors_ok)
    return {"ok": bool(ok), "members": mem, "corr": corr_ok,
            "ew_repro_leg": ew_leg, "iv_repro_leg": iv_leg,
            "iv_weights_ok": iv_w_ok, "anchors_ok": anchors_ok,
            "ew_repro": {k: {kk: vv for kk, vv in q.items()
                             if kk != "equity"}
                         for k, q in ew_repro.items()},
            "iv_repro": {k: {kk: vv for kk, vv in q.items()
                             if kk != "equity"}
                         for k, q in iv_repro.items()},
            "iv_weights_computed": iv}


# ---------------------------------------------------------- selftest

def self_test_t27() -> bool:
    ok = True
    n = 200
    idx = pd.bdate_range("2024-01-01", periods=n)
    # --- B closed form: Walsh-orthogonal deterministic pair, sigma 1:2
    #     -> exact weights (2/3, 1/3); no sampling noise (J18 fixture law)
    a = pd.Series([0.01 if k % 2 == 0 else -0.01 for k in range(n)], index=idx)
    b = pd.Series([0.02 if (k // 2) % 2 == 0 else -0.02 for k in range(n)],
                  index=idx)
    b_ret = mdp_weights(pd.DataFrame({"A": a, "B": b}))
    ok &= b_ret["solver_path"] == "closed_form"
    ok &= abs(b_ret["weights"]["A"] - 2.0 / 3.0) < 1e-6
    ok &= abs(b_ret["weights"]["B"] - 1.0 / 3.0) < 1e-6
    ok &= b_ret["dr_solution"] > b_ret["dr_ew_baseline"]
    # --- B fallback: A = 2*B + epsilon (pure redundancy, higher vol) ->
    #     closed form has a negative component; fallback keeps simplex +
    #     DR>=EW + deterministic
    rng = np.random.default_rng(7)
    base = rng.normal(0, 0.01, n)
    rB = pd.Series(0.01 * base + rng.normal(0, 0.00005, n), index=idx)
    rA = 2.0 * rB + pd.Series(rng.normal(0, 0.00001, n), index=idx)
    rC = pd.Series(rng.normal(0, 0.0002, n), index=idx)
    fb = mdp_weights(pd.DataFrame({"A": rA, "B": rB, "C": rC}))
    ok &= fb["solver_path"] == "pg_fallback_local_optimum"
    ok &= all(v >= 0 for v in fb["weights"].values())
    ok &= abs(sum(fb["weights"].values()) - 1.0) < 1e-6
    ok &= fb["dr_solution"] >= fb["dr_ew_baseline"] - 1e-9
    fb2 = mdp_weights(pd.DataFrame({"A": rA, "B": rB, "C": rC}))
    ok &= fb2["weights"] == fb["weights"]
    # --- C formula identity: mirror the function's own windowing exactly
    eq_a = (1.0 + a).cumprod()
    eq_b = (1.0 + b).cumprod()
    sl = {"A": {"x1": {"eq_s": eq_a}}, "B": {"x1": {"eq_s": eq_b}}}
    c = ivmom_weights(sl)
    is_a = eq_a[eq_a.index < pd.Timestamp(OOS_START)]
    is_b = eq_b[eq_b.index < pd.Timestamp(OOS_START)]
    vol_a = float(is_a.pct_change().dropna().std())
    vol_b = float(is_b.pct_change().dropna().std())
    m_a = float(is_a.iloc[-1] / is_a.iloc[0] - 1.0)
    m_b = float(is_b.iloc[-1] / is_b.iloc[0] - 1.0)
    raw_a = max(0.0, (1.0 / vol_a) * (1.0 + m_a))
    raw_b = max(0.0, (1.0 / vol_b) * (1.0 + m_b))
    ok &= abs(c["weights"]["A"] - raw_a / (raw_a + raw_b)) < 1e-6
    ok &= abs(sum(c["weights"].values()) - 1.0) < 2e-6
    # --- D offensive: Sharpe-proportional + zero-positive fallback
    sl2 = {"A": {"x1": {"is": {"sharpe": 0.9}}},
           "B": {"x1": {"is": {"sharpe": 0.3}}},
           "C": {"x1": {"is": {"sharpe": -0.2}}}}
    o = sharpe_offensive_weights(sl2)
    ok &= abs(o["weights"]["A"] - 0.75) < 1e-6
    ok &= abs(o["weights"]["B"] - 0.25) < 1e-6
    ok &= o["weights"]["C"] == 0.0
    sl3 = {t: {"x1": {"is": {"sharpe": -1.0}}} for t in ("A", "B")}
    ok &= (sharpe_offensive_weights(sl3)["path"]
           == "ew_fallback_no_positive_sharpe")
    # --- D causality: state flip lands on t+1; first day defaults normal
    days = pd.bdate_range("2024-01-02", periods=4)
    R = pd.DataFrame({"A": [0.01, 0.02, -0.01, 0.01],
                      "B": [-0.01, 0.01, 0.02, -0.02]}, index=days)
    bear = pd.Series([False, False, True, True], index=days)
    K0 = {"i_bar": 0.0, "vi_bar": 0.0, "dd_min": -1.0, "trades_min": 1}
    fr = eval_frame(R, K0, {"A": 1.0, "B": 1.0}, 30, 30,
                    regime_w={"defensive": {"A": 1.0, "B": 0.0},
                              "offensive": {"A": 0.0, "B": 1.0}},
                    bear=bear)
    exp = [R["B"].iloc[0], R["B"].iloc[1], R["B"].iloc[2], R["A"].iloc[3]]
    ok &= all(abs(g - e) < 1e-12 for g, e in zip(fr["port_ret_head"],
                                                 exp[:3]))
    full_ret = _frame_returns(R, None,
                              {"defensive": {"A": 1.0, "B": 0.0},
                               "offensive": {"A": 0.0, "B": 1.0}}, bear)
    ok &= all(abs(float(full_ret.iloc[i]) - exp[i]) < 1e-12
              for i in range(4))
    # --- E identity: EW frame == row-mean of returns
    fe = eval_frame(R, K0, {"A": 1.0, "B": 1.0}, 30, 30,
                    static_w={"A": 0.5, "B": 0.5})
    ok &= all(abs(g - float(R.iloc[i].mean())) < 1e-12
              for i, g in enumerate(fe["port_ret_head"]))
    # --- JSON-face fixture law (machine pitfall #1): str keys survive a
    #     JSON round-trip; the column guard RAISES on mismatch (no silent
    #     empty-set pass-through)
    w_json = json.loads(json.dumps({"A": 0.5, "B": 0.5}))
    _guard_weights(w_json, ["A", "B"])
    try:
        _guard_weights({"A": 0.5}, ["A", "B"])
        ok = False
    except ValueError:
        pass
    return bool(ok)


# ---------------------------------------------------------- main

def run_batch() -> int:
    t0 = time.time()
    log(f"{BATCH} start (prereg frozen; cells={BATCH_CELLS})")
    if not self_test_patches():
        log("patch self-test FAILED -- abort"); return 2
    if not self_test_portfolio_math():
        log("portfolio-math self-test FAILED -- abort"); return 2
    if not self_test_iv_math():
        log("IV-math self-test FAILED -- abort"); return 2
    if not self_test_t27():
        log("t27-math self-test FAILED -- abort"); return 2
    log("patch + portfolio-math + iv-math + t27-math self-tests: PASS")

    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"),
              encoding="utf-8") as fh:
        calib = json.load(fh)
    g = calib["g1_prime_gate"]
    K = {"i_bar": g["i_full_sharpe_gt"], "vi_bar": g["vi_full_sharpe_gt"],
         "dd_min": g["iii_dd_min"], "trades_min": g["iv_trades_min"]}
    with open(IV6_JSON, encoding="utf-8") as fh:
        rec = json.load(fh)
    cutoff_rec = max(m["cutoff"] for m in rec["members"].values())

    tids = sorted(p.stem for p in TRADERS_DIR.glob("*.json")
                  if not p.name.startswith("_"))
    if set(tids) != set(rec["members"]):
        log("ROSTER DRIFT vs IV6 record -- batch void")
        return write_outputs(K, tids, None, None, None, None, None, None,
                             None, None, 0, t0, cutoff=cutoff_rec,
                             void=True, void_reason="roster_drift_vs_iv6")
    log(f"members ({len(tids)}): {tids}")

    # ---------- sleeves (12 engine cells, anchor-cum-sleeve reuse) ----------
    jobs = [(f"{tid}|{mult}", member_run_iv6, (tid, mult))
            for tid in tids for mult in (None, 2)]
    res = run_cells_parallel(jobs, workers=min(worker_cap(), MAX_WORKERS),
                             desc="t27-sleeves", initializer=_init_worker)
    workers = int(res.pop("__workers__"))
    sleeves = {}
    for tid in tids:
        r1, r2 = res[f"{tid}|None"], res[f"{tid}|2"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
        log(f"  {tid:<16} x1 full_s={r1['full']['sharpe']:>7.4f} "
            f"entries={r1['n_entries']:<4} | x2 full_s="
            f"{r2['full']['sharpe']:>7.4f}")
    cutoff = max(sleeves[t]["x1"]["cutoff"] for t in tids)

    traders = {tid: load_trader(tid) for tid in tids}
    anchors = {tid: anchor_checks(traders[tid], sleeves[tid]["x1"],
                                  sleeves[tid]["x2"]) for tid in tids}

    norm1 = pd.concat({tid: sleeves[tid]["x1"]["eq_s"] /
                       sleeves[tid]["x1"]["eq_s"].iloc[0] for tid in tids},
                      axis=1, join="inner").dropna()
    rets1 = norm1.pct_change().dropna()
    is2_mask = rets1.index >= pd.Timestamp(OOS_START)
    corr = {"full": corr_block(rets1), "is": corr_block(rets1, ~is2_mask),
            "is2": corr_block(rets1, is2_mask)}

    member_s = {tid: sleeves[tid]["x1"]["full"]["sharpe"] for tid in tids}
    n_tr_sum = sum(sleeves[tid]["x1"]["n_trades"] for tid in tids)
    n_ent_sum = sum(sleeves[tid]["x1"]["n_entries"] for tid in tids)

    tw = twin_gate(sleeves, corr, anchors, rec, K, member_s, n_tr_sum,
                   n_ent_sum)
    log(f"twin gate vs portfolio_iv6.json: {'PASS' if tw['ok'] else 'FAIL'}")
    if not tw["ok"]:
        log("TWIN GATE BROKEN (data drift since IV6) -- batch void")
        return write_outputs(K, tids, sleeves, anchors, corr, tw, None,
                             None, None, None, workers, t0, cutoff=cutoff,
                             void=True, void_reason="twin_gate_drift_vs_iv6")

    # ---------- regime single-source consistency (EW6 s2.8 pattern) ----------
    bench = load_benchmark_close()
    bear = bear_series(bench)
    st_last = major_bear_state(bench)
    cons_ok = (bool(bear.iloc[-1]) == st_last["is_major_bear"]
               and bool(bench.iloc[-1] < bench.rolling(MA_WINDOW)
                        .mean().iloc[-1]) == st_last["below_ma250"])
    log(f"regime consistency gate: {'PASS' if cons_ok else 'FAIL'} "
        f"(bear={st_last['is_major_bear']})")
    if not cons_ok:
        return write_outputs(K, tids, sleeves, anchors, corr, tw, None,
                             None, None, st_last, workers, t0,
                             cutoff=cutoff, void=True,
                             void_reason="regime_source_mismatch")

    # ---------- frozen weight rules (IS-segment only, causal) ----------
    R1 = daily_ret_matrix(sleeves, "x1")
    R2 = daily_ret_matrix(sleeves, "x2")
    R1_is = R1[R1.index < pd.Timestamp(OOS_START)]
    wA = iv_weights(sleeves)
    wB = mdp_weights(R1_is)
    wC = ivmom_weights(sleeves)
    wE = {tid: round(1.0 / len(tids), 6) for tid in tids}
    wD_off = sharpe_offensive_weights(sleeves)
    log(f"weights A(IV)={wA['weights']}")
    log(f"weights B(MAXDIV path={wB['solver_path']} dr={wB['dr_solution']} "
        f"vs EW {wB['dr_ew_baseline']}) {wB['weights']}")
    log(f"weights C(IVMOM path={wC['path']}) {wC['weights']}")
    log(f"weights D(offensive path={wD_off['path']}) {wD_off['weights']}")

    statics = {"A_IV": wA["weights"], "B_MAXDIV": wB["weights"],
               "C_IVMOM": wC["weights"], "E_EW": wE}
    regime_w = {"defensive": wA["weights"], "offensive": wD_off["weights"]}

    cands = {}
    for name in METHODS:
        cands[name] = {}
        for r_mat, key in ((R1, "x1"), (R2, "x2")):
            if name == "D_REGIME":
                cands[name][key] = eval_frame(
                    r_mat, K, member_s, n_tr_sum, n_ent_sum,
                    regime_w=regime_w, bear=bear)
            else:
                cands[name][key] = eval_frame(
                    r_mat, K, member_s, n_tr_sum, n_ent_sum,
                    static_w=statics[name])
        p, px = cands[name]["x1"], cands[name]["x2"]
        p["x2_survive"] = bool(px["full"]["sharpe"] > K["vi_bar"]
                               and px["is2"]["sharpe"] > 0)
        p["robust"] = {"is_sharpe_pos": bool(p["is"]["sharpe"] > 0),
                       "worst_year_ok": bool(p["worst_year"] > CRASH_YEAR)}
        p["v2"] = g1_prime_v2(
            p["full"]["sharpe"],
            _frame_returns(R1, None if name == "D_REGIME"
                           else statics[name], regime_w, bear),
            batch_cells=BATCH_CELLS, n_trades=n_tr_sum, n_entries=n_ent_sum)
        p["eligible"] = bool(
            all(p["clauses"].values()) and p["benefit"] > 0
            and (p["dr"] or 0) > 1 and p["x2_survive"]
            and all(p["robust"].values()) and p["v2"]["pass_v2"])
        log(f"  {name:<10} x1 full_s={p['full']['sharpe']:>7.4f} "
            f"benefit={p['benefit']:>7.4f} DR={p['dr']} "
            f"dd={p['full']['max_drawdown']} | x2 full_s="
            f"{px['full']['sharpe']:>7.4f} survive={p['x2_survive']} "
            f"v2={p['v2']['pass_v2']} -> eligible={p['eligible']}")
    # segment cells (frozen ledger composition: 5 methods x 4 windows)
    seg_cells = {name: _regime_slices(_frame_returns(
        R1, None if name == "D_REGIME" else statics[name], regime_w, bear),
        bear) for name in METHODS}

    # ---------- three faces + median-rank winner (frozen s4) ----------
    faces = {}
    for name in METHODS:
        p = cands[name]["x1"]
        faces[name] = {"benefit": p["benefit"],
                       "drawdown": p["full"]["max_drawdown"],
                       "x2_margin": round(cands[name]["x2"]["full"]["sharpe"]
                                          - K["vi_bar"], 4)}
    elig = [n for n in METHODS if cands[n]["x1"]["eligible"]]
    ranks = {f: sorted(elig, key=lambda n: -faces[n][f])
             for f in ("benefit", "drawdown", "x2_margin")} if elig else {}

    def med_rank(nm):
        r = [ranks[f].index(nm) for f in ("benefit", "drawdown", "x2_margin")]
        return (sorted(r)[1], ranks["benefit"].index(nm))

    winner = sorted(elig, key=med_rank)[0] if elig else None
    log(f"eligible={elig} winner={winner}")

    # candidate return corr (descriptive, prereg s1)
    pret = {n: _frame_returns(R1, None if n == "D_REGIME" else statics[n],
                             regime_w, bear) for n in METHODS}
    cand_corr = pd.concat(pret, axis=1).corr()

    verdict = {
        "template": "T27 tournament (prereg s4): winner = proposed paper-"
                    "canon blend method, GM ratify + 7-day veto pending; "
                    "adoption NOT wired in this batch",
        "eligible": elig,
        "winner": winner,
        "faces": faces,
        "ranks": {f: {nm: ranks[f].index(nm) for nm in ranks[f]}
                  for f in ranks},
        "segment_cells": seg_cells,
        "no_winner_action": "IV canon retained (frozen s4)",
    }
    weights_out = {"A_IV": wA, "B_MAXDIV": wB, "C_IVMOM": wC,
                   "D_REGIME": {"defensive": wA["weights"],
                                "offensive": wD_off},
                   "E_EW": {"weights": wE}}
    return write_outputs(K, tids, sleeves, anchors, corr, tw, cands,
                         verdict, cand_corr, st_last, workers, t0,
                         cutoff=cutoff, weights=weights_out)


def write_outputs(K, tids, sleeves, anchors, corr, tw, cands, verdict,
                  cand_corr, st_last, workers, t0, cutoff=None, void=False,
                  void_reason=None, weights=None):
    ledger = append_ledger(
        BATCH, BATCH_CELLS,
        file_name="results/portfolio_blend_tournament.json",
        evidence_cutoff=cutoff or "unknown",
        note="12 engine member runs (anchor-cum-sleeve, x1+x2, IV6-identical "
             "cells) + 10 ranking-frame portfolio evaluations (5 methods x 2 "
             "cost faces, daily-rebalanced) + 20 window/segment cells "
             "(5 methods x IS/IS2/bear/normal); zero search, zero new signal "
             "functions => zero nulls (composition disclosed, prereg s3); "
             "twin-gate re-derivations and v2 readouts are gates/disclosures, "
             "not ledger cells")
    prereg_sha = hashlib.sha256(open(PREREG, "rb").read()).hexdigest()

    rows = []
    if cands:
        for name in METHODS:
            for key in ("x1", "x2"):
                p = cands[name][key]
                rows.append({"method": name, "cost_mult": key,
                             "full_sharpe": p["full"].get("sharpe"),
                             "full_ann": p["full"].get("annual_return"),
                             "full_dd": p["full"].get("max_drawdown"),
                             "is_sharpe": p["is"].get("sharpe"),
                             "is2_sharpe": p["is2"].get("sharpe"),
                             "benefit": p.get("benefit"),
                             "dr": p.get("dr"),
                             "worst_year": p.get("worst_year"),
                             "n_trades": p.get("n_trades"),
                             "n_entries": p.get("n_entries")})
    cols = ["method", "cost_mult", "full_sharpe", "full_ann", "full_dd",
            "is_sharpe", "is2_sharpe", "benefit", "dr", "worst_year",
            "n_trades", "n_entries"]
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])
    log(f"saved: {CSV_PATH} ({len(rows)} rows)")

    out = {
        "batch": BATCH,
        "task": "T-2026-09-24-27 blend-method tournament (O-20260924-1702)",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/T27_BLEND_TOURNAMENT.md",
        "prereg_sha256_at_run": prereg_sha,
        "void": void, "void_reason": void_reason,
        "universe": {"pool": "core48-bare-codes",
                     "members": list(tids),
                     "member_cutoffs": ({t: sleeves[t]["x1"]["cutoff"]
                                         for t in tids} if sleeves else None)},
        "oos_start": OOS_START,
        "members": ({t: {"cutoff": sleeves[t]["x1"]["cutoff"],
                        "n_entries": sleeves[t]["x1"]["n_entries"],
                        "x1": {k: sleeves[t]["x1"][k] for k in
                               ("full", "is", "is2", "n_trades",
                                "oos_trades")},
                        "x2": {k: sleeves[t]["x2"][k] for k in
                               ("full", "is2", "n_trades", "n_entries")}}
                     for t in tids} if sleeves else None),
        "anchors": anchors,
        "correlation": corr,
        "twin_gate_vs_iv6": ({k: v for k, v in tw.items()
                              if k in ("ok", "members", "corr",
                                       "ew_repro_leg", "iv_repro_leg",
                                       "iv_weights_ok", "anchors_ok")}
                             if tw else None),
        "twin_reproductions": ({k: tw[k] for k in
                                ("ew_repro", "iv_repro",
                                 "iv_weights_computed")} if tw else None),
        "weights": weights,
        "candidates": ({n: {key: {k: v for k, v in cands[n][key].items()}
                            for key in ("x1", "x2")} for n in cands}
                       if cands else None),
        "candidate_return_corr": (cand_corr.round(4).to_dict()
                                   if cand_corr is not None else None),
        "regime_state_latest": st_last,
        "verdict": verdict,
        "trials_ledger": ledger,
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": 0 if sleeves is None else 2 * len(tids),
                  "n_frame_evals": 0 if cands is None else 10,
                  "n_segment_cells": 0 if cands is None else 20,
                  "batch_cells_ledger": BATCH_CELLS,
                  "workers": workers,
                  "parallel": f"parallel_runner ProcessPool workers={workers}"},
    }
    if cutoff:
        out.update(cutoff_meta(cutoff))
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    log(f"saved: {OUT_JSON}")

    # gate_attrition entry (science_audit C4; create-or-merge, dedupe)
    entry = {"batch": BATCH, "ts": out["generated"], "kind": "tournament",
             "cells_ledger_delta": BATCH_CELLS,
             "ledger_total_after": int(ledger["total"]),
             "gates": {"void": void,
                       "eligible_count": 0 if not verdict else
                       len(verdict.get("eligible") or []),
                       "winner": None if not verdict else
                       verdict.get("winner")},
             "eliminated": None,
             "refs": {"results": "results/portfolio_blend_tournament.json",
                      "prereg": "research/T27_BLEND_TOURNAMENT.md"}}
    if os.path.exists(ATTRITION_JSON):
        with open(ATTRITION_JSON, encoding="utf-8") as fh:
            data = json.load(fh)
        data["entries"] = [e for e in data.get("entries", [])
                           if e.get("batch") != BATCH] + [entry]
    else:
        data = {"schema": "gate-attrition-ledger v1",
                "created": out["generated"],
                "purpose": "science_audit C4: per-batch gate-chain losses "
                           "account (s7-T retro mandatory)",
                "entries": [entry]}
    with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    log(f"saved: {ATTRITION_JSON} ({len(data['entries'])} entries)")

    if void:
        summary = f"VOID ({void_reason})"
    else:
        summary = f"winner={verdict['winner']} eligible={verdict['eligible']}"
    log(f"===== {BATCH} verdict: {summary} =====")
    log(f"elapsed={time.time() - t0:.0f}s ledger N={ledger['total']} "
        f"(prev={ledger['prev_total']})")
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        ok = (self_test_patches() and self_test_portfolio_math()
              and self_test_iv_math() and self_test_t27())
        print("selftest:", "ALL PASS" if ok else "FAIL")
        return 0 if ok else 2
    if mode == "status":
        if not os.path.exists(OUT_JSON):
            print("not run yet")
            return 0
        with open(OUT_JSON, encoding="utf-8") as fh:
            d = json.load(fh)
        print(f"void={d['void']} verdict={d['verdict']}")
        return 0
    if mode == "run":
        return run_batch()
    print(f"unknown mode: {mode}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
