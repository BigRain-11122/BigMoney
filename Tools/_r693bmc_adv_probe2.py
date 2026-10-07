"""r693 bm-c advisory-evidence probe leg-2: full FUND-DIVLOWVOL-P1-NULLS
pool entry + full crash-fuse DIVLOWVOL record + fund_divlowvol_p1 results
dir census (progress faces visible from this machine)."""
import glob
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

with open(os.path.join(REPO, "results", "runnable_pool.json"), encoding="utf-8") as fh:
    pool = json.load(fh)
entries = pool.get("entries", pool if isinstance(pool, list) else [])
for e in entries:
    if isinstance(e, dict) and e.get("id") == "FUND-DIVLOWVOL-P1-NULLS":
        print("== NULLS full entry:")
        print(json.dumps(e, ensure_ascii=False, indent=1))

with open(os.path.join(REPO, "results", "crash_fuse.json"), encoding="utf-8") as fh:
    fuse = json.load(fh)
sigs = fuse.get("sigs", {})
for k, v in sigs.items():
    if "divlowvol" in k.lower() or "divlowvol" in json.dumps(v).lower():
        print("== fuse DIVLOWVOL record [%s]:" % k)
        print(json.dumps(v, ensure_ascii=False, indent=1))
print("== fuse active:", fuse.get("active"), "| cleared:", len(fuse.get("cleared", {})))

d = os.path.join(REPO, "results", "fund_divlowvol_p1")
if os.path.isdir(d):
    files = sorted(os.listdir(d))
    print("== results/fund_divlowvol_p1:", len(files), "files;", files[-12:])
    for f in files:
        if "null" in f.lower() or "progress" in f.lower() or "checkpoint" in f.lower():
            fp = os.path.join(d, f)
            print("   ", f, os.path.getsize(fp), "B")
else:
    print("== results/fund_divlowvol_p1 MISSING")

for pat in ("results/*divlowvol*", "results/fund_divlowvol_p1/*"):
    for f in sorted(glob.glob(os.path.join(REPO, pat))):
        base = os.path.basename(f)
        if base.startswith("_") and ("null" in base.lower() or "watch" in base.lower() or "burn" in base.lower()):
            print("== misc:", base, os.path.getsize(f), "B")
