# -*- coding: utf-8 -*-
# r494bma: seed three-step take-number law -- ast-read SEED_REGISTRY int values, pick clean bases.
import ast, sys

src = open("scripts/science_gates.py", encoding="utf-8").read()
tree = ast.parse(src)
reg = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "SEED_REGISTRY":
                reg = ast.literal_eval(node.value)
vals = sorted(v for v in reg.values() if isinstance(v, int) and v > 0)
print("registry int keys:", len(vals))
print("max:", vals[-1], "min:", vals[0])
print("all 203xxxxx values:", [v for v in vals if 20300000 <= v <= 20400000])

# candidate check: base must not equal any registry value and not fall in any
# plausible derived band [base, base+300] of another 203xxxxx key (conservative).
occupied = set()
for v in vals:
    if 20300000 <= v <= 20400000:
        occupied.add(v)
        for d in range(0, 301):
            occupied.add(v + d)
cands = []
b = 20300000
while b < 20400000 and len(cands) < 6:
    if b not in occupied:
        cands.append(b)
        b += 500
    else:
        b += 100
print("candidate clean bases:", cands)
sys.stdout.flush()
