import json, io, hashlib, os
RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
POOL = RB + r"\results\runnable_pool.json"
FUSE = RB + r"\results\crash_fuse.json"

def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)

pool = load(POOL)
items = pool if isinstance(pool, list) else pool.get("entries", pool.get("items", []))
targets = [e for e in items if isinstance(e.get("id"), str) and "NULLS" in e["id"] and e["id"].startswith("FUND")]
print("=== FUND NULLS POOL ENTRIES (%d) ===" % len(targets))
for e in targets:
    print(json.dumps(e, ensure_ascii=False, sort_keys=True)[:1200])
    print("---")

fuse = load(FUSE)
print("=== CRASH FUSE top-level type: %s ===" % type(fuse).__name__)
if isinstance(fuse, dict):
    for k, v in fuse.items():
        if "fund" in k.lower():
            print("FUSE_KEY:", k[:200])
            print(json.dumps(v, ensure_ascii=False, sort_keys=True)[:800])
            print("---")
    if "entries" in fuse:
        for e in fuse["entries"]:
            s = json.dumps(e, ensure_ascii=False)
            if "fund" in s.lower():
                print("FUSE_ENT:", s[:800])
                print("---")
