# -*- coding: utf-8 -*-
# r1017 bm-a scratch: byte-truth probe of gen a2 closer lines
import io

gen = io.open('results/_r1017bma_w246_gen.py', encoding='utf-8', newline='').read()
lines = gen.split('\n')
for needle in ('machine-checkable)', 'B_hop_lands_inside_A=false)'):
    hits = [n for n, ln in enumerate(lines) if needle in ln]
    print('=== %s hits: %s ===' % (needle, [h + 1 for h in hits]))
    for h in hits:
        ln = lines[h]
        print('L%d len=%d tail-bytes=%s' % (h + 1, len(ln), [hex(ord(c))[-2:] for c in ln[-16:]]))
        print('  repr: %r' % ln)
