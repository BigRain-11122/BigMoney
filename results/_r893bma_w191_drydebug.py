# -*- coding: utf-8 -*-
"""r893 bm-a DRY-debug: locate the residual '190' stray context in the
tokenized W190 freeze src (vestigial @N171@ check)."""
import ast
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
blob = open(r"results/_r893bma_w191_prereg_src.txt", "rb").read().decode("utf-8")
src892 = io.open(r"results/_r892bma_w190_prereg_build.py",
                 encoding="utf-8").read()
tree = ast.parse(src892)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError(ast.dump(n)[:60])


BACK210 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK210" and \
           isinstance(node.value, ast.List):
            BACK210 = [(ev(p.elts[0]), ev(p.elts[1]))
                       for p in node.value.elts]
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {ev(k): ev(v) for k, v in
                      zip(node.value.keys, node.value.values)}

# registry patch (no-op this generation)
SRC0 = blob.replace("SEED_REGISTRY \u5168\u952e 190 \u503c",
                    "SEED_REGISTRY \u5168\u952e 190 \u503c")
out_t = SRC0
for old, tok in [(v, t) for (t, v) in BACK210]:
    exp = EXPECT[tok]
    if exp == 0:
        continue
    n = out_t.count(old)
    if n != exp:
        print("TOK MISS", tok, "count", n, "expect", exp)
        continue
    out_t = out_t.replace(old, tok)
stripped = out_t.replace("MSG-183x", "")
for m in re.finditer(r"190", stripped):
    i = m.start()
    print("STRAY@%d:" % i, stripped[max(0, i - 60):i + 60]
          .encode("unicode_escape").decode("ascii"))
# also: which tokens did the r892 tool NOT find in the W190 src?
print("---")
for old, tok in [(v, t) for (t, v) in BACK210]:
    exp = EXPECT[tok]
    if exp == 0:
        continue
    n = SRC0.count(old)
    if n != exp:
        print("SRC COUNT MISMATCH", tok, n, exp)
