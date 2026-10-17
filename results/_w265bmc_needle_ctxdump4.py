# -*- coding: utf-8 -*-
# r1084 bm-c: W265 derive ctxdump4 (last faces)
import io, json
t = io.open("results/_w264bmc_freeze_edits.py", encoding="utf-8", newline="").read()
for k in ["_w == 263", "_w == 264", "bm-a (upstream seat honored)", "bm-c (upstream seat honored)",
          "RECEIPT_IN", "results/_w264bmc_20261017_probe_receipt.json",
          "18:2x bm-a r1038 freeze window", "upstream W263)", "W265 FREEZE UNBLOCKED"]:
    print("FACE %-60r = %d" % (k[:60], t.count(k)))
lines = t.split("\n")
for i, l in enumerate(lines):
    if "_w == " in l or "upstream seat honored" in l:
        print("CTX L%d: %s" % (i + 1, l.strip()[:180]))
p = "results/_w265bmc_20261017_probe_receipt.json"
r = json.load(open(p, encoding="utf-8"))
print("RECEIPT verdict =", r.get("verdict"))
print("RECEIPT bands =", r.get("bands"))
print("RECEIPT leg1 =", {k: r.get("legs", {}).get("leg1", {}).get(k) for k in ["A", "B", "hops_A", "hops_B"]})
