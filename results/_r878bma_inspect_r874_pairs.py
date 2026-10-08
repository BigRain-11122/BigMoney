# -*- coding: utf-8 -*-
import ast, io
src = io.open(r"results/_r874bma_w184_freeze_edits.py", encoding="utf-8").read()
tree = ast.parse(src)

def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return ev(n.left) + ev(n.right)
    if isinstance(n, ast.Name) and n.id == "NL":
        return "\r\n"
    raise AssertionError("unsupported node")

PAIRS = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
       isinstance(node.targets[0], ast.Name) and \
       node.targets[0].id in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS") and \
       isinstance(node.value, ast.List):
        out = []
        for el in node.value.elts:
            out.append((ev(el.elts[0]), ev(el.elts[1]), ev(el.elts[2])))
        PAIRS[node.targets[0].id] = out

for k in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
    print("=====", k, len(PAIRS[k]))
    for i, (old, new, cnt) in enumerate(PAIRS[k]):
        print("[%d] cnt=%d old[%d]=%r ... new[%d]=%r ..." % (
            i, cnt, len(old), old[:60], len(new), new[-70:] if len(new) > len(old) else new[:70]))
