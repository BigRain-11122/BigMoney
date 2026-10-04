# -*- coding: utf-8 -*-
# r661 bm-b S0.5 orders diff probe: same-caliber ls-tree vs heartbeat ack (r646 law)
import json, subprocess, io, sys

def ls_orders():
    p = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--", "fleet/orders/"],
                       capture_output=True)
    names = [l for l in p.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    # same caliber: O-*.md only (both sides)
    return set(n.split("/")[-1] for n in names if n.split("/")[-1].startswith("O-") and n.endswith(".md"))

hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
all_orders = ls_orders()
missing = sorted(all_orders - acked)
extra = sorted(acked - all_orders)
out = {
    "machine": "bm-b", "probe": "orders_diff",
    "total_orders_on_origin": len(all_orders),
    "acked_count": len(acked),
    "missing_unacked": missing,
    "acked_but_not_on_origin": extra,
}
with io.open("results/_r661bmb_orders_diff.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("MISSING=", len(missing), missing)
