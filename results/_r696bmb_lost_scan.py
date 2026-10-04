"""r696 bm-b: staged-merge faces lost-theirs scan (worktree==HEAD means theirs lost)."""
import subprocess

# faces the merge staged (differ HEAD->index)
r = subprocess.run(["git", "diff", "--cached", "--name-only", "HEAD"],
                   capture_output=True)
faces = r.stdout.decode("utf-8", "replace").split()
print("staged faces:", len(faces))


def blob_bytes(rev, path):
    rr = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return rr.stdout if rr.returncode == 0 else None


def wt_bytes(path):
    try:
        return open(path, "rb").read()
    except OSError:
        return None


lost = []
live = []
for f in faces:
    if "MERGE_HEAD" in f:
        continue
    wt = wt_bytes(f)
    head = blob_bytes("HEAD", f)
    if wt is None:
        lost.append((f, "worktree-missing"))
        continue
    if head is not None and wt == head:
        lost.append((f, "worktree==HEAD (theirs content lost on disk)"))
    else:
        live.append(f)
print("== LOST-THEIRS suspects ==")
for f, why in lost:
    print("  ", f, "|", why)
print("== worktree-ahead/other (live writes or resolver output):", len(live))
for f in live:
    print("  ", f)
