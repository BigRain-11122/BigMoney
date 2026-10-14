# -*- coding: utf-8 -*-
# r1007 bm-a: pattern census of the committed W243 freeze-editor source
# (transform design baseline, fail-closed SUB pair counts).
src = open('results/_w243bma_freeze_edits.py', encoding='utf-8').read()
pats = [
    'w243', 'W243', 'w242', 'W242',
    '243: {"a"', '243: {"batch"', '242: {"batch"', '    242: {"a"',
    'range(16, 243)', 'range(17, 243)', 'if w < 243)', 'if w < 242)',
    'below 243', 'below-243',
    'arith_a243', 'arith_b243', 'n3r1_used243', '_set_wave(243)',
    'WAVE_CONFIGS[243]', 'WAVE_CONFIGS[242]',
    '541_404', '541_500', '541_603',
    '551_501', '553_500', '541_501', '541_700',
    '956_735', '956,735', '530_320', '530,320',
    '958,935', '532,520', '958_935', '532_520',
    'rows 232', '== 232', '== 124', '== 67',
    'bma_ordinal=125', '125th', '126th', '233rd',
    'one hundred and twenty-fifth', 'ONE HUNDRED AND TWENTY-FIFTH',
    'TWO HUNDRED AND FORTY-THIRD',
    'fifth consecutive', 'fourth consecutive', 'sixth consecutive',
    'MSG-20261014-2107', '20261014', '2026-10-14', '6207e60e9', '08df387e0',
    'r998', 'r999', 'r1000', 'r1001', 'r1002', 'r1003',
    'range(232, 242)', 'range(209, 244)', '(241, 240',
    'W244p', 'W245p', 'W244+', 'W244 freezer', 'W244 seat', 'W244p face',
    'parity rows', '101 parity', '== 100', '== 10 and',
    'legs 10', 'legs (10)',
    '_w243bma', '_w242bma',
    '4574bfeca', '5cd36464',
    'perpetual_n2_w15_gen', 'live-seed', 'LIVE-SEED', 'REFUSED', 'refuser',
    'B_live_seed_hop_face', 'B_clean_at_naive_start',
    'refused naive base', 'thirty-second', 'thirty-third',
    'W241', 'W232..W241', 'estate 90', 'W211..W231',
    'hops=1', 'hops_B", 1', 'B_naive_hops", 1',
    'first-clean', 'hop chain', 'hop_chain',
    'fourth consecutive seed-gap', 'fifth consecutive seed-gap',
    'queue-depth supply depth-1',
    'same freeze window', 'frozen W242 tpl', 'absorbed r1001 window',
    '234th', 'third consecutive', 'seventh', 'eighth',
]
for p in pats:
    print('%-42r %d' % (p, src.count(p)))
