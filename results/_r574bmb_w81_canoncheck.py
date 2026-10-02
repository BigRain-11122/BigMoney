# -*- coding: utf-8 -*-
"""r574 bm-b: canon anchor checks + W82+ projection pre-check for the W81 canon row."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

canon = open(os.path.join(ROOT, 'research', 'PERPETUAL_FACES.md'), encoding='utf-8').read()
print('leg0b prose A (205_004..207_003):', '205_004..207_003' in canon)
print('leg0b prose B (53_801..54_000):', '53_801..54_000' in canon)
anchor = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
print('canon sec.5 anchor count:', canon.count(anchor))
print('canon W80 row count:', canon.count('- N1 \u6ce280\uff08'))
print('canon eol:', 'CRLF' if '\r\n' in canon else 'LF')

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
w82_a = (207_004, 209_003)
w82_b = (54_201, 54_400)
a_hits = sorted(p for p in points if w82_a[0] <= p <= w82_a[1])
b_hits = sorted(p for p in points if w82_b[0] <= p <= w82_b[1])
print('W82+ proj A 207_004..209_003 hits:', a_hits)
print('W82+ proj B 54_201..54_400 hits:', b_hits)

def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])
for w, cfg in N1_BANDS.items():
    for key in ('a', 'b_exit'):
        if overlaps(tuple(cfg[key]), w82_a):
            print('W82+ A overlap W%d.%s' % (w, key))
        if overlaps(tuple(cfg[key]), w82_b):
            print('W82+ B overlap W%d.%s' % (w, key))
print('SEED_REGISTRY size:', len(science_gates.SEED_REGISTRY))
print('W81 candidate A overlap check vs W80:', overlaps((205_004, 207_003), tuple(N1_BANDS[80]['a'])))
print('W81 candidate B overlap check vs W80:', overlaps((54_001, 54_200), tuple(N1_BANDS[80]['b_exit'])))
