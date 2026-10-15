# -*- coding: utf-8 -*-
# _r1025bmc_clone_atomic.py -- clone git-atomic-push.py for bm-c group-tree root
src = open('K:/Fluxgroup/FluxGroup/Tools/git-atomic-push.py', encoding='utf-8').read()
old = 'ROOT = r"C:\\Users\\sjs20\\Desktop\\FluxGroup"'
new = 'ROOT = r"K:\\Fluxgroup\\FluxGroup"'
assert old in src, 'ROOT anchor not found in source tool'
out = src.replace(old, new)
open('Tools/git-atomic-push-bmc.py', 'w', encoding='utf-8', newline='').write(out)
print('cloned OK -> Tools/git-atomic-push-bmc.py (ROOT=K: group tree)')
