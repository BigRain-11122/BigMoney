"""W8 freeze-round construction probe (INNOVATION_QUOTA_W8 draft sec.C step-1).

Measures the LW construction facts for COV-SHRINK-AB-P1 before prereg freeze:

- member face: t27 FROZEN_ROSTER 28 members verbatim, x1 sleeves via
  iv6_portfolio.member_run_iv6 (probe faces same as t27 run_batch x1 leg).
- LW implementation adjudication: sklearn NOT in requirements.txt
  (ModuleNotFoundError live-probed) -> hand-rolled Ledoit-Wolf 2004 JMV
  (mu*I related target), numpy verbatim, N = n-1 (pandas .cov() ddof=1
  consistent) -- implementation-level choice frozen this round, zero new
  dependency.
- A arm = t27 mdp_weights VERBATIM (import, sample cov).
- B arm = mdp body with the single cov= line parameterized to the LW-shrunk
  face (sigma unchanged; solve/PG machinery identical).
- static IS face (production B_MAXDIV mirror) + rolling 252d anchors at
  every-21td cadence over the full matrix.
- facts: shrinkage lambda, cond(sample) vs cond(shrunk), solver paths,
  max/L1 weight divergence, DR divergence.
- determinism: full fact table computed twice, SHA256(canonical json)
  compared (byte-identity gate).
- G-ANCHOR-FACE four-tuple (O-20260928-1712) for each anchor face below.

Read-only wrt repo state; writes results/_r449bmb_w8_probe.json only.
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
sys.path.insert(0, HERE)

from iv6_portfolio import member_run_iv6, _init_worker          # noqa: E402
from live.paper import OOS_START                                # noqa: E402
from t27_blend_tournament import (                              # noqa: E402
    FROZEN_ROSTER, _div_ratio, _proj_simplex, mdp_weights)

OUT = os.path.join(HERE, "_r449bmb_w8_probe.json")
ROLL = 252          # candidate rolling window (draft sec.C step-1)
CADENCE = 21        # candidate anchor cadence in trading days


def lw_shrink_cov(rets: pd.DataFrame) -> dict:
    """Ledoit-Wolf 2004 JMV shrinkage toward mu*I (related target).

    N = n-1 (pandas .cov() ddof=1 caliber). Norms are the paper's
    normalized Frobenius <A,A'> = trace(AA')/p. Returns shrunk cov,
    lambda, and intermediate intensities. Formula frozen verbatim here.
    """
    X = rets.values
    n, p = X.shape
    N = n - 1
    Xd = X - X.mean(axis=0)
    S = (Xd.T @ Xd) / N                     # == pandas rets.cov()
    mu = float(np.trace(S)) / p
    d2 = float(((S - mu * np.eye(p)) ** 2).sum()) / p
    # b_bar^2 = (1/N^2) * sum_k ||x_k x_k' - S||^2  (normalized norm /p)
    outer = Xd[:, :, None] * Xd[:, None, :]          # (n,p,p)
    diff = outer - S
    b_bar2 = float((diff ** 2).sum(axis=(1, 2)).sum()) / (p * N * N)
    b2 = min(b_bar2, d2)
    lam = b2 / d2 if d2 > 0 else 1.0
    shrunk = (1.0 - lam) * S + lam * mu * np.eye(p)
    return {"cov": shrunk, "S": S, "lam": float(lam), "mu": mu,
            "d2": d2, "b_bar2": b_bar2, "b2": b2, "n": n, "p": p}


def mdp_weights_cov(rets: pd.DataFrame, cov: np.ndarray) -> dict:
    """t27 mdp_weights body with the single cov input parameterized.

    Line-for-line mirror of scripts/t27_blend_tournament.py mdp_weights
    except `cov = rets_is.cov().values` -> caller-supplied cov face
    (sigma stays rets.std(); solve + PG machinery identical).
    """
    sigma = rets.std().values
    tids = list(rets.columns)
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


def _cond(a: np.ndarray) -> float:
    ev = np.linalg.eigvalsh(a)
    return float(ev.max() / ev.min()) if ev.min() > 0 else float("inf")


def arm_face(rets: pd.DataFrame) -> dict:
    lw = lw_shrink_cov(rets)
    try:
        A = mdp_weights(rets)
    except np.linalg.LinAlgError:
        # FREEZE FACT: rolling sample cov singular at this window --
        # A arm (production recipe verbatim) undefined; B arm (shrunk,
        # PD by construction) still computable -> honest disclosure row.
        B = mdp_weights_cov(rets, lw["cov"])
        return {"n": lw["n"], "p": lw["p"],
                "n_over_p": round(lw["n"] / lw["p"], 2),
                "lambda": round(lw["lam"], 6),
                "cond_sample": None,
                "cond_shrunk": round(_cond(lw["cov"]), 1),
                "solver_A": "SINGULAR_SAMPLE_COV",
                "solver_B": B["solver_path"],
                "max_wdiff": None, "l1_wdiff": None,
                "dr_A": None, "dr_B": B["dr_solution"],
                "dr_ew_A": B["dr_ew_baseline"]}
    B = mdp_weights_cov(rets, lw["cov"])
    wa = np.array([A["weights"][t] for t in rets.columns])
    wb = np.array([B["weights"][t] for t in rets.columns])
    return {"n": lw["n"], "p": lw["p"], "n_over_p": round(lw["n"] / lw["p"], 2),
            "lambda": round(lw["lam"], 6),
            "cond_sample": round(_cond(lw["S"]), 1),
            "cond_shrunk": round(_cond(lw["cov"]), 1),
            "solver_A": A["solver_path"], "solver_B": B["solver_path"],
            "max_wdiff": round(float(np.abs(wa - wb).max()), 6),
            "l1_wdiff": round(float(np.abs(wa - wb).sum()), 6),
            "dr_A": A["dr_solution"], "dr_B": B["dr_solution"],
            "dr_ew_A": A["dr_ew_baseline"]}


def _selfcheck_lw() -> list:
    """LW estimator invariants (hermetic): lambda in [0,1]; shrunk PSD;
    lambda -> 0 on huge-n IID face; d2>0 guard."""
    rng = np.random.default_rng(20285500)
    X = rng.normal(size=(500, 6)) * 0.01
    rets = pd.DataFrame(X, columns=[f"c{i}" for i in range(6)])
    lw = lw_shrink_cov(rets)
    ev = np.linalg.eigvalsh(lw["cov"]).min()
    Xs = rng.normal(size=(40, 6))
    lw_s = lw_shrink_cov(pd.DataFrame(Xs, columns=rets.columns))
    ok = [0 <= lw["lam"] <= 1, ev > 0, lw_s["lam"] >= 0, lw_s["d2"] > 0,
          abs(lw["mu"] - float(np.trace(lw["S"])) / 6) < 1e-15]
    return ok


def build_facts() -> dict:
    _init_worker()
    sleeves = {tid: member_run_iv6(tid, None) for tid in FROZEN_ROSTER}
    eqs = pd.concat({t: pd.Series(sleeves[t]["eq"],
                     index=pd.to_datetime(sleeves[t]["dates"])) for t in sleeves},
                    axis=1, join="inner").dropna()
    R = eqs.pct_change().dropna()
    cutoff = max(sleeves[t]["cutoff"] for t in sleeves)

    is_R = R[R.index < pd.Timestamp(OOS_START)]
    static_face = arm_face(is_R)

    anchors = []
    for end in range(ROLL, len(R), CADENCE):
        win = R.iloc[end - ROLL:end]
        f = arm_face(win)
        f["anchor_date"] = str(R.index[end - 1].date())
        f["window"] = f"{str(R.index[end - ROLL].date())}..{f['anchor_date']}"
        anchors.append(f)

    lam = [a["lambda"] for a in anchors]
    mw = [a["max_wdiff"] for a in anchors if a["max_wdiff"] is not None]
    n_sing = sum(1 for a in anchors
                 if a["solver_A"] == "SINGULAR_SAMPLE_COV")
    if n_sing:
        first_sing = next(a["anchor_date"] for a in anchors
                          if a["solver_A"] == "SINGULAR_SAMPLE_COV")
    else:
        first_sing = None
    return {"probe": "W8 LW construction freeze facts (draft sec.C step-1)",
            "roster_n": len(FROZEN_ROSTER), "matrix_shape": list(R.shape),
            "matrix_first": str(R.index[0].date()),
            "matrix_last": str(R.index[-1].date()), "cutoff": cutoff,
            "oos_start": str(OOS_START),
            "anchor_four_tuples": {
                "member_sleeve_matrix": {
                    "path": "firm/traders/*.json + data/daily core48 "
                            "(via iv6_portfolio.member_run_iv6)",
                    "loader": "iv6_portfolio.member_run_iv6(tid, None)",
                    "start_window": str(R.index[0].date()),
                    "warmup_window": "engine per-member signal warmup "
                                     "(in sleeves, not the cov window)"},
                "rolling_cov_window": {
                    "path": "member x1 eq curves pct-change matrix",
                    "loader": "this probe lw_shrink_cov/mdp_weights_cov",
                    "start_window": str(R.index[ROLL].date()),
                    "warmup_window": f"{ROLL} trailing trading days"}},
            "lw_implementation": "hand-rolled Ledoit-Wolf 2004 JMV "
                                 "(mu*I target), N=n-1 pandas ddof=1 "
                                 "consistent; sklearn absent from env",
            "lw_selfcheck": [bool(x) for x in _selfcheck_lw()],
            "roll_window": ROLL, "anchor_cadence_td": CADENCE,
            "n_anchors": len(anchors),
            "n_singular_A_windows": n_sing,
            "first_singular_anchor": first_sing,
            "lambda_stats": {"min": round(min(lam), 6),
                             "median": round(float(np.median(lam)), 6),
                             "max": round(max(lam), 6)},
            "max_wdiff_stats": {"n_valid": len(mw),
                                "min": round(min(mw), 6),
                                "median": round(float(np.median(mw)), 6),
                                "max": round(max(mw), 6)} if mw else None,
            "solver_paths_A": {p: sum(1 for a in anchors
                                      if a["solver_A"] == p)
                               for p in ("closed_form",
                                         "pg_fallback_local_optimum",
                                         "SINGULAR_SAMPLE_COV")},
            "solver_paths_B": {p: sum(1 for a in anchors
                                      if a["solver_B"] == p)
                               for p in ("closed_form",
                                         "pg_fallback_local_optimum")},
            "static_IS_face": static_face,
            "anchors": anchors}


def main() -> None:
    facts1 = build_facts()
    facts2 = build_facts()
    h1 = hashlib.sha256(json.dumps(facts1, sort_keys=True,
                                   ensure_ascii=False).encode()).hexdigest()
    h2 = hashlib.sha256(json.dumps(facts2, sort_keys=True,
                                   ensure_ascii=False).encode()).hexdigest()
    facts1["determinism_double_run_sha256_match"] = (h1 == h2)
    facts1["sha256_run1"] = h1[:16]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(facts1, f, ensure_ascii=False, indent=1)
    print("double_run_match:", h1 == h2)
    print("static_face:", json.dumps(facts1["static_IS_face"], indent=1))
    print("lambda_stats:", facts1["lambda_stats"])
    print("max_wdiff_stats:", facts1["max_wdiff_stats"])
    print("solver_A:", facts1["solver_paths_A"],
          "solver_B:", facts1["solver_paths_B"])
    print("n_anchors:", facts1["n_anchors"],
          "matrix:", facts1["matrix_shape"], facts1["matrix_first"],
          "..", facts1["matrix_last"])
    print("lw_selfcheck:", facts1["lw_selfcheck"])
    print("OUT:", OUT)


if __name__ == "__main__":
    main()
