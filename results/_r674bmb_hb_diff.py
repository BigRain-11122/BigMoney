# -*- coding: utf-8 -*-
# r674 bm-b push-race resolve prep: origin bm-b.json vs local (subprocess raw bytes, r660/pit-ps law)
import subprocess, json, os

r = subprocess.run(["git", "show", "origin/main:fleet/machinesines/bm-b.json"], capture_output=True)
r = subprocess.run(["git", "show", "origin/main:fleet/machines/bm-b.json"], capture_output=True)
assert r.returncode == 0, r.stderr.decode()[:200]
ob = json.loads(r.stdout.decode("utf-8"))
lb = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))

sa, sb = set(lb.get("orders_ack", [])), set(ob.get("orders_ack", []))
out = {
    "mine_ack": len(sa), "theirs_ack": len(sb),
    "theirs_only": sorted(sb - sa), "mine_only": sorted(sa - sb),
    "theirs_last_seen": ob.get("last_seen"), "theirs_epoch": ob.get("heartbeat_epoch_utc"),
    "mine_last_seen": lb.get("last_seen"), "mine_epoch": lb.get("heartbeat_epoch_utc"),
    "theirs_keys": sorted(ob.keys()), "mine_keys": sorted(lb.keys()),
}
with open(r"results\_r674bmb_hb_diff.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK mine=%d theirs=%d theirs_only=%d mine_only=%d" % (
    len(sa), len(sb), len(sb - sa), len(sa - sb)))
