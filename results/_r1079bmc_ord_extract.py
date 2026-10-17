# -*- coding: utf-8 -*-
# r1079 bm-c: extract group-tree origin orders.md (verbatim bytes) + print tail rows for S0.5 judgment
import subprocess, io, sys, os

GROUP = r"K:\Fluxgroup\FluxGroup"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "_r1079bmc_ordtail.txt")

r = subprocess.run(["git", "-C", GROUP, "show", "origin/main:docs/orders.md"], capture_output=True)
if r.returncode != 0:
    sys.stderr.write("git fail: %s" % r.stderr.decode("utf-8", "replace"))
    raise SystemExit(1)
with io.open(OUT, "wb") as f:
    f.write(r.stdout)
lines = r.stdout.decode("utf-8", "replace").splitlines()
sys.stdout.write("TOTAL_LINES %d\n" % len(lines))
sys.stdout.write("\n".join(lines[-45:]))
sys.stdout.write("\n")
