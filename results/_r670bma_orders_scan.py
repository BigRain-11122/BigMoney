# r670 bm-a S0.5: orders full-scan vs heartbeat orders_ack diff (canon: ls-tree vs local set, same-caliber)
import json, subprocess, os

def ls_tree_orders():
    b = subprocess.run(["git", "ls-tree", "origin/main", "--name-only", "fleet/orders/"], capture_output=True).stdout
    return set(x for x in b.decode("utf-8").splitlines() if x.strip().endswith(".md") and os.path.basename(x).startswith("O-"))

def ls_local_orders():
    p = "fleet/orders"
    try:
        return set(os.path.join(p, f).replace("\\", "/") for f in os.listdir(p) if f.startswith("O-") and f.endswith(".md"))
    except FileNotFoundError:
        return set()

remote = ls_tree_orders()
local = ls_local_orders()
print("remote O count:", len(remote), "local O count:", len(local))
only_remote = sorted(remote - local)
only_local = sorted(local - remote)
print("only in remote (need pull/pull missed):", only_remote)
print("only in local (unpushed?):", only_local)

hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
ack = hb.get("orders_ack", {})
print("heartbeat orders_ack entries:", len(ack))
remote_names = {os.path.basename(x): x for x in remote}
unacked = sorted(n for n in remote_names if n not in ack)
print("UNACKED orders (count=%d):" % len(unacked))
for n in unacked:
    print("  ", n)
