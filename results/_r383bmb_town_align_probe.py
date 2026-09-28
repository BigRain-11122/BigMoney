# -*- coding: utf-8 -*-
# r383 bm-b probe 2: systematic diff town.html building mandate faces vs org_chart dept table
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

t = open("town.html", encoding="utf-8").read()
o = open("firm/org_chart.md", encoding="utf-8").read()

# buildings: { id:..., label:..., dept:..., mandate:... } blocks
blds = []
for m in re.finditer(r"\{\s*id:'([^']+)'[^}]*?label:'([^']+)'[^}]*?dept:'([^']+)'[^}]*?mandate:'((?:[^'\\]|\\.)*)'", t, re.S):
    blds.append((m.group(1), m.group(2), m.group(3), m.group(4)))
print("== town buildings ==")
for b in blds:
    print(f"[{b[0]}] label={b[1]} | dept={b[2]}")
    print(f"    mandate={b[3][:150]}")

print()
print("== org_chart dept table (v2 section) ==")
# table rows: | dept | mandate | files | KPI | automation | boss |
for m in re.finditer(r"^\|([^|\n]+)\|([^|\n]+)\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|", o, re.M):
    cells = [c.strip() for c in m.groups()]
    if cells[0] in ("部门", "---") or "mandate" in cells[0] or cells[0].startswith("-"):
        continue
    if len(cells) >= 4:
        print(f"DEPT ROW: {cells[0]}")
        print(f"    mandate={re.sub(r'[**`]', '', cells[1])[:150]}")
        print(f"    KPI={re.sub(r'[**`]', '', cells[3])[:150]}")
