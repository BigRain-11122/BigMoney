# -*- coding: utf-8 -*-
"""r677 S0.5 probe: orders diff-set vs heartbeat ack + D-19 decisions/orders watermark (raw-bytes law r660)."""
import json, subprocess, sys, io, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
OUT = os.path.join(REPO, "results", "_r677bma_s05_probe.json")
res = {}

# 1) orders set-compare (both sides same-caliber: O-*.md basename set from disk)
orders_dir = os.path.join(REPO, "fleet", "orders")
disk = sorted(f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md"))
res["orders_disk_count"] = len(disk)

hb_path = os.path.join(REPO, "fleet", "machines", "bm-a.json")
with open(hb_path, "r", encoding="utf-8") as f:
    hb = json.load(f)
ack = set(hb.get("orders_ack", []))
res["orders_ack_count"] = len(ack)
disk_set = set(disk)
unacked = sorted(disk_set - ack)
res["unacked_orders"] = unacked
# acked-but-gone (should be empty)
res["ghost_ack"] = sorted(ack - disk_set)

# 2) D-19 decisions/orders watermark: git show origin/main raw bytes -> sha256 (r660 law)
GROUP = r"K:\Fluxgroup\FluxGroup"
if not os.path.isdir(GROUP):
    GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
def blob_sha(repo, path):
    p = subprocess.run(["git", "-C", repo, "show", "origin/main:" + path],
                       capture_output=True)
    if p.returncode != 0:
        return {"error": p.stderr.decode("utf-8", "replace")[:200]}
    import hashlib
    return {"sha256": hashlib.sha256(p.stdout).hexdigest(), "bytes": len(p.stdout)}

res["group_tree_present"] = os.path.isdir(GROUP)
# fresh fetch (zero tree touch)
if res["group_tree_present"]:
    subprocess.run(["git", "-C", GROUP, "fetch", "origin"], capture_output=True)
    res["decisions_origin"] = blob_sha(GROUP, "docs/decisions.md")
    res["group_orders_origin"] = blob_sha(GROUP, "docs/orders.md")
else:
    res["decisions_origin"] = {"error": "group tree absent"}
    res["group_orders_origin"] = {"error": "group tree absent"}

# 3) compare with state watermark keys
with open(os.path.join(REPO, "state-bm-a.json"), "r", encoding="utf-8") as f:
    st = json.load(f)
res["state_watermarks"] = {k: v for k, v in st.items() if "sha" in k.lower() or "watermark" in k.lower()}
res["state_round_no"] = st.get("round_no")
res["match_decisions"] = res["state_watermarks"].get("last_decisions_sha") == res["decisions_origin"].get("sha256")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("PROBE-OK unacked=%d decisions_match=%s" % (len(unacked), res["match_decisions"]))
