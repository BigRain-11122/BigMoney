# -*- coding: utf-8 -*-
"""r1055 probe: extract P5e face regions from the actual W253 freeze-edits
script + the W254 probe receipt relation_asserts keys, to rebuild the W254
editor P5e chunk needles/values from ground truth."""
import io, json, re

SRC = r"results\_w253bmc_freeze_edits.py"
t = io.open(SRC, encoding="utf-8").read()

def region(start_kw, end_kw, name):
    i0 = t.find(start_kw)
    i1 = t.find(end_kw, i0)
    assert i0 >= 0 and i1 > i0, "region %s anchors not found" % name
    seg = t[i0:i1 + len(end_kw)]
    print("=== %s len=%d ===" % (name, len(seg)))
    print(seg[:1200])
    print("...TAIL:", seg[-260:])
    return seg

hdr = region("# NEW FACE vs the W252 editor", "# B_hop_lands_inside_A=false; hops=1).", "HDR")
bandfacts = region("# W253 FACE (probe receipt leg1 relation_asserts):", "# machine-derived from the LIVE registered row, never transcribed.", "BANDFACTS")
ra = region('ra = leg1.get("relation_asserts") or {}', 'f"probe receipt leg1 relation_asserts face drift: {ra}"', "RA")
pfcmt = region('"    # band gate ADMIT results/_w253bmc_20261016_probe_receipt.json: A = 1-HOP"', '"B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",', "PFCMT")
pre = region(' "wave 253: "', 'no staircase-equality assumption); ADMIT receipt "', "PRE")
pr = region(' "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1', 'chain-order splice from the "', "PR")
tailcmt = region('"        # band facts (law sec.4 W253 row): A = 1-HOP STAIRCASE-AFFECTS-A"', 'no staircase-equality assumption);"', "TAILCMT")

# relation_asserts keys from the actual W254 probe receipt
rec = json.load(io.open(r"results\_w254bmc_20261016_probe_receipt.json", encoding="utf-8"))
print("=== PROBE RECEIPT relation_asserts ===")
leg1 = None
for k, v in rec.items():
    if isinstance(v, dict) and "relation_asserts" in v:
        leg1 = v
        print("leg key:", k)
        print(json.dumps(v.get("relation_asserts"), ensure_ascii=False, indent=1))
        print("bands:", {kk: vv for kk, vv in v.items() if "band" in kk or kk in ("a_lo","a_hi","b_lo","b_hi","hops")})
print("top keys:", list(rec.keys()))
