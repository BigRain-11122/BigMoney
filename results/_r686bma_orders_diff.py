import json, subprocess, os
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
# orders on origin (full file names with .md suffix - r477 form law)
r = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", "origin/main", "fleet/orders/"], capture_output=True)
orders = set()
for ln in r.stdout.decode('utf-8').splitlines():
    base = os.path.basename(ln)
    if base.startswith("O-") and base.endswith(".md"):
        orders.add(base)
# heartbeat ack (bm-a)
with open(os.path.join(repo, "fleet", "machines", "bm-a.json"), "rb") as f:
    hb = json.loads(f.read().decode('utf-8'))
acked = set(hb.get("orders_ack", []))
unacked = sorted(orders - acked)
print("total orders:", len(orders), " acked:", len(acked), " unacked:", len(unacked))
for u in unacked:
    print("UNACKED:", u)
