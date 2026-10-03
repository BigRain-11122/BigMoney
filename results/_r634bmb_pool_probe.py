"""r634 bm-b: runnable pool face snapshot (ready/unclaimed/active)."""
import json

pool = json.load(open(r"results/runnable_pool.json", encoding="utf-8"))
entries = pool if isinstance(pool, list) else pool.get("entries", [])
from collections import Counter

st = Counter()
faces = []
for e in entries:
    s = e.get("status")
    st[s] += 1
    if s in ("ready", "claimed", "running"):
        faces.append(
            {
                "id": e.get("entry_id") or e.get("id"),
                "name": (e.get("name") or e.get("label") or "")[:60],
                "status": s,
                "owner": e.get("owner") or e.get("claimed_by") or e.get("worker"),
                "worker": (e.get("worker_host") or e.get("host") or "")[:12],
                "since": e.get("owner_since") or e.get("claimed_at"),
            }
        )
print("POOL_COUNTS:", json.dumps(dict(st), ensure_ascii=False))
for f in faces:
    print("FACE:", json.dumps(f, ensure_ascii=False))
