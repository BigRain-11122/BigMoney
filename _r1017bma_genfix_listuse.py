# -*- coding: utf-8 -*-
# r1017 bm-a scratch: how does the W245 editor consume the block-lines list
import io, re

t = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
i = t.find('_entry_shard_of(0, 12)')
j = t.rfind('= [', 0, i)
j2 = t.rfind('=[', 0, i)
k = min(x for x in (j, j2) if x > 0)
print('list head:', repr(t[max(0, k - 150):k + 80]))
for m in re.finditer(r'join\([A-Za-z_]+|for [A-Za-z_]+ in [A-Za-z_]+|EOL\b', t):
    s = m.start()
    if abs(s - i) < 4000:
        print('near-use @%d: %r' % (s, t[s:s + 80]))
