# -*- coding: utf-8 -*-
# r772 bm-a W157 xform PRE-DIAGNOSTIC: which r769 pair NEW sides still match the
# live W156 prereg (post-r771-editor + post-r772-backfill)? count==1 = clean token
# face; count!=1 = editor-rewritten span -> override needed.
import io

R769 = "results/_r769bma_w156_prereg_xform.py"
src769 = io.open(R769, encoding="utf-8").read()
cut = src769.find("\n# --- sec7/sec8 span replacement")
assert cut > 0
ns = {}
exec(compile(src769[:cut], R769, "exec"), ns)
pairs156 = ns["pairs156"] if "pairs156" in ns else None
if pairs156 is None:
    pairs156 = ns["pairs"]
rep = ns["rep"]
print("pairs156 =", len(pairs156))

live = io.open(r"research/PERPETUAL_N1_W156_PREREG.md", encoding="utf-8").read()
bad = []
for i, (o, n) in enumerate(pairs156):
    c = live.count(n)
    if c != 1:
        bad.append((i, c, n[:90].replace("\n", "\\n")))
print("non-count==1 needles:", len(bad))
for i, c, s in bad:
    print(f"  [{i}] count={c} :: {s}")
