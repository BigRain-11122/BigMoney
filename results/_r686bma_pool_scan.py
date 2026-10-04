import json
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
with open(repo + r"\results\runnable_pool.json", "rb") as f:
    pool = json.loads(f.read().decode('utf-8'))
entries = pool.get("entries", [])
print("total entries:", len(entries))
from collections import Counter
st = Counter(e.get("status") for e in entries)
print("status dist:", dict(st))
for e in entries:
    s = e.get("status")
    if s in ("waiting", "ready", "running"):
        print(f"{e.get('id')} | {s} | owner={e.get('owner')} | priority={e.get('priority')}")
