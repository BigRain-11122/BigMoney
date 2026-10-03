# -*- coding: utf-8 -*-
"""r644 bm-a: mechanical BAN pre-read for the 71-face tail roster
(same classify rule as scripts/g2_slot_stock_p1.py classify_ban, prefix
filter widened to tail families + old-correction faces). Facts only."""
import json
import re

import sys
sys.path.insert(0, ".")
from scripts.g2_slot_stock_p1 import PANEL_INPUTS, VOLUME_TOKENS, PRICE_CHANGE_PAT  # noqa: E402

probe = json.load(open("results/_r644bma_slot_tail_roster_probe.json", encoding="utf-8"))
faces = probe["roster_freeze"]["burn_faces"]
c = json.load(open("results/g2_overlap_census_p2.json", encoding="utf-8"))
rows = {r["face"]: r for r in c["rows"]}

from collections import Counter
cnt = Counter()
banned = []
for f in faces:
    formula = rows.get(f, {}).get("doc_formula") or ""
    toks = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", formula))
    has_volume = bool(toks & VOLUME_TOKENS)
    change_content = bool(PRICE_CHANGE_PAT.search(formula))
    if not has_volume:
        cls = "price_banned" if change_content else "price_other"
    else:
        cls = "volume_price"
    cnt[cls] += 1
    if cls == "price_banned":
        banned.append((f, formula[:60]))

print(dict(cnt), "total", len(faces))
for f, fo in banned:
    print("BANNED:", f, "|", fo)
# per-family breakdown
fam_cnt = {}
for f in faces:
    formula = rows.get(f, {}).get("doc_formula") or ""
    toks = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", formula))
    cls = ("volume_price" if (toks & VOLUME_TOKENS)
           else ("price_banned" if PRICE_CHANGE_PAT.search(formula) else "price_other"))
    fam = f.rsplit("_", 1)[0]
    fam_cnt.setdefault(fam, Counter())[cls] += 1
for fam, cc in sorted(fam_cnt.items()):
    print(fam, dict(cc))
