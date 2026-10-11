# -*- coding: utf-8 -*-
# _r860bmc_resolve_pool.py - resolve UU block in results/runnable_pool.json (bm-b claim wins per commit-time law)
import io, json

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\runnable_pool.json"
body = io.open(P, encoding="utf-8").read()

old = (
    "<<<<<<< HEAD\n"
    "     \"owner\": \"bm-b\",\n"
    "     \"owner_since\": \"2026-10-11 08:08:08\"\n"
    "||||||| parent of 0ab7c2bb4 (autofill tick claim n2-mp1-run-0of1 owner=bm-c (r199 launch-claim + r290 self-commit) [via bm-c])\n"
    "     \"owner\": \"bm-b\",\n"
    "     \"owner_since\": \"2026-10-11 07:42:11\"\n"
    "=======\n"
    "     \"owner\": \"bm-c\",\n"
    "     \"owner_since\": \"2026-10-11 08:04:38\"\n"
    ">>>>>>> 0ab7c2bb4 (autofill tick claim n2-mp1-run-0of1 owner=bm-c (r199 launch-claim + r290 self-commit) [via bm-c])\n"
)
new = (
    "     \"owner\": \"bm-b\",\n"
    "     \"owner_since\": \"2026-10-11 08:08:08\"\n"
)
assert old in body, "conflict block not found verbatim"
body = body.replace(old, new)
d = json.loads(body)
io.open(P, "w", encoding="utf-8", newline="").write(body)
found = []
def walk(o):
    if isinstance(o, dict):
        if o.get("key") == "n2-mp1-run-0of1":
            found.append((o.get("owner"), o.get("owner_since"), o.get("status")))
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
walk(d)
assert "<<<<<<<" not in body and ">>>>>>>" not in body, "markers remain"
print("RESOLVED json-valid entry:", found)
