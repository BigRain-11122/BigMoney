# r328 bm-a: rebase UU batch resolver (16 files, bm-c r84 closeout vs my round-328 replay)
# Skill recipes: memory-union / mixed-dict+ledger / rolling-ledger / js-wrapper-snapshot / snapshot
# Sides in a REBASE (inverted vs merge): :2: ours = HEAD = origin/main (bm-c face);
# :3: theirs = the commit being replayed (bm-a round-328 face). Tie -> HEAD = :2: (r140).
import io, json, os, re, subprocess, sys

def sh(args):
    return subprocess.run(args, capture_output=True, check=True).stdout

def blob(revspec, path):
    return sh(["git", "show", "%s:%s" % (revspec, path)])

def unmerged():
    out = sh(["git", "diff", "--name-only", "--diff-filter=U"]).decode("utf-8")
    return [l for l in out.splitlines() if l.strip()]

FILES = unmerged()
print("unmerged count:", len(FILES))

TS_KEYS = ("ts", "generated", "generated_at", "updated_at", "last_attempt",
           "last_seen", "asof", "time", "epoch", "date")

def deep_ts(obj, depth=0):
    """(path, value) of first ts-like leaf; ints/floats or ISO-like strings."""
    if depth > 6 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            return (k, v)
        if isinstance(v, str) and len(v) >= 8 and re.match(r"^\d{4}-\d{2}-\d{2}", v):
            return (k, v)
    for v in obj.values():
        if isinstance(v, dict):
            r = deep_ts(v, depth + 1)
            if r:
                return r
    return None

def ts_key(t):
    return t[1] if t else None

def cmp_ts(a, b):
    """-1/0/1 with mixed int/str tolerance (ISO strings sort naturally)."""
    if a is None and b is None:
        return 0
    if a is None:
        return -1
    if b is None:
        return 1
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return (a > b) - (a < b)
    return (str(a) > str(b)) - (str(a) < str(b))

def take_newer_json(path):
    a = json.loads(blob(":2", path).decode("utf-8"))
    b = json.loads(blob(":3", path).decode("utf-8"))
    ta, tb = deep_ts(a), deep_ts(b)
    c = cmp_ts(ts_key(ta), ts_key(tb))
    if c >= 0:
        pick, side = a, "HEAD(origin/bm-c) tie-or-newer"
    else:
        pick, side = b, "REPLAYED(bm-a) newer"
    write(path, json.dumps(pick, ensure_ascii=False, indent=1) + "\n")
    return side, (ts_key(ta), ts_key(tb))

def write(path, text):
    eol = "\r\n" if b"\r\n" in open(path, "rb").read()[:2000] else "\n"
    if eol == "\r\n":
        text = text.replace("\n", "\r\n")
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

def write_bytes(path, data):
    with io.open(path, "wb") as f:
        f.write(data)

report = []

# ------------------------------------------------------------------ memory-union
def resolve_memory_union(path):
    base = blob(":1", path)
    ours = blob(":2", path)     # origin/bm-c face
    theirs = blob(":3", path)   # bm-a face
    if not (ours.startswith(base) and theirs.startswith(base)):
        raise RuntimeError("memory-union prefix assertion FAILED for %s" % path)
    merged = base + ours[len(base):] + theirs[len(base):]
    write_bytes(path, merged)
    n_b = len(base) - len(base.rstrip(b"\r\n"))
    report.append((path, "memory-union", len(base), len(ours) - len(base),
                   len(theirs) - len(base), len(merged)))

