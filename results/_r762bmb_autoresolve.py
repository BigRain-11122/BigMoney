# r762 generic UU auto-resolver: classify at runtime, route canonical recipes, fail-closed on unknown
# Families: append-log(jsonl)=union | rolling-ledger=union+take-new | snapshot/docs=take-new-by-ts
#           daemon-live faces=ours | md-with-ts=take-new | else: UNKNOWN (exit 1, resolve by hand)
import subprocess, json, sys, re
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def sh(args):
    r = subprocess.run(args, capture_output=True)
    return r.stdout if r.returncode == 0 else None

def stage_bytes(path, stage):
    return sh(["git", "show", f":{stage}:{path}"])

def norm_ts(v):
    if v is None:
        return None
    s = str(v).strip()
    s2 = s.replace(" ", "T", 1) if "T" not in s else s
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s2, fmt)
        except ValueError:
            continue
    return None

TS_KEYS = ["generated_at", "generated", "ts", "updated", "scan_ts", "last_scan", "run_ts", "now"]
def find_ts(obj, depth=0):
    if depth > 3 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        if k in obj and norm_ts(obj[k]):
            return (k, obj[k])
    for v in obj.values():
        if isinstance(v, dict):
            got = find_ts(v, depth + 1)
            if got:
                return got
    return None

def union_jsonl(path, o, t):
    ol = [l for l in o.decode("utf-8").splitlines() if l.strip()]
    tl = [l for l in t.decode("utf-8").splitlines() if l.strip()]
    seen, union = set(), []
    for line in ol + tl:
        if line not in seen:
            seen.add(line); union.append(line)
    def line_ts(l):
        try:
            g = find_ts(json.loads(l))
            return norm_ts(g[1]) if g else None
        except Exception:
            return None
    if union and all(line_ts(l) is not None for l in union):
        union.sort(key=lambda l: line_ts(l))
    for l in union:
        json.loads(l)
    return ("union %d+%d->%d" % (len(ol), len(tl), len(union)), ("\n".join(union) + "\n").encode("utf-8"))

def ledger_union(path, o, t):
    oo, tt = json.loads(o), json.loads(t)
    do, dt = norm_ts(find_ts(oo)[1]), norm_ts(find_ts(tt)[1])
    newer = oo if (do or datetime.min) >= (dt or datetime.min) else tt
    out = {}
    for k in (oo.keys() | tt.keys()):
        ov, tv = oo.get(k), tt.get(k)
        if isinstance(ov, list) and isinstance(tv, list):
            seen, un = set(), []
            for el in ov + tv:
                key = json.dumps(el, sort_keys=True, ensure_ascii=False)
                if key not in seen:
                    seen.add(key); un.append(el)
            def el_ts(e):
                g = find_ts(e)
                return norm_ts(g[1]) if g else None
            if all(el_ts(e) is not None for e in un):
                un.sort(key=lambda e: el_ts(e))
            out[k] = un
        else:
            out[k] = newer.get(k, ov if ov is not None else tv)
    blob = (json.dumps(out, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    json.loads(blob)
    return ("ledger-union", blob)

def take_new_ts(path, o, t):
    oo, tt = json.loads(o), json.loads(t)
    go, gt = find_ts(oo), find_ts(tt)
    if not go or not gt:
        return None
    do, dt = norm_ts(go[1]), norm_ts(gt[1])
    if do is None or dt is None:
        return None
    return ("take-new %s>= %s" % (go[1], gt[1]), o if do >= dt else t)

DAEMON_LIVE = {"results/saturation_engine/face_bm-b.json", "results/saturation_engine/state_bm-b.json",
               "results/p1d_gates.json", "results/saturation_engine_state.bm-b.json",
               "results/autofill_state.bm-b.json"}
ROLLING_LEDGER = {"results/compute_audit.json", "results/regime_state.json"}

uu = sh(["git", "diff", "--name-only", "--diff-filter=U"]).decode().split()
if not uu:
    print("NO-UU")
    sys.exit(0)
results, unknown = [], []
for p in uu:
    o, t = stage_bytes(p, 2), stage_bytes(p, 3)
    if o is None or t is None:
        unknown.append(p); continue
    try:
        if p in DAEMON_LIVE:
            json.loads(o)
            side, blob = ("ours-live", o)
        elif p.endswith(".jsonl"):
            side, blob = union_jsonl(p, o, t)
        elif p in ROLLING_LEDGER:
            side, blob = ledger_union(p, o, t)
        elif p.endswith(".json"):
            got = take_new_ts(p, o, t)
            if got is None:
                unknown.append(p); continue
            side, blob = got
        elif p.endswith(".md"):
            pat = re.compile(r"(20\d{2}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})")
            mo = pat.search(o.decode("utf-8", "replace")[:400]); mt = pat.search(t.decode("utf-8", "replace")[:400])
            if not mo or not mt:
                unknown.append(p); continue
            do = datetime.strptime(mo.group(1) + "T" + mo.group(2), "%Y-%m-%dT%H:%M:%S")
            dt = datetime.strptime(mt.group(1) + "T" + mt.group(2), "%Y-%m-%dT%H:%M:%S")
            side = "take-new md"
            blob = o if do >= dt else t
        else:
            unknown.append(p); continue
        open(p, "wb").write(blob)
        subprocess.run(["git", "add", p], check=True)
        results.append(f"{p}: {side}")
    except Exception as e:
        unknown.append(f"{p}: EXC {e}")
for r in results:
    print(r)
if unknown:
    print("UNKNOWN-FAIL-CLOSED:")
    for u in unknown:
        print("  " + u)
    sys.exit(1)
print(f"OK resolved={len(results)}")
