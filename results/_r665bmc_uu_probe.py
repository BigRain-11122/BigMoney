import subprocess, json, os
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
def blob(stage, path):
    return subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True).stdout
for path in ["results/compute_audit.json", "results/token_usage.json"]:
    for s in (2, 3):
        b = blob(s, path)
        d = json.loads(b)
        print("===", path, "stage", s, "keys:", list(d.keys())[:12])
        for k, v in d.items():
            if isinstance(v, list):
                print("  ", k, ": list len", len(v), "| first:", json.dumps(v[0], ensure_ascii=False)[:220] if v else None)
            elif isinstance(v, dict):
                ks = list(v.keys())
                print("  ", k, ": dict keys", ks[:8])
            else:
                print("  ", k, "=", json.dumps(v, ensure_ascii=False)[:120])
