# -*- coding: utf-8 -*-
"""r801 bm-c DEC-delta rows probe (closing sweep companion): diff group
origin/main docs/decisions.md vs last-consumed blob (sha 83813196 face),
print only NEW rows for S0.5 consumption. Zero-window CNW law."""
import subprocess

GRP = r"K:\Fluxgroup\FluxGroup"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git(args):
    p = subprocess.run(["git", "-C", GRP] + args, capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


rc, cur, _ = git(["show", "origin/main:docs/decisions.md"])
lines = cur.splitlines()
# last-consumed face: dec_sha 83813196 == r785 batch 3f4a5ec blob
rc, prev, _ = git(["show", "3f4a5ec:docs/decisions.md"]) if rc == 0 else (1, "", "")
prev_set = set(prev.splitlines())
new = [l for l in lines if l not in prev_set and l.strip()]
out = ["cur_lines=%d prev_lines=%d new_rows=%d" % (len(lines), len(prev.splitlines()), len(new))]
for l in new:
    out.append("+" + l[:1600])
open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r801bmc_dec_rows.txt", "w",
     encoding="utf-8").write("\n".join(out))
print("written results/_r801bmc_dec_rows.txt rows=%d" % len(new))
