"""Closure for the basis-timing GO: is the sizing gain an alignment or a coincidence?

The GO in `bench_basis_timing_size` says weighting by the trailing percentile of
the discount beats holding always (+7.4pp/yr on IC, +3.7pp on IM). A gain that
size on ~2,400 days could be an artefact of the weight series' own
autocorrelation. The only honest test is to destroy the *alignment* while keeping
everything else: circular-shift the weight series by a random lag (so its
distribution, smoothness and turnover survive) and recompute the difference.

Statistic: D = annualised(weighted carry) - annualised(always-on carry).
Null: 5,000 circular shifts. p = share of null draws with D_null >= D_observed.
Verdict: SIGNIFICANT if p < 0.01 on both IC and IM; otherwise the GO is not
evidence and must be withdrawn.

This is deliberately CPU-bound (5,000 x 2,400 x 2) because it is the kind of work
that *should* burn a core for a minute: it decides whether a published GO stands.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402

OUT = os.path.join(bc.RESULTS, "bench_basis_timing_perm.json")
PAGE = os.path.join(bc.RESEARCH, "BENCH-BASIS-TIMING-PERM.md")
WINDOW = 250
MIN_OBS = 60
COST_BP_SIDE = 1.5
DRAWS = 5000
SEED = 20261124
TZ = timezone(timedelta(hours=8))


def load_product(code):
    pair = base.PAIRS[code]
    fut = {}
    path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
    for r in base.read_csv_rows(path):
        try:
            v = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            fut[str(r["date"])[:10]] = v
    idx = base.load_index(pair[0])
    dates, f, i = base.aligned(fut, idx)
    basis, spread, roll = base.basis_face(f, i, dates)
    return dates[1:], np.array(spread, dtype=float), np.array(roll, dtype=bool), np.array(basis, dtype=float)


def weights(basis, window=WINDOW):
    n = len(basis)
    w = np.zeros(n)
    for k in range(n):
        lo = max(0, k - window + 1)
        win = basis[lo:k + 1]
        if len(win) < MIN_OBS:
            continue
        p = 100.0 * (np.sum(win < basis[k]) + 0.5 * np.sum(win == basis[k])) / len(win)
        w[k] = max(0.0, min(1.0, (80.0 - p) / 60.0))
    return w


def annualised(x):
    eq = float(np.cumprod(1.0 + x)[-1])
    years = len(x) / bc.TRADING_DAYS
    return (eq ** (1.0 / years) - 1.0) * 100 if years > 0 and eq > 0 else -100.0


def carry_curve(spread, roll, w_next):
    """w_next[k] drives day k+1's carry; roll days are excluded; size costs charged."""
    cost = np.abs(np.diff(w_next, prepend=0.0)) * COST_BP_SIDE / 10000.0
    return np.where(roll, 0.0, w_next * spread) - cost


def run():
    bc.weight_priority()
    rng = np.random.default_rng(SEED)
    out = {}
    for code in ("IC", "IM"):
        dates, spread, roll, basis = load_product(code)
        w = weights(basis)
        w_next = w[:-1]
        n = len(w_next)
        base_curve = np.where(roll, 0.0, spread) - 0.0
        always = annualised(np.where(roll, 0.0, 1.0 * spread)
                            - np.abs(np.diff(np.ones(n), prepend=0.0)) * COST_BP_SIDE / 10000.0)
        observed = annualised(carry_curve(spread, roll, w_next))
        d_obs = observed - always
        null = np.empty(DRAWS)
        for j in range(DRAWS):
            k = int(rng.integers(20, max(21, n - 20)))
            shifted = np.roll(w_next, k)
            null[j] = annualised(carry_curve(spread, roll, shifted)) - always
        p = float((null >= d_obs).mean())
        out[code] = {
            "bars": int(n),
            "weighted_ann_pct": round(observed, 2),
            "always_on_ann_pct": round(always, 2),
            "difference_pp": round(d_obs, 2),
            "null_mean_pp": round(float(null.mean()), 2),
            "null_p95_pp": round(float(np.percentile(null, 95)), 2),
            "p_value": round(p, 4),
            "draws": DRAWS,
            "significant": bool(p < 0.01),
        }
    verdict = ("SIGNIFICANT" if all(v["significant"] for v in out.values())
               else ("NOT_SIGNIFICANT" if any(not v["significant"] for v in out.values())
                     else "INCONCLUSIVE"))
    payload = {
        "cell": "basis_timing_perm",
        "generated": datetime.now(TZ).isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1] if "dates" in dir() else "see products",
        "null": "circular shift of the weight series (alignment destroyed, distribution kept)",
        "statistic": "annualised(weighted carry) - annualised(always-on carry)",
        "draws": DRAWS, "seed": SEED,
        "criteria": {"cost_bp_side": COST_BP_SIDE, "target_edge_pp": 5.0,
                     "window": WINDOW, "min_obs": MIN_OBS},
        "products": out, "verdict": verdict,
        "reading": {"SIGNIFICANT": "the GO survives; sizing by percentile is aligned with the carry",
                    "NOT_SIGNIFICANT": "the GO does not survive; withdraw it and hold always",
                    "INCONCLUSIVE": "mixed; report both and do not size on it"},
    }
    bc.write_json(OUT, payload)
    lines = ["# 基差定仓位的置换检验", "",
             f"generated {payload['generated']} | 判决 **{verdict}** | 抽样 {DRAWS} 次", "",
             "| 品种 | 加权年化 | 常驻年化 | 差 | 零分布均值 | 零分布95分位 | p | 显著 |",
             "|---|---|---|---|---|---|---|---|"]
    for code, v in out.items():
        lines.append(f"| {code} | {v['weighted_ann_pct']}% | {v['always_on_ann_pct']}% | "
                     f"{v['difference_pp']}pp | {v['null_mean_pp']}pp | {v['null_p95_pp']}pp | "
                     f"{v['p_value']} | {v['significant']} |")
    lines += ["", "零假设：把权重序列做循环移位（保留分布与平滑度，只破坏与行情的对齐）。",
              "p = 零分布中 ≥ 观测差的比例；p<0.01 才算显著。", "",
              "## 读法", "", f"- {payload['reading'][verdict]}"]
    with open(PAGE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps({"ok": True, "verdict": verdict,
                      "per_product": {k: v["difference_pp"] for k, v in out.items()},
                      "p_values": {k: v["p_value"] for k, v in out.items()}},
                     ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("ok", True) else 1)
