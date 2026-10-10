import subprocess, json, sys

# post-rebase surgical merge: MINE (local squash 0911fdbc4) vs THEIRS (origin/main),
# newer-wins union per entry, tie -> origin bytes (EOL-healed lineage)
TARGET = sys.argv[1]
MINE_REF = "0911fdbc4e3067beecc7641deaf4922551089a33:" + TARGET
THEIRS_REF = "origin/main:" + TARGET

def side(ref):
    p = subprocess.run(["git", "show", ref], capture_output=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    return json.loads(p.stdout.decode("utf-8"))

theirs = side(THEIRS_REF)  # pushed lineage (base)
mine = side(MINE_REF)      # local pick content

TS_KEYS = ("last_refusal_ts", "last_crash_ts", "cleared_ts", "owner_since", "ts", "last_seen",
           "updated", "updated_at", "last_round_at", "last_pulled_at", "last_decisions_read_at",
           "last_orders_read_at", "last_orders_at", "round_ref", "written_at")

def entry_ts(d):
    best = ""
    for k in TS_KEYS:
        v = d.get(k) or ""
        if isinstance(v, str) and v > best:
            best = v
        elif isinstance(v, (int, float)) and str(v) > best:
            best = str(v)
    return best

def is_entry(d):
    return isinstance(d, dict) and any(k in d for k in TS_KEYS)

def newer(x, y):
    tx, ty = entry_ts(x), entry_ts(y)
    if tx != ty:
        return y if tx < ty else x
    cx, cy = x.get("count", 0), y.get("count", 0)
    if cx != cy:
        return x if cx >= cy else y
    return x  # tie -> theirs (origin lineage)

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
        return y if len(y) >= len(x) else x
    return x

merged = merge(theirs, mine)
with open(TARGET, "w", encoding="utf-8", newline="") as f:
    json.dump(merged, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("surgical-merged", TARGET)
