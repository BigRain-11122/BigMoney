"""r837 bm-c heartbeat orders_ack surgery (r818 load-modify-save law):
1. normalize 'O-...' entries to canonical '<name>.md' form (r836 wrote
   O-20261010-1906-bm-c without the .md suffix = the live false-positive
   that re-flagged an acked order);
2. append the O-20261010-1945-bm-a.md ack (consumed this round);
3. pass-through non-O- legacy entries verbatim (README.md = committed
   legacy scanner artifact, fleet/orders/README.md is a real non-order
   file; NOT deleted without archaeology - honest note in round report)."""

import json

HB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"
NEW_ACK = "O-20261010-1945-bm-a.md"

hb = json.load(open(HB, encoding="utf-8"))
acks = hb.get("orders_ack", [])
fixed = []
changed = 0
for a in acks:
    if isinstance(a, str) and a.startswith("O-"):
        s = a[:-3] if a.endswith(".md") else a
        canon = s + ".md"
        if canon != a:
            changed += 1
        fixed.append(canon)
    else:
        fixed.append(a)  # legacy pass-through
appended = False
if NEW_ACK not in fixed:
    fixed.append(NEW_ACK)
    appended = True
assert fixed.count(NEW_ACK) == 1
hb["orders_ack"] = fixed
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
rb = json.load(open(HB, encoding="utf-8"))
assert rb["orders_ack"] == fixed and len(fixed) == len(acks) + (1 if appended else 0)
print("acks n=%d normalized=%d appended=%s" % (len(fixed), changed, appended))
