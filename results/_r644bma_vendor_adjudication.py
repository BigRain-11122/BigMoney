# -*- coding: utf-8 -*-
"""r644 bm-a: vendor ground-truth adjudication for the 15 r639-flagged
non-derivable tail faces (facts-only, zero network)."""
import os
import re

BASE = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading\src\mlquant\features"
FACES = [
    ("_factors_add.py", "add_004"), ("_factors_add.py", "add_026"),
    ("_factors_add.py", "add_029"), ("_factors_best.py", "best_004"),
    ("_factors_best.py", "best_005"), ("_factors_best.py", "best_011"),
    ("_factors_best.py", "best_015"), ("_factors_better.py", "better_001"),
    ("_factors_better.py", "better_005"), ("_factors_better.py", "better_008"),
    ("_factors_better.py", "better_013"), ("_factors_better.py", "better_014"),
    ("_factors_better.py", "better_022"), ("_factors_better.py", "better_023"),
    ("_factors_extra.py", "extra_001"),
]

PANEL_ATTRS = {"open", "close", "high", "low", "volume", "vwap", "amount",
               "mask", "ret", "returns", "adv20", "cap", "vol"}

for fname, fid in FACES:
    t = open(os.path.join(BASE, fname), encoding="utf-8").read()
    m = re.search(r'@register_legacy_factor\("' + fid + r'"\)\ndef ' + fid +
                  r'\(.*?\n(?=@|\Z)', t, re.S)
    if not m:
        print(fid, "NOT FOUND")
        continue
    body = m.group(0)
    # panel.<attr> accesses
    attrs = sorted(set(re.findall(r"panel\.([a-zA-Z_][a-zA-Z_0-9]*)", body)))
    non_panel = [a for a in attrs if a not in PANEL_ATTRS]
    print(fid, "| panel attrs:", attrs, "| non-panel:", non_panel)
