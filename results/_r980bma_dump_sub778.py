# -*- coding: utf-8 -*-
import io, json
d = json.load(io.open(r'results/_r980bma_sub_audit.json', encoding='utf-8'))
buf = []
for r in d:
    if r['sub'] in (7, 8, 26):
        buf.append('===== SUB#%d OLD =====' % r['sub'])
        buf.append(r['old'])
        buf.append('----- NEW -----')
        buf.append(r['new'])
        buf.append('')
io.open(r'results/_r980bma_sub778_26.txt', 'w', encoding='utf-8', newline='').write('\n'.join(buf))
print('written')
