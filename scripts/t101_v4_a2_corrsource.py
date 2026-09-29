"""T-101-V4-A2-CORRSOURCE — survivor-cell correlation-source decomposition (D6 exit child).

Prereg: research/T-101-V4-A2-CORRSOURCE_PREREG.md (frozen pre-run, r434 bm-a).
Parent: research/T-101-V4_PREREG.md (T-101-V4-A2-PRESCREEN, r433). Subject cell =
510050|RSV30_low<0.2 (sole prescreen survivor; D6 max|corr| vs own B&H = 0.9424
-> REJECT_corr>=0.7, deferred behind this mandated correlation-source analysis).

Zero reimplementation: gate/position/returns machinery imported from
scripts/t101_v4_a2_prescreen.py (probe-anchor same-face assertion inside
load_panel). Frozen dual-exit verdict (prereg sec.4):
  TIMING_ALPHA (eligible for full-judge face, excess framing) iff
    OOS alpha HAC t >= 2 AND true OOS excess > same-mask circular-shift null p95;
  else BETA_SAME_SOURCE -> line-close (A2 arm fully closed, zero cells advance).
Cost V1 parity (COST_LEG=0.0005); evidence_cutoff=2026-09-28 (D2 lockbox).
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import science_gates as sg  # noqa: E402
import t101_v4_a2_prescreen as parent  # noqa: E402

EVIDENCE_CUTOFF = "2026-09-28"
CODE = "510050"
GATE_N = 30
SPLIT = "2017-01-01"  # parent split parity
NULL_K = 200
NULL_SEED_BASE = sg.SEED_REGISTRY["t101_v4_a2_corrnull"]
HAC_LAG = 5


def ols_hac(y: np.ndarray, x: np.ndarray, lag: int = HAC_LAG) -> dict:
    """OLS with Newey-West HAC t-stats (lag=5, prereg sec.3)."""
    n = len(y)
    X = np.column_stack([np.ones(n), x])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    # HAC covariance (Newey-West)
    S = (X * resid[:, None]).T @ (X * resid[:, None]) / n
    for l in range(1, lag + 1):
        w = 1.0 - l / (lag + 1.0)
        G = (X[l:] * resid[l:, None]).T @ (X[:-l] * resid[:-l, None]) / n
        S += w * (G + G.T)
    cov = XtX_inv @ (S * n) @ XtX_inv
    se = np.sqrt(np.diag(cov))
    tvals = beta / se
    ybar = y.mean()
    r2 = 1.0 - (resid @ resid) / ((y - ybar) @ (y - ybar))
    return {"alpha_daily": float(beta[0]), "alpha_t": float(tvals[0]),
            "alpha_ann": float(beta[0] * 252), "beta": float(beta[1]),
            "r2": float(r2)}


def main() -> int:
    t0 = time.time()
    df = parent.load_panel(CODE)  # probe-anchor same-face assertion inside
    mask = parent.gate_mask(df, GATE_N)
    pos = parent.position_series(mask)
    r = parent.daily_returns(df, pos)  # strategy daily returns, parent parity
    bh = df["close"].pct_change().fillna(0.0)
    dates = df["date"].values
    oos_sel = dates >= SPLIT

    # --- exposure decomposition (prereg sec.3) ---
    pos_arr = pos.values.astype(bool)
    exposure = {
        "on_share_full": float(pos_arr.mean()),
        "on_share_oos": float(pos_arr[oos_sel].mean()),
        "on_days_full": int(pos_arr.sum()), "n_days_full": int(len(pos_arr)),
        "on_days_oos": int(pos_arr[oos_sel].sum()), "n_days_oos": int(oos_sel.sum()),
    }

    # --- correlation reproduction (parent D6 face) ---
    corr = {
        "full": float(np.corrcoef(r.values, bh.values)[0, 1]),
        "oos": float(np.corrcoef(r.values[oos_sel], bh.values[oos_sel])[0, 1]),
    }

    # --- OLS attribution (HAC lag=5) ---
    ols = {
        "oos": ols_hac(r.values[oos_sel].astype(float), bh.values[oos_sel].astype(float)),
        "full": ols_hac(r.values.astype(float), bh.values.astype(float)),
    }

    # --- excess identity: strategy excess == -(sum of OFF-day B&H returns) - cost drag
    # (prereg sec.3 frozen formula). NOTE T+1 open-fill convention breaks the
    # close-to-close identity by the overnight-gap interaction -> residual is
    # reported as the execution-convention gap, not an error term.
    off = ~pos_arr
    off_oos = off & oos_sel
    yrs_oos = oos_sel.sum() / 252.0
    off_ret_all = bh.values[off_oos]
    avoided_oos = float(off_ret_all.sum())  # net B&H return the strategy sat out
    cost_drag_oos = float(parent.COST_LEG * 2 * parent.count_entries(pos, oos_sel))  # round-trips
    excess_oos = parent.ann_ret(r[oos_sel].values) - parent.ann_ret(bh.values[oos_sel])
    # loss-avoidance pool: negative OFF-day returns are the losses the gate sat out
    neg_off = off_ret_all[off_ret_all < 0]
    pos_off = off_ret_all[off_ret_all >= 0]
    top5_neg = np.sort(off_ret_all)[:5]  # 5 most negative = largest avoided losses
    top5_share = float(top5_neg.sum() / neg_off.sum()) if neg_off.size and neg_off.sum() != 0 else float("nan")
    identity = {
        "avoided_off_ret_sum_oos": avoided_oos,
        "avoided_off_ann_oos": avoided_oos / yrs_oos,
        "cost_drag_sum_oos": cost_drag_oos,
        "cost_drag_ann_oos": cost_drag_oos / yrs_oos,
        "excess_ann_oos_true": float(excess_oos),
        "identity_residual_ann": float(excess_oos - (-avoided_oos / yrs_oos - cost_drag_oos / yrs_oos)),
        "avoided_loss_sum_oos": float(neg_off.sum()) if neg_off.size else 0.0,
        "avoided_gain_sum_oos": float(pos_off.sum()) if pos_off.size else 0.0,
        "top5_avoided_share_of_loss_pool": top5_share,
        "top5_avoided_days": [str(dates[i]) for i in np.where(off_oos)[0][np.argsort(off_ret_all)[:5]]],
    }

    # --- null: same-mask circular shift K=200, OOS excess face ---
    rng = np.random.default_rng(NULL_SEED_BASE)
    null_excess = []
    for _ in range(NULL_K):
        k = int(rng.integers(1, len(pos_arr) - 1))
        shifted = np.roll(pos_arr.astype(int), k).astype(bool)
        r_null = parent.daily_returns(df, pd.Series(shifted, index=df.index))
        null_excess.append(parent.ann_ret(r_null.values[oos_sel]) - parent.ann_ret(bh.values[oos_sel]))
    null_p95 = float(np.nanpercentile(null_excess, 95))
    null_med = float(np.nanmedian(null_excess))
    null = {"k": NULL_K, "seed_base": NULL_SEED_BASE, "med_excess": null_med, "p95_excess": null_p95}

    # --- frozen dual-exit verdict (prereg sec.4) ---
    t_alpha = ols["oos"]["alpha_t"]
    legs = {
        "leg1_alpha_hac_t": t_alpha,
        "leg1_pass": bool(t_alpha >= 2.0),
        "leg2_excess_gt_null_p95": bool(excess_oos > null_p95),
    }
    verdict = "TIMING_ALPHA" if (legs["leg1_pass"] and legs["leg2_excess_gt_null_p95"]) else "BETA_SAME_SOURCE"
    line_action = ("eligible_full_judge_excess_framing" if verdict == "TIMING_ALPHA"
                   else "LINE_CLOSE_A2_arm_10_of_10_resolved_zero_cells_advance")

    out = {
        "batch": "T-101-V4-A2-CORRSOURCE",
        "prereg": "research/T-101-V4-A2-CORRSOURCE_PREREG.md",
        "parent_batch": "T-101-V4-A2-PRESCREEN",
        "subject_cell": f"{CODE}|RSV{GATE_N}_low<0.2",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": {"cutoff": EVIDENCE_CUTOFF}},
        "split": SPLIT, "cost_leg": parent.COST_LEG, "hac_lag": HAC_LAG,
        "exposure": exposure, "corr": corr, "ols": ols,
        "excess_identity": identity, "null": null,
        "verdict_legs": legs, "verdict": verdict, "line_action": line_action,
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "host": "bm-a",
                  "lane": "bm-a (local ETF panel data/daily)"},
    }
    out["trials_ledger"] = sg.append_ledger(
        "T-101-V4-A2-CORRSOURCE", 1, "t101_v4_a2_corrsource.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="D6-exit child of T-101-V4-A2-PRESCREEN; verdict closure on sole survivor cell")
    with open("results/t101_v4_a2_corrsource.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"elapsed={out['audit']['elapsed_sec']}s verdict={verdict} action={line_action}")
    print(f"exposure on_share_oos={exposure['on_share_oos']:.4f} corr_full={corr['full']:.4f} corr_oos={corr['oos']:.4f}")
    print(f"OLS oos: alpha_ann={ols['oos']['alpha_ann']:+.5f} t={t_alpha:+.3f} beta={ols['oos']['beta']:.4f} r2={ols['oos']['r2']:.4f}")
    print(f"excess true={excess_oos:+.6f} null_med={null_med:+.6f} null_p95={null_p95:+.6f} leg2_pass={legs['leg2_excess_gt_null_p95']}")
    print(f"identity: avoided_ann={identity['avoided_off_ann_oos']:+.5f} cost_drag_ann={identity['cost_drag_ann_oos']:+.5f} "
          f"residual_ann={identity['identity_residual_ann']:+.5f} "
          f"loss_pool={identity['avoided_loss_sum_oos']:+.4f} gain_pool={identity['avoided_gain_sum_oos']:+.4f} "
          f"top5_share={identity['top5_avoided_share_of_loss_pool']:.3f} top5_days={identity['top5_avoided_days']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
