# -*- coding: utf-8 -*-
"""r890 bm-a: dump key BACK188 faces from the r888 prereg build script
(AST, zero exec) to plan the S86 (W188->W189) fact map."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"results/_r888bma_w188_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK188 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK188" and \
           isinstance(node.value, ast.List):
            BACK188 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts
                       if isinstance(p, ast.Tuple)]
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {ev(k): ev(v) for k, v in
                      zip(node.value.keys, node.value.values)}
assert BACK188 is not None and EXPECT is not None
print("BACK188 pairs:", len(BACK188), "EXPECT:", len(EXPECT))
for tok in ("@TITLE@", "@S51@", "@S51B@", "@S52@", "@S53@", "@KLKEY@",
            "@KLT@", "@SEMT@", "@CHAIN@", "@S5ANCH@", "@ANCHOR@", "@POOL@",
            "@EOB@", "@B@", "@R250@", "@ODOLD@", "@SD@", "@KOLD@",
            "@WPN2@", "@W136TO@", "@W2TO@", "@W1TO@", "@V2W@", "@WN@",
            "@W@", "@N171@", "@N170@", "@N169@", "@AFACE@", "@BFACE@"):
    v = dict(BACK188).get(tok)
    if v is None:
        print("%-11s = <absent>" % tok)
        continue
    s = v if isinstance(v, str) else repr(v)
    print("%-11s = %s" % (tok, s[:300]))
    print(" " * 13 + "..." if len(s) > 300 else "")
print()
zero_exp = [t for t, v in EXPECT.items() if v == 0]
print("EXPECT zero (vestigial):", zero_exp)
print("EXPECT nonzero sample:",
      {t: EXPECT[t] for t in ("@TITLE@", "@B@", "@CHAIN@", "@S52@",
                               "@KLT@", "@SEMT@", "@ANCHOR@", "@POOL@",
                               "@AFACE@", "@BFACE@", "@S55@", "@S53@")})
