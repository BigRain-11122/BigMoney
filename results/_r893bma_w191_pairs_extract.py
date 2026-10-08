# -*- coding: utf-8 -*-
"""r893 bm-a: AST-extract ALL pair lists (PF/EN/MAT/CL) from the r892
EMITTED tool; dump (old,new,cnt) triples to a UTF-8 text file for S90
construction analysis."""
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


out = io.open(r"results\_r893bma_w191_pairs_dump.txt", "w",
              encoding="utf-8", newline="\n")
for name in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
    got = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
           isinstance(node.targets[0], ast.Name) and \
           node.targets[0].id == name and isinstance(node.value, ast.List):
            got = []
            for el in node.value.elts:
                assert isinstance(el, ast.Tuple) and len(el.elts) == 3
                got.append((ev(el.elts[0]), ev(el.elts[1]), ev(el.elts[2])))
            break
    assert got is not None, name
    out.write("##### %s (%d pairs) #####\n" % (name, len(got)))
    for k, (o, n, c) in enumerate(got):
        out.write("--- %s[%d] cnt=%d\nOLD:: %s\nNEW:: %s\n" %
                  (name, k, c, o, n))
    print(name, len(got))
out.close()
print("dumped to results/_r893bma_w191_pairs_dump.txt")
