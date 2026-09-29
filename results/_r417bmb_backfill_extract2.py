# -*- coding: utf-8 -*-
"""r417 bm-b: W1-W5 sec.5 predictions + attrition rows + screen ledger hops (read-only)."""
import json
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"E:\Fluxgroup\FluxGroup\quant\bigmoney"


def sec5(w):
    p = os.path.join(ROOT, "research", f"TRIAL_LABOR_{w}_PREREG.md")
    t = io.open(p, encoding="utf-8").read()
    i = t.find("## §5")
    j = t.find("## §6")
    return t[i:j]


for w in ("W1", "W2", "W3", "W4", "W5"):
    print("=" * 25, w, "sec.5")
    print(sec5(w)[:2400])
    print()

# screen ledger hops
print("=" * 25, "screen trials_ledger hops")
for n in (1, 2, 3, 4, 5, 6):
    s = json.load(io.open(os.path.join(ROOT, "results", f"trial_labor_w{n}", f"w{n}_screen.json"), encoding="utf-8"))
    tl = s.get("trials_ledger", {})
    print(f"W{n} screen ledger:", json.dumps(tl, ensure_ascii=False)[:220])

# attrition rows for the trial-labor batches
print("=" * 25, "gate_attrition trial-labor rows")
ga = json.load(io.open(os.path.join(ROOT, "results", "gate_attrition.json"), encoding="utf-8"))
rows = ga.get("entries", []) + ga.get("history", [])
for r in rows:
    b = str(r.get("batch", ""))
    if "TRIAL_LAB" in b or "MASS_TRIAL" in b:
        print(json.dumps(r, ensure_ascii=False)[:320])
