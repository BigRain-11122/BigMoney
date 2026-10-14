import json, subprocess, sys
GIT = r"C:\Program Files\Git\cmd\git.exe"

def origin_blob(path):
    r = subprocess.run([GIT, "show", "origin/main:" + path], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

files = [
    "results/token_usage.json",
    "results/_attrition_guard_scan.json",
    "results/queue_head_collision_probe.json",
    "results/_r686bmb_d19_check.json",
]

def probe_ts(d):
    if not isinstance(d, dict):
        return "nondict:" + type(d).__name__
    for k in ("ts", "updated_at", "updated", "generated", "asof", "scan_ts"):
        if k in d:
            return f"{k}={d[k]}"
    return "keys=" + ",".join(list(d.keys())[:8])

for f in files:
    ob = origin_blob(f)
    if ob is None:
        print(f, "| origin: MISSING")
        continue
    try:
        od = json.loads(ob.decode("utf-8-sig"))
        ots = probe_ts(od)
    except Exception as e:
        ots = f"parse-err {e}"
    try:
        ld = json.load(open(f, encoding="utf-8-sig"))
        lts = probe_ts(ld)
    except Exception as e:
        lts = f"parse-err {e}"
    same = ob.decode("utf-8-sig", "replace").strip() == open(f, encoding="utf-8-sig").read().strip()
    print(f)
    print("   origin:", ots)
    print("   local :", lts)
    print("   byte-identical-after-sig:", same)
