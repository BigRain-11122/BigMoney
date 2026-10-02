# r358 bm-c S0.5: orders diff machine-proof + D-19 group decisions watermark.
# Laws: R13 (no timestamp-filter, full-set machine diff), r292 (raw-blob
# bytes SHA, no PS pipeline), r503 (upper() normalize), D-20260930-13 SLA.
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"

# 1) orders diff (directory O-*.md set minus heartbeat orders_ack set)
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"),
                  "r", encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
orders_dir = os.path.join(ROOT, "fleet", "orders")
orders = {f for f in os.listdir(orders_dir)
          if f.startswith("O-") and f.endswith(".md")}
diff = sorted(orders - ack)
print("ORDERS_DIFF=%s" % (diff if diff else "EMPTY"))
print("n_orders=%d n_ack=%d ack_extra=%s" % (
    len(orders), len(ack), sorted(ack - orders)))

# 2) D-19: group decisions.md content-addressed watermark (raw blob bytes)
subprocess.run(["git", "-C", GROUP, "fetch", "origin"], capture_output=True)
out = subprocess.check_output(["git", "-C", GROUP, "show",
                               "origin/main:docs/decisions.md"])
sha = hashlib.sha256(out).hexdigest().upper()
st = json.load(open(os.path.join(ROOT, "state-bm-c.json"), "r", encoding="utf-8"))
prev = str(st.get("last_decisions_sha", "")).upper()
print("DEC_SHA=%s" % sha)
print("PREV_SHA=%s" % prev)
print("D19_VERDICT=%s" % ("MATCH-unchanged" if sha == prev else "CHANGED"))
