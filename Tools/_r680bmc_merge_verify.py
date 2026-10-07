# -*- coding: utf-8 -*-
"""r680 bm-c: post-resolve face verification before merge commit.
1) pool DIVLOWVOL shard owner_since == origin newer (14:12:07) not regressed;
2) token_usage.json bm-c sub-face not regressed vs my round commit c09013750;
3) compute_audit history union row count >= both sides;
ascii-safe prints."""
import json
import subprocess

def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    return json.loads(r.stdout.decode("utf-8-sig"))

# 1) pool face
pool = json.load(open("results/runnable_pool.json", encoding="utf-8-sig"))
found = []
for e in pool.get("entries", []):
    eid = e.get("id", "")
    if "DIVLOWVOL" in eid:
        for sh in e.get("shards", []):
            found.append((eid, sh.get("id"), sh.get("owner_since"), sh.get("owner")))
print("POOL DIVLOWVOL shards:", found)

# 2) token_usage bm-c face
mine = show("c09013750", "results/token_usage.json")
merged = json.load(open("results/token_usage.json", encoding="utf-8-sig"))
for key in ("bm-c", "machines", "per_machine"):
    if key in mine or key in merged:
        a, b = mine.get(key), merged.get(key)
        print("token_usage key=%s same=%s" % (key, a == b))
        if a != b and isinstance(a, dict) and isinstance(b, dict):
            for k in sorted(set(a) | set(b)):
                if a.get(k) != b.get(k):
                    print("  diff %s: mine=%r merged=%r" % (k, str(a.get(k))[:60], str(b.get(k))[:60]))
print("token_usage top keys mine=%s merged=%s" % (sorted(mine.keys()), sorted(merged.keys())))

# 3) compute_audit history
ours_hist = show("c09013750", "results/compute_audit.json").get("history", [])
merged_ca = json.load(open("results/compute_audit.json", encoding="utf-8-sig"))
mh = merged_ca.get("history", [])
theirs_hist = show("34dfba1bb", "results/compute_audit.json").get("history", [])
print("compute_audit history: ours=%d theirs=%d merged=%d" % (len(ours_hist), len(theirs_hist), len(mh)))
print("union_ok=%s" % (len(mh) >= max(len(ours_hist), len(theirs_hist))))
print("merged ts=%r" % merged_ca.get("ts"))
