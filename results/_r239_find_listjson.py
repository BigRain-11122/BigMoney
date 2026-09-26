# -*- coding: utf-8 -*-
"""Find list-shaped top-level JSONs under results/ that crash science_gates.ledger_head."""
import glob
import json
import os

hits = []
for path in glob.glob(os.path.join("results", "**", "*.json"), recursive=True):
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:
        continue
    if isinstance(d, list):
        hits.append((path, len(d)))
for p, n in hits:
    print(p, "list len", n, "| mtime", __import__("time").strftime("%Y-%m-%d %H:%M:%S", __import__("time").localtime(os.path.getmtime(p))))
print("total list-shaped:", len(hits))
