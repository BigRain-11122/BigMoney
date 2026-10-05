# r762 pick-2 (817e73f9d) UU resolver: same recipes as batch-1 (union jsonl / ours-live daemon faces)
# standalone (no import from batch-1 module: it executes its PLAN at import time)
import subprocess, json, sys
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

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

TS_KEYS = ["generated_at", "generated", "ts", "updated", "scan_ts", "last_scan", "run_ts"]
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

def resolve_union_jsonl(path):
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    ol = [l for l in o.decode("utf-8").splitlines() if l.strip()]
    tl = [l for l in t.decode("utf-8").splitlines() if l.strip()]
    seen, union = set(), []
    for line in ol + tl:
        if line not in seen:
            seen.add(line)
            union.append(line)
    def line_ts(line):
        try:
            obj = json.loads(line)
            got = find_ts(obj)
            return norm_ts(got[1]) if got else None
        except Exception:
            return None
    if all(line_ts(l) is not None for l in union):
        union.sort(key=lambda l: line_ts(l))
    for l in union:
        json.loads(l)
    return ("union", ("\n".join(union) + "\n").encode("utf-8"), len(ol), len(tl), len(union))

def resolve_ours_live(path):
    o = stage_bytes(path, 2)
    json.loads(o)
    return ("ours-live", o)

out = []
for p in ["results/fund_quality_p1/nulls.jsonl", "results/saturation_engine/history_bm-b.jsonl"]:
    side, blob, no, nt, nu = resolve_union_jsonl(p)
    open(p, "wb").write(blob)
    subprocess.run(["git", "add", p], check=True)
    out.append(f"{p}: union ours={no} theirs={nt} -> {nu} zero-loss={nu>=max(no,nt)}")
for p in ["results/saturation_engine/face_bm-b.json", "results/saturation_engine/state_bm-b.json"]:
    side, blob = resolve_ours_live(p)
    open(p, "wb").write(blob)
    subprocess.run(["git", "add", p], check=True)
    out.append(f"{p}: {side}")
print("\n".join(out))
print("OK-2")
