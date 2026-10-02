# -*- coding: utf-8 -*-
# r570 bm-a: extract W70/W71 WAVE_CONFIGS entries + prereg structure for W72 adaptation
import io
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
out = io.StringIO()
for w in (70, 71):
    key = '%d: {"batch": "PERPETUAL-N1-W%d"' % (w, w)
    i = t.find(key)
    assert i >= 0, 'config %d not found' % w
    j = t.find('}', t.find('engine_owner', i))
    out.write('=== WAVE_CONFIGS[%d] ===\n' % w)
    out.write(t[i:i-j*-1 if False else j+2])
    out.write('\n\n')
open('results/_r570bma_cfg_extract.txt', 'w', encoding='utf-8').write(out.getvalue())
print('written, len', len(out.getvalue()))
