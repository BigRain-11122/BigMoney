# -*- coding: utf-8 -*-
# _r1010bmc_group_atomic_push.py -- bm-c-adapted copy of Tools/git-atomic-push.py
# (group canon tool has ROOT hardcoded to bm-a tree; bm-c group tree = K:\Fluxgroup\FluxGroup).
# Only change: ROOT. Run with cwd = K:\Fluxgroup\FluxGroup.
src = r"K:\Fluxgroup\FluxGroup\Tools\git-atomic-push.py"
dst = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1010bmc_group_atomic_push_v2.py"
t = open(src, encoding="utf-8").read()
old = 'ROOT = r"C:\\Users\\sjs20\\Desktop\\FluxGroup"'
assert old in t, "ROOT anchor not found"
t = t.replace(old, 'ROOT = r"K:\\Fluxgroup\\FluxGroup"')
open(dst, "w", encoding="utf-8", newline="").write(t)
import re
m = re.search(r"ROOT = .*", t)
print("ADAPTED COPY WRITTEN:", dst)
print(m.group(0))
