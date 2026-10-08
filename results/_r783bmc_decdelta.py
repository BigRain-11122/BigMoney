"""r783 bm-c S7 closing double-sweep DEC delta probe: locate prev DEC blob
(EE70CEF0) in recent group history, unified diff vs origin/main, write
results/_r783bmc_dec_delta.txt. Facts-driven (r583 law)."""
import hashlib
import os
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PREV_SHA = "EE70CEF0F4A5E3B8DB4C67936CE2A2AEEE222FFF8D03F33339B390EAC814AC8C"


def git_out(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True)
    return p.returncode, p.stdout, p.stderr


rc, hist, _ = git_out(["rev-list", "-15", "origin/main", "--", "docs/decisions.md"])
prev_commit = None
for c in hist.decode("utf-8", "replace").split():
    rc2, blob, _ = git_out(["show", "%s:docs/decisions.md" % c])
    if hashlib.sha256(blob).hexdigest().upper() == PREV_SHA:
        prev_commit = c
        break
print("prev_commit:", prev_commit)
if prev_commit:
    rc3, diff, _ = git_out(["diff", "--unified=0",
                            "%s:docs/decisions.md" % prev_commit,
                            "origin/main:docs/decisions.md"])
    dtxt = diff.decode("utf-8", "replace")
    with open(os.path.join(REPO, "results", "_r783bmc_dec_delta.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(dtxt)
    added = [l for l in dtxt.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in dtxt.splitlines() if l.startswith("-") and not l.startswith("---")]
    print("added_rows:", len(added), "removed_rows:", len(removed))
    for l in added:
        print("ADDED:", l[:400])
