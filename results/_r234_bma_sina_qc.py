# -*- coding: utf-8 -*-
"""R234 bm-a T-72 s2 supervision R7 spot QC probe.

Freshest-tail 6-stock QC (per R233 probe pattern _r233_bma_sina_qc.py):
- 14-col frozen schema column-identical
- exactly 100 rows/stock (num=100 frozen caliber)
- tail = 2026-09-24 (latest bar day)
- netamount vs sum(r0..r3_net) four-tier self-consistency (sina law)
"""
import csv
import json
import os
PANEL = os.path.join("data", "sina_mf", "per")  # per-stock layout data/sina_mf/per/<code>.csv

# frozen schema per scripts/update_sina_mf.py L83-85 (prereg section-1):
# date key opendate + 13 raw-ASCII value cols
FROZEN_COLS = ["opendate", "trade", "changeratio", "turnover", "netamount",
               "ratioamount", "r0", "r1", "r2", "r3",
               "r0_net", "r1_net", "r2_net", "r3_net"]


def qc_stock(code):
    path = os.path.join(PANEL, f"{code}.csv")
    if not os.path.exists(path):
        return {"code": code, "ok": False, "why": "file_missing"}
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {"code": code, "ok": False, "why": "zero_rows"}
    cols_ok = list(rows[0].keys()) == FROZEN_COLS
    if not cols_ok:
        return {"code": code, "ok": False, "why": f"schema_drift:{list(rows[0].keys())}"}
    n = len(rows)
    tail = rows[-1]["opendate"]
    # four-tier self-consistency on the tail rows: netamount ~ sum(r0..r3_net)
    max_dev = 0.0
    for r in rows[-5:]:
        try:
            net = float(r["netamount"])
            tiers = sum(float(r[k]) for k in ("r0_net", "r1_net", "r2_net", "r3_net"))
            scale = max(abs(net), 1.0)
            max_dev = max(max_dev, abs(net - tiers) / scale)
        except (ValueError, KeyError):
            max_dev = float("nan")
            break
    return {"code": code, "ok": n == 100 and tail == "2026-09-24" and max_dev < 1e-6,
            "rows": n, "tail": tail, "tier_dev": max_dev}


if __name__ == "__main__":
    prog = json.load(open(os.path.join("data", "sina_mf", "_progress.json"), encoding="utf-8-sig"))
    codes = prog["done"][-6:]
    out = [qc_stock(c) for c in codes]
    ok_n = sum(1 for o in out if o["ok"])
    print(json.dumps({"probe": "_r234_bma_sina_qc", "codes": codes,
                      "pass": f"{ok_n}/{len(out)}", "detail": out}, ensure_ascii=False, indent=1))
