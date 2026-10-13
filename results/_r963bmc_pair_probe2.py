# -*- coding: utf-8 -*-
# r963 bm-c continuation pair probe round 2: runtime var definition regions
# (W228 dict, tails, upstream face defs, post-edit gate, family-6 gate code)
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "_w229bmc_freeze_edits.py")
t = open(BASE, "r", encoding="utf-8", newline="").read()
lines = t.split("\n")

def dump(name, pat, before=2, after=8, maxhits=3):
    hits = [i for i, l in enumerate(lines) if re.search(pat, l)]
    out = {"name": name, "pattern": pat, "hits": len(hits), "blocks": []}
    for h in hits[:maxhits]:
        lo = max(0, h - before); hi = min(len(lines), h + after + 1)
        out["blocks"].append({"line": h + 1, "text": "\n".join(lines[lo:hi])})
    return out

probes = [
 dump("w228_dict_def", r"^W228 = |^W228=|W228 = pf", 1, 3, 2),
 dump("a_tail_def", r"w229_a_tail = |w229_a_tail=", 1, 3, 2),
 dump("b_tail_def", r"w229_b_tail = |w229_b_tail=", 1, 3, 2),
 dump("upstream_face_defs", r"w228_freeze_sha = |w228_prereg_sha = ", 0, 6, 2),
 dump("post_edit_gate_line", r"n1_t4\.count\(f\'assert pf\.N1_BANDS\[228\]", 1, 3, 1),
 dump("family6_gate_code", r"MUST move together", 0, 14, 1),
 dump("band_literal", r"\(520_604, 520_803\)", 2, 4, 1),
 dump("probe_receipt_read", r"_w229bmc_20261013_probe_receipt\.json", 0, 3, 3),
 dump("set_wave", r"_set_wave\(229\)", 1, 2, 1),
 dump("arith_defs", r"arith_a229 = |arith_b229 = ", 0, 3, 2),
 dump("n3r1_region", r"n3r1_used229", 0, 3, 1),
 dump("c228_region", r"_c228", 0, 2, 2),
 dump("wv229_colon", r"wave 229: ", 1, 3, 1),
 dump("cfg_new_block", r"new_cfg = \[", 0, 30, 1),
 dump("row_new_block", r"new_row = \[", 0, 14, 1),
 dump("banned_gate", r"banned", 0, 4, 3),
 dump("seed_admit", r"seed_admit", 0, 3, 3),
 dump("wave_configs_assert", r"WAVE_CONFIGS\[229\]", 1, 3, 2),
 dump("bandfacts_assert", r"WAVE_CONFIGS\[228\]", 1, 3, 3),
 dump("pf_mirror_assert", r"pf\.N1_BANDS\[228\]", 0, 2, 6),
 dump("est_ws_83", r"_estate_ws\[83\]", 0, 3, 1),
 dump("hdr_def", r"hdr = \[", 0, 6, 1),
 dump("tail_def", r"^tail = \[", 0, 6, 1),
]
outp = os.path.join(HERE, "_r963bmc_pair_probe2.json")
open(outp, "w", encoding="utf-8").write(json.dumps(probes, indent=1, ensure_ascii=False))
print("WROTE", outp, "probes:", len(probes))
for p in probes:
    print(f"[{p['name']}] hits={p['hits']}")
