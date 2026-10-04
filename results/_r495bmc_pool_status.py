# r691 bm-b pool status probe (reuses trio_watch structure law r675: shards nested in entries[].shards[])
import json, io, sys

with io.open(r"results/runnable_pool.json", encoding="utf-8") as f:
    d = json.load(f)

out = []
for ent in d.get("entries", []):
    key = ent.get("key", ent.get("id", "?"))
    shards = ent.get("shards", [])
    if shards:
        st = {}
        own = {}
        for sh in shards:
            st[sh.get("status")] = st.get(sh.get("status"), 0) + 1
            own[sh.get("owner") or "None"] = own.get(sh.get("owner") or "None", 0) + 1
        out.append("%s | entry_status=%s | shards=%s | owners=%s | lane_owner=%s | pri=%s" % (
            key, ent.get("status", "?"), st, own, ent.get("lane_owner"), ent.get("priority")))
    else:
        out.append("%s | entry_status=%s | (flat) | owner=%s | lane_owner=%s | pri=%s" % (
            key, ent.get("status", "?"), ent.get("owner"), ent.get("lane_owner"), ent.get("priority")))

with io.open(r"results/_r495bmc_pool_status.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("WROTE results/_r495bmc_pool_status.txt lines=%d" % len(out))
