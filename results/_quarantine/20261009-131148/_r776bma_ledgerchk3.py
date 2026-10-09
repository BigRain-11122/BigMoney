# -*- coding: utf-8 -*-
"""Post-run verification: ledger head contains THEME_DEEPEN_P1 exactly once
+ gate_attrition append-only line (kind=measurement)."""
import json
import sys

sys.path.insert(0, "scripts")
import science_gates as sg

head = sg.ledger_head()
entries = head.get("entries", head) if isinstance(head, dict) else head
hits = []
if isinstance(entries, list):
    hits = [e for e in entries if e.get("batch") == "THEME_DEEPEN_P1"]
print("ledger total:", head.get("total") if isinstance(head, dict) else "?")
print("THEME_DEEPEN_P1 entries:", len(hits))
for h in hits:
    print("  ", json.dumps(h, ensure_ascii=False)[:200])

p = "results/gate_attrition.json"
d = json.load(open(p, encoding="utf-8"))
hist = d.get("history", [])
already = [h for h in hist if h.get("batch") == "THEME_DEEPEN_P1"]
print("gate_attrition existing entries for batch:", len(already))
