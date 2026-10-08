# -*- coding: utf-8 -*-
"""r890 bm-a: dump the r885 BACK187 faces (src of the r888 roll) to pin the
@KLKEY@/@S51@/@S52@/@S53@/@SEMT@/@KLT@ tail semantics before writing S86."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"results/_r885bma_w187_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK187 = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK187" and \
           isinstance(node.value, ast.List):
            BACK187 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts
                       if isinstance(p, ast.Tuple)]
assert BACK187 is not None
m = dict(BACK187)
for tok in ("@KLKEY@", "@S51@", "@S52@", "@S53@", "@S51B@", "@SEMT@",
            "@KLT@", "@ANCHOR@", "@S5ANCH@", "@TITLE@"):
    v = m[tok]
    print("=== %s (len %d) ===" % (tok, len(v)))
    print(v)
    print()
print("=== @KLT@ tail 120 ===")
print(m["@KLT@"][-120:])
print("=== @SEMT@ tail 120 ===")
print(m["@SEMT@"][-120:])
