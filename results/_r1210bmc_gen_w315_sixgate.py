# -*- coding: utf-8 -*-
"""r1210 bm-c: generate the W315 PRE-FINALIZE six-gate from the frozen W314 lineage
(results/_r1208bmc_w314_sixgate.py) as a canon-clone.

Pitfall family r1168/r1171/r1184/r1199/r1206/r1208:
  * count table printed BEFORE any write,
  * self-reference cut ('316: {') and prior-wave boundary digits sentineled FIRST,
  * exact numeric literals next (block-by-block count asserts),
  * ONE single-pass token cascade LAST (W314->W315, 313->314, 312->313),
  * sentinels untangled at the end, produced file re-counted against a CHECKS table.
"""
import io
import re

SRC = 'results/_r1208bmc_w314_sixgate.py'
DST = 'results/_r1210bmc_w315_sixgate.py'
t = io.open(SRC, encoding='utf-8').read()

STEPS = [
    # 1. self-reference / boundary digits -> sentinels (never in the numeric pass)
    (2, "'315: {'", "'@CUT@: {'"),
    (1, '703901', '@BNDA@'),
    (1, '705901', '@BNDB@'),
    # 2. current-wave numeric faces
    (3, '706101', '708301'),
    (3, '708101', '710301'),
    (1, 'law sec.4 W314 A: 706_101..708_100', 'law sec.4 W315 A: 708_301..710_300'),
    (1, 'law sec.4 W314 B: 708_101..708_300', 'law sec.4 W315 B: 710_301..710_500'),
    (1, 'WAVE = 314', 'WAVE = 315'),
    (1, 'PREV = 313', 'PREV = @PV@'),
    (1, 'PREV_TOTAL, PREV_K = 1112941, 686520',
        'PREV_TOTAL, PREV_K = 1115141, 688720'),
    (1, '_r1206bmc_w313_sixgate.py, 77th consecutive', '@LIN@, 78th consecutive'),
    (1, '77th', '78th'),
    (1, 'W313 finalize (bm-c r1206 one-pass 1,112,941/K=686,520)',
        'W314 finalize (bm-c r1208 one-pass 1,115,141/K=688,720)'),
    (1, 'shard-7/9/10 finished 19:49:36-38', 'shard-7/9/10 finished 21:02:42-44'),
]
print('== step count table ==')
for want, old, new in STEPS:
    c = t.count(old)
    print('%3d/%3d  %r -> %r' % (c, want, old[:60], new[:60]))
    assert c == want, 'step count %d != %d for %r' % (c, want, old)
    t = t.replace(old, new)

TOK = [('W314', 'W315'), ('W313', 'W314'), ('w314', 'w315'), ('w313', 'w314'),
       ('r1208', 'r1210'), ('314', '315'), ('313', '314'), ('312', '313')]
print('== wave-token pre-cascade table ==')
print({k: t.count(k) for k, _ in TOK})
pat = re.compile('|'.join(re.escape(k) for k, _ in TOK))
assert t.count('r1206') == 0, 'r1206 still present: an explicit anchor step was skipped'
out = pat.sub(lambda m: dict(TOK)[m.group(0)], t)

for sent, val in (('@CUT@', '316'), ('@BNDA@', '706101'), ('@BNDB@', '708101'),
                  ('@PV@', '314'), ('@LIN@', '_r1208bmc_w314_sixgate.py')):
    assert out.count(sent) >= 1, (sent, out.count(sent))
    out = out.replace(sent, val)

CHECKS = [
    ('WAVE = 315', 1),
    ('PREV = 314', 1),
    ('A_BASE, B_BASE = 708301, 710301', 1),
    ('PREV_TOTAL, PREV_K = 1115141, 688720', 1),
    ("'W315 five-face freeze splice'", 1),
    ('_w315bmc_freeze_receipt.json', 3),
    ('law sec.4 W315 A: 708_301..710_300', 1),
    ('law sec.4 W315 B: 710_301..710_500', 1),
    ('results/p2cal_ext/n1_w315', 1),
    ('research/PERPETUAL_N1_W315_PREREG.md', 1),
    ('_n1_face_adjudication_w315.json', 1),
    ('results/perpetual_faces/n1_w314_results.json', 2),
    ("fr['upstream_w314']", 1),
    ('results/_r1210bmc_w315_sixgate.json', 1),
    ('_r1208bmc_w314_sixgate.py, 78th consecutive', 1),
    ('W315 wave row missing', 1),
    ('315: {"batch": "PERPETUAL-N1-W315"', 1),
    ('prior_wave_314_boundary_kept', 1),
    ('w314_finalize_present', 3),
    ('"w314_finalize_product_present"', 1),
    ('w315_block_has_315', 2),
    ('whole_file_315_count', 2),
    ('k314pos', 2),
    ('after314', 4),
    ('_set_wave(315)', 2),
    ('_set_wave(314)', 4),
    ('_set_wave(305)', 2),
    ("if '316: {' in seg:", 1),
    ("seg[:seg.find('316: {')]", 1),
    ("if '315: {' in w314_seg:", 1),
    ("w314_seg[:w314_seg.find('315: {')]", 1),
    ("r'314: ", 1),
    ('_w315bmc_prereg_derive.py', 1),
    ('_w315bmc_20261024_probe_receipt.json', 1),
    ('_w315bmc_freeze_edits.py', 1),
    ("boundary = bool(m313) and '706101' in w314_seg and '708101' in w314_seg", 1),
]
print('== post-generation count table ==')
bad = []
for lit, want in CHECKS:
    got = out.count(lit)
    flag = '' if got == want else '  <-- MISMATCH'
    print('%3d/%3d  %s%s' % (got, want, lit[:70], flag))
    if got != want:
        bad.append((lit, got, want))
BANNED = ['706_101..708_100', '708_101..708_300', '1112941', '686520',
          '1,112,941', '77th', "'315: {' in seg", 'w313', 'W313', 'r1208 bm-c',
          'r1206 one-pass', '@CUT@', '706_101', '708_101']
for b in BANNED:
    if b in out:
        bad.append(('BANNED still present: ' + b, out.count(b), 0))
if bad:
    print('GENERATOR FAIL', bad)
    raise SystemExit(1)

io.open(DST, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE', DST, len(out), 'bytes')