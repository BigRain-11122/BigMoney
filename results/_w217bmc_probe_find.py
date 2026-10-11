# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w217bmc_editor_gen.py", encoding="utf-8").read()
marker = "for find, repl, what in E:"
head = src[:src.index(marker)]
g = {"__name__": "drycore"}
exec(compile(head, "gen", "exec"), g)
t = g["t"]

E = [l for l in src.splitlines() if "gate05-print-probe" in l or "bmc_ordinal=46 seat-time" in l]
print("GEN LINES:")
for x in E:
    print(repr(x))

i = t.find("probe receipt leg0 bmc_ordinal=46")
print("ACTUAL:", repr(t[i:i+90]))

find = 'probe receipt leg0 bmc_ordinal=46 seat-time live face disclosed")'
seg = t[i:i+len(find)+4]
print("SEG   :", repr(seg))
mism = None
for k in range(min(len(find), len(seg))):
    if find[k] != seg[k]:
        mism = k
        break
if mism is None:
    print("prefix equal up to", min(len(find), len(seg)))
else:
    print("first mismatch at", mism, repr(find[mism]), repr(seg[mism]))

# also probe the other 5 failing finds' actual regions
probes = {
  "lineage": "Lineage: _w216bmc_freeze_edits.py",
  "print-list": 'W216+W215+W213+W212+W211 finalize',
  "structural": "# (74 rows: estate 69",
  "hdr-rows205": "(engine_owner rows 205 + candidate; gate",
  "receipt-parity": "+ W212 + W213 legs -> W217 block",
}
for name, pat in probes.items():
    j = t.find(pat)
    print(f"--- {name} @ {j}")
    if j >= 0:
        print(repr(t[max(0,j-60):j+200]))
