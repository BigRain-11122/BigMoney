# r379 post-surgical face checkout (r578 classifier + r374 stale-face law + r378 dead-gap prevention)
import subprocess

def git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", creationflags=0x08000000)

r = git(["status", "--porcelain"])
restore, keep_m = [], 0
for line in r.stdout.splitlines():
    if len(line) < 4:
        continue
    xy, path = line[:2], line[3:]
    if xy == " D" or xy == "D ":
        restore.append(path)
    elif "M" in xy:
        keep_m += 1
print("worktree-missing faces to restore:", len(restore), "| M faces (keep/live-writer):", keep_m)
if restore:
    for p in restore[:10]:
        print("  D:", p)
    rc = subprocess.run(["git", "checkout", "--"] + restore, capture_output=True,
                         text=True, encoding="utf-8", errors="replace", creationflags=0x08000000)
    print("checkout rc=", rc.returncode, (rc.stderr or "")[-200:])
r2 = git(["status", "--porcelain"])
lines = [l for l in r2.stdout.splitlines() if l.strip()]
print("post status lines:", len(lines))
for l in lines[:12]:
    print(" ", l[:100])
