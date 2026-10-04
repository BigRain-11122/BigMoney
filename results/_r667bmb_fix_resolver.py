# -*- coding: utf-8 -*-
# one-line fixer: repair unbalanced lambda paren in _r667bmb_merge_resolve.py line ~106
import io
p = r"results\_r667bmb_merge_resolve.py"
src = io.open(p, encoding="utf-8").read()
lines = src.split("\n")
hit = 0
for i, l in enumerate(lines):
    if "key=lambda" in l and '"updated"' in l and l.count(")") + 1 == l.count("("):
        lines[i] = l.replace('""")):', '"""))):')
        hit += 1
assert hit == 1, "fixer expected exactly 1 target line, hit %d" % hit
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
import ast
ast.parse(io.open(p, encoding="utf-8").read())
print("fixer OK, ast.parse PASS")
