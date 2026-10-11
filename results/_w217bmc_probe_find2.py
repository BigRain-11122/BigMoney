# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w217bmc_editor_gen.py", encoding="utf-8").read()
marker = "for find, repl, what in E:"
head = src[:src.index(marker)]
g = {"__name__": "drycore"}
exec(compile(head, "gen", "exec"), g)
t = g["t"]
find = 'probe receipt leg0 bmc_ordinal=46 seat-time live face disclosed")'
i = t.find("probe receipt leg0 bmc_ordinal=46")
seg = t[i:i+len(find)+4]
print("len(find) =", len(find))
print("find[55:75] =", repr(find[55:75]))
print("seg [55:75] =", repr(seg[55:75]))
for k in range(55, 75):
    if k < len(find) and k < len(seg):
        print(k, repr(find[k]), repr(seg[k]), "SAME" if find[k] == seg[k] else "DIFF")
