"""r555 bm-c porcelain raw-line probe (r548 family diagnostic): dump raw
repr of lines mentioning daily_scorecard to find the exact column layout."""
import os
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000
r = subprocess.run(["git", "status", "--porcelain", "--no-renames"],
                   cwd=ROOT, capture_output=True, creationflags=CREATE)
out = (r.stdout or b"").decode("utf-8", "replace")
for ln in out.splitlines():
    if "daily_scorecard" in ln:
        print(repr(ln))
        print("len=%d head-bytes=%r" % (len(ln), ln[:6]))
# also dump first 3 lines raw for context
for i, ln in enumerate(out.splitlines()[:3]):
    print("L%d %r" % (i, ln))
