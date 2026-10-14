# -*- coding: utf-8 -*-
import io
src = io.open(r'results\_w239bmc_prereg_derive.py', encoding='utf-8').read()
head = src.split('# ---------- apply ----------')[0]
ns = {}
exec(head, ns)
out = ns['tpl']
for i, (old, new) in enumerate(ns['SUBS'], 1):
    assert out.count(old) == 1, i
    out = out.replace(old, new)
for s in ['540_604..540_803', '542_501..544_500']:
    print('===', s)
    idx = 0
    while True:
        j = out.find(s, idx)
        if j < 0:
            break
        print('  @', j, ':', out[max(0, j-40):j+50].replace('\n', ' | ')[:120])
        idx = j + 1
