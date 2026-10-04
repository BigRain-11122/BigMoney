# -*- coding: utf-8 -*-
# r666 bm-b token_usage + crash_fuse + audit face diff probe (pre-resolution, blobs via subprocess)
import json, subprocess, io

def blob(ref, path):
    p = subprocess.run(["git", "show", ref + ":" + path], capture_output=True)
    return p.stdout if p.returncode == 0 else None

for path in ("results/token_usage.json", "results/crash_fuse.json", "results/compute_audit.json"):
    o = blob("HEAD", path)
    t = blob("MERGE_HEAD", path)
    if o is None or t is None:
        print(path, "BLOB_FAIL", o is None, t is None)
        continue
    od = json.loads(o.decode("utf-8", "replace"))
    td = json.loads(t.decode("utf-8", "replace"))
    if path.endswith("token_usage.json"):
        om = od.get("machines", {})
        tm = td.get("machines", {})
        print(path, "ours_keys", sorted(om.keys()), "| theirs_keys", sorted(tm.keys()))
        print("  ours generated:", od.get("generated"), "| theirs generated:", td.get("generated"))
        for k in sorted(set(om) | set(tm)):
            og = str((om.get(k) or {}).get("generated"))
            tg = str((tm.get(k) or {}).get("generated"))
            print("  machine", k, "ours_gen", og, "theirs_gen", tg)
    elif path.endswith("crash_fuse.json"):
        os_ = set(od.get("sigs", od).keys()) if isinstance(od.get("sigs", od), dict) else ["?"]
        print(path, "ours top keys:", list(od.keys())[:8], "| theirs top keys:", list(td.keys())[:8])
    else:
        print(path, "ours history", len(od.get("history", [])), "theirs history", len(td.get("history", [])))

def canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)
