"""r943 bm-b: D-19 ORD delta line-diff v2 -- content-sha1 face (the stored
watermark is python hashlib.sha1 of blob CONTENT, r292 raw-bytes law; git
rev-parse blob ids are a DIFFERENT hash and will never match -- v1 miss)."""
import hashlib
import subprocess

T = r"C:\Fluxgroup\FluxGroup"
OLD = "746ab69349891fbd810f2bcd7d34b8f1636063ce"


def blob(c):
    return subprocess.check_output(["git", "-C", T, "show",
                                    c + ":docs/orders.md"])


commits = subprocess.check_output(
    ["git", "-C", T, "log", "origin/main", "--format=%H", "-n", "50", "--",
     "docs/orders.md"]).decode("utf-8", "replace").split()
found = None
oldb = None
for c in commits:
    b = blob(c)
    if hashlib.sha1(b).hexdigest() == OLD:
        found = c
        oldb = b
        break
print("old_blob_commit:", (found or "NOT-FOUND")[:12],
      "(walked %d)" % len(commits))
if found:
    newb = blob("origin/main")
    old_lines = set(oldb.decode("utf-8", "replace").splitlines())
    new_lines = newb.decode("utf-8", "replace").splitlines()
    new_set = set(new_lines)
    added = [l for l in new_lines if l not in old_lines]
    removed = [l for l in old_lines if l not in new_set]
    print("added=%d removed=%d" % (len(added), len(removed)))
    for l in added[:120]:
        print("+ " + l[:400])
    for l in removed[:15]:
        print("- " + l[:200])
