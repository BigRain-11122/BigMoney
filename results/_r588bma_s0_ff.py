# r588 bm-a S0 pure-FF integration (r578/r585 law: update-ref + reset --mixed + per-face checkout)
import subprocess, sys

def git(args, **kw):
    r = subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    return r.returncode, r.stdout, r.stderr

old_head = git(["rev-parse", "HEAD"])[1].strip()
origin = git(["rev-parse", "origin/main"])[1].strip()
# FF check: old_head must be ancestor of origin
rc, out, err = git(["merge-base", "--is-ancestor", old_head, origin])
if rc != 0:
    print("NOT-FF abort:", old_head, origin); sys.exit(1)

# Locally dirty files (protect from checkout)
rc, status, _ = git(["status", "--porcelain"])
dirty = set()
for line in status.splitlines():
    p = line[3:].strip().strip('"')
    dirty.add(p)

# Origin-diff file list
rc, diff, _ = git(["diff", "--name-only", "-z", old_head, origin])
files = [f for f in diff.split("\0") if f]
checkout = [f for f in files if f not in dirty]

rc1, _, e1 = git(["update-ref", "refs/heads/main", origin, old_head])
rc2, _, e2 = git(["reset", "--mixed", origin])
if rc1 != 0 or rc2 != 0:
    print("FAIL update-ref/reset:", e1, e2); sys.exit(1)

if checkout:
    rc3, _, e3 = git(["checkout", "--"] + checkout)
    if rc3 != 0:
        print("FAIL checkout:", e3); sys.exit(1)

rc, fin, _ = git(["status", "-sb"])
print(fin.splitlines()[0])
print("old_head", old_head[:9], "-> new", origin[:9])
print("dirty_preserved", len(dirty), "checked_out", len(checkout), "skipped_dirty", len(files) - len(checkout))
rc, rem, _ = git(["rev-list", "--count", "main..origin/main"])
print("behind_after", rem.strip())
