# -*- coding: utf-8 -*-
"""r417 bm-b: full gate_attrition dump (read-only)."""
import json
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ga = json.load(io.open(r"E:\Fluxgroup\FluxGroup\quant\bigmoney\results\gate_attrition.json", encoding="utf-8"))
print("top keys:", list(ga.keys()))
for key in ("entries", "history"):
    rows = ga.get(key, [])
    print(f"== {key}: {len(rows)} rows")
    for r in rows:
        print(f"  [{r.get('ts')}] {r.get('batch')} delta={r.get('cells_ledger_delta')} total_after={r.get('ledger_total_after')}")
