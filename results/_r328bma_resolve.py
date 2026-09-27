# r328 bm-a: stash-pop UU resolver for results/autofill_state.json (mixed-dict+ledger, skill r203/R208/r215/r220/r322/r83)
# Sides: :2: = HEAD (origin/main after pull, bm-b r328 face); :3: = stash (local bm-a watchdog face)
import json, subprocess, sys, io

PATH = "results/autofill_state.json"

def blob(rev):
    b = subprocess.run(["git", "show", rev + PATH], capture_output=True, check=True).stdout
    return b

b_base = blob(":1:"); b_ours = blob(":2:"); b_theirs = blob(":3:")
print("bytes: base=%d ours(HEAD)=%d theirs(stash)=%d" % (len(b_base), len(b_ours), len(b_theirs)))

def parse(b):
    return json.loads(b.decode("utf-8"))

d_base, d_ours, d_theirs = parse(b_base), parse(b_ours), parse(b_theirs)

CK = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")

def ck(e):
    return tuple(e.get(k) for k in CK)

launches_union = {}
dup_pairs = []
divergent = []

def add_side(side, tag):
    for e in side.get("launches", []):
        k = ck(e)
        if k in launches_union:
            prev = launches_union[k]
            # r322 identity check: field-set diff only additions = merge union keep one
            sp, se = set(prev.keys()), set(e.keys())
            common = sp & se
            same_vals = all(prev.get(c) == e.get(c) for c in common)
            if same_vals and (sp <= se or se <= sp):
                merged = dict(prev); merged.update(e)  # union of fields
                launches_union[k] = merged
                dup_pairs.append((tag, k, "identity-merged"))
            else:
                divergent.append((tag, k, sorted(sp ^ se), [prev.get(c) for c in sorted(common) if prev.get(c) != e.get(c)]))
                # keep the richer one (more fields), but flag for report
                launches_union[k] = prev if len(sp) >= len(se) else e
        else:
            launches_union[k] = e

add_side(d_ours, "HEAD")
add_side(d_theirs, "STASH")
print("launches: HEAD=%d STASH=%d union-unique=%d dup-collisions=%d divergent=%d" % (
    len(d_ours.get("launches", [])), len(d_theirs.get("launches", [])),
    len(launches_union), len(dup_pairs), len(divergent)))
for t, k, note in dup_pairs:
    print("  dup-identity:", t, k, note)
for t, k, fd, diffs in divergent:
    print("  DIVERGENT:", t, k, "field-diff:", fd, "value-conflicts:", diffs)

# sort ts desc -> cap 50 -> re-sort ts ascending before write-back (r245 law)
entries = list(launches_union.values())
entries.sort(key=lambda e: e.get("ts", 0), reverse=True)
cap = 50
dropped = entries[cap:]
entries = entries[:cap]
entries.sort(key=lambda e: e.get("ts", 0))  # ascending producer order
print("cap: kept=%d dropped=%d (dropped ts range shown if any)" % (len(entries), len(dropped)))
for e in dropped[:5]:
    print("  dropped:", ck(e))

# last_tick: compare inner ts (deep probe), whole-dict assign, no str(), tie -> HEAD (r140)
def find_ts(obj, depth=0):
    # deep probe: top-level 'ts' preferred (int/float or "YYYY-MM-DD HH:MM:SS" string); else recurse (D-09)
    if not isinstance(obj, dict):
        return None
    if "ts" in obj and (isinstance(obj["ts"], (int, float)) or (isinstance(obj["ts"], str) and len(obj["ts"]) >= 10)):
        return ("ts", obj["ts"])
    for k in ("last_tick_ts", "tick_ts", "now_ts", "epoch", "updated_at", "last_seen"):
        if k in obj and isinstance(obj[k], (int, float)):
            return (k, obj[k])
    for v in obj.values():
        if isinstance(v, dict):
            r = find_ts(v, depth + 1)
            if r:
                return r
    return None

lt_ours = d_ours.get("last_tick"); lt_theirs = d_theirs.get("last_tick")
print("last_tick: HEAD type=%s, STASH type=%s" % (type(lt_ours).__name__, type(lt_theirs).__name__))
ts_o = find_ts(lt_ours); ts_t = find_ts(lt_theirs)
print("  HEAD ts probe:", ts_o, "| STASH ts probe:", ts_t)

if isinstance(lt_theirs, dict) and isinstance(lt_ours, dict) and ts_o and ts_t:
    if ts_t[1] > ts_o[1]:
        last_tick = lt_theirs; lt_src = "STASH(newer-ts)"
    else:
        last_tick = lt_ours; lt_src = "HEAD(tie-or-newer r140)"
elif isinstance(lt_theirs, dict) and not isinstance(lt_ours, dict):
    last_tick = lt_theirs; lt_src = "STASH(only-dict)"
else:
    last_tick = lt_ours; lt_src = "HEAD(default)"
print("  last_tick taken from:", lt_src)

# merge remaining top-level scalar/other keys: union of keys, ours default, theirs fill-missing-or-newer-by-ts
# conservative: keep HEAD face for non-launches/last_tick keys unless missing in HEAD (fill from stash)
merged = dict(d_ours)
merged["launches"] = entries
merged["last_tick"] = last_tick
for k, v in d_theirs.items():
    if k not in merged:
        merged[k] = v
        print("  key filled from STASH:", k)

# byte-face mirroring: line ending + indent from base/HEAD blob
crlf = b"\r\n" in b_ours
raw_ours = b_ours.decode("utf-8")
indent = 1
for line in raw_ours.splitlines():
    if line.startswith(" {"):
        indent = len(line) - len(line.lstrip(" "))
        break
out = json.dumps(merged, ensure_ascii=False, indent=indent)
if crlf:
    out = out.replace("\n", "\r\n")
with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(out)

# verify: parse back + assertions
v = json.loads(io.open(PATH, "r", encoding="utf-8", newline="").read())
assert isinstance(v.get("last_tick"), dict), "last_tick must be dict"
assert isinstance(v.get("launches"), list), "launches must be list"
keys = [ck(e) for e in v["launches"]]
assert len(keys) == len(set(map(str, keys))), "composite-key uniqueness after resolve"
tss = [e.get("ts", 0) for e in v["launches"]]
assert tss == sorted(tss), "launches must be ts-ascending"
assert len(v["launches"]) <= 50
print("VERIFIED: last_tick dict OK, launches=%d unique ascending cap<=50" % len(v["launches"]))
if divergent:
    print("WARNING: divergent composite keys present - see DIVERGENT lines; escalate in round report", file=sys.stderr)
    sys.exit(3)
print("RESOLVE OK")
