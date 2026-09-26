# -*- coding: utf-8 -*-
"""R239 pre-push poison scan (r231/r235 laws): line-START marker check on replayed commits."""
import subprocess

out = subprocess.run(["git", "log", "-4", "--format=%H %s"], capture_output=True, text=True, encoding="utf-8", errors="replace")
commits = [ln.split(" ", 1)[0] for ln in out.stdout.splitlines() if ln.strip()]
print("scanning", len(commits), "commits")
bad = 0
for c in commits:
    files = subprocess.run(["git", "show", "--name-only", "--format=", c], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.split()
    for f in files:
        blob = subprocess.run(["git", "show", f"{c}:{f}"], capture_output=True)
        if not blob.stdout:
            continue
        n = 0
        for ln in blob.stdout.splitlines():
            if ln.startswith((b"<<<<<<<", b"=======", b">>>>>>>")):
                n += 1
        if n:
            bad += 1
            print(f"POISONED: {c[:8]} {f} markers={n}")
print("scan result:", "CLEAN" if bad == 0 else f"{bad} POISONED FILES")
