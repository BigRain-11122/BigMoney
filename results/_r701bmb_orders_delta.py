# r701 bm-b: orders.md delta scan vs r699 baseline (UTF-8 safe file output)
import re

old = open("results/_r699bmb_group_orders.md", encoding="utf-8",
           errors="replace").read().splitlines()
new = open("results/_r701bmb_orders.md", encoding="utf-8",
           errors="replace").read().splitlines()
os_, ns_ = set(l.strip() for l in old if l.strip()), set(
    l.strip() for l in new if l.strip())
added = [l for l in new if l.strip() and l.strip() not in os_]
removed = [l for l in old if l.strip() and l.strip() not in ns_]

BM_PAT = re.compile(r"BigMoney|bigmoney|quant|金融|量化|对冲", re.I)

out = ["added=%d removed=%d" % (len(added), len(removed)), ""]
for l in added:
    hit = " <== BM-RELEVANT" if BM_PAT.search(l) else ""
    out.append("+ " + l + hit)
out.append("")
for l in removed:
    out.append("- " + l)
open("results/_r701bmb_orders_delta.txt", "w", encoding="utf-8").write(
    "\n".join(out))
print("added", len(added), "removed", len(removed),
      "bm_relevant_added",
      sum(1 for l in added if BM_PAT.search(l)))
