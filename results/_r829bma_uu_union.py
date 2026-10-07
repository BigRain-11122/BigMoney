# -*- coding: utf-8 -*-
"""r829 UU union-face resolver driver: materialize :1:/:2:/:3: stage blobs to
temp files, run merge_lane_views resolve per face (union laws), write out."""
import subprocess
import sys
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UNION_FACES = [
    "results/compute_audit.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

os.makedirs("results/_r829_uu_tmp", exist_ok=True)
fails = []
for rel in UNION_FACES:
    base = rel.replace("/", "_").replace("\\", "_").replace(".", "_")
    paths = {}
    ok = True
    for stage in (1, 2, 3):
        r = subprocess.run(["git", "show", f":{stage}:{rel}"], capture_output=True)
        if r.returncode != 0:
            print(f"SKIP {rel}: :{stage}: blob missing")
            ok = False
            break
        p = f"results/_r829_uu_tmp/{base}_s{stage}.json"
        open(p, "wb").write(r.stdout)
        paths[stage] = p
    if not ok:
        fails.append((rel, "stage-missing"))
        continue
    r = subprocess.run(
        ["python", "scripts\\merge_lane_views.py", "resolve", rel,
         "--stage1", paths[1], "--stage2", paths[2], "--stage3", paths[3],
         "--out", rel],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (r.stdout or r.stderr or "").strip().splitlines()
    print(f"[{r.returncode}] {rel}: {tail[-1][:140] if tail else ''}")
    if r.returncode != 0:
        fails.append((rel, r.returncode))
    for p in paths.values():
        os.remove(p)

os.rmdir("results/_r829_uu_tmp")
print("union resolves:", len(UNION_FACES) - len(fails), "ok,", len(fails), "fail")
if fails:
    print("FAILS:", fails)
    sys.exit(1)
print("ALL UNION RC0")
