# -*- coding: utf-8 -*-
# r1020 bm-a: ORD delta fe846588 -> current (boundary = last row consumed by r1019 commit 4c403cb16)
import subprocess, hashlib, sys
sys.stdout.reconfigure(encoding="utf-8")

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
rc = subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True).returncode
out = subprocess.run(["git", "-C", GRP, "show", "origin/main:docs/orders.md"], capture_output=True).stdout
sha = hashlib.sha256(out).hexdigest()
text = out.decode("utf-8", "replace")
print("current_ord_sha", sha[:16], "fetch_rc", rc)

BOUNDARY = "前三波深研收口"  # last row of r1019-consumed delta (fe846588 face)
lines = text.splitlines()
bidx = -1
for i, ln in enumerate(lines):
    if BOUNDARY in ln and ln.strip().startswith("|"):
        bidx = i
print("boundary_idx", bidx, "total_lines", len(lines))
new = [ln for ln in lines[bidx + 1:] if ln.strip().startswith("|")]
print("new_rows_total", len(new))
for ln in new:
    tag = "BM" if ("bigmoney" in ln.lower() or "quant" in ln.lower()) else "  "
    print(tag, "|", ln[:230])
