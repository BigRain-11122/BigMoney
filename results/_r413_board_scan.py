import collections
import glob
import json
import os

files = sorted(glob.glob("fleet/tasks/*.json"))
c = collections.Counter()
active = []
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    st = d.get("status", "?")
    c[st] += 1
    if st in ("open", "claimed", "in_progress"):
        active.append((os.path.basename(f), st, d.get("claimed_by", "-"), str(d.get("title", d.get("subject", "")))[:70]))
for a in active:
    print("ACTIVE:", a)
print("all statuses:", dict(c))
