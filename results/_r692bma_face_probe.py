# r692 probe-3: trio shard sub-field diff
import json, subprocess

CREATE_NO_WINDOW = 0x08000000


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    return r.stdout if r.returncode == 0 else None

o = json.loads(blob("HEAD", "results/runnable_pool.json").decode("utf-8"))
t = json.loads(blob("MERGE_HEAD", "results/runnable_pool.json").decode("utf-8"))
oe = {e["id"]: e for e in o.get("entries", [])}
te = {e["id"]: e for e in t.get("entries", [])}
k = "FUND-VALUE-P1-NULLS"
so, st = oe[k]["shards"][0], te[k]["shards"][0]
for f in sorted(set(so) | set(st)):
    if so.get(f) != st.get(f):
        print(f"shard field diff [{k}]:")
        print("  ", f, "ours:", repr(str(so.get(f))[:100]))
        print("  ", f, "theirs:", repr(str(st.get(f))[:100]))

# crash_fuse sigs diff detail (per-sig union judgment)
jo = json.loads(blob("HEAD", "results/crash_fuse.json").decode("utf-8"))
jt = json.loads(blob("MERGE_HEAD", "results/crash_fuse.json").decode("utf-8"))
so_, st_ = jo["sigs"], jt["sigs"]
o_only = sorted(set(so_) - set(st_))
t_only = sorted(set(st_) - set(so_))
print("crash_fuse sigs: ours-only:", len(o_only), o_only[:4],
      "theirs-only:", len(t_only), t_only[:4])
diff_cnt = [(k2, so_[k2].get("count"), st_[k2].get("count"))
            for k2 in sorted(set(so_) & set(st_))
            if so_[k2] != st_[k2]]
print("common sig count diffs:", len(diff_cnt), diff_cnt[:6])
newer_ours = sum(1 for _, a, b in diff_cnt if (a or 0) > (b or 0))
newer_theirs = sum(1 for _, a, b in diff_cnt if (b or 0) > (a or 0))
print("count newer: ours=%d theirs=%d" % (newer_ours, newer_theirs))
