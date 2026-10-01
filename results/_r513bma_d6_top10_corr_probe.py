"""r513 bm-a backoff-round analysis probe: D6 same-family correlation
matrix for the T-139 stage-B promotion list.

Why (feeds the stage-B judgment prereg freeze, r512 next-pointer): the
REFINE_BENCH_REV_CENSUS top10_independent list is a single corner
(exit=time, H=20 across depth x entry x liq combos), so the stage-B
prereg must apply D6 "same-family strict" (O-20260928-1506: max|corr|
>= 0.7 reject) and pre-register only the truly independent hypotheses.
This probe measures the actual daily-return correlations so the freeze
cites a number, not an adjective.

Method: rebuild each promoted cell's daily blended series using the
census runner's own frozen faces (refine_bench_rev_census._pick_axis /
_sim_axis / _exit_pair over rev_osc_stock_p1.signal_grid, RV.COST_X1,
bucket-blend skeleton verbatim from RC._cell_job) -- engine zero
re-implementation (r511 law).  Fail-closed anchor: RV.cell_stats(series)
must reproduce the committed shard row (entries / ann_ret / sharpe_full)
exactly; any mismatch aborts before writing any output.

Marks / ledger / SEED / pool faces: +0 (pure measurement, no judged
face touched, no pool entry claimed -- r505 inline-probe precedent).
"""
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import rev_osc_stock_p1 as RV            # frozen engine faces (reuse law)
import refine_bench_rev_census as RC      # frozen census axes (reuse law)

OUT_DIR = os.path.join(ROOT, "results", "refine_bench_stock", "rev_census")
RANK_PATH = os.path.join(OUT_DIR, "census_ranking.json")
OUT_PATH = os.path.join(OUT_DIR, "d6_top10_corr.json")
D6_THRESHOLD = 0.7


def _committed_rows():
    rows = {}
    rank = json.load(open(RANK_PATH, encoding="utf-8"))
    for sf in rank["shard_files"]:
        blob = json.load(open(os.path.join(OUT_DIR, sf), encoding="utf-8"))
        for r in (blob["rows"] if isinstance(blob, dict) else blob):
            rows[r["name"]] = r
    return rank, rows


def _cell_series(P, cell):
    """Verbatim skeleton of RC._cell_job with the daily series kept."""
    cost = RV.COST_X1
    tp_pct, sl_pct = RC._exit_pair(cell["exit"])
    b = [np.zeros(P["T"]), np.zeros(P["T"])]
    entries = 0
    for g, t in enumerate(RV.signal_grid()):
        picks, _why = RC._pick_axis(P, t, cell)
        if picks is None:
            continue
        w = np.ones(len(picks)) / len(picks)
        bucket = g % 2
        for i, s in enumerate(picks):
            net, exit_d, _tag = RC._sim_axis(P, int(s), t, cell["H"],
                                            tp_pct, sl_pct, cost)
            if net is None:
                continue
            entries += 1
            span = max(1, exit_d - (t + 1))
            b[bucket][t + 1:t + 1 + span] += float(w[i]) * float(net) / span
    series = 0.5 * (b[0] + b[1])
    return series, entries


def _components(names, corr, thr):
    """Connected components under |corr| >= thr (D6 same-family law)."""
    n = len(names)
    seen, groups = set(), []
    for i in range(n):
        if i in seen:
            continue
        stack, comp = [i], []
        seen.add(i)
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in range(n):
                if v != u and v not in seen and abs(corr[u][v]) >= thr:
                    seen.add(v)
                    stack.append(v)
        groups.append([names[k] for k in comp])
    return groups


def main():
    t0 = time.time()
    rank, committed = _committed_rows()
    cells = rank["top10_independent"]
    names = [c["name"] for c in cells]

    P = RV.load_panel()
    P["T"] = P["F"]["close"].shape[0]
    P["amt20"] = RV._roll_mean20(P["F"]["amount"])

    series, anchors = [], []
    for cell in cells:
        s, entries = _cell_series(P, cell)
        stats = RV.cell_stats(s)
        ref = committed[cell["name"]]
        ok = (entries == ref["entries"]
              and abs(stats["ann_ret"] - ref["ann_ret"]) < 1e-9
              and abs(stats["sharpe_full"] - ref["sharpe_full"]) < 1e-9)
        anchors.append({"name": cell["name"], "entries": entries,
                        "ref_entries": ref["entries"],
                        "ann_ret": stats["ann_ret"], "match": bool(ok)})
        if not ok:
            print(f"ANCHOR FAIL {cell['name']}: entries {entries} vs "
                  f"{ref['entries']}, ann_ret {stats['ann_ret']} vs "
                  f"{ref['ann_ret']}, sharpe {stats['sharpe_full']} vs "
                  f"{ref['sharpe_full']} -- abort, no output written")
            return 2
        series.append(s)
        print(f"anchor ok: {cell['name']}  entries={entries} "
              f"ann_ret={stats['ann_ret']:.6f}")

    X = np.vstack(series)
    corr = np.corrcoef(X).tolist()
    off = [(abs(corr[i][j]), i, j)
           for i in range(len(names)) for j in range(i + 1, len(names))]
    pairs_ge = [(names[i], names[j], round(corr[i][j], 4))
                for _a, i, j in off if _a >= D6_THRESHOLD]
    groups = _components(names, corr, D6_THRESHOLD)

    out = {
        "probe": "d6_top10_corr (r513 bm-a, T-139 stage-B feed)",
        "purpose": "same-family D6 evidence for stage-B judgment prereg: "
                   "top10_independent is a single time-exit H20 corner; "
                   "this measures true daily-return independence",
        "cells": names,
        "corr_matrix": [[round(v, 4) for v in row] for row in corr],
        "max_abs_offdiag": round(max(a for a, _i, _j in off), 4),
        "mean_abs_offdiag": round(sum(a for a, _i, _j in off) / len(off), 4),
        "d6_threshold": D6_THRESHOLD,
        "pairs_ge_threshold": pairs_ge,
        "independent_groups_at_threshold": groups,
        "n_independent_groups": len(groups),
        "anchors": anchors,
        "law_refs": ["O-20260928-1506 D6 (max|corr|>=0.7 reject)",
                     "r512 census honesty warning (same-corner top10)",
                     "r511 engine-reuse law (zero re-implementation)"],
        "evidence_cutoff": rank["meta"]["audit"].get("evidence_cutoff"),
        "panel": rank["meta"]["audit"].get("panel"),
        "audit": {"machine": "bm-a", "workers": 1,
                  "elapsed_sec": round(time.time() - t0, 1),
                  "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
    }
    tmp = OUT_PATH + ".tmp"
    json.dump(out, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, OUT_PATH)
    print(f"WROTE {OUT_PATH}")
    print(f"max|corr|={out['max_abs_offdiag']} mean={out['mean_abs_offdiag']} "
          f"pairs>=0.7: {len(pairs_ge)} groups: {len(groups)} "
          f"(elapsed {out['audit']['elapsed_sec']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
