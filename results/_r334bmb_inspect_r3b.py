# -*- coding: utf-8 -*-
"""r334 bm-b round-3 deep: dump ours CODELY full + both 二十批 archive sections."""
import io
import subprocess


def blob(stage, path):
    return subprocess.run(["git", "show", f"{stage}:{path}"],
                          capture_output=True).stdout


c = blob(":2", "CODELY.md").decode("utf-8")
print("===== OURS CODELY (9873B) FULL =====")
for l in c.splitlines():
    print(repr(l)[:230])

for tag, s in (("OURS", ":2"), ("THEIRS(mine)", ":3")):
    a = blob(s, r"research/memory-archive/202609.md").decode("utf-8")
    lines = a.splitlines()
    idx = [i for i, l in enumerate(lines) if l.startswith("## ") and "二十批" in l]
    if idx:
        i = idx[-1]
        print(f"\n===== ARCHIVE {tag} 二十批 section (line {i}..) =====")
        for l in lines[i:i + 9]:
            print(repr(l)[:160])
