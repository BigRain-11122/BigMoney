# -*- coding: utf-8 -*-
"""r334 bm-b round-3 dump-to-file (console-GBK-safe)."""
import io
import subprocess


def blob(stage, path):
    return subprocess.run(["git", "show", f"{stage}:{path}"],
                          capture_output=True).stdout


out = io.open(r"results\_r334bmb_r3dump.txt", "w", encoding="utf-8", newline="")
c = blob(":2", "CODELY.md").decode("utf-8")
out.write("===== OURS(:2) CODELY FULL %dB =====\n" % len(c.encode()))
out.write(c)
for tag, s in (("OURS", ":2"), ("MINE", ":3")):
    a = blob(s, r"research/memory-archive/202609.md").decode("utf-8")
    lines = a.splitlines()
    idx = [i for i, l in enumerate(lines) if l.startswith("## ") and "二十批" in l]
    if idx:
        i = idx[-1]
        j = i + 1
        while j < len(lines) and not lines[j].startswith("## "):
            j += 1
        out.write("\n===== ARCHIVE %s 二十批 section lines %d..%d =====\n" % (tag, i, j))
        out.write("\n".join(lines[i:j]))
out.close()
print("dump written")
