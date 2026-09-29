"""r240 bm-c storm probe: for every unmerged path, report side sizes, deep-ts,
byte-equality; jsonl line counts + key-collision check."""
import json, re, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {spec} rc={r.returncode}")
    return r.stdout

WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
KEYP = ("generated", "updated", "asof", "ts", "lastseen", "cutoff", "timestamp")

def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in KEYP) and WALL.match(v):
                if v > best:
                    best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def probe(path):
    t2, t3, eq = "", "", False
    try:
        b2, b3 = blob(f":2:{path}"), blob(f":3:{path}")
        eq = b2 == b3
        try:
            t2 = deep_ts(json.loads(b2.decode("utf-8")))
        except Exception:
            t2 = "(nonjson)"
        try:
            t3 = deep_ts(json.loads(b3.decode("utf-8")))
        except Exception:
            t3 = "(nonjson)"
    except Exception as e:
        print(f"[err] {path}: {e}")
        return
    print(f"{path}\n  :2:={len(b2)}B ts={t2 or '-'} | :3:={len(b3)}B ts={t3 or '-'} | identical={eq}")

def probe_jsonl(path, keyfields):
    b2, b3 = blob(f":2:{path}"), blob(f":3:{path}")
    l2 = [l for l in b2.decode("utf-8").splitlines() if l.strip()]
    l3 = [l for l in b3.decode("utf-8").splitlines() if l.strip()]
    s2, s3 = set(l2), set(l3)
    common = s2 & s3
    only2 = [l for l in l2 if l not in s3]
    only3 = [l for l in l3 if l not in s2]
    def keys(lines):
        out = {}
        for l in lines:
            try:
                d = json.loads(l)
                k = tuple(str(d.get(f)) for f in keyfields)
                out.setdefault(k, []).append(l)
            except Exception:
                out.setdefault(("<parse-fail>",), []).append(l)
        return out
    k2, k3 = keys(only2), keys(only3)
    shared_keys = set(k2) & set(k3)
    coll = [k for k in shared_keys if k2[k] != k3[k]]
    print(f"{path}\n  lines :2:={len(l2)} :3:={len(l3)} common={len(common)} only2={len(only2)} only3={len(only3)}")
    print(f"  only2 first: {only2[0][:150] if only2 else '-'}")
    print(f"  only3 first: {only3[0][:150] if only3 else '-'}")
    print(f"  key-collisions (same key, diff content): {len(coll)} {list(coll)[:3]}")

r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, text=True)
paths = [p for p in r.stdout.splitlines() if p.strip()]
print(f"=== {len(paths)} unmerged paths ===")
for p in sorted(paths):
    if p.endswith(".jsonl"):
        if "t24_prospect" in p:
            probe_jsonl(p, ["cell_id", "cutoff"])
        else:
            probe_jsonl(p, ["ts"])
    else:
        probe(p)
