# -*- coding: utf-8 -*-
# r1017 bm-a scratch: compare W244/W245 editor pickaxe query targets
import io, re

for w in (244, 245):
    t = io.open('results/_w%dbma_freeze_edits.py' % w, encoding='utf-8', newline='').read()
    print('=== W%d editor pickaxe lines ===' % w)
    for m in re.finditer(r'r = git\("log"[^\r\n]*\)', t):
        print('  ', m.group(0)[:115])
    i = t.find('w243_upstream')
    if i > 0:
        ls = t.rfind('\n', 0, i) + 1
        print('   upstream key line:', t[ls:ls + 120])
