# -*- coding: utf-8 -*-
"""r912 bm-a PARKING-P1 data anchor probe: row counts, first/last bar
dates, and zero-row stats for the three-arm instruments (§2 G-ANCHOR-FACE
facts for the prereg). Read-only."""
import csv
import io
import json

ARMS = {
    "A_treasury": ["sh511010", "sh511090", "sh511260"],
    "B_convertible": ["sh511380"],
    "C_money_baseline": ["sh511880", "sh511990"],
}
out = {}
for arm, codes in ARMS.items():
    for c in codes:
        path = "data/daily/%s.csv" % c
        with io.open(path, encoding="utf-8", errors="replace", newline="") as fh:
            rows = list(csv.DictReader(fh))
        dates = [r.get("date") or r.get("trade_date") or "" for r in rows]
        closes = [float(r["close"]) for r in rows if r.get("close")]
        nz = [x for x in closes if x != 0]
        out[c] = {
            "rows": len(rows),
            "first": dates[0] if dates else None,
            "last": dates[-1] if dates else None,
            "close_min": min(nz) if nz else None,
            "close_max": max(nz) if nz else None,
        }
json.dump(out, open("results/_r912bma_parking_probe.json", "w", encoding="ascii"),
          indent=1)
for k, v in out.items():
    print(k, v)
