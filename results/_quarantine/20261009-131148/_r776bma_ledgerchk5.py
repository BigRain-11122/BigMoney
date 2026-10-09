# -*- coding: utf-8 -*-
"""Verify chain head file + trials_ledger block in batch JSON."""
import json
import sys

sys.path.insert(0, "scripts")
import science_gates as sg

h = sg.ledger_head()
print("head:", json.dumps(h, ensure_ascii=False))
doc = json.load(open("results/theme_deepen_p1/theme_deepen_p1.json", encoding="utf-8"))
print("trials_ledger block:", json.dumps(doc["trials_ledger"], ensure_ascii=False))
print("n_starts_total:", doc["face2"]["n_starts_total"])
print("evidence_cutoff:", doc["evidence_cutoff"])
print("cutoff_meta present:", "science_gates_cutoff_meta" in doc)
print("dropped ids:", [x["id"] for x in doc["face1"]["dropped"]])
print("expansion computed:", [m["id"] for m in doc["face1"]["expansion_events"]])
