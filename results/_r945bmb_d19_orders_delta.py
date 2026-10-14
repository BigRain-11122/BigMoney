# r945 bm-b: D-19 orders delta extraction v2 -- locate old content by sha1 in group git history
import subprocess, difflib, io, os, sys, hashlib

GROUP = r"C:\Fluxgroup\FluxGroup"
OLD_SHA = "1176e4c470a59ba19c7b9a7fd0a90062f596c02f"
FRESH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r686bmb_orders_fresh.md")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r945bmb_d19_orders_delta.txt")

if not os.path.isdir(GROUP):
    print("GROUP_TREE_MISSING", GROUP); sys.exit(2)

# fresh content + verify its sha1 matches probe
with io.open(FRESH, "rb") as f:
    fresh_bytes = f.read()
fresh_sha = hashlib.sha1(fresh_bytes).hexdigest()
print("fresh_sha1=" + fresh_sha)

# walk history of docs/orders.md to find old content
r = subprocess.run(["git", "-C", GROUP, "log", "--format=%H", "-n", "60", "origin/main", "--", "docs/orders.md"],
                   capture_output=True)
if r.returncode != 0:
    print("LOG_FAIL", r.stderr[:200].decode("utf-8", "replace")); sys.exit(2)
commits = r.stdout.decode().split()
old_bytes = None; old_commit = None
for c in commits:
    rr = subprocess.run(["git", "-C", GROUP, "show", "%s:docs/orders.md" % c], capture_output=True)
    if rr.returncode != 0:
        continue
    if hashlib.sha1(rr.stdout).hexdigest() == OLD_SHA:
        old_bytes = rr.stdout; old_commit = c; break
if old_bytes is None:
    print("OLD_VERSION_NOT_FOUND_in_%d_commits" % len(commits)); sys.exit(2)
print("old_commit=" + old_commit)

old_text = old_bytes.decode("utf-8", "surrogateescape")
new_text = fresh_bytes.decode("utf-8", "surrogateescape")
old_lines = old_text.splitlines(keepends=True)
new_lines = new_text.splitlines(keepends=True)
diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="orders@" + OLD_SHA[:8], tofile="orders@fresh", n=1))
add_only = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
rem_only = [l for l in diff if l.startswith("-") and not l.startswith("---")]
with io.open(OUT, "w", encoding="utf-8") as f:
    f.writelines(diff)
print("delta_lines_total=%d added=%d removed=%d" % (len(diff), len(add_only), len(rem_only)))
print("out=%s bytes=%d" % (OUT, os.path.getsize(OUT)))
