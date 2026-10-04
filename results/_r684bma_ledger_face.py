"""Locate the actual ledger file face via science_gates internals (zero-write read)."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath("scripts"))
sys.path.insert(0, os.path.abspath("."))
import science_gates as sg

cands = []
for attr in ("LEDGER_FILE", "LEDGER_PATH", "TRIALS_LEDGER"):
    if hasattr(sg, attr):
        cands.append((attr, getattr(sg, attr)))
print("module attrs:", cands)
print("RESULTS_DIR:", getattr(sg, "RESULTS_DIR", None))
head = sg.ledger_head()
print("ledger_head:", head)
for root, dirs, files in os.walk("results"):
    dirs[:] = [d for d in dirs if "quarantine" not in d and "p2cal" not in d and "saturation" not in d and "g2_" not in d]
    for f in files:
        if "ledger" in f.lower() and f.endswith(".json"):
            p = os.path.join(root, f)
            try:
                d = json.load(open(p, encoding="utf-8"))
                if isinstance(d, dict) and "entries" in d:
                    print("LEDGER FACE:", p, "entries:", len(d["entries"]),
                          "tail_total:", d["entries"][-1].get("total") if d.get("entries") else None)
                elif isinstance(d, list):
                    print("ledger-like list:", p, len(d))
            except Exception as e:
                print("unreadable:", p, e)
