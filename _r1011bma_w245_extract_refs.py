# -*- coding: utf-8 -*-
# r1011 bm-a: extract remaining OLD/reference one-liners from W244/W243 editors
import io

w243 = io.open('results/_w243bma_freeze_edits.py', encoding='utf-8').read()
w244 = io.open('results/_w244bma_freeze_edits.py', encoding='utf-8').read()

def one_line(t, needle, name):
    i = t.find(needle)
    assert i >= 0, name + ' not found'
    ls = t.rfind('\n', 0, i) + 1
    return t[ls:].split('\n')[0]

def window(t, anchor, n):
    i = t.find(anchor)
    assert i >= 0, 'anchor not found: ' + anchor[:70]
    ls = t.rfind('\n', 0, i) + 1
    seg = t[ls:].split('\n')[:n]
    assert seg[-1] != '', 'degenerate'
    return '\n'.join(seg)

# ---- A8: cfg PRE projection tail ----
seg = window(w244, 'f"W245+ projection per this window gate: "', 8)
io.open('_r1011bma_w245_old_a8.txt', 'w', encoding='utf-8').write(seg)
print('a8 old lines:', len(seg.split('\n')))
seg = window(w243, 'f"W244+ projection per this window gate: "', 7)
io.open('_r1011bma_w245_ref_a8.txt', 'w', encoding='utf-8').write(seg)
print('a8 ref lines:', len(seg.split('\n')))

# ---- A13: receipt band_semantics B line ----
seg = one_line(w244, '"B": "FIRST-CLEAN arithmetic continuation of the prior-wave B tail')
io.open('_r1011bma_w245_old_a13.txt', 'w', encoding='utf-8').write(seg)
print('a13 old len:', len(seg))
seg = one_line(w243, '"B": "LIVE-SEED-REFUSAL face (naive staircase')
io.open('_r1011bma_w245_ref_a13.txt', 'w', encoding='utf-8').write(seg)
print('a13 ref len:', len(seg))

# ---- A14: receipt downstream_seat line ----
seg = one_line(w244, '"downstream_seat": "W245 seat NOT YET PUBLISHED')
io.open('_r1011bma_w245_old_a14.txt', 'w', encoding='utf-8').write(seg)
print('a14 old len:', len(seg))
seg = one_line(w243, '"downstream_seat": "W244 seat NOT YET PUBLISHED')
io.open('_r1011bma_w245_ref_a14.txt', 'w', encoding='utf-8').write(seg)
print('a14 ref len:', len(seg))

# ---- A15: band assert literal line ----
seg = one_line(w244, 'assert (a_lo, a_hi) == (553_501, 555_500)')
io.open('_r1011bma_w245_old_a15.txt', 'w', encoding='utf-8').write(seg)
print('a15 old:', seg)

# ---- A17: cfg b_exit comment line ----
seg = one_line(w244, 'f\'{MEM_I}"b_exit_seed_base": {b_lo},')
io.open('_r1011bma_w245_old_a17.txt', 'w', encoding='utf-8').write(seg)
print('a17 old len:', len(seg))
seg = one_line(w243, 'f\'{MEM_I}"b_exit_seed_base": {b_lo},')
io.open('_r1011bma_w245_ref_a17.txt', 'w', encoding='utf-8').write(seg)
print('a17 ref len:', len(seg))

# ---- A12 print fragments (already extracted) + A9B 6-line old window fix ----
i = w244.find('f\'        assert WAVE_CONFIGS[244]["b_exit_seed_base"] == {b_lo} == {w243_b_tail} + 1, (\'')
ls = w244.rfind('\n', 0, i) + 1
seg = '\n'.join(w244[ls:].split('\n')[:6])
io.open('_r1011bma_w245_old_a9b.txt', 'w', encoding='utf-8').write(seg)
print('a9b old lines:', len(seg.split('\n')))
print(seg)
print('DONE')
