# -*- coding: utf-8 -*-
# r1007 bm-a: W244 freeze editor gen-comma repair v2 (AST-precise).
# Rule: inside the editor's List literals, every element is a single-line
# string. An element spanning >1 physical line = implicit string concat from a
# gen-SUB that dropped trailing commas = BUG (print()/paren concats outside
# lists are intentional and are NOT flagged). Fix = append ',' to every
# physical line of the element except the last.
import io, ast, py_compile

P = "results/_w244bma_freeze_edits.py"
src = io.open(P, "r", encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in src[:5000] else "\n"
lines = src.split(nl)

tree = ast.parse(src)
fixes = []  # (lineno, linode_index)
for node in ast.walk(tree):
    if isinstance(node, ast.List):
        for elt in node.elts:
            if getattr(elt, "end_lineno", None) and elt.end_lineno > elt.lineno:
                for ln in range(elt.lineno, elt.end_lineno):
                    idx = ln - 1
                    t = lines[idx].rstrip()
                    assert not t.endswith(","), f"L{ln} already has comma?"
                    assert not t.endswith("\\"), f"L{ln} ends with continuation backslash -- unexpected"
                    fixes.append(idx)

got = sorted(x + 1 for x in fixes)
print("AST concat-in-list element lines to comma:", got)
EXPECT = [408, 553, 554, 555, 556, 618, 619]
assert got == EXPECT, f"unexpected set {got} != {EXPECT}"

for idx in fixes:
    raw = lines[idx]
    cr = "\r" if raw.endswith("\r") else ""
    lines[idx] = raw.rstrip() + "," + cr
io.open(P, "w", encoding="utf-8", newline="").write(nl.join(lines))
py_compile.compile(P, doraise=True)
print(f"FIXED {len(fixes)} commas; editor compiles OK")

# verify: reparse -> zero multi-line list elements remain
src2 = io.open(P, "r", encoding="utf-8", newline="").read()
tree2 = ast.parse(src2)
bad = [ (e.lineno, e.end_lineno) for n in ast.walk(tree2) if isinstance(n, ast.List)
        for e in n.elts if getattr(e, "end_lineno", None) and e.end_lineno > e.lineno ]
assert not bad, f"residual multi-line list elements: {bad}"
print("reparse: zero implicit-concat list elements remain")
