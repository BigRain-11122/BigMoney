import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    return json.loads(r.stdout.decode("utf-8"))


for rev in ("HEAD", "MERGE_HEAD"):
    d = show(rev, "results/compute_audit.json")
    print("=== ", rev, " type:", type(d).__name__)
    if isinstance(d, dict):
        for k, v in list(d.items())[:14]:
            print("  ", k, "=", str(v)[:120])
    elif isinstance(d, list):
        print("  list len", len(d), "last:", str(d[-1])[:200])
