# -*- coding: utf-8 -*-
t = open('CODELY.md', encoding='utf-8').read()
lines = t.splitlines()
out = ['total lines: %d | bytes: %d' % (len(lines), len(t.encode('utf-8')))]
for i in range(max(0, len(lines) - 14), len(lines)):
    out.append('%d %s' % (i, lines[i][:110]))
open('results/_r570bma_codely_tail.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
