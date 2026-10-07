"""r693 bm-c advisory-evidence probe: FUND-DIVLOWVOL-P1-NULLS pool face
progress numbers + crash-fuse refusal counters + Money02 cache presence,
for the GM-lane stall advisory (r692 next-pointer (c) escalation duty).
Small facts -> stdout."""
import datetime
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
print("== now:", datetime.datetime.now().isoformat())

with open(os.path.join(REPO, "results", "runnable_pool.json"), encoding="utf-8") as fh:
    pool = json.load(fh)
entries = pool.get("entries", pool if isinstance(pool, list) else [])
hits = [e for e in entries if isinstance(e, dict) and "FUND-DIVLOWVOL-P1" in str(e.get("id", e.get("sig", "")))]
print("== pool entries total:", len(entries), "| DIVLOWVOL faces:", len(hits))
for e in hits:
    keep = {k: e.get(k) for k in (
        "id", "sig", "status", "done", "total", "shards_done", "shards_total",
        "owner", "owner_since", "cleared_ts", "last_progress_ts", "eta",
        "host_gates", "claimed_by", "updated", "ts") if k in e}
    print(json.dumps(keep, ensure_ascii=False))

cf = os.path.join(REPO, "results", "crash_fuse.json")
if os.path.exists(cf):
    with open(cf, encoding="utf-8") as fh:
        fuse = json.load(fh)
    print("== crash_fuse keys:", list(fuse.keys())[:12])
    for k, v in fuse.items():
        if isinstance(v, dict) and ("refus" in json.dumps(v)[:400] or "divlowvol" in k.lower()):
            print("== fuse[%s]:" % k, json.dumps(v, ensure_ascii=False)[:500])
        elif isinstance(v, (int, float, str)) and "refus" in k.lower():
            print("== fuse[%s]:" % k, v)
else:
    print("== crash_fuse.json MISSING")

for p in (r"K:\Money02\data\cache\p1c_stock", r"K:\Fluxgroup\Money02\data\cache\p1c_stock",
          r"D:\Money02\data\cache\p1c_stock", r"K:\Money02"):
    print("== money02 probe", p, "->", os.path.isdir(p))
