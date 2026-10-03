# -*- coding: utf-8 -*-
"""r663 bm-a: S0 netpath intersection probe (r437 law)."""
import subprocess


def lines_of(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [l for l in r.stdout.splitlines() if l.strip()]


dirty = lines_of(["git", "status", "--porcelain"])
dirty_files = [l[3:].strip().strip('"') for l in dirty if l.strip()]
diff_files = set(lines_of(["git", "diff", "--name-only", "HEAD", "origin/main"]))
inter = [f for f in dirty_files if f in diff_files]
print("dirty_count=", len(dirty_files))
for f in dirty_files:
    print("  DIRTY:", f, "| incoming:", f in diff_files)
print("intersection=", inter)
print("diff_total=", len(diff_files))
