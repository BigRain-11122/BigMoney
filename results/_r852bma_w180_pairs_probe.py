# -*- coding: utf-8 -*-
import io
import ast
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"results\_r849bma_w179_freeze_edits.py", encoding="utf-8").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return ev(n.left) + ev(n.right)
    if isinstance(n, ast.Name) and n.id == "NL":
        return "\r\n"
    raise AssertionError(ast.dump(n)[:60])


P = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
       isinstance(node.targets[0], ast.Name) and \
       node.targets[0].id in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS") and \
       isinstance(node.value, ast.List):
        P[node.targets[0].id] = [(ev(e.elts[0]), ev(e.elts[1]), ev(e.elts[2]))
                                 for e in node.value.elts if isinstance(e, ast.Tuple)]
print("pair counts:", {k: len(v) for k, v in P.items()})
mat = io.open(r"results\_r852bma_w180_probe_n1_mat.txt", encoding="utf-8", newline="").read()
print("stamps with freeze:")
for s in sorted(set(re.findall(r"bm-a r\d+ freeze [0-9a-f]+", mat))):
    print("  ", s, "x", mat.count(s))
print("r307 stamps:")
for s in sorted(set(re.findall(r"\(r307; bm-a r\d+\)", mat))):
    print("  ", s, "x", mat.count(s))
print("chain tail lines:")
i = mat.find("assert pf.N1_BANDS[176]")
print(mat[i:i + 500])
print("--- pair-new containment probes:")
for probe in ("bm-a r845 freeze ", "bm-a r849 freeze,", "r849 bm-a freeze",
              "r849 bm-a] ", "de4716da2", "4c645c95f", "bm-a r845 freeze,"):
    hits = [(k, i) for k in P for i, (o, n, c) in enumerate(P[k]) if probe in n]
    print("  ", repr(probe), "->", hits[:8])
