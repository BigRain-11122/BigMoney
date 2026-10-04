# r689: peek top-level ts keys of 4 new conflict faces (ours HEAD side, pre-resolver)
import json, subprocess, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACES = ["results/dashboard_status.js", "results/dashboard_status.json",
         "results/scorecard_v1.json", "results/strategy_scorecard.json"]
for p in FACES:
    r = subprocess.run(["git", "show", "HEAD:" + p], cwd=ROOT, capture_output=True)
    b = r.stdout
    print("==", p, "bytes", len(b))
    if p.endswith(".js"):
        head = b[:200].decode("utf-8", "replace").replace("\n", " ")
        print("   head:", head[:180])
        continue
    try:
        o = json.loads(b.decode("utf-8"))
        ks = [k for k in o.keys()][:12]
        print("   top_keys:", ks)
        for k in ("ts", "updated", "updated_at", "generated", "generated_at",
                  "asof", "cutoff", "last_run", "scan_ts"):
            if k in o:
                print("   ts_key:", k, "=", str(o[k])[:40])
                break
    except Exception as e:
        print("   parse_err:", e)
