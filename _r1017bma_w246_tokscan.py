# -*- coding: utf-8 -*-
# r1017 bm-a: W245 editor full wave-token scan (vmap construction evidence)
import io, re
T = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
lines = T.splitlines()
pats = [
    (r'W24[0-9]', 'Wref'), (r'w24[0-9]', 'wref'), (r'24[0-9]: \{"', 'dictkey'),
    (r'N1_BANDS\[24[0-9]\]', 'nbidx'), (r'N1_BANDS\.get\(24[0-9]\)', 'nbget'),
    (r'WAVE_CONFIGS\[24[0-9]\]', 'wcidx'), (r'_set_wave\(24[0-9]\)', 'setwave'),
    (r'range\(2[0-9][0-9], 24[0-9]\)', 'range24x'), (r'range\(16, 24[0-9]\)', 'range16'),
    (r'range\(17, 24[0-9]\)', 'range17'), (r'range\(232, 24[0-9]\)', 'range232'),
    (r'n1_?w24[0-9]', 'n1wref'), (r'r10[0-9][0-9]', 'roundref'),
    (r'\b5[0-9][0-9]_[0-9][0-9][0-9]\b', 'bandlit'), (r'[0-9a-f]{9}\b', 'sha16ish'),
    (r'MSG-2026[0-9]+-[0-9]+-bm-[ac]-w24[0-9]-seat', 'seatmsg'),
    (r'(hundred|consecutive|ordinal|rows 2[0-9][0-9]|bma_ordinal|owner_rows)', 'ordinals'),
    (r'(twelve|eleven|thirteen) legs', 'legcount'),
    (r'W232\.\.W24[0-9]', 'parityspan'), (r'if w < 24[0-9]\)', 'ifwless'),
    (r'w<24[0-9]', 'wlt'), (r'below 24[0-9]', 'below'),
    (r'PERPETUAL-N1-W24[0-9]', 'perpn1'), (r'PERPETUAL_N1_W24[0-9]', 'perpn1us'),
]
seen = set()
for i, l in enumerate(lines):
    hits = [name for pat, name in pats if re.search(pat, l)]
    if hits:
        key = tuple(sorted(set(hits)))
        print('%4d [%s] %s' % (i, ','.join(sorted(set(hits)))[:52], l.strip()[:118]))
print('---COUNTS---')
for s in ['W245', 'W244', 'W243', 'w245bma', 'w244bma', 'w243bma', 'n1_w245', 'n1_w244', 'n1w245',
          '245: {"batch"', '244: {"batch"', '243: {"batch"', '245: {"a"', '244: {"a"', '243: {"a"',
          '245: {{"batch"', '245: {{"a"', '_set_wave(245)', 'WAVE_CONFIGS[245]', 'WAVE_CONFIGS[244]',
          'WAVE_CONFIGS[243]', 'N1_BANDS.get(244)', 'N1_BANDS[244]', 'N1_BANDS.get(243)', 'N1_BANDS[243]',
          'range(209, 246)', 'range(16, 245)', 'range(17, 245)', 'range(232, 244)', 'list(range(232, 244))',
          'w<245', 'w<244', 'if w < 245)', 'if w < 244)', 'below 245', 'w244_a_tail', 'w244_b_tail',
          'w245_a_tail', 'w245_b_tail', 'arith_a245', 'arith_b245', 'arith_a244', 'arith_b244',
          'PERPETUAL-N1-W245', 'PERPETUAL_N1_W245', 'n1_w245_results', 'n1_w246_results',
          '542_000', '542_001', '542_200', '541_901', '542_100', '555_501', '557_500',
          'bma_ordinal=127', 'bma_ordinal=128', '127th', '128th', '235th', '236th', 'rows 234', 'rows 235',
          'rows 126', 'rows 127', '233/125', '234/126', '963,335', '536,920', '961,135', '534,720',
          '6473fb7f8', '260ffd3f8', '2b0947947', '785936d84', '29d3ab761', 'MSG-20261015-0844',
          'MSG-20261015-1328', 'W246p_', 'W247p_', 'twelfth', 'twelve legs', 'thirteen',
          'estate 90', '== 102', '!= 102', '-> 103', '103 parity', '104',
          'TWO HUNDRED AND FORTY-FIFTH', 'one hundred and twenty-seventh', 'r1013', 'r1015', 'r1016',
          'r1007', 'r1008', 'r1010', 'r1011', '12:4x', '13:2x', '14:1x']:
    print('%-42r %d' % (s, T.count(s)))
