"""r536 bm-c: which commits touched group docs/orders.md since r535 (10-05 ~11:26)?"""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
GROUP = r"K:\Fluxgroup\FluxGroup"

r = subprocess.run(["git", "log", "--since=2026-10-05T11:00:00+08:00", "--oneline",
                    "-20", "--", "docs/orders.md"], capture_output=True, cwd=GROUP,
                   creationflags=CREATE_NO_WINDOW)
print("LOG-SINCE rc=%d" % r.returncode)
print((r.stdout or b"").decode("utf-8", "replace"))
print((r.stderr or b"").decode("utf-8", "replace")[:200])
# also: last 3 commits touching orders.md regardless of time
r2 = subprocess.run(["git", "log", "-3", "--format=%h %ad %s", "--date=iso",
                     "--", "docs/orders.md"], capture_output=True, cwd=GROUP,
                    creationflags=CREATE_NO_WINDOW)
print("--- last 3 orders.md commits ---")
print((r2.stdout or b"").decode("utf-8", "replace"))
