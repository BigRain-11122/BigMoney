# -*- coding: utf-8 -*-
"""Post-run ledger verification + gate_attrition line append (append-only)."""
import inspect
import json
import sys
import time

sys.path.insert(0, "scripts")
import science_gates as sg

src = inspect.getsource(sg.append_ledger)
print("--- append_ledger source ---")
print(src[:1200])
print("--- TRIAL LEDGER state ---")
le = getattr(sg, "LEDGER", None) or getattr(sg, "TRIAL_LEDGER", None)
for name in dir(sg):
    if "LEDGER" in name.upper():
        print("attr:", name, str(type(getattr(sg, name))))
