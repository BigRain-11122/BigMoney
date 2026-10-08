"""r774 bm-c ORD-delta lane probe (facts-driven, read-only): locate MV review
package contract path on group origin, scan fleet tickets for open/claimed,
check very-recent mv_work scratch activity (claim-collision avoidance)."""
import glob
import json
import os
import subprocess

G = r"K:\Fluxgroup\FluxGroup"
R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

p = subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)
print("gfetch_rc", p.returncode)
t = subprocess.run(["git", "-C", G, "ls-tree", "-r", "--name-only", "origin/main"],
                   capture_output=True)
tt = t.stdout.decode("utf-8", "replace")
hits = [l for l in tt.splitlines()
        if "REVIEW-PACKAGE" in l or "review-package" in l]
print("review_pkg_paths", len(hits))
for h in hits[:10]:
    print("P:", h)
# mv_work scratch face (untracked, frozen lane)
mv = os.path.join(R, "results", "mv_work")
if os.path.isdir(mv):
    entries = sorted(os.listdir(mv))
    print("mv_work_entries", len(entries))
    for e in entries[-12:]:
        fp = os.path.join(mv, e)
        mt = os.path.getmtime(fp)
        import datetime
        print("MV:", e, datetime.datetime.fromtimestamp(mt).isoformat(timespec="minutes"))
else:
    print("mv_work_missing")
# fleet tickets non-done
for f in sorted(glob.glob(os.path.join(R, "fleet", "tasks", "*.json"))):
    try:
        j = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("TKERR", os.path.basename(f), e)
        continue
    st = j.get("status")
    if st in ("open", "claimed", "in_progress"):
        print("TK:", os.path.basename(f), st, j.get("claimed_by", ""),
              str(j.get("subject", ""))[:80])
