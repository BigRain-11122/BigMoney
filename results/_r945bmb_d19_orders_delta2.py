# r945 bm-b: D-19 orders delta extraction v3 -- second delta (1bb6ffe7 -> fresh)
import subprocess, difflib, io, os, sys, hashlib

GROUP = r"C:\Fluxgroup\FluxGroup"
OLD_SHA = "1bb6ffe79ff1fa9ffbd117f7151881c5f58f629f"
FRESH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r686bmb_orders_fresh.md")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r945bmb_d19_orders_delta2.txt")

with io.open(FRESH, "rb") as f:
    fresh_bytes = f.read()
print("fresh_sha1=" + hashlib.sha1(fresh_bytes).hexdigest())

r = subprocess.run(["git", "-C", GROUP, "log", "--format=%H", "-n", "40", "origin/main", "--", "docs/orders.md"],
                   capture_output=True)
old_bytes = None; old_commit = None
for c in r.stdout.decode().split():
    rr = subprocess.run(["git", "-C", GROUP, "show", "%s:docs/orders.md" % c], capture_output=True)
    if rr.returncode == 0 and hashlib.sha1(rr.stdout).hexdigest() == OLD_SHA:
        old_bytes = rr.stdout; old_commit = c; break
if old_bytes is None:
    print("OLD_VERSION_NOT_FOUND"); sys.exit(2)
print("old_commit=" + old_commit)

old_lines = old_bytes.decode("utf-8", "surrogateescape").splitlines(keepends=True)
new_lines = fresh_bytes.decode("utf-8", "surrogateescape").splitlines(keepends=True)
diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="orders@" + OLD_SHA[:8], tofile="orders@fresh2", n=1))
add_only = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
rem_only = [l for l in diff if l.startswith("-") and not l.startswith("---")]
with io.open(OUT, "w", encoding="utf-8") as f:
    f.writelines(diff)
print("delta_lines_total=%d added=%d removed=%d" % (len(diff), len(add_only), len(rem_only)))
print("out=%s bytes=%d" % (OUT, os.path.getsize(OUT)))
