"""r634 bm-b: scan recent fleet messages addressed to bm-b + waiting pool entry."""
import glob
import json
import os

# 1) waiting pool entry identity
pool = json.load(open(r"results/runnable_pool.json", encoding="utf-8"))
entries = pool if isinstance(pool, list) else pool.get("entries", [])
for e in entries:
    if e.get("status") == "waiting":
        print("WAITING_ENTRY:", json.dumps(e, ensure_ascii=False)[:400])

# 2) recent MSG files mentioning bm-b (last ~36h)
cands = []
for p in glob.glob(r"fleet/messages/*.md") + glob.glob(r"fleet/MSG/*.md") + glob.glob(r"fleet/inbox/processed/*.md"):
    cands.append(p)
print("MSG_DIRS:", sorted(set(os.path.dirname(p) for p in cands))[:5])
