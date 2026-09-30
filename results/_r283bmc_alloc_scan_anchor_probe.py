# -*- coding: utf-8 -*-
"""Probe: four-asset panel anchor facts for ALLOCATION_POLICY_SCAN prereg freeze.

Read-only. Emits results/_r283bmc_alloc_scan_anchor_probe.json.
Faces: data/daily/sh{510300,511010,518880,513500}.csv raw read (four-tuple
face 1: path / pd.read_csv / listing-date start / no warmup), joint inner-join
window stats, repo_daily presence (cash-leg face), row/date/last-bar facts.
"""
import json
import os
import sys

import pandas as pd

SYMS = ["510300", "511010", "518880", "513500"]
DATA = os.path.join("data", "daily")
REPO = os.path.join("Money0923", "data", "repo_daily.csv")


def main():
    out = {"probe": "alloc-scan-anchor", "faces": {}, "joint": {}, "cash_leg": {}}
    px = {}
    for s in SYMS:
        p = os.path.join(DATA, f"sh{s}.csv")
        df = pd.read_csv(p)
        df["date"] = df["date"].astype(str)
        rows = len(df)
        first, last = df["date"].iloc[0], df["date"].iloc[-1]
        close = df.set_index("date")["close"]
        px[s] = close
        out["faces"][s] = {
            "path": p, "loader": "pd.read_csv", "rows": int(rows),
            "first_date": first, "last_date": last,
            "null_close": int(close.isna().sum()),
        }
    panel = pd.DataFrame(px).sort_index().dropna()
    out["joint"] = {
        "first_date": str(panel.index[0]), "last_date": str(panel.index[-1]),
        "rows": int(len(panel)),
        "years": round(len(panel) / 252.0, 3),
        "n_complete_months": int(panel.groupby(panel.index.str[:7]).size().shape[0]),
    }
    out["cash_leg"] = {
        "repo_daily_csv_present": os.path.exists(REPO), "path": REPO,
        "note": "all scan variants are full-investment (CASH weight 0); "
                "repo accrual immaterial to residue only",
    }
    # monthly anchor counts on the joint panel (all-start grid faces)
    month_first = ~panel.index.str[:7].duplicated()
    out["joint"]["month_first_anchors"] = int(month_first.sum())
    qp = panel.index.str[:7]
    q_keys = qp.str[:4] + "Q" + ((qp.str[5:7].astype(int) - 1) // 3 + 1).astype(str)
    out["joint"]["quarter_first_anchors"] = int((~pd.Series(q_keys).duplicated()).sum())
    out["joint"]["year_first_anchors"] = int((~qp.str[:4].duplicated()).sum())
    path = "results/_r283bmc_alloc_scan_anchor_probe.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print("PROBE-OK")


if __name__ == "__main__":
    sys.exit(main())