# --------------------------------------------------------- mixed-dict+ledger
def resolve_autofill(path):
    a = json.loads(blob(":2", path).decode("utf-8"))   # origin face
    b = json.loads(blob(":3", path).decode("utf-8"))   # my face
    CK = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
    un = {}
    divergent = []
    for side in (a, b):
        for e in side.get("launches", []):
            k = tuple(e.get(c) for c in CK)
            if k in un:
                prev = un[k]
                sp, se = set(prev), set(e)
                same = all(prev.get(c) == e.get(c) for c in (sp & se))
                if same and (sp <= se or se <= sp):
                    m = dict(prev); m.update(e); un[k] = m
                else:
                    divergent.append(k)
                    un[k] = prev if len(sp) >= len(se) else e
            else:
                un[k] = e
    ent = sorted(un.values(), key=lambda e: str(e.get("ts", "")))
    ent = ent[-50:]
    ent.sort(key=lambda e: str(e.get("ts", "")))
    lt_a, lt_b = a.get("last_tick"), b.get("last_tick")
    if isinstance(lt_a, dict) and isinstance(lt_b, dict):
        c = cmp_ts(lt_a.get("ts"), lt_b.get("ts"))
        last_tick = lt_a if c >= 0 else lt_b
    else:
        last_tick = lt_a if isinstance(lt_a, dict) else lt_b
    assert isinstance(last_tick, dict)
    merged = dict(a)
    for k, v in b.items():
        if k not in merged:
            merged[k] = v
    merged["launches"] = ent
    merged["last_tick"] = last_tick
    write(path, json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
    v = json.loads(io.open(path, encoding="utf-8").read())
    assert isinstance(v["last_tick"], dict) and len(v["launches"]) <= 50
    keys = [tuple(e.get(c) for c in CK) for e in v["launches"]]
    assert len(keys) == len(set(map(str, keys)))
    report.append((path, "mixed-dict+ledger", len(a.get("launches", [])),
                   len(b.get("launches", [])), len(ent), "divergent=%d" % len(divergent)))
    if divergent:
        print("DIVERGENT composite keys:", divergent)

# ---------------------------------------------------------------- rolling-ledger
def resolve_rolling(path):
    a = json.loads(blob(":2", path).decode("utf-8"))
    b = json.loads(blob(":3", path).decode("utf-8"))
    merged = {}
    for k in set(list(a.keys()) + list(b.keys())):
        va, vb = a.get(k), b.get(k)
        if isinstance(va, list) and isinstance(vb, list):
            seen, out = set(), []
            for it in va + vb:
                key = json.dumps(it, sort_keys=True, ensure_ascii=False)
                if key in seen:
                    continue
                seen.add(key)
                out.append(it)
            if out and all(isinstance(x, dict) for x in out):
                out.sort(key=lambda x: str(deep_ts(x) or ("", "")))
            merged[k] = out
        elif isinstance(va, dict) and isinstance(vb, dict):
            ta, tb = deep_ts(va), deep_ts(vb)
            merged[k] = va if cmp_ts(ts_key(ta), ts_key(tb)) >= 0 else vb
        else:
            ta, tb = deep_ts(a), deep_ts(b) if not isinstance(va, (dict, list)) else None, None
            # scalars: decide by whole-doc ts side
            da, db = deep_ts(a), deep_ts(b)
            pick_left = cmp_ts(ts_key(da), ts_key(db)) >= 0
            merged[k] = va if pick_left else vb
    write(path, json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
    json.loads(io.open(path, encoding="utf-8").read())
    report.append((path, "rolling-ledger", "?", "?", "union", "ok"))

# ------------------------------------------------------------- js-wrapper-snapshot
def resolve_js_wrapper(path):
    a = blob(":2", path).decode("utf-8")
    b = blob(":3", path).decode("utf-8")
    ts_in = lambda t: re.findall(r'"generated"[:\s]*"([^"]+)"', t) or re.findall(
        r'"ts"[:\s]*"([^"]+)"', t)
    ta = ts_in(a); tb = ts_in(b)
    c = cmp_ts(ta[0] if ta else None, tb[0] if tb else None)
    pick = a if c >= 0 else b
    write_bytes(path, pick.encode("utf-8"))
    json.loads(re.search(r"=\s*(\{.*\})\s*;?\s*$", pick, re.S).group(1))
    report.append((path, "js-wrapper-snapshot", ta[:1], tb[:1],
                   "took " + ("HEAD(origin)" if c >= 0 else "REPLAYED(bm-a)"), "ok"))

CLASS_MAP = {}
for p in FILES:
    if p == "CODELY.md":
        CLASS_MAP[p] = "memory-union"
    elif p == "results/autofill_state.json":
        CLASS_MAP[p] = "mixed-dict+ledger"
    elif p in ("results/compute_audit.json", "results/regime_state.json"):
        CLASS_MAP[p] = "rolling-ledger"
    elif p == "results/dashboard_status.js":
        CLASS_MAP[p] = "js-wrapper-snapshot"
    else:
        # snapshots + 4 classifier-unknowns (deterministic same-day re-derive
        # products: daily_report pair, scorecard pair) -> snapshot take-newer
        CLASS_MAP[p] = "snapshot"

for p in FILES:
    cls = CLASS_MAP[p]
    if cls == "memory-union":
        resolve_memory_union(p)
    elif cls == "mixed-dict+ledger":
        resolve_autofill(p)
    elif cls == "rolling-ledger":
        resolve_rolling(p)
    elif cls == "js-wrapper-snapshot":
        resolve_js_wrapper(p)
    else:
        side, (ta, tb) = take_newer_json(p)
        report.append((p, "snapshot", str(ta), str(tb), side, "ok"))

print("== resolve report ==")
for r in report:
    print(" ", r)
print("RESOLVE DONE")
