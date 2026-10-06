# -*- coding: utf-8 -*-
import io
import re
import subprocess

raw = subprocess.run(["git", "show", "6957f509e^:scripts/perpetual_faces.py"],
                     capture_output=True).stdout
src = raw.decode("utf-8")
i = src.find("    # W157 (bm-a r772 freeze")
k = src.find('157: {"a": (360_204, 362_203)', i)
blk = src[i:k]
print("W157 block freezer lines:")
for m in re.finditer(r"W1\d\d A window;[^\n]*", blk):
    print("  ", repr(m.group(0)))
print("W157 block projection header:")
for m in re.finditer(r"W1\d\d\+ projection[^\n]*", blk):
    print("  ", repr(m.group(0)))
print("old2 count in block:", blk.count("W158 A window; W158 freezer MUST re-derive on the post-W157"))
p = blk.find("W157+ projection")
print("raw projection region:")
print(blk[p:p + 700])
