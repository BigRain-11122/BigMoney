import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    return r.stdout


for path in ["results/daily_scorecard.json",
             "results/paper_export/latest.json",
             "results/paper_export/export-2026-09-30.json"]:
    print("=====", path)
    sides = {}
    for rev in ("HEAD", "MERGE_HEAD"):
        b = show(rev, path)
        d = json.loads(b.decode("utf-8"))
        sides[rev] = d
        print(f"-- {rev} top keys:", list(d)[:12])
        for k, v in list(d.items())[:8]:
            print("   ", k, "=", str(v)[:100])
    o, t = sides["HEAD"], sides["MERGE_HEAD"]
    if isinstance(o, dict) and isinstance(t, dict):
        for k in sorted(set(o) | set(t)):
            if k not in o:
                print("   THEIRS-ONLY KEY:", k)
            elif k not in t:
                print("   OURS-ONLY KEY:", k)
            elif o[k] != t[k]:
                print("   DIFF KEY:", k, "| ours=", str(o[k])[:80],
                      "| theirs=", str(t[k])[:80])
