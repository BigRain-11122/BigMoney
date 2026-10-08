# -*- coding: utf-8 -*-
import ast
import io
src = io.open(r"results/_r890bma_w189_freeze_edits.py", encoding="utf-8").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return ev(n.left) + ev(n.right)
    if isinstance(n, ast.Name) and n.id == "NL":
        return "\r\n"
    raise AssertionError(ast.dump(n)[:80])


for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) \
       and node.targets[0].id == "MAT_PAIRS" and isinstance(node.value, ast.List):
        pairs = [(ev(e.elts[0]), ev(e.elts[1]), ev(e.elts[2])) for e in node.value.elts]
        print("emitted MAT_PAIRS:", len(pairs))
        for old, new, cnt in pairs:
            if "parity drift" in old:
                print("APPEND PAIR cnt=%d" % cnt)
                print("OLD:", repr(old[:90]))
                print("NEW:", repr(new[:400]))
        break
