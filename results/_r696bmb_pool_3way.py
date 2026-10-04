"""r696 bm-b: SHARD-3 three-way topology probe (merge-base vs HEAD vs MERGE_HEAD)."""
import json
import subprocess


def pool_at(rev):
    r = subprocess.run(["git", "show", f"{rev}:results/runnable_pool.json"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    doc = json.loads(r.stdout.decode("utf-8"))
    e = [x for x in doc["entries"] if x.get("id") == "PERPETUAL-N2-W15-SHARD-3"]
    if not e:
        return None
    s = e[0]["shards"][0]
    return {"status": s.get("status"), "owner": s.get("owner"),
            "since": s.get("owner_since")}


mb = subprocess.run(["git", "merge-base", "HEAD", "MERGE_HEAD"],
                    capture_output=True).stdout.decode().strip()
print("merge-base =", mb)
for rev, tag in ((mb, "BASE"), ("HEAD", "HEAD"), ("MERGE_HEAD", "MERGE_HEAD")):
    print(tag, pool_at(rev))
# and: is the daemon keepalive commit on my side?
r = subprocess.run(["git", "log", "-1", "--format=%H %ad %s", "--date=iso",
                    "df18b49f5"], capture_output=True)
print("df18b49f5:", r.stdout.decode("utf-8", "replace")[:160])
r2 = subprocess.run(["git", "merge-base", "--is-ancestor", "df18b49f5", "HEAD"],
                    capture_output=True)
print("df18b49f5 ancestor-of-HEAD rc =", r2.returncode, "(0=yes)")
r3 = subprocess.run(["git", "merge-base", "--is-ancestor", "28af1fae5", mb],
                    capture_output=True)
print("28af1fae5(SHARD-3 close) ancestor-of-BASE rc =", r3.returncode, "(0=yes)")
