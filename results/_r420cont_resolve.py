import json, re, subprocess
TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None
def probe_ts(obj, best=("", )):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and TS_RE.match(v) and any(nk.startswith(p) for p in ("updated", "generated", "asof", "cutoff", "last")):
                if v > best[0]: best = (v, )
            else:
                best = probe_ts(v, best)
    elif isinstance(obj, list):
        for v in obj: best = probe_ts(v, best)
    return best
p = "results/prospect_promotion/_summary.json"
a, b = blob(2, p), blob(3, p)
ta, tb = probe_ts(json.loads(a))[0], probe_ts(json.loads(b))[0]
side = 2 if ta >= tb else 3
data = a if side == 2 else b
open(p, "wb").write(data)
json.loads(data)
print(f"[take-new] {p}: ours_ts={ta} theirs_ts={tb} -> side={':2:ours' if side==2 else ':3:theirs'}")
