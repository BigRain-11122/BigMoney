# r1026: verify ORD watermark phantom — compute content-sha1 of docs/orders.md at recent group-tree commits
import subprocess, hashlib

GT = r"K:\Fluxgroup\FluxGroup"
def run(args):
    r = subprocess.run(["git", "-C", GT] + args, capture_output=True)
    return r.stdout, r.stderr

log, _ = run(["log", "--format=%H|%ci|%s", "-6", "--", "docs/orders.md"])
commits = [l for l in log.decode("utf-8", "replace").splitlines() if l.strip()]
for line in commits:
    sha, ci, subj = line.split("|", 2)
    content, err = run(["show", "%s:docs/orders.md" % sha])
    if err:
        print("ERR", sha[:9], err.decode()[:80]); continue
    csha = hashlib.sha1(content).hexdigest()
    tag = ""
    if csha == "46c60d47911c3f4ac94beef90ba5e2841501129b": tag = " <== CURRENT-ORIGIN-FACE (r1025-consumed)"
    if csha == "489f21d87a2cb9307ed6d28e049348439b2b905f": tag = " <== WM-KEY (real!)"
    print("%s %s content-sha1=%s%s" % (sha[:9], ci[:16], csha[:12], tag))
    # also raw blob sha for cross-check
print("WM-KEY 489f21d8 present in history: see tags above")
