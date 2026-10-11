# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w217bmc_editor_gen.py", encoding="utf-8").read()
marker = "for find, repl, what in E:"
head = src[:src.index(marker)]
g = {"__name__": "drycore"}
exec(compile(head, "gen", "exec"), g)
t = g["t"]

# 1) full receipt parity note (post-blanket)
i = t.find('"full-span estate W138..W206 (69 rows, r858 absorb generation)')
print("=== receipt parity note region ===")
print(repr(t[i-60:i+560]))

# 2) the extraction comment region
j = t.find("# STRUCTURAL CHOICE: extract the estate")
print("=== extraction comment region ===")
print(repr(t[j:j+430]))

# 3) uniqueness checks for planned fix finds
planned = [
    "Lineage: _w216bmc_freeze_edits.py pattern (proven live-fire freeze,\n# r912 window executed)",
    'f"W216+W215+W213+W212+W211 finalize products present "',
    "bmc_ordinal=46 seat",
    "parity\n# (74 rows: estate 69 + W211 leg + W212 leg + W213 leg + W215 leg + W216 leg).",
    "(engine_owner rows 205 + candidate; gate",
    "(r912 window editor)",
    "own W211 leg + own W212 leg +\n# own W213 leg)",
]
for p in planned:
    print(f"count={t.count(p)} :: {p[:70]!r}")
