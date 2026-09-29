"""T-101-V4-A2-PRESCREEN — RSV dual-gate regime-timing arm, cheap pre-screen face.

Prereg: research/T-101-V4_PREREG.md (frozen pre-run, r433 bm-a).
Gate formula replicated verbatim from toolstack/gate_verify.py gates_of():
    RSV_n = (C - LLV_n) / (HHV_n - LLV_n), n in {30,60}; gate_on = RSV_n < 0.2
Five-member frozen universe O-1555; T+1 open execution (O-1132 conservative proxy);
cost 0.05% per leg (0.1% round-trip, gate_verify cost_rt parity); IS/OOS split
2017-01-01; bear/bull/chop segmentation on 510300 MA200; same-mask circular-shift
nulls K=200/cell seed base 20308000 (SEED_REGISTRY t101_v4_a2_scrnull).
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import science_gates as sg  # noqa: E402

EVIDENCE_CUTOFF = "2026-09-28"
UNIVERSE = ["510300", "510050", "510500", "512100", "588000"]
GATES = ["RSV60_low<0.2", "RSV30_low<0.2"]
SPLIT = "2017-01-01"
COST_LEG = 0.0005  # 0.05% per leg -> 0.1% round-trip (gate_verify cost_rt parity)
NULL_K = 200
NULL_SEED_BASE = sg.SEED_REGISTRY["t101_v4_a2_scrnull"]
MIN_OOS_ENTRIES = 15  # gate_verify min_ev_per_split parity
MAXDD_FLOOR = -0.35  # descriptive clause (BACKTEST_SCIENCE)
ANCHOR_FACE = {c: f"data/daily/sh{c}.csv" for c in UNIVERSE}  # G-ANCHOR-FACE probe-anchor same-face assertion


def load_panel(code: str) -> pd.DataFrame:
    path = ANCHOR_FACE[code]
    if not os.path.exists(path):
        raise SystemExit(f"FACE-MISMATCH VOID: declared anchor {path} missing")
    df = pd.read_csv(path)  # raw direct read, per prereg four-tuple
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= EVIDENCE_CUTOFF].reset_index(drop=True)  # D2 forward lockbox
    if df.empty or df["date"].iloc[-1] != EVIDENCE_CUTOFF:
        raise SystemExit(f"FACE-MISMATCH VOID: {code} tail {df['date'].iloc[-1] if len(df) else 'empty'} != {EVIDENCE_CUTOFF}")
    return df


def gate_mask(df: pd.DataFrame, n: int) -> pd.Series:
    c, h, l = df["close"], df["high"], df["low"]
    hh, ll = h.rolling(n).max(), l.rolling(n).min()
    rsv = (c - ll) / (hh - ll).replace(0, np.nan)
    return (rsv < 0.2).fillna(False)


def regime_segment(benchmark: pd.DataFrame) -> pd.Series:
    c = benchmark["close"]
    ma200 = c.rolling(200).mean()
    slope = ma200.diff(60)
    bear = (c < ma200) & (slope < 0)
    bull = (c > ma200) & (slope > 0)
    seg = pd.Series("chop", index=benchmark.index)
    seg[bear] = "bear"
    seg[bull] = "bull"
    return seg


def position_series(mask: pd.Series) -> pd.Series:
    return mask.shift(1).fillna(False).astype(bool)  # T+1: signal day t -> executed day t+1


def daily_returns(df: pd.DataFrame, pos: pd.Series) -> pd.Series:
    o, c = df["open"].values, df["close"].values
    close_prev = np.roll(c, 1)
    close_prev[0] = np.nan
    ret = np.full(len(c), np.nan)
    p = pos.values
    for i in range(1, len(c)):
        if p[i] and p[i - 1]:
            ret[i] = c[i] / c[i - 1] - 1  # holding day
        elif p[i] and not p[i - 1]:
            ret[i] = c[i] / o[i] - 1 - COST_LEG  # entry day (open fill - cost)
        elif not p[i] and p[i - 1]:
            ret[i] = o[i] / c[i - 1] - 1 - COST_LEG  # exit day (open fill - cost)
        else:
            ret[i] = 0.0  # cash leg 0%
    return pd.Series(ret, index=df.index).fillna(0.0)


def sharpe(r: pd.Series) -> float:
    if len(r) < 20 or r.std() == 0:
        return float("nan")
    return float(r.mean() / r.std() * np.sqrt(252))


def max_drawdown(r: pd.Series) -> float:
    eq = (1 + r).cumprod()
    return float((eq / eq.cummax() - 1).min())


def ann_ret(r: pd.Series) -> float:
    total = float((1 + r).prod())
    yrs = len(r) / 252
    return total ** (1 / yrs) - 1 if yrs > 0 and total > 0 else float("nan")


def count_entries(pos: pd.Series, sel: pd.Series) -> int:
    p = pos[sel].values
    prev = np.roll(p, 1)
    prev[0] = False
    return int(((p) & (~prev)).sum())


def main() -> int:
    t0 = time.time()
    panels = {c: load_panel(c) for c in UNIVERSE}  # probe-anchor same-face assertion: same path used
    bm = panels["510300"]
    seg_all = regime_segment(bm)
    seg_by_date = pd.Series(seg_all.values, index=bm["date"].values)

    rows, json_cells, strat_daily = [], {}, {}
    for code in UNIVERSE:
        df = panels[code]
        bh = df["close"] / df["close"].iloc[0]
        bh_ret = df["close"].pct_change().fillna(0.0)
        for gate in GATES:
            n = 60 if "60" in gate else 30
            mask = gate_mask(df, n)
            pos = position_series(mask)
            r = daily_returns(df, pos)
            strat_daily[(code, gate)] = pd.Series(r.values, index=df["date"].values)
            is_sel = df["date"] < SPLIT
            oos_sel = ~is_sel
            full_stats = {"sharpe": sharpe(r), "ann_ret": ann_ret(r), "maxdd": max_drawdown(r)}
            is_stats = {"sharpe": sharpe(r[is_sel]), "ann_ret": ann_ret(r[is_sel])}
            oos_stats = {"sharpe": sharpe(r[oos_sel]), "ann_ret": ann_ret(r[oos_sel]), "maxdd": max_drawdown(r[oos_sel]),
                         "entries": count_entries(pos, oos_sel)}
            oos_excess = oos_stats["ann_ret"] - ann_ret(bh_ret[oos_sel])
            # segmentation (regime faces on 510300 dates)
            cell = {"inst": code, "gate": gate, "first_valid": str(df["date"].iloc[n]),
                    "IS": is_stats, "OOS": oos_stats, "full": full_stats,
                    "oos_excess_vs_bh": oos_excess, "oos_n": int(oos_sel.sum()), "is_n": int(is_sel.sum())}
            seg_stats = {}
            seg_lookup = seg_by_date.reindex(df["date"].values).fillna("pre_benchmark")
            for segname in ("bear", "bull", "chop"):
                sel = (seg_lookup == segname) & (df["date"].values >= SPLIT)
                if sel.sum() >= 30:
                    seg_stats[segname] = {"oos_ann_ret": ann_ret(r[sel.values]), "oos_days": int(sel.sum())}
            cell["segments_oos"] = seg_stats
            # nulls: same-mask circular shift K=200
            rng = np.random.default_rng(NULL_SEED_BASE)
            pos_arr = pos.values.astype(int)
            null_sharpes = []
            for _ in range(NULL_K):
                k = int(rng.integers(1, len(pos_arr) - 1))
                shifted = np.roll(pos_arr, k)
                r_null = daily_returns(df, pd.Series(shifted.astype(bool), index=df.index))
                null_sharpes.append(sharpe(r_null))
            cell["null"] = {"k": NULL_K, "med_sharpe": float(np.nanmedian(null_sharpes)),
                            "p95_sharpe": float(np.nanpercentile(null_sharpes, 95))}
            # pre-screen verdict (frozen 4 criteria, prereg sec.4)
            verdict = "SURVIVE" if (
                oos_excess > 0
                and oos_stats["entries"] >= MIN_OOS_ENTRIES
                and full_stats["maxdd"] >= MAXDD_FLOOR
                and oos_stats["sharpe"] > cell["null"]["med_sharpe"]
            ) else "KILL"
            fail = []
            if oos_excess <= 0: fail.append("oos_excess<=0")
            if oos_stats["entries"] < MIN_OOS_ENTRIES: fail.append("entries<15")
            if full_stats["maxdd"] < MAXDD_FLOOR: fail.append("maxdd<-35%")
            if not (oos_stats["sharpe"] > cell["null"]["med_sharpe"]): fail.append("sharpe<=null_med")
            cell["verdict"] = verdict
            cell["fail_reasons"] = fail
            json_cells[f"{code}|{gate}"] = cell
            rows.append({"inst": code, "gate": gate, "verdict": verdict,
                         "oos_excess_vs_bh": round(oos_excess, 6),
                         "oos_sharpe": round(oos_stats["sharpe"], 4),
                         "oos_entries": oos_stats["entries"],
                         "full_maxdd": round(full_stats["maxdd"], 4),
                         "null_med_sharpe": round(cell["null"]["med_sharpe"], 4),
                         "fail_reasons": ";".join(fail)})

    # D6 same-family correlation: strategy daily returns vs each member B&H + gate-pair
    d6 = {"vs_bh": {}, "gate_pair": {}}
    bh_daily = {c: pd.Series(panels[c]["close"].pct_change().fillna(0).values, index=panels[c]["date"].values) for c in UNIVERSE}
    for (code, gate), sr in strat_daily.items():
        for bc, br in bh_daily.items():
            common = sr.index.intersection(br.index)
            if len(common) > 250:
                v = float(np.corrcoef(sr.loc[common], br.loc[common])[0, 1])
                d6["vs_bh"][f"{code}|{gate}_vs_{bc}"] = round(v, 4)
    for code in UNIVERSE:
        a, b = strat_daily[(code, GATES[0])], strat_daily[(code, GATES[1])]
        v = float(np.corrcoef(a.values, b.values)[0, 1])
        d6["gate_pair"][code] = round(v, 4)
    d6["max_abs_vs_bh"] = max(abs(v) for v in d6["vs_bh"].values())
    d6["d6_verdict"] = "ACCEPT" if d6["max_abs_vs_bh"] < 0.7 else "REJECT_corr>=0.7"
    # in-roster 6-trader daily series: unavailable in paper_export (metrics summary only) -> defer per prereg sec.1
    d6["in_roster_daily_series"] = "unavailable_in_paper_export_deferred_to_full_judge_per_prereg_sec1"

    out = {
        "batch": "T-101-V4-A2-PRESCREEN",
        "prereg": "research/T-101-V4_PREREG.md",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": {"cutoff": EVIDENCE_CUTOFF}},
        "universe": UNIVERSE, "gates": GATES, "split": SPLIT,
        "cost_leg": COST_LEG, "null_k": NULL_K, "null_seed_base": NULL_SEED_BASE,
        "cells": json_cells, "d6": d6,
        "summary": {
            "n_cells": len(json_cells),
            "survivors": sum(1 for c in json_cells.values() if c["verdict"] == "SURVIVE"),
            "killed": sum(1 for c in json_cells.values() if c["verdict"] == "KILL"),
        },
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "host": "bm-a",
                  "lane": "bm-a (local ETF panel data/daily)"},
    }
    with open("results/t101_v4_a2_prescreen.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    pd.DataFrame(rows).to_csv("results/t101_v4_a2_prescreen.csv", index=False)
    print(f"elapsed={out['audit']['elapsed_sec']}s cells={len(json_cells)} "
          f"survivors={out['summary']['survivors']} killed={out['summary']['killed']} "
          f"d6_max|corr|={d6['max_abs_vs_bh']} d6={d6['d6_verdict']}")
    for r in rows:
        print(f"{r['inst']} {r['gate']:14s} {r['verdict']:7s} oos_excess={r['oos_excess_vs_bh']:+.4f} "
              f"sharpe={r['oos_sharpe']:+.3f} entries={r['oos_entries']} maxdd={r['full_maxdd']:+.2%} "
              f"null_med={r['null_med_sharpe']:+.3f} {r['fail_reasons']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
