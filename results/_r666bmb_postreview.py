# -*- coding: utf-8 -*-
# r666 bm-b post_review REPORT face check (r660: official REPORT face, not raw ledger)
import glob, io

fs = sorted(glob.glob(r"results\post_review\REPORT-*.md"))
f = fs[-1]
t = io.open(f, encoding="utf-8", errors="replace").read()
rows = [l for l in t.splitlines() if ("✗" in l or "判定分布" in l or "✓" in l)]
out = io.open(r"results\_r666bmb_postreview.txt", "w", encoding="utf-8")
out.write("latest: %s\n" % f)
for l in rows[-8:]:
    out.write(l[:200] + "\n")
out.close()
print("written", len(rows))
