"""r827 bm-b E7 scratch: incumbent GRID cells' same-metric reference (offline).

Computes the exact metrics of scripts/etf_grid_candidates.py on the five
frozen GRID cells (grid_paper.py roster: 510300/159915/512880/518880/511010)
from the LOCAL core48 panel (data/daily/<code>.csv, as-traded basis) --
zero network, descriptive only. Output: results/etf_grid_candidates/grid_ref.json
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from etf_grid_candidates import (ann_log_ret, ann_vol, avg_range_pct,  # noqa: E402
                                 amount_60d_avg, max_drawdown, threshold_tags)

CELLS = {"510300": "HS300", "159915": "ChiNext", "512880": "Securities",
         "518880": "Gold", "511010": "Treasury"}
out = {}
for code, label in CELLS.items():
    path = os.path.join(ROOT, "data", "daily", code + ".csv")
    with io.open(path, encoding="utf-8-sig") as f:
        rd = list(csv.DictReader(f))
    rows = [{"date": r["date"], "open": float(r["open"]), "high": float(r["high"]),
             "low": float(r["low"]), "close": float(r["close"]),
             "volume": float(r["volume"]), "amount": float(r["amount"])} for r in rd]
    closes = [r["close"] for r in rows]
    m = {"code": code, "label": label, "n_rows": len(rows),
         "first_date": rows[0]["date"], "last_date": rows[-1]["date"],
         "ann_log_ret": ann_log_ret(closes), "ann_vol": ann_vol(closes),
         "avg_daily_range_pct": avg_range_pct(rows), "max_drawdown": max_drawdown(closes),
         "amount_60d_avg": amount_60d_avg(rows)}
    m["tags"] = threshold_tags(m)
    out[code] = m

dest = os.path.join(ROOT, "results", "etf_grid_candidates", "grid_ref.json")
with io.open(dest, "w", encoding="utf-8") as f:
    json.dump({"face": "incumbent GRID cells reference metrics (local panel, as-traded)",
               "cells": out}, f, ensure_ascii=False, indent=1)
for code, m in out.items():
    print(code, m["label"], "rows", m["n_rows"], "vol", round(m["ann_vol"], 4),
          "range%", round(m["avg_daily_range_pct"], 2), "mdd", round(m["max_drawdown"], 3),
          "amt60dM", int((m["amount_60d_avg"] or 0) / 1e6), "annret",
          round(m["ann_log_ret"], 3), m["tags"])
print("evidence:", dest)
