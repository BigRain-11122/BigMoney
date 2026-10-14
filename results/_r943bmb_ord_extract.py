"""r943 bm-b: extract group-tree docs/orders.md (raw bytes) to %TEMP% for
D-19 ORD delta consumption (r481/r686 lineage: local group tree first,
python raw-bytes face, zero PS redirection)."""
import os
import subprocess

TREES = [r"K:\Fluxgroup\FluxGroup", r"C:\Fluxgroup\FluxGroup"]
DEST = os.path.join(os.environ["TEMP"], "orders_r943.md")

for t in TREES:
    if os.path.isdir(os.path.join(t, ".git")):
        b = subprocess.check_output(
            ["git", "-C", t, "show", "origin/main:docs/orders.md"])
        with open(DEST, "wb") as f:
            f.write(b)
        print("tree=%s bytes=%d dest=%s" % (t, len(b), DEST))
        break
else:
    print("NO-GROUP-TREE")
