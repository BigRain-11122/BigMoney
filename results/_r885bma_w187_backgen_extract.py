# -*- coding: utf-8 -*-
"""r885 bm-a W187 prereg buildgen helper: AST-extract TOK186/BACK186/EXPECT
from the r881 build script (no exec of its live asserts)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"results/_r881bma_w186_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


out = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id in ("TOK186", "BACK186", "EXPECT") \
           and isinstance(node.value, (ast.List, ast.Dict)):
            if isinstance(node.value, ast.List):
                pairs = []
                for el in node.value.elts:
                    if isinstance(el, ast.Tuple) and len(el.elts) == 2:
                        pairs.append((ev(el.elts[0]), ev(el.elts[1])))
                    elif isinstance(el, ast.Tuple) and len(el.elts) == 3:
                        # TOK186 triplets (old, tok, count-not-used in 186 form?)
                        pairs.append((ev(el.elts[0]), ev(el.elts[1])))
                    else:
                        pairs.append(("UNSUPPORTED", ast.dump(el)[:60]))
                out[tg.id] = pairs
            else:
                d = {}
                for k, v in zip(node.value.keys, node.value.values):
                    d[ev(k)] = ev(v)
                out[tg.id] = d

print("extracted:", {k: (len(v) if hasattr(v, "__len__") else v)
                     for k, v in out.items()})
if "BACK186" in out:
    with open(r"results\_r885bma_w187_back186_dump.txt", "w", encoding="utf-8") as f:
        for tok, val in out["BACK186"]:
            f.write("=== %s ===\n%s\n\n" % (tok, val))
    print("BACK186 dumped to results/_r885bma_w187_back186_dump.txt")
