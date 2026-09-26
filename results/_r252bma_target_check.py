# -*- coding: utf-8 -*-
"""R252 bm-a: verify surgical replacement-target uniqueness (read-only)."""
import io

KEY = '"ledger": {'
TL = '"trials_ledger": {'
targets = {
    "results/div_lowvol_p1.json": [],
    "results/cny_window_p1.json": ['"prev_total": 184826', '"total": 184849'],
    "results/cn_rev_tilt/p1_results.json": ['"prev_total": 185798', '"total": 185852'],
    "results/cn_div_lowvol_rot/p1_results.json": ['"prev_total": 185798', '"total": 185852'],
}
for p, tt in targets.items():
    t = io.open(p, encoding="utf-8-sig").read()
    print(p)
    print("  ", repr(KEY), "count=", t.count(KEY), "| existing trials_ledger:", t.count(TL))
    for s in tt:
        print("  ", repr(s), "count=", t.count(s))
