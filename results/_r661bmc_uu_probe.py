# -*- coding: utf-8 -*-
# r661 bm-c rebase UU face probe: structure + ts of stage2/3 for aggregate faces
import json, subprocess, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CNW = 0x08000000

def blob(stage, path):
    r = subprocess.run(["git", "cat-file", "-p", ":%d:%s" % (stage, path)],
                       capture_output=True, creationflags=CNW)
    return r.stdout

for path in ("results/token_usage.json", "results/compute_audit.json",
             "results/dashboard_status.json", "results/update_status.json"):
    print("=" * 20, path)
    for st in (2, 3):
        b = blob(st, path)
        try:
            d = json.loads(b)
            keys = sorted(d.keys()) if isinstance(d, dict) else type(d).__name__
            ts = d.get("ts") or d.get("generated") or d.get("updated") or ""
            print(" stage%d dict-keys=%s ts=%s bytes=%d" % (st, keys, ts, len(b)))
            if path == "results/token_usage.json" and isinstance(d, dict):
                for k, v in sorted(d.items()):
                    if isinstance(v, dict):
                        inner_ts = v.get("ts") or v.get("updated_at") or v.get("last_ts") or ""
                        print("   .%s sub-keys=%s ts=%s" % (k, sorted(v.keys())[:8], inner_ts))
        except Exception as e:
            print(" stage%d non-json/err %s bytes=%d" % (st, e, len(b)))
