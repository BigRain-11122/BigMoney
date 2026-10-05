# r762 onto-rebase batch-4: pick c225aac37 (r761 pre-pull churn) vs bm-c r595 -- 2 append-log unions
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

out = []
for p in ["results/fund_quality_p1/nulls.jsonl", "results/saturation_engine/history_bm-b.jsonl"]:
    o, t = stage_bytes(p, 2), stage_bytes(p, 3)
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
    if all(line_ts(l) is not None for l in union):
        union.sort(key=lambda l: line_ts(l))
    for l in union:
        json.loads(l)
    open(p, "wb").write(("\n".join(union) + "\n").encode("utf-8"))
    subprocess.run(["git", "add", p], check=True)
    out.append(f"{p}: union ours={len(ol)} theirs={len(tl)} -> {len(union)} zero-loss={len(union)>=max(len(ol),len(tl))}")
print("\n".join(out))
print("OK-4")
