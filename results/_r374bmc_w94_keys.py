# -*- coding: utf-8 -*-
"""r374 bm-c: W94 finalize full key dump (W99 prereg sec.5 anchor source) +
summary-segment exact anchor bytes."""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

w94 = json.load(open(os.path.join(REPO, "results", "perpetual_faces",
                                 "n1_w94_results.json"), encoding="utf-8"))
print("== W94 TOP KEYS ==")
print(sorted(w94.keys()))
print("== FULL DUMP (compact, 4000 chars) ==")
print(json.dumps(w94, ensure_ascii=False)[:4000])

n1 = open(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), "rb").read().decode("utf-8")
print("== SUMMARY ANCHOR EXACT ==")
needle = '"law sec.4 W98 row, r582 bm-a] "'
print("count:", n1.count(needle))
k = n1.find(needle)
print(repr(n1[k - 120:k + 200]))
