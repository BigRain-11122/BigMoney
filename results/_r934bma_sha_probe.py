# -*- coding: utf-8 -*-
import subprocess, difflib, io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
CNW = 0x08000000
r = subprocess.run([GIT, "-C", ROOT, "show", "c76a84dc2:research/PERPETUAL_N1_W202_PREREG.md"],
                   capture_output=True, creationflags=CNW)
blob = r.stdout.decode("utf-8")
cur = io.open(ROOT + r"\research\PERPETUAL_N1_W202_PREREG.md", encoding="utf-8").read()
b = blob.splitlines()
c = cur.splitlines()
for line in difflib.unified_diff(b, c, "blob", "current", lineterm="", n=1):
    print(line)
# which commit changed it?
r2 = subprocess.run([GIT, "-C", ROOT, "log", "--format=%h %s", "-n", "3",
                     "--", "research/PERPETUAL_N1_W202_PREREG.md"],
                    capture_output=True, creationflags=CNW)
print(r2.stdout.decode("utf-8", "replace"))
