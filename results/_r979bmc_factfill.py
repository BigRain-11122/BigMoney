# -*- coding: utf-8 -*-
"""r979 fact-fill probe: remaining W235 editor facts."""
import io, re
t = io.open(r"results\_w234bmc_freeze_edits.py", encoding="utf-8", newline="").read()
print("=== base transitive/prose counts ===")
for n in ["934,189", "508,320", "931,989", "w233_transitive", '"w232_transitive"',
          "(92 rows: estate 69", "r976 (seat", "r973 (seat", "executed bm-c r973",
          "probe receipt @ r976 window", "r976 continuation", "NINETEEN", "EIGHTEEN",
          "46/46", "79 pairs", "preflight", "replay"]:
    print("%-40r %d" % (n, t.count(n)))
print()
print("=== receipt note (prereg provenance) full block ===")
m = t.index('"prereg_sha": w234_prereg_sha')
print(repr(t[max(0, m-400):m+700]))
print()
print("=== P9 region (seat/prose) ===")
for mm in list(re.finditer(re.escape("executed bm-c r973"), t))[:3]:
    print(repr(t[max(0, mm.start()-260):mm.start()+330]))
    print("---")
print()
print("=== structural-choice line ===")
mm = t.index("structure known")
print(repr(t[max(0, mm-260):mm+60]))
print()
print("=== upstream_cycle / receipt note faces (search 'repair_chain_note') ===")
for mm in list(re.finditer("repair_chain_note", t))[:3]:
    print(repr(t[max(0, mm.start()-120):mm.start()+420]))
    print("---")
print()
print("=== W235 prereg md provenance faces ===")
p = io.open(r"research/PERPETUAL_N1_W235_PREREG.md", encoding="utf-8", newline="").read()
for pat in ["replay", "preflight", "level", "46", "STALE", "NEW", "takeover", "bm-a"]:
    ms = list(re.finditer(re.escape(pat), p))
    print("--", pat, len(ms))
    for mm in ms[:2]:
        print("   ", repr(p[max(0, mm.start()-80):mm.start()+100].replace("\n", "\\n")))
