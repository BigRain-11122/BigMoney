# -*- coding: utf-8 -*-
"""r893 bm-a DRY-debug2: replicate the r892 EMITTED tool's TOK loop
against ITS OWN src (W189 freeze blob 735f7c288 + registry patch) and
count the @N171@='190' vestigial strays -- resolve how the r892 run
passed the same check that fails for W191."""
import ast
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
blob = subprocess.run(
    ["git", "show", "632761894:research/PERPETUAL_N1_W189_PREREG.md"],
    capture_output=True).stdout.decode("utf-8")
assert "SEED_REGISTRY \u5168\u952e 189 \u503c" in blob
SRC0 = blob.replace("SEED_REGISTRY \u5168\u952e 189 \u503c",
                    "SEED_REGISTRY \u5168\u952e 190 \u503c")
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

out_t = SRC0
miss = 0
for old, tok in [(v, t) for (t, v) in BACK210]:
    exp = EXPECT[tok]
    if exp == 0:
        stripped = out_t.replace("MSG-183x", "")
        n = stripped.count(old)
        tag = "VESTIGIAL %s stray=%d" % (tok, n)
        print(tag, old[:30].encode("unicode_escape").decode("ascii"))
        continue
    n = out_t.count(old)
    if n != exp:
        miss += 1
        print("TOK MISS", tok, n, exp)
        continue
    out_t = out_t.replace(old, tok)
print("misses:", miss)
import re  # noqa: E402
stripped = out_t.replace("MSG-183x", "")
for tok in ("@N171@", "@N170@", "@N169@"):
    old = dict(BACK210)[tok]
    n = stripped.count(old)
    print("FINAL", tok, "old=", old, "stray=", n)
