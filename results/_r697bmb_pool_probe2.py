"""r697 bm-b: r648 two-sided probe for claw-blocked pool faces."""
import json
import subprocess


def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def face(blob, entry_key, shard_key):
    if blob is None:
        return "FILE-MISSING"
    p = json.loads(blob)
    for e in p.get("entries", []):
        if (e.get("key") or e.get("id")) == entry_key:
            for s in e.get("shards", []):
                sid = s.get("shard_id") or s.get("key", "")
                if shard_key in sid:
                    return "%s owner=%s since=%s" % (
                        s.get("status"), (s.get("owner") or "").strip(),
                        s.get("owner_since"))
    return "ENTRY-MISSING"


CHECKS = [
    ("results/runnable_pool.json", "CONTEST-YTD-P1-RC-0OF1", "contest-ytd"),
    ("results/runnable_pool.json", "PERPETUAL-N2-W15-SHARD-11", "n2w15-11of12"),
    ("results/runnable_pool.bm-b.json", "CONTEST-YTD-P1-RC-0OF1", "contest-ytd"),
    ("results/runnable_pool.bm-b.json", "PERPETUAL-N2-W15-SHARD-11", "n2w15-11of12"),
]
for path, ek, sk in CHECKS:
    h = face(show("HEAD", path), ek, sk)
    o = face(show("origin/main", path), ek, sk)
    print("%s | %s | %s\n  HEAD:   %s\n  ORIGIN: %s" % (path, ek, sk, h, o))
