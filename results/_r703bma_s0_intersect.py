# r703 bm-a S0 probe 2: dirty-tree x origin-wave intersection (r437 law)
import subprocess

def git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout

origin_files = set(l.strip() for l in git(["diff", "--name-only", "HEAD..origin/main"]).splitlines() if l.strip())
st = git(["status", "--porcelain"])
local_paths = set()
for l in st.splitlines():
    if not l.strip():
        continue
    p = l[3:].strip()
    if p.startswith('"') and p.endswith('"'):
        p = p[1:-1]
    local_paths.add(p)
inter = origin_files & local_paths
print("origin_touched=", len(origin_files), " local_dirty=", len(local_paths), " INTERSECTION=", len(inter))
for f in sorted(inter):
    print("  INT:", f)
print("--- origin wave files (first 40) ---")
for f in sorted(origin_files)[:40]:
    print("  O:", f)
