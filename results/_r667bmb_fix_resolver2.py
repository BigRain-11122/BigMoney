# -*- coding: utf-8 -*-
# surgical fix 2: L106 lambda line closes its own 3 parens but not sorted( -- add one ')' before ':'
import io
p = r"results\_r667bmb_merge_resolve.py"
lines = io.open(p, encoding="utf-8").read().split("\n")
hit = 0
for i, l in enumerate(lines):
    if "key=lambda" in l and '"updated"' in l and l.count("(") == 3 and l.count(")") == 3:
        assert l.rstrip().endswith(":"), "unexpected tail: %r" % l[-8:]
        lines[i] = l.rstrip()[:-1] + "):"
        hit += 1
assert hit == 1, "expected 1 target line, hit %d" % hit
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
import ast
ast.parse(io.open(p, encoding="utf-8").read())
print("surgical fix OK, ast.parse PASS")
