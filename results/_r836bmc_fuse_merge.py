import subprocess, json, sys

def stage(n):
    p = subprocess.run(["git", "show", ":%d:results/crash_fuse.json" % n], capture_output=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    return json.loads(p.stdout.decode("utf-8"))

a = stage(2)  # ours  = base lineage (bm-a / origin side, already pushed)
b = stage(3)  # theirs= the replayed bm-c pick

TS_KEYS = ("last_refusal_ts", "last_crash_ts", "cleared_ts", "owner_since", "ts", "last_seen")

def entry_ts(d):
    best = ""
    for k in TS_KEYS:
        v = d.get(k) or ""
        if isinstance(v, str) and v > best:
            best = v
    return best

def is_entry(d):
    return isinstance(d, dict) and any(k in d for k in TS_KEYS)

def newer(x, y):
    tx, ty = entry_ts(x), entry_ts(y)
    if tx != ty:
        return x if tx > ty else y
    cx, cy = x.get("count", 0), y.get("count", 0)
    if cx != cy:
        return x if cx >= cy else y
    return x  # tie -> keep ours (pushed lineage)

def merge(x, y):
    if isinstance(x, dict) and isinstance(y, dict):
        if is_entry(x) and is_entry(y):
            return newer(x, y)
        out = {}
        for k in list(x.keys()) + [k for k in y.keys() if k not in x]:
            if k in x and k in y:
                out[k] = merge(x[k], y[k])
            elif k in x:
                out[k] = x[k]
            else:
                out[k] = y[k]
        return out
    return x

merged = merge(a, b)

def count_leaves(d):
    if isinstance(d, dict):
        return sum(count_leaves(v) for v in d.values())
    return 1

diff = {"sigs_ours": len(a.get("sigs", {})), "sigs_theirs": len(b.get("sigs", {})),
        "sigs_merged": len(merged.get("sigs", {})),
        "active_ours": len(a.get("active", {})), "active_theirs": len(b.get("active", {})),
        "active_merged": len(merged.get("active", {}))}

with open("results/crash_fuse.json", "w", encoding="utf-8", newline="") as f:
    json.dump(merged, f, indent=1, ensure_ascii=False)
    f.write("\n")

print(json.dumps(diff))
