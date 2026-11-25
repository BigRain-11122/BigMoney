"""Block bootstrap for the one GO: what range does its excess carry live in?

The GO reports IC +7.36pp and IM +3.64pp over always-on, with a circular-shift
permutation p=0.0000. Permutation answers "is the alignment real"; it does not
answer "how wide is the error bar". Daily carry is autocorrelated, so an iid
bootstrap would be too narrow. This uses a moving-block bootstrap (block = 20
sessions, ~2,500 resamples), which keeps the short-run dependence and gives a
confidence interval a reader can size money against.

This is deliberately CPU-bound: 2,500 x 2,400 x 2 products of vectorised work.
It is the kind of unit the CPU-fill agent should run when it has a free core.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import paper_basis_timing as paper  # noqa: E402

OUT = os.path.join(bc.RESULTS, "boot_basis_timing.json")
BLOCK = 20
REPS = 2500
SEED = 20261124
TZ = timezone(timedelta(hours=8))


def annualised(x):
    eq = float(np.cumprod(1.0 + x)[-1])
    years = len(x) / bc.TRADING_DAYS
    return (eq ** (1.0 / years) - 1.0) * 100 if years > 0 and eq > 0 else -100.0


def product_curves(code):
    dates, f, i = paper.series(code)
    basis = f / i - 1.0
    spread = np.diff(f) / f[:-1] - np.diff(i) / i[:-1]
    db = np.abs(np.diff(basis))
    scale = max(float(np.median(db)), 0.001) if len(db) else 0.001
    roll = np.array([x > 8.0 * scale and x > 0.005 for x in db])

    prev = None
    weighted, always, w_prev = [], [], 0.0
    for k in range(len(spread)):
        w = paper.weight_for(basis[:k + 2])
        cost_w = abs(w - w_prev) * paper.COST_BP_SIDE / 10000.0
        base_ret = 0.0 if roll[k] else spread[k]
        weighted.append((0.0 if roll[k] else w_prev * spread[k]) - cost_w)
        always.append(base_ret)
        w_prev = w
    return np.array(weighted), np.array(always)


def main():
    global REPS, BLOCK
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", type=int, default=BLOCK,
                    help="block length in sessions (robustness check)")
    ap.add_argument("--reps", type=int, default=REPS,
                    help="resamples; each unit of CPU work is a tighter interval")
    args = ap.parse_args()
    REPS = args.reps
    BLOCK = args.block
    rng = np.random.default_rng(SEED)
    out = {}
    for code in ("IC", "IM"):
        w_curve, a_curve = product_curves(code)
        n = len(w_curve)
        nb = int(np.ceil(n / BLOCK))
        d_obs = annualised(w_curve) - annualised(a_curve)
        diffs = np.empty(REPS)
        for r in range(REPS):
            starts = rng.integers(0, max(1, n - BLOCK), size=nb)
            idx = (starts[:, None] + np.arange(BLOCK)[None, :]).ravel()
            idx = idx[idx < n]
            diffs[r] = annualised(w_curve[idx]) - annualised(a_curve[idx])
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        out[code] = {
            "bars": int(n),
            "difference_pp": round(float(d_obs), 2),
            "boot_mean_pp": round(float(diffs.mean()), 2),
            "ci95_pp": [round(float(lo), 2), round(float(hi), 2)],
            "p_leq_zero": round(float((diffs <= 0).mean()), 4),
            "reps": REPS, "block": BLOCK,
            "verdict": ("CI_EXCLUDES_ZERO" if lo > 0 else "CI_INCLUDES_ZERO"),
        }
    payload = {
        "cell": "boot_basis_timing",
        "generated": datetime.now(TZ).isoformat(timespec="seconds"),
        "method": f"moving-block bootstrap, block={BLOCK} sessions, {REPS} resamples",
        "statistic": "annualised(weighted carry) - annualised(always-on carry)",
        "products": out,
        "verdict": ("BOTH_CI_EXCLUDE_ZERO"
                    if all(v["verdict"] == "CI_EXCLUDES_ZERO" for v in out.values())
                    else "AT_LEAST_ONE_CI_INCLUDES_ZERO"),
    }
    bc.write_json(OUT, payload)
    print(json.dumps({"ok": True, "verdict": payload["verdict"],
                      "per_product": {k: {"diff": v["difference_pp"], "ci": v["ci95_pp"],
                                          "p": v["p_leq_zero"]} for k, v in out.items()}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
