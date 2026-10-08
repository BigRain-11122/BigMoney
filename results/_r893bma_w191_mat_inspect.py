# -*- coding: utf-8 -*-
"""r893 bm-a: AST-extract the r892 EMITTED tool's MAT_PAIRS; print the
tail re-label pairs + the append full-tail composite (S90 grounding)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"results\_r892bma_w190_freeze_edits.py", encoding="utf-8").read()
tree = ast.parse(src)
NL = "\r\n"


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return ev(n.left) + ev(n.right)
    if isinstance(n, ast.Name) and n.id == "NL":
        return NL
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
       isinstance(node.targets[0], ast.Name) and \
       node.targets[0].id == "MAT_PAIRS" and isinstance(node.value, ast.List):
        pairs = []
        for el in node.value.elts:
            assert isinstance(el, ast.Tuple) and len(el.elts) == 3
            pairs.append((ev(el.elts[0]), ev(el.elts[1]), ev(el.elts[2])))
        break
print("MAT_PAIRS count:", len(pairs))
print()
print("== last 6 pairs (tail region) ==")
for old, new, cnt in pairs[-6:]:
    print("OLD>>", repr(old[:300]))
    print("NEW>>", repr(new[:300]))
    print("cnt=", cnt)
    print("---")
print()
print("== longest pair (append composite?) ==")
mx = max(pairs, key=lambda p: len(p[0]))
print("OLD>>", repr(mx[0][:2000]))
print("NEW>>", repr(mx[1][:2000]))
print("cnt=", mx[2], " oldlen=", len(mx[0]), " newlen=", len(mx[1]))
