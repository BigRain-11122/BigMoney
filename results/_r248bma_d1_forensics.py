# -*- coding: utf-8 -*-
"""R248 bm-a: REV60_bare max|d1|=5.06 forensics (read-only data-artifact probe).

Replicates the deterministic selection face (same loader/schedule/sig/topk),
tracks held basket to the audit argmax day, prints per-name day ratios to
identify the artifact stock + its raw close window. Zero writes.
"""
import io
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cn_rev_tilt_p1 as R


def main() -> int:
    r = json.load(io.open(os.path.join(ROOT, "results", "cn_rev_tilt", "p1_results.json"), encoding="utf-8"))
    audit = r["judged_x1_returns_6dp_audit"]["REV60_bare"]
    arr = np.asarray(audit, dtype=float)
    i_max = int(np.argmax(np.abs(arr)))
    print(f"audit len={len(arr)} argmax_idx={i_max} val={arr[i_max]:.6f}")

    close = R.load_panel()
    close_arr = close.values.astype(np.float64)
    idx = close.index
    T, N = close_arr.shape
    print(f"panel T={T} N={N} first={idx[0]} last={idx[-1]}")

    day = i_max if len(arr) == T else i_max + 1
    date = idx[day]
    print(f"max day -> panel idx {day} date {date}")

    sched = R.rebal_schedule(T)
    valid = R.signal_valid(close_arr, 60)
    sig = R.sig_matrix(close_arr, 60, "rev")
    sels = R.topk_selections(sig, valid, sched)

    # held basket at `day`: last transition e = r+1 <= day
    trans = {}
    for rr, cols in sels:
        e = rr + 1
        if e < T:
            trans[e] = cols
    e_active = max(e for e in trans if e <= day)
    basket = trans[e_active]
    r_sel = e_active - 1
    print(f"active rebalance r={r_sel} (date {idx[r_sel]}) e={e_active} k={basket.size}")

    ratio = close_arr[day, basket] / close_arr[day - 1, basket]
    order = np.argsort(-np.abs(ratio))
    print("top |day-ratio| names in basket:")
    for o in order[:6]:
        j = int(basket[o])
        prev, cur = close_arr[day - 1, j], close_arr[day, j]
        col = close.columns[j]
        print(f"  col={col} prev={prev:.4g} cur={cur:.4g} ratio={ratio[o]:+.6g}")
        w0 = max(0, day - 3)
        print(f"    window close[{w0}..{day+2}]: {np.round(close_arr[w0:day+3, j], 4)}")
    print(f"basket mean ratio={float(np.nanmean(ratio)):+.6g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
