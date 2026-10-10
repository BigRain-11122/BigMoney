import subprocess, json, sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else "results/crash_fuse.json"

def stage(n):
    p = subprocess.run(["git", "show", ":%d:%s" % (n, TARGET)], capture_output=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    return json.loads(p.stdout.decode("utf-8"))

a = stage(2)  # ours  = base lineage (origin side, already pushed)
b = stage(3)  # theirs= the replayed bm-c pick

TS_KEYS = ("last_refusal_ts", "last_crash_ts", "cleared_ts", "owner_since", "ts", "last_seen",
           "updated", "updated_at", "last_round_at", "heartbeat_epoch_utc")

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
    if isinstance(x, list) and isinstance(y, list):
        return y if len(y) >= len(x) else x  # rolling ledgers: longer/newer side wins
    return x

merged = merge(a, b)
with open(TARGET, "w", encoding="utf-8", newline="") as f:
    json.dump(merged, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("merged", TARGET)
