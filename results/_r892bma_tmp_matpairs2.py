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


for name in ("MAT_PAIRS",):
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) \
           and node.targets[0].id == name and isinstance(node.value, ast.List):
            pairs = [(ev(e.elts[0]), ev(e.elts[1]), ev(e.elts[2])) for e in node.value.elts]
            print(name, "count:", len(pairs))
            for i, (old, new, cnt) in enumerate(pairs):
                if "parity drift" in old or "parity drift" in new or "426_204" in old \
                   or old == new:
                    print("[%d] cnt=%d" % (i, cnt))
                    print("  OLD:", repr(old[:150]))
                    print("  NEW:", repr(new[:200]))
            break
# also look at MAT_NEG
for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) \
       and node.targets[0].id == "MAT_NEG" and isinstance(node.value, ast.List):
        negs = [ev(e) for e in node.value.elts]
        print("MAT_NEG count:", len(negs))
        for n in negs:
            if "parity" in n or "886" in n or "W187" in n:
                print("  NEG:", repr(n))
        break
