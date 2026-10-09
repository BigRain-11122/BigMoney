# r910 bm-a leg-2 residual-2: saturation_engine bm-a-owned faces (snapshot take-new + history line-union)
import json, re, subprocess

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def show(ref):
    r = subprocess.run([GIT, "show", ref], capture_output=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else None

WALLCLOCK_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def probe_max_ts(blob):
    try:
        obj = json.loads(blob)
    except Exception:
        return None
    vals = []
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
        elif isinstance(o, str) and WALLCLOCK_RE.match(o):
            vals.append(o)
    walk(obj)
    return max(vals) if vals else None

def take_new_snapshot(path):
    b2, b3 = show(f":2:{path}"), show(f":3:{path}")
    assert b2 is not None and b3 is not None, f"stages missing for {path}"
    t2, t3 = probe_max_ts(b2), probe_max_ts(b3)
    side = 3 if (t3 and (not t2 or t3 > t2)) else 2
    blob = b3 if side == 3 else b2
    json.loads(blob)  # parse-verify
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(blob)
    print(f"{path}: :2:={t2} :3:={t3} -> side {side}")

def union_jsonl(path):
    b2, b3 = show(f":2:{path}"), show(f":3:{path}")
    assert b2 is not None and b3 is not None, f"stages missing for {path}"
    l2 = [l for l in b2.split(b"\n") if l.strip()]
    l3 = [l for l in b3.split(b"\n") if l.strip()]
    seen, merged = set(), []
    for l in l2 + l3:
        if l not in seen:
            seen.add(l); merged.append(l)
    assert len(merged) == len(set(l2) | set(l3)), "union count mismatch"
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(b"\n".join(merged) + b"\n")
    print(f"{path}: |A|={len(l2)} |B|={len(l3)} -> |A u B|={len(merged)} zero-loss")

take_new_snapshot("results/saturation_engine/face_bm-a.json")
take_new_snapshot("results/saturation_engine/state_bm-a.json")
union_jsonl("results/saturation_engine/history_bm-a.jsonl")
print("ENGINE FACE RESOLUTIONS DONE")
