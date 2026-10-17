import subprocess, hashlib, sys

GT = r"K:\Fluxgroup\FluxGroup"
TARGET = "docs/orders.md"
OLD_SHA1 = "85407b18067b3e8a4b022ec81f4e180187d871e1"
NEW_SHA1 = "ffc63a12ed726482f3e020d73e57da57185a755c"

def git(*args):
    r = subprocess.run(["git", "-C", GT] + list(args), capture_output=True)
    if r.returncode != 0:
        sys.stderr.write("GIT FAIL: " + " ".join(args) + " :: " + r.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    return r.stdout

def blob_at(rev):
    return git("show", rev + ":" + TARGET)

# recent commits touching orders.md
log = git("log", "--format=%H|%ci|%s", "-10", "origin/main", "--", TARGET).decode("utf-8", "replace")
rows = [l.split("|", 2) for l in log.splitlines() if l.strip()]

old_rev = None
new_rev = None
for h, ci, s in rows:
    b = blob_at(h)
    s1 = hashlib.sha1(b).hexdigest()
    tag = ""
    if s1 == OLD_SHA1:
        old_rev = h; tag = " <== OLD watermark"
    if s1 == NEW_SHA1:
        new_rev = h; tag = " <== NEW watermark"
    print(h[:9], ci, "sha1=" + s1[:12], tag)
    print("   subj:", s[:150].encode("unicode_escape").decode("ascii"))

if new_rev is None:
    print("FATAL: new watermark blob not found in last-10 orders.md commits")
    sys.exit(3)
if old_rev is None:
    print("FATAL: old watermark blob not found in last-10 orders.md commits (widen window)")
    sys.exit(3)

old_lines = blob_at(old_rev).decode("utf-8", "replace").splitlines()
new_lines = blob_at(new_rev).decode("utf-8", "replace").splitlines()
old_set = set(l.rstrip("\r") for l in old_lines)
new_set = set(l.rstrip("\r") for l in new_lines)
added = [l for l in new_lines if l.rstrip("\r") not in old_set]
print()
print("OLD total_lines=%d  NEW total_lines=%d  ADDED_LINES=%d" % (len(old_lines), len(new_lines), len(added)))
print("=== ADDED ROWS ===")
for l in added:
    print(l.encode("unicode_escape").decode("ascii"))
    print("---")
