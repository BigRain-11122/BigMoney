# r263 bm-b: extract #95 GF higher-moment timing code-cell params (clean-room: param semantics only).
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
TMP = os.environ.get("TEMP", ".")
t = open(os.path.join(TMP, "gf_hmom_nb.ipynb.txt"), encoding="utf-8").read()
print("dump len:", len(t))
cells = re.findall(r"===== cell (\d+) \[(\w+)\] =====\n(.*?)(?====== cell|\Z)", t, re.S)
print("cells:", len(cells))
# print code cells that mention params/keywords, trimmed
KEYS = ["skew", "kurt", "rolling", "window", "threshold", "percentile", "mean", "std", "signal", "position"]
for i, ty, src in cells:
    if ty != "code":
        continue
    body = src.strip()
    if not body or len(body) < 20:
        continue
    low = body.lower()
    if any(k in low for k in KEYS):
        print(f"===== cell {i} [code] ({len(body)} chars) =====")
        print(body[:1800])
        print()
