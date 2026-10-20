"""Shared runner core for FUND-VALUE-P2 / FUND-QUALITY-P2 (r1089 bm-a).

Single source for the two sibling P2 runners: frozen cell table (read from the
r1088 PLAN artifacts), cost faces, the exit-axis parameter family, the
engine-canonical burn loop, the metrics kernel and the finalize envelope.

Nothing numeric is restated here. Every threshold and every cell id comes from
results/<family>_p2/PLAN.json, which scripts/fund_vq_p2_plan.py derives from the
frozen prereg; this module only executes that plan. The family runners implement
their own signal definition and data binding and nothing else.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from contextlib import nullcontext

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUTOFF = pd.Timestamp("2026-09-22")      # P-family D2 lockbox (P1 same anchor)

# exit-axis parameter family (prereg sec.3 leg3). Every variant disables the
# engine default stack through BOTH channels; only the declared stop differs.
BASE_PARAMS = {
    "position_size_pct": 1.0, "max_positions": 1,
    "sizing_mode": "fixed_initial", "report_num_entries": True,
    "take_profit_levels": (),
    "trailing_stop_activate": 1e12,
    "initial_stop": -1.0,
    "time_decay_period": 10 ** 9,
}
EXIT_PATCH_OVERRIDES = {"loss_time_days": 10 ** 9, "global_hard_limit": 10 ** 9}
PLAN_BY_KIND = {
    "value": "results/fund_value_p2/PLAN.json",
    "quality": "results/fund_quality_p2/PLAN.json",
}


def now_iso() -> str:
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def dump(obj, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def log(out_dir: str, msg: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "runner.log"), "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


# ------------------------------------------------------------------- plan face

def load_plan(kind: str) -> dict:
    """Read the frozen judged-cell plan; fail closed when missing."""
    rel = PLAN_BY_KIND[kind]
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        raise RuntimeError(f"plan missing: {rel} (run fund_vq_p2_plan.py)")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cells_of(plan: dict) -> dict:
    """cell_id -> frozen cell spec (id carries the cost face)."""
    return {c["cell_id"]: c for c in plan["judged_cells"]}


def exit_params(exit_axis: dict):
    """(params, patch) for one frozen exit spec; default stack dead in both
    channels on every variant (prereg sec.3 leg3)."""
    params = dict(BASE_PARAMS)
    kind = exit_axis["kind"]
    if kind == "hard_stop":
        params["initial_stop"] = float(exit_axis["level"])
    elif kind == "trailing":
        params["trailing_stop_activate"] = float(exit_axis["activate"])
        params["trailing_lock"] = float(exit_axis["drawdown"])
    elif kind != "hold_through":
        raise RuntimeError(f"undeclared exit kind: {kind}")
    return params, dict(EXIT_PATCH_OVERRIDES)


# --------------------------------------------------------------- rank kernels

def avg_rank(x) -> np.ndarray:
    """1-based average-tie rank (ascending). Deterministic, no scipy."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    out = np.zeros(n, dtype=np.float64)
    if n == 0:
        return out
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        out[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return out


def top_asc(pj, vals, n, codes):
    """Cheapest-first (ascending) selection; code tiebreak."""
    if len(pj) == 0:
        return pj
    order = np.lexsort((codes[pj], vals))
    return pj[order[:min(n, len(pj))]]


def top_desc(pj, vals, n, codes):
    """Best-first (descending) selection; code tiebreak."""
    if len(pj) == 0:
        return pj
    order = np.lexsort((codes[pj], -vals))
    return pj[order[:min(n, len(pj))]]


def top_composite_asc(pj, score, n, codes):
    """Lowest composite rank first (the ranking convention of both families:
    value ascends on cheapness, quality descends, so the composite is built
    from descending ranks and the lowest sum wins)."""
    if len(pj) == 0:
        return pj
    order = np.lexsort((codes[pj], score))
    return pj[order[:min(n, len(pj))]]


# ---------------------------------------------------------------- engine face

def run_cell(p1, G, spans, face, lo, hi, exit_axis):
    """Engine-canonical burn over [lo..hi]: P1's per-symbol span-sliced
    sub-account decomposition verbatim, only the exit/param face differs."""
    from engine import run_backtest
    from live.paper import ExitPatch
    from science_gates import CostPatch

    params, patch = exit_params(exit_axis)
    idx = G["idx"]
    syms = G["syms"]
    win_idx = idx[lo:hi + 1]
    pnl = None
    n_trades = n_entries = 0
    reasons = Counter()
    for j in sorted(spans):
        sp = spans[j]
        e_lo = max(sp[0][0] - 2, lo)
        e_hi = min(sp[-1][1] + 2, hi)
        if e_hi < e_lo:
            continue
        sym = syms[j]
        ent, scale = p1._sym_arrays(j, sp)
        ent_df = pd.DataFrame({sym: pd.Series(ent, index=idx)})
        frame = p1._sym_frame(j, e_lo, e_hi)
        with ExitPatch(patch), (CostPatch(2.0) if face == "x2" else nullcontext()):
            res = run_backtest({sym: frame}, dict(params),
                               entry_signal=ent_df,
                               exit_signal=ent_df <= 0,
                               entry_size_scale=scale)
        eq = pd.Series(res["equity_curve"],
                       index=frame.index[:len(res["equity_curve"])])
        p = (eq - p1.CAPITAL).reindex(win_idx).ffill().fillna(0.0)
        pnl = p if pnl is None else pnl + p
        n_trades += len(res["trades"])
        n_entries += int(res["metrics"].get("num_entries", 0))
        for tr in res["trades"]:
            reasons[str(tr.get("reason", tr.get("exit_reason", "na")))] += 1
    if pnl is None:
        return None
    nav = (pnl + p1.CAPITAL).reindex(win_idx).ffill().fillna(p1.CAPITAL)
    return {"nav": nav, "n_trades": n_trades, "n_entries": n_entries,
            "exit_reasons": dict(reasons)}


def metrics(nav) -> dict:
    rets = nav.pct_change().dropna()
    if len(rets) < 30 or float(rets.std(ddof=1)) == 0:
        return {"n_days": int(len(rets)), "sharpe_ann": None,
                "ann_ret": None, "max_dd": None, "total_ret": None}
    mu, sd = float(rets.mean()), float(rets.std(ddof=1))
    sharpe = mu / sd * np.sqrt(252.0)
    ann = (1.0 + mu) ** 252 - 1.0
    peak = nav.cummax()
    mdd = float((nav / peak - 1.0).min())
    return {"n_days": int(len(rets)), "sharpe_ann": round(sharpe, 6),
            "ann_ret": round(ann, 6), "max_dd": round(mdd, 6),
            "total_ret": round(float(nav.iloc[-1] / nav.iloc[0] - 1.0), 6)}


def default_stack_share(exit_reasons: dict, n_trades: int) -> float:
    off = sum(v for k, v in exit_reasons.items() if k != "signal_reversal")
    return round(off / max(1, n_trades), 6)


def daily_returns(nav) -> list:
    """Cell payload returns series (fund_value_p1 convention).

    G1'v2 needs >=20 returns for the stationary-bootstrap CI, and finalize
    reads them back from the per-cell checkpoint -- so every burned cell must
    carry them (r1071 bm-b: payloads written without returns made
    finalize raise ValueError('bootstrap needs >= 20 returns')).
    """
    return [round(float(v), 8) for v in nav.pct_change().dropna().to_numpy()]


def status_payload(cell_dir: str, cells: dict) -> dict:
    done = {}
    if os.path.isdir(cell_dir):
        for fn in sorted(os.listdir(cell_dir)):
            if not fn.endswith(".json"):
                continue
            try:
                with open(os.path.join(cell_dir, fn), encoding="utf-8") as fh:
                    d = json.load(fh)
            except Exception:
                continue
            done[fn[:-5]] = d.get("metrics") or {"mode": d.get("mode")}
    want = sorted(cells)
    return {"want": len(want), "done": len(done),
            "missing": [w for w in want if w not in done], "cells": done}


def finalize_payload(plan: dict, cell_dir: str, batch: str, family_key: str,
                     out_name: str) -> dict:
    from science_gates import cutoff_meta, g1_prime_v2

    n_cells = len(plan["judged_cells"])
    n_eff = int(plan["n_eff"])
    k_nulls = int(plan["nulls"]["k"])
    rows = {}
    if os.path.isdir(cell_dir):
        for fn in sorted(os.listdir(cell_dir)):
            if fn.endswith(".json"):
                with open(os.path.join(cell_dir, fn), encoding="utf-8") as fh:
                    rows[fn[:-5]] = json.load(fh)
    burns = {k: v for k, v in rows.items() if v.get("mode") != "dry-run"}
    head = burns.get("MAIN-x1")
    g1 = None
    head_rets = list((head or {}).get("returns") or [])
    if (head and head.get("metrics", {}).get("sharpe_ann") is not None
            and len(head_rets) >= 20):
        g1 = g1_prime_v2(head["metrics"]["sharpe_ann"], head_rets, n_eff,
                         n_trades=head.get("n_trades"),
                         n_entries=head.get("n_entries"))
    if g1:
        note = ("g1 computed on headline cell; registration columns "
                "require the batch null family")
    elif head and len(head_rets) < 20:
        note = ("headline cell carries no returns series (<20) -- cell "
                "predates the r1071 returns-in-payload fix; re-burn before "
                "judging")
    else:
        note = "judged face incomplete"
    return {
        "batch": batch, "family_key": family_key,
        "n_eff": n_eff, "nulls": k_nulls,
        "cells_burned": len(burns), "cells_expected": n_cells,
        "headline_cell": "MAIN-x1",
        "g1_prime_v2": g1,
        "verdict_note": note,
        "rows": {k: {"metrics": v.get("metrics"),
                     "n_trades": v.get("n_trades"),
                     "default_stack_share": v.get("default_stack_share")}
                 for k, v in sorted(burns.items())},
        **cutoff_meta(CUTOFF.date()), "ts": now_iso(),
    }, out_name