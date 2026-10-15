# -*- coding: utf-8 -*-
# r1012 bm-a: inventory + physical extraction of ALL W245 gen Phase-A OLD
# anchors from the W244 editor (results/_w244bma_freeze_edits.py).
# Zero transcribe: every OLD extracted by anchor+n_lines at run time;
# each verified count==1 in the template. Output: results/_r1012bma_w245_oldblocks/
import io, os, json

T = io.open('results/_w244bma_freeze_edits.py', encoding='utf-8').read()
OUT = 'results/_r1012bma_w245_oldblocks'
os.makedirs(OUT, exist_ok=True)

def window(anchor, n, name):
    i = T.find(anchor)
    assert i >= 0, name + ' ANCHOR NOT FOUND: ' + anchor[:60]
    ls = T.rfind('\n', 0, i) + 1
    seg = T[ls:].split('\n')[:n]
    assert seg[-1] != '', name + ' degenerate window'
    block = '\n'.join(seg)
    c = T.count(block)
    print('%-6s lines=%-3d bytes=%-5d count=%d' % (name, n, len(block), c))
    io.open(os.path.join(OUT, name + '.txt'), 'w', encoding='utf-8', newline='').write(block)
    return block

# A1 header NEW FACE block (23 lines per committed scratch a1_old)
window('# NEW FACE vs the W243 editor (honest disclosure): the W244 B band returns', 23, 'a1')
# A2 face comment+asserts block (33 lines per committed scratch old_a23)
window('# W244 FACE (probe receipt leg1 relation_asserts):', 33, 'a2')
# A3A one-liner
window('assert leg1.get("hops_A") == 0 and leg1.get("hops_B") == 0', 1, 'a3a')
# A3B one-liner
window('assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0', 1, 'a3b')
# A3C 3-line relation asserts
window('assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1")', 3, 'a3c')
# A5 pf comment B block (6 lines = B_A5_NEW shape)
window('"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",', 6, 'a5')
# A6 pf comment W245+ projection block (8 lines)
window('"    # W245+ projection (gate-derived pre-seat probe leg4, pre-W244",', 8, 'a6')
# A7 cfg PRE B text (9 lines)
window(' "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ",', 9, 'a7')
# A8 cfg PRE W245+ projection tail (5 lines, f-string face)
window('"ADMIT convention); W245+ projection per this window gate: ",', 5, 'a8')
# A9A materializer band-facts FULL comment (40 lines per committed scratch old_a9)
window('"        # band facts (law sec.4 W244 row): A = FIRST-CLEAN arithmetic",', 40, 'a9')
# A9B materializer B staircase asserts (6 lines)
window(" f'        assert WAVE_CONFIGS[244][\"b_exit_seed_base\"] == {b_lo} == {w243_b_tail} + 1, ('", 6, 'a9b')
# A9C materializer B CLEAN assert msg (3 lines)
window("f\"        arith_b244 = set(range({b_lo}, {b_hi + 1}))\"", 3, 'a9c')
# A12 print B fragments (2 lines)
window('"+ B=FIRST-CLEAN arithmetic continuation of the prior-wave B tail (B-continuation face, "', 2, 'a12')
# A13 receipt band_semantics B line (1 line)
window('"B": "FIRST-CLEAN arithmetic continuation of the prior-wave B tail', 1, 'a13')
# A14 receipt downstream_seat line (1 line)
window('"downstream_seat": "W245 seat NOT YET PUBLISHED', 1, 'a14')
# A15 band assert literal line (1 line)
window('assert (a_lo, a_hi) == (553_501, 555_500)', 1, 'a15')
# A17 cfg b_exit comment line (1 line)
window("f'{MEM_I}\"b_exit_seed_base\": {b_lo},   # law sec.4 W244 B:", 1, 'a17')
print('INVENTORY OK')
