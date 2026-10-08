# -*- coding: utf-8 -*-
"""r754 bm-c ORD delta consumption: identify commits touching docs/orders.md
since the previous watermark consumption (r753 ~10:40), print the delta rows
involving BigMoney/quant for the decision review gate."""
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


rc, out, err = git(["log", "--format=%h|%ci|%s", "-8", "origin/main", "--",
                    "docs/orders.md"])
print("recent commits touching docs/orders.md:")
print(out)
# diff of the newest touching commit for context lines
rc, out, err = git(["log", "-2", "--format=%h", "origin/main", "--",
                    "docs/orders.md"])
shas = out.split()
if len(shas) >= 2:
    rc, diff, _ = git(["diff", "%s..%s" % (shas[1], shas[0]), "--", "docs/orders.md"])
    print("=== delta diff (%s..%s) ===" % (shas[1], shas[0]))
    print(diff[:4000])
