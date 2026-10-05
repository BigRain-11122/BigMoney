"""r536 bm-c S0.5: read group orders.md CEO pending-physical-items rows
(origin blob, zero tree touch) + tail of decisions for cross-check.
CREATE_NO_WINDOW per U060."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
GROUP = r"K:\Fluxgroup\FluxGroup"


def git(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


rc, out, err = git(["show", "origin/main:docs/orders.md"], GROUP)
print("rc=%d len=%d" % (rc, len(out)))
if rc == 0:
    lines = out.splitlines()
    # print last 80 lines (CEO pending physical items live at tail region)
    print("--- TAIL 80 ---")
    for l in lines[-80:]:
        print(l)
