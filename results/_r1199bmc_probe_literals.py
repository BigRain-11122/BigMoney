# -*- coding: utf-8 -*-
"""r1199 bm-c: literal-count probe for the W310 six-gate canon-clone (r1171/r1184 law:
count table first, generator second)."""
import io

n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
TOKENS = [
    'law sec.4 W310 A: 697_301..699_300',
    'law sec.4 W310 B: 699_301..699_500',
    'law sec.4 W309 A: 695_101..697_100',
    'law sec.4 W309 B: 697_101..697_300',
    'n1_w310',
    'n1_w310_results.json',
    'a_seed_base_697301',
    'b_exit_seed_base_699301',
    '_set_wave(310)',
    '_set_wave(309)',
    '_set_wave(305)',
    '310: {"batch": "PERPETUAL-N1-W310"',
    '309: {"batch": "PERPETUAL-N1-W309"',
    '695101',
    '697101',
    '692901',
    '694901',
    '697301',
    '699301',
]
for t in TOKENS:
    print('%4d  %s' % (n1.count(t), t))