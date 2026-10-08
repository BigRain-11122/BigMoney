# -*- coding: utf-8 -*-
"""r893 bm-a: extract BACK210 + EXPECT from the r892 EMITTED tool
(_r892bma_w190_prereg_build.py) -- the extraction-from-emission source
for the W191 buildgen.  Prints each token's W190-era value in
unicode-escaped form (console-safe, r666 mojibake law)."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = io.open(r"results\_r892bma_w190_prereg_build.py",
              encoding="utf-8").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK210 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK210" and \
           isinstance(node.value, ast.List):
            BACK210 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2
                BACK210.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK210 is not None and EXPECT is not None
assert len(BACK210) == 50 and len(EXPECT) == 50, (len(BACK210), len(EXPECT))
print("pairs:", len(BACK210), "expect:", len(EXPECT))
for tok, val in BACK210:
    e = EXPECT[tok]
    v = val.encode("unicode_escape").decode("ascii")
    print("@@%s|%d|%s" % (tok, e, v[:400]))
