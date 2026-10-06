# -*- coding: utf-8 -*-
"""Empirical settle: run the r775 vmap machinery on the pre-775 W157
pf block; print the post-vmap freezer line + old1/old2 counts."""
import io
import re
import subprocess
import sys

sys.path.insert(0, "results")
src = io.open(r"results\_r775bma_w158_freeze_edits.py", encoding="utf-8").read()
exec(src[src.find("TOK = ["):src.find("def edit(")], globals())

raw = subprocess.run(["git", "show", "6957f509e^:scripts/perpetual_faces.py"],
                     capture_output=True).stdout
pfsrc = raw.decode("utf-8")
i1 = pfsrc.find("    # W157 (bm-a r772 freeze")
k1 = pfsrc.find('157: {"a": (360_204, 362_203)', i1)
j1 = pfsrc.find('"engine_owner": "bm-a"},', k1) + len('"engine_owner": "bm-a"},')
blk157 = pfsrc[i1:j1]

post = vmap(blk157)
print("post-vmap freezer line:")
for mm in re.finditer(r"W1\d\d A window;[^\n]*", post):
    print("  ", repr(mm.group(0)))
print("post-vmap projection header:")
for mm in re.finditer(r"W1\d\d\+ projection \(gate[^\n]*", post):
    print("  ", repr(mm.group(0)))
print("old1 count:", post.count("362_204..364_203 CLEAN hops=0 / B first-clean 362_404..362_603"))
print("old2 count:", post.count("W158 A window; W158 freezer MUST re-derive on the post-W157"))
