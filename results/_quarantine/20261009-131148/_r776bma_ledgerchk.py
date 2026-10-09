# -*- coding: utf-8 -*-
"""Check gate_attrition.json tail + trial ledger tail (post-run verification)."""
import json
import os

p = "results/gate_attrition.json"
if os.path.exists(p):
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, dict):
        hist = d.get("history", [])
        print("gate_attrition history tail:")
        for h in hist[-3:]:
            print(" ", json.dumps(h, ensure_ascii=False)[:200])
        kinds = [h.get("kind") for h in hist[-5:]]
        print("last kinds:", kinds)
    else:
        print("gate_attrition list len:", len(d))
        for h in d[-2:]:
            print(" ", json.dumps(h, ensure_ascii=False)[:200])
else:
    print("no gate_attrition.json")

# find the trial ledger file appended by science_gates.append_ledger
for cand in ("research/TRIAL_LEDGER.json", "results/trial_ledger.json",
             "research/BACKTEST_PLAN.md"):
    if os.path.exists(cand):
        print("exists:", cand)
import science_gates as sg
import inspect
src = inspect.getsource(sg.append_ledger)
print("--- append_ledger source head ---")
print(src[:900])
