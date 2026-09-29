import subprocess, json
A = json.loads(subprocess.run(["git", "show", ":2:results/runnable_pool.json"], capture_output=True).stdout)["entries"]
B = json.loads(subprocess.run(["git", "show", ":3:results/runnable_pool.json"], capture_output=True).stdout)["entries"]
ma, mb = {e["id"]: e for e in A}, {e["id"]: e for e in B}
print("ids ours-only:", sorted(set(ma) - set(mb)), "| bmb-only:", sorted(set(mb) - set(ma)))
for i in sorted(set(ma) & set(mb)):
    if ma[i] != mb[i]:
        sa, sb = ma[i].get("status"), mb[i].get("status")
        sha = ma[i].get("shards"); shb = mb[i].get("shards")
        print("DIFF id=%s status ours=%s bmb=%s" % (i, sa, sb))
        if sha != shb:
            if isinstance(sha, list) and isinstance(shb, list):
                ka = {s.get("key"): s.get("status") for s in sha}
                kb = {s.get("key"): s.get("status") for s in shb}
                print("   shards ours:", ka, "| bmb:", kb)
            else:
                print("   shards type:", type(sha), type(shb), repr(sha)[:80], repr(shb)[:80])
        for k in set(ma[i]) | set(mb[i]):
            if ma[i].get(k) != mb[i].get(k) and k != "shards":
                print("   field %s: ours=%s bmb=%s" % (k, repr(ma[i].get(k))[:100], repr(mb[i].get(k))[:100]))
