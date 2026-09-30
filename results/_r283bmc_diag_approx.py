# -*- coding: utf-8 -*-
"""r283 diagnostic: which validation face blew the 1% approx gate?
Reuses allocation_policy_scan functions verbatim; prints per-row rel_dev
at s=0 for representative rows. Infra debug only (no products, no ledger)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import allocation_policy_scan as aps
import alloc_backtest as ab

dates, prices, adv, cash_ret, panel = aps.load_faces()
n = len(dates)
anchors = aps.anchor_indices(dates)
wg = aps.weight_grid()
starts_m = anchors["M"]

rows = [0, 5, 14, 28, 42, 56]          # spread + equal-weight anchor
for rname, mode, thr in aps.RULES:
    if mode == "buyhold":
        segs, _ = aps.never_closed_form(prices, wg[56], [0], n)
        w = wg[56]
        wdict = {aps.SYMS[k]: w[k] for k in range(4)}
        wdict["CASH"] = 0.0
        res = ab.simulate(dates, prices, adv, cash_ret, wdict, aps.CAPITAL,
                          mode=mode, cost_fn=ab.side_cost_v2, p2=False,
                          start_idx=0)
        e0 = (res["eq"].iloc[-1] / res["eq"].iloc[0]) ** (252.0 / n) - 1.0
        a0 = segs[0]
        print("NEVER  W56 engine=%.5f approx=%.5f rel_dev=%.4f" %
              (e0, a0, abs(a0 - e0) / max(abs(e0), 1e-9)))
        continue
    if mode == "daily-threshold":
        seg_rows, _ = aps.threshold_approx(prices, [wg[r] for r in rows],
                                           thr, [0], n)
        for j, r in enumerate(rows):
            w = wg[r]
            wdict = {aps.SYMS[k]: w[k] for k in range(4)}
            wdict["CASH"] = 0.0
            ab.P3B_THRESHOLD = thr
            res = ab.simulate(dates, prices, adv, cash_ret, wdict,
                              aps.CAPITAL, mode=mode,
                              cost_fn=ab.side_cost_v2, p2=False,
                              start_idx=0)
            e0 = (res["eq"].iloc[-1] / res["eq"].iloc[0]) ** (252.0 / n) - 1.0
            a0 = seg_rows[j][0]
            print("THR%s W%02d engine=%.5f approx=%.5f rel_dev=%.4f trades=%d" %
                  (int(thr * 100), r, e0, a0,
                   abs(a0 - e0) / max(abs(e0), 1e-9), res["trades"]))
        ab.P3B_THRESHOLD = 0.05
