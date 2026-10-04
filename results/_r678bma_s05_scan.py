import json, os, subprocess, hashlib
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
G = r"C:\Users\sjs20\Desktop\FluxGroup"
out = []
orders_dir = os.path.join(B, "fleet", "orders")
order_files = sorted([f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md")])
hb = json.load(open(os.path.join(B, "fleet", "machines", "bm-a.json"), encoding="utf-8"))
acked = hb.get("orders_ack", [])
unacked = [f for f in order_files if f not in acked]
out.append("orders_total=%d acked=%d unacked=%s" % (len(order_files), len(acked), ",".join(unacked) if unacked else "NONE"))
subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True, timeout=90)
p = subprocess.run(["git", "-C", G, "show", "origin/main:docs/decisions.md"], capture_output=True, timeout=60)
dec_sha = hashlib.sha256(p.stdout).hexdigest()
st = json.load(open(os.path.join(B, "state-bm-a.json"), encoding="utf-8"))
wm = st.get("last_decisions_sha")
out.append("decisions_sha256=%s" % dec_sha[:16])
out.append("state_watermark=%s" % (str(wm)[:16] if wm else wm))
out.append("decisions_changed=%s" % (dec_sha != wm))
if dec_sha != wm:
    txt = p.stdout.decode("utf-8", errors="replace")
    lines = txt.strip().splitlines()
    out.append("decisions_last_lines:")
    for l in lines[-30:]:
        out.append("  " + l[:200])
    p2 = subprocess.run(["git", "-C", G, "show", "origin/main:docs/orders.md"], capture_output=True, timeout=60)
    o_txt = p2.stdout.decode("utf-8", errors="replace")
    out.append("group_orders_tail:")
    for l in o_txt.strip().splitlines()[-20:]:
        out.append("  " + l[:200])
    # count orders lines for context
    out.append("dec_sha_full=%s" % dec_sha)
open(os.path.join(B, "results", "_r678bma_s05_scan.json"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
