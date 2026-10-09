# -*- coding: utf-8 -*-
import io

n1n = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8',
              newline='').read().replace('\r\n', '\n')
pfn = io.open('scripts/perpetual_faces.py', encoding='utf-8',
              newline='').read().replace('\r\n', '\n')


def show(text, tag, needle, before=10, after=90):
    i = text.find(needle)
    print('---', tag, 'found at', i)
    if i >= 0:
        print(repr(text[i - before:i + after]))


# mat face regions
i = n1n.find('    # --- W194 materializer face')
j = n1n.find('    _set_wave(2)', i)
chunk = n1n[i:j + len('    _set_wave(2)')]
show(chunk, 'mat-refused-comment', 'is REFUSED at its own start', 0, 80)
show(chunk, 'mat-refused-assert', 'REFUSED at its own start by the W193 B', 30, 60)
# cfg regions
c0 = n1n.find('194: {"batch": "PERPETUAL-N1-W194"')
c1 = n1n.find('"engine_owner": "bm-a"},', c0)
cfg = n1n[c0:c1 + len('"engine_owner": "bm-a"},')]
show(cfg, 'cfg-arith-refused', 'arithmetic continuation 441_404', 0, 110)
show(cfg, 'cfg-aseed-line', '"a_seed_base": 441_604', 0, 320)
show(cfg, 'cfg-staircase-span', 'staircase card); W1..W193', 0, 200)
# pf regions
p0 = pfn.find('    # W194 (bm-a r905 freeze')
p1 = pfn.find('"engine_owner": "bm-a"},', p0)
pf = pfn[p0:p1 + len('"engine_owner": "bm-a"},')]
show(pf, 'pf-refused-line', 'REFUSED at its own start by the W193 B band', 30, 60)
print('--- cfg staircase span with newlines:')
k = cfg.find('staircase card); W1..W193')
print(repr(cfg[k:k + 260]))
