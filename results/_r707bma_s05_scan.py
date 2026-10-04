# r707 bm-a S0.5 orders scan: same-form full-name set-diff (r477 law) + D-19 dual-key check
import json, os, glob, hashlib, subprocess, io

# 1) orders set-diff
order_files = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
h = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
ack = h.get("orders_ack", [])
acked = set(ack)
present = set(order_files)
unacked = sorted(present - acked)
print("orders present:", len(present), "| acked:", len(acked), "| unacked:", len(unacked))
for u in unacked:
    print("  UNACKED:", u)

# 2) D-19 dual-key: group tree via Desktop real-path fetch + git show raw bytes (r660/r689 law)
GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
r = subprocess.run(["git", "-C", GROUP, "fetch", "origin"], capture_output=True)
print("group fetch rc:", r.returncode, r.stderr.decode("utf-8", "replace")[-100:] if r.returncode else "")
def blob(path):
    rr = subprocess.run(["git", "-C", GROUP, "show", f"origin/main:{path}"], capture_output=True)
    return rr.stdout
dec = blob("docs/decisions.md")
orders_group = blob("docs/orders.md")
sha_dec = hashlib.sha256(dec).hexdigest()
sha_ord = hashlib.sha256(orders_group).hexdigest()
st = json.load(io.open("state-bm-a.json", encoding="utf-8"))
print("decisions sha:", sha_dec[:16], "state:", str(st.get("last_decisions_sha", ""))[:16],
      "MATCH" if sha_dec == st.get("last_decisions_sha") else "CHANGED")
print("orders sha:", sha_ord[:16], "state:", str(st.get("last_orders_sha", ""))[:16],
      "MATCH" if sha_ord == st.get("last_orders_sha") else "CHANGED")
